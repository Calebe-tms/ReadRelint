# -*- coding: utf-8 -*-
"""
Extrator especializado de Localização, Endereço e Georreferenciamento via LLM (Passo 2 do Pipeline Multi-Pass).
"""

import logging
import re
import unicodedata
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from backend.engine.cleaners.text_cleaner import dms_to_decimal, enforce_rs_coordinate_signs, normalize_line_broken_sign
from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.engine.extractors.llm.schemas.location_schema import LocationExtraction

logger = logging.getLogger(__name__)


def sanitize_address_field(text: str) -> str:
    """
    Higieniza campos de endereço removendo ruídos narrativos, links, coordenadas e termos institucionais.
    """
    if not text:
        return ""

    s = str(text).strip()

    # 1. Trunca antes de links HTTP
    s = re.split(r'https?://', s)[0].strip()

    # 2. Trunca antes de termos de coordenadas/GPS
    s = re.split(r'(?i)\b(?:coordenadas\s*geogr[áa]ficas|coordenadas|coord\.|lat\/long|\(-?\d{1,2}\.\d+)', s)[0].strip()

    # 3. Trunca antes de verbos ou expressões narrativas institucionais
    s = re.split(
        r'(?i)\b(?:foi\s+informado|foi\s+acionad[oa]|atrav[ée]s\s+da\s+sala|via\s+telefone|chegou\s+ao\s+conhecimento|uma\s+guarni[çc][ãa]o|a\s+equipe|ap[óo]s\s+liga[çc][ãa]o|em\s+cumprimento|comunica[çc][ãa]o\s+de\s+venda|diante\s+dessas)\b',
        s
    )[0].strip()

    # 4. Remove parênteses de referências comerciais ou pontos de referência (ex: "( FARMÁCIA SÃO JOÃO )")
    s = re.sub(r'\([^\)]*\)', '', s).strip()

    # 5. Remove pontuações periféricas e ruídos isolados
    s = re.sub(r'^[,\.–—\-:;()]+|[,\.–—\-:;()]+$', '', s).strip()

    return s


def check_raw_text_geo_sources(text: str) -> Tuple[bool, bool, str, str]:
    """
    Analisa o texto bruto do documento para determinar com precisão a origem das informações geográficas:
    - has_raw_coords: True se há coordenadas explicitamente digitadas no documento.
    - has_raw_map_url: True se há link do Google Maps explicitamente presente no documento.
    Retorna: (has_raw_coords: bool, has_raw_map_url: bool, raw_coords: str, raw_map_url: str)
    """
    if not text:
        return False, False, "", ""

    text = normalize_line_broken_sign(text)

    # 1. Busca coordenadas explícitas no texto (decimal ou DMS, já convertida para decimal)
    raw_coords = ""
    match_dec = re.search(r'(-?\d{1,2}\.\d{4,8})\s*[\s,;/]+\s*(-?\d{1,2}\.\d{4,8})', text)
    if match_dec:
        raw_coords = f"{match_dec.group(1)}, {match_dec.group(2)}"
    else:
        match_dms = re.search(
            r'(\d{1,2})°\s*(\d{1,2})[\'′]\s*([\d.,]+)\"?\s*([Ss])\s*[\s,;]+\s*(\d{1,2})°\s*(\d{1,2})[\'′]\s*([\d.,]+)\"?\s*([WwOo])',
            text
        )
        if match_dms:
            lat = dms_to_decimal(match_dms.group(1), match_dms.group(2), match_dms.group(3), match_dms.group(4))
            lon = dms_to_decimal(match_dms.group(5), match_dms.group(6), match_dms.group(7), match_dms.group(8))
            raw_coords = f"{lat:.6f}, {lon:.6f}"

    # 2. Busca link explícito do Google Maps no texto
    raw_map_url = ""
    match_url = re.search(r'https?://(?:maps\.app\.goo\.gl|google\.com/maps|goo\.gl/maps)/[^\s,;><\)\']+', text)
    if match_url:
        raw_map_url = match_url.group(0).strip()

    has_coords = bool(raw_coords)
    has_map_url = bool(raw_map_url)

    return has_coords, has_map_url, raw_coords, raw_map_url


def extract_street_and_number_fallback(text: str) -> Tuple[str, str, str]:
    """
    Extrai deterministicamente rua, número e bairro do texto quando a LLM falha ou omite a rua.
    Preserva nomes compostos e abreviaturas de ruas (ex: 'Rua Elias C. Lash, 255').
    Retorna: (street, number, neighborhood)
    """
    if not text:
        return "", "", ""

    # Padrão flexível para logradouros comuns em RELINTs (sem cortar em pontos de abreviatura)
    pat = re.search(
        r'(?i)\b(?:na|no|em|localizad[oa]\s+na|localizad[oa]\s+no)\s+((?:Rua|Avenida|Av\.|Av|Travessa|Beco|Estrada|Linha|Rodovia|BR|RS)\b[^,\n\(\)]+?)(?:,\s*(?:n[oº°\.]*\s*|km\s*)?([0-9A-Za-z\/\-]+|S\/N))?(?:,\s*(?:bairro\s*)?([^,\n\(\)\-]+?))?(?:,\s*\(|\s*\(|,\s*(?:em|no|na)\s+[A-Za-zÀ-ÿ\s]+?-\s*RS|\n|-|\Z)',
        text
    )
    if pat:
        street = sanitize_address_field(pat.group(1))
        num = sanitize_address_field(pat.group(2) or "")
        neigh = sanitize_address_field(pat.group(3) or "")

        street = re.sub(r'(?i)^(?:na|no|em|localizad[oa]\s+na|localizad[oa]\s+no)\s+', '', street).strip()
        if neigh.lower().startswith("bairro"):
            neigh = re.sub(r'(?i)^bairro\s*', '', neigh).strip()
        # Se o bairro capturou 'centro de [cidade]', extrai apenas 'Centro'
        if "centro de" in neigh.lower():
            neigh = "Centro"
        return street, num, neigh

    return "", "", ""


def extract_municipality_from_context(text: str, filename: str = "") -> str:
    """
    Extrai deterministicamente o município a partir do Assunto ou do nome do arquivo.
    """
    if text:
        # Padrão: ASSUNTO: ... EM [CIDADE] - RS
        m_assunto = re.search(r'(?i)ASSUNTO\s*:\s*.*?\bem\s+([A-Za-zÀ-ÿ\s]+?)\s*-\s*RS', text)
        if m_assunto:
            muni = m_assunto.group(1).strip()
            if len(muni) > 2:
                return muni.title() if muni.isupper() else muni

    if filename:
        # Padrão no nome do arquivo: ... em [CIDADE] - RS.pdf
        m_fn = re.search(r'(?i)\bem\s+([A-Za-zÀ-ÿ\s]+?)\s*-\s*RS', filename)
        if m_fn:
            muni = m_fn.group(1).strip()
            if len(muni) > 2:
                return muni.title() if muni.isupper() else muni

    return ""


def resolve_short_maps_url(url: str, timeout: float = 3.0) -> Tuple[str, str]:
    """
    Resolve links encurtados do Google Maps (maps.app.goo.gl) seguindo o redirect
    para extrair as coordenadas latitude e longitude em formato decimal.
    Retorna tupla: (expanded_url: str, coordinates: str)
    """
    if not url or "maps.app.goo.gl" not in url:
        return url, ""

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            final_url = response.geturl()
            match = re.search(r'(-?\d{1,2}\.\d{4,8})\s*,\s*(-?\d{1,2}\.\d{4,8})', final_url)
            if match:
                coords = f"{match.group(1)}, {match.group(2)}"
                return final_url, coords
            return final_url, ""
    except Exception as err:
        logger.debug(f"Não foi possível resolver link encurtado {url}: {err}")
        return url, ""


def format_google_standard_address(
    street: str = "",
    number: str = "",
    neighborhood: str = "",
    municipality: str = ""
) -> str:
    """
    Monta o endereço no padrão oficial: Logradouro, nº [ou S/N] - Bairro, Município - RS
    Descarta automaticamente placeholders como 'Sem informação', 'Não informado', etc.
    """
    INVALID_PLACEHOLDERS = {
        "sem informação", "sem informacao", "não informado", "nao informado",
        "não consta", "nao consta", "não possui", "nao possui", "n/i", "n/a",
        "none", "null", "desconhecido", "xxx", "-"
    }

    clean_street = sanitize_address_field(street or "")
    clean_number = sanitize_address_field(number or "")
    clean_neigh = sanitize_address_field(neighborhood or "")
    clean_muni = sanitize_address_field(municipality or "")

    if clean_street.lower() in INVALID_PLACEHOLDERS:
        clean_street = ""
    if clean_number.lower() in INVALID_PLACEHOLDERS:
        clean_number = ""
    if clean_neigh.lower() in INVALID_PLACEHOLDERS:
        clean_neigh = ""
    if clean_muni.lower() in INVALID_PLACEHOLDERS:
        clean_muni = ""

    # Normalização de zona rural para o bairro
    is_rural = any(term in clean_street.lower() for term in ["linha", "estrada", "assentamento", "interior", "fazenda", "br-", "rs-", "rodovia"])
    if is_rural and not clean_neigh:
        clean_neigh = "Interior"

    parts = []
    if clean_street:
        if clean_number:
            # Se o número for indicação de Km (ex: 'Km 47'), anexa com vírgula se a rua já não contiver
            if "km" in clean_number.lower():
                if "km" not in clean_street.lower():
                    parts.append(f"{clean_street}, {clean_number}")
                else:
                    parts.append(clean_street)
            # Se a rua já contiver explicitamente 'nº 123' ou ', 123'
            elif re.search(r'\b(?:n[oº°]?\s*)\d+\b', clean_street, re.IGNORECASE) or re.search(r',\s*\d+\b', clean_street):
                parts.append(clean_street)
            else:
                num_str = f"nº {clean_number}" if clean_number.upper() != "S/N" else "S/N"
                parts.append(f"{clean_street}, {num_str}")
        else:
            parts.append(clean_street)

    formatted = ", ".join(parts)

    if clean_neigh and clean_neigh.lower() not in formatted.lower():
        if formatted:
            formatted = f"{formatted} - {clean_neigh}"
        else:
            formatted = clean_neigh

    if clean_muni:
        if clean_muni.lower() not in formatted.lower():
            if formatted:
                formatted = f"{formatted}, {clean_muni} - RS"
            else:
                formatted = f"{clean_muni} - RS"
        elif not formatted.endswith("- RS") and not formatted.endswith("RS"):
            formatted = f"{formatted} - RS"

    return formatted.strip(" ,-") or "-"


def normalize_for_match(value: str) -> str:
    """Normaliza texto para comparação tolerante: remove acento, baixa a caixa e colapsa espaços."""
    if not value:
        return ""
    stripped_accents = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r'\s+', ' ', stripped_accents).strip().lower()


def text_contains(candidate: str, text: str) -> bool:
    """Verifica se um valor aparece literalmente no texto, tolerando acento/caixa/espaçamento."""
    norm_candidate = normalize_for_match(candidate)
    return bool(norm_candidate) and norm_candidate in normalize_for_match(text)


# Tabela determinística de área de cobertura territorial dos batalhões da Brigada Militar.
# Fonte: fornecida pelo usuário. Único critério primário para resolução de 'police_unit'.
MUNICIPALITY_TO_BATTALION: Dict[str, str] = {}


def _register_battalion_coverage(battalion: str, municipalities: List[str]) -> None:
    for municipality in municipalities:
        MUNICIPALITY_TO_BATTALION[normalize_for_match(municipality)] = battalion


_register_battalion_coverage("16º BPM", [
    "Cruz Alta", "Boa Vista do Cadeado", "Pejuçara", "Ibirubá", "XV de Novembro",
    "Fortaleza dos Valos", "Selbach", "Saldanha Marinho", "Salto do Jacuí",
    "Boa Vista do Incra", "Jacuizinho",
])
_register_battalion_coverage("37º BPM", [
    "Frederico Westphalen", "Caiçara", "Seberi", "Erval Seco", "Palmitinho",
    "Pinheirinho do Vale", "Taquaruçu do Sul", "Vista Alegre", "Planalto",
    "Alpestre", "Ametista", "Rodeio Bonito", "Cristal do Sul", "Iraí", "Vicente Dutra",
])
_register_battalion_coverage("39º BPM", [
    "Palmeira das Missões", "Panambi", "Novo Barreiro", "São Pedro das Missões",
    "São José das Missões", "Dois Irmãos das Missões", "Boa Vista das Missões",
    "Jaboticaba", "Cerro Grande", "Pinhal", "Novo Tiradentes", "Lajeado do Bugre",
    "Sagrada Família", "Condor", "Santa Bárbara do Sul",
])


def resolve_battalion_by_municipality(municipality: str) -> str:
    """Consulta a tabela fixa de município -> BPM territorial (fonte primária)."""
    return MUNICIPALITY_TO_BATTALION.get(normalize_for_match(municipality), "")


def extract_battalion_mentions(text: str) -> List[str]:
    """Retorna a lista de números de batalhão válidos (16/37/39) citados literalmente no texto, sem duplicar."""
    if not text:
        return []
    mentions: List[str] = []
    for match in re.finditer(r'\b(\d{1,2})[º°]?\s*BPM\b', text, re.IGNORECASE):
        number = match.group(1)
        if number in ("16", "37", "39") and number not in mentions:
            mentions.append(number)
    return mentions


def resolve_police_unit(municipality: str, text: str) -> str:
    """
    Resolve 'police_unit' em 3 camadas 100% determinísticas (campo não passa mais pela LLM):
    1. Exatamente 1 batalhão citado literalmente no texto -> o texto decide (cobre apoio mútuo entre batalhões).
    2. Zero ou mais de uma menção (ambíguo) -> a tabela de município decide.
    3. Município fora da tabela e sem menção literal única -> vazio.
    """
    mentions = extract_battalion_mentions(text)
    if len(mentions) == 1:
        return f"{mentions[0]}º BPM"
    return resolve_battalion_by_municipality(municipality)


class LocationExtractor:
    """
    Extrator cognitivo dedicado para geolocalização, endereçamento e coordenadas.
    """

    def __init__(self, processor: ILlmProcessor) -> None:
        self.processor = processor

    def extract(self, text: str, filename: str = "") -> Dict[str, Any]:
        """
        Executa o Pass 2 focado exclusivamente na extração da localização.
        Classifica estritamente a precisão em 3 níveis:
        - Alta: Coordenadas encontradas explicitamente no texto do documento.
        - Média: Link do Google Maps encontrado no documento (coordenadas geradas via link).
        - Baixa: Somente endereço no documento (coordenadas/links gerados por busca com município).
        """
        # Corrige de saída o artefato de quebra de linha do PyMuPDF entre um "-" isolado e o dígito seguinte
        text = normalize_line_broken_sign(text)

        has_raw_coords, has_raw_map_url, raw_coords, raw_map_url = check_raw_text_geo_sources(text)

        # Determina com rigor a precisão com base na fonte textual bruta
        if has_raw_coords:
            precision_level = "alta"
        elif has_raw_map_url:
            precision_level = "media"
        else:
            precision_level = "baixa"

        # Extrai município determinístico do Assunto ou do nome do arquivo
        fb_muni = extract_municipality_from_context(text, filename=filename)

        data: Dict[str, Any] = {
            "street": "",
            "number": "",
            "neighborhood": "",
            "municipality": fb_muni,
            "police_unit": "",
            "address": "",
            "coordinates": raw_coords,
            "map_url": raw_map_url,
            "geo_precision": precision_level,
            "location_types": []
        }

        if not text or not text.strip():
            return data

        try:
            logger.info("Executando Pass 2 (Localização) via LLM...")
            raw_response = self.processor.process_text(
                text=text,
                schema_model=LocationExtraction
            )

            if isinstance(raw_response, dict):
                data["street"] = sanitize_address_field(str(raw_response.get("street") or "").strip())
                data["number"] = sanitize_address_field(str(raw_response.get("number") or "").strip())
                data["neighborhood"] = sanitize_address_field(str(raw_response.get("neighborhood") or "").strip())

                # Guardrail determinístico: descarta a rua se ela não existir literalmente no texto
                # (evita o viés de âncora no exemplo do prompt, ex: "Rua General Osório" cravada sem sustentação)
                if data["street"] and not text_contains(data["street"], text):
                    logger.warning(f"Descartando rua sem evidência no texto ('{data['street']}').")
                    data["street"] = ""

                # Regra determinística (ADR-089): o município do cabeçalho ASSUNTO é sempre autoritativo,
                # mesmo quando a LLM extrai um nome de cidade diferente citado em outro trecho do texto.
                if not fb_muni:
                    extracted_muni = sanitize_address_field(str(raw_response.get("municipality") or "").strip())
                    if extracted_muni and len(extracted_muni) > 2:
                        data["municipality"] = extracted_muni

                # Validação anti-alucinação de coordenadas:
                # Só aceita coordenadas da LLM se os dígitos existirem literalmente no texto
                extracted_coords = str(raw_response.get("coordinates") or "").strip()
                if extracted_coords and extracted_coords.lower() not in ["none", "null", ""]:
                    # Extrai o primeiro número decimal da coordenada da LLM
                    m_d = re.search(r'-?\d{2}\.\d{3,}', extracted_coords)
                    if m_d and (m_d.group(0) in text or (raw_map_url and m_d.group(0) in raw_map_url)):
                        data["coordinates"] = extracted_coords
                    elif not data["coordinates"]:
                        logger.warning(f"Descartando coordenadas alucinadas pela LLM ({extracted_coords}) pois não existem no texto.")

                # Se a LLM capturou link do maps que existe no documento
                extracted_map = str(raw_response.get("map_url") or "").strip()
                if extracted_map and extracted_map.lower() not in ["none", "null", ""] and not data["map_url"]:
                    if "maps.app.goo.gl" in extracted_map or "google.com/maps" in extracted_map:
                        data["map_url"] = extracted_map

                # Categorização livre do tipo de local (sem enum fechado, sem guardrail de
                # evidência literal — é classificação de contexto, não uma citação do texto).
                # Só descarta placeholders óbvios, dedupe e limita a 5 categorias.
                raw_types = raw_response.get("location_types")
                if isinstance(raw_types, list):
                    seen_types = set()
                    clean_types = []
                    for item in raw_types:
                        cleaned = sanitize_address_field(str(item or "").strip())
                        if not cleaned or cleaned.lower() in ["none", "null", "n/a", "não informado"]:
                            continue
                        key = cleaned.lower()
                        if key in seen_types:
                            continue
                        seen_types.add(key)
                        clean_types.append(cleaned)
                    data["location_types"] = clean_types[:5]

        except Exception as err:
            logger.error(f"Erro na execução do LocationExtractor: {err}. Mantendo fallback.")

        # Resolução 100% determinística de 'police_unit' (tabela município -> BPM + evidência textual).
        # O campo não é mais perguntado à LLM (elimina o viés de âncora no exemplo do prompt).
        data["police_unit"] = resolve_police_unit(data["municipality"], text)

        # 1.1. Fallback determinístico de logradouro se a LLM omitiu ou colocou apenas o bairro na rua
        if data["street"].lower().startswith("bairro"):
            data["neighborhood"] = re.sub(r'(?i)^bairro\s*', '', data["street"]).strip()
            data["street"] = ""

        if not data["street"] or len(data["street"]) < 3:
            fb_street, fb_num, fb_neigh = extract_street_and_number_fallback(text)
            if fb_street:
                data["street"] = fb_street
            if fb_num and not data["number"]:
                data["number"] = fb_num
            if fb_neigh and not data["neighborhood"]:
                data["neighborhood"] = fb_neigh

        # 2. Regra de Bairro para Zona Rural:
        # Se for linha rural / rodovia / estrada e o bairro não for informado, marca 'Interior'
        is_rural = any(term in data["street"].lower() for term in ["linha", "estrada", "assentamento", "interior", "fazenda", "br-", "rs-", "rodovia"])
        if is_rural and (not data["neighborhood"] or data["neighborhood"].lower() in ["none", "null", ""]):
            data["neighborhood"] = "Interior"

        # 3. Resolução de Coordenadas do Link Encurtado (se tiver link e não tiver coords digitadas)
        if data["map_url"] and not data["coordinates"] and "maps.app.goo.gl" in data["map_url"]:
            _, resolved_coords = resolve_short_maps_url(data["map_url"])
            if resolved_coords:
                data["coordinates"] = resolved_coords

        # Normaliza formato, força o sinal negativo (100% dos RELINTs são do RS) e valida a faixa geográfica.
        # Qualquer placeholder textual ("N/A", "Sem informação", link não resolvido, DMS não convertido etc.)
        # é descartado aqui por não bater no formato decimal esperado.
        data["coordinates"] = enforce_rs_coordinate_signs(data["coordinates"])

        # 4. Formatação do Endereço Padrão Google (Garante Município e RS)
        formatted_addr = format_google_standard_address(
            street=data["street"],
            number=data["number"],
            neighborhood=data["neighborhood"],
            municipality=data["municipality"]
        )
        data["address"] = formatted_addr

        # 5. Geração do Link do Google Maps se não houver link no documento
        if not data["map_url"]:
            if data["coordinates"]:
                coords_clean = data["coordinates"].replace(" ", "")
                data["map_url"] = f"https://www.google.com/maps?q={coords_clean}"
            elif formatted_addr and formatted_addr != "-":
                query = urllib.parse.quote_plus(formatted_addr)
                data["map_url"] = f"https://www.google.com/maps/search/?api=1&query={query}"

        # 6. Fixa o nível de precisão, rebaixando se as coordenadas foram descartadas no passo
        # anterior (ex: fora da faixa geográfica do RS) — evita badge "alta" sem coordenada real.
        # Usa has_raw_map_url (link real encontrado no texto bruto), não data["map_url"], que a
        # esta altura já pode ter sido sintetizado como link de busca pelo passo 5 acima.
        if not data["coordinates"] and precision_level == "alta":
            precision_level = "media" if has_raw_map_url else "baixa"
        data["geo_precision"] = precision_level

        return data
