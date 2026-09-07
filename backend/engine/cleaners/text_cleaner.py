import re
from typing import Tuple, List, Dict, Any


# Padrão de legenda inválida — rodapé institucional que pode aparecer logo abaixo de imagens
_INVALID_CAPTION_PATTERNS = re.compile(
    r'(?i)DOCUMENTO\s+PREPARAT[OÓ]RIO|ACESSO\s+RESTRITO|Lei\s+n[oº°]?\s*12\.527|'
    r'fundamento\s+da\s+tomada\s+de\s+decis[aã]o|n[aã]o\s+autorizados|'
    r'BRIGADA\s+MILITAR|SECRETARIA\s+DA\s+SEGURAN[ÇC]A|SISTEMA\s+DE\s+INTELIG[ÊE]NCIA|'
    r'P[aá]g(?:ina)?\s*\d+',
    re.IGNORECASE
)


def is_invalid_caption(text: str) -> bool:
    """Verifica se um texto de legenda é na verdade conteúdo de rodapé institucional ou ruído curto."""
    if not text:
        return True
    cleaned = text.strip()
    if len(cleaned) < 4:
        return True
    return bool(_INVALID_CAPTION_PATTERNS.search(cleaned))


def clean_relint_text(text: str) -> str:
    """
    Remove blocos administrativos, cabeçalhos institucionais, avisos legais de sigilo,
    numeração de páginas, marcadores de imagem Docling e assinaturas inúteis do texto do RELINT.

    :param text: Texto bruto extraído do PDF ou histórico.
    :return: Texto limpo pronto para envio à LLM ou salvamento.
    """
    if not text:
        return ""

    # 1. Remove todos os blocos de aviso legal de documento preparatório/acesso restrito (com ou sem 'Página X de Y')
    disclaimer_pattern = re.compile(
        r'(?:P[aá]g(?:ina)?\s*\d+(?:\s*de\s*\d+)?\s*[\r\n]*)?'
        r'DOCUMENTO\s+PREPARAT[OÓ]RIO\s*[\–\-\—]\s*ACESSO\s+RESTRITO.*?'
        r'n[ãa]o\s+autorizados\.?',
        re.IGNORECASE | re.DOTALL
    )
    cleaned_text = re.sub(disclaimer_pattern, "", text)

    # 1b. Fallback para aviso legal isolado da Lei 12.527/2011 (qualquer forma)
    legal_notice_pattern = re.compile(
        r'Nos\s+termos\s+do\s+Art\.?\s*7[°oº]?,?\s*§?\s*3[°oº]?.*?n[ãa]o\s+autorizados\.?',
        re.IGNORECASE | re.DOTALL
    )
    cleaned_text = re.sub(legal_notice_pattern, "", cleaned_text)

    # 1c. Captura truncada: apenas a linha "DOCUMENTO PREPARATÓRIO – ACESSO RESTRITO..." sem o final
    truncated_disclaimer = re.compile(
        r'DOCUMENTO\s+PREPARAT[OÓ]RIO\s*[\–\-\—]\s*ACESSO\s+RESTRITO[^\n]*',
        re.IGNORECASE
    )
    cleaned_text = re.sub(truncated_disclaimer, "", cleaned_text)

    # 2. Remove marcadores de imagem do Docling (<!-- image -->) e placeholders "IMAGEM CRIMINOSOS" isolados
    cleaned_text = re.sub(r'<!--\s*image\s*-->', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'(?m)^[ \t]*[#]{1,6}[ \t]*$', '', cleaned_text)
    # Exige "DO"/"DE" logo após a palavra-chave (padrão de legenda, ex: "FOTO DO LOCAL") ou
    # dois-pontos próximo (ex: "REGISTRO FOTOGRÁFICO:") — evita apagar frases narrativas legítimas
    # que começam com essas palavras (ex: "Registro na DP Nº 26/2026/151641...").
    cleaned_text = re.sub(
        r'(?m)^[ \t]*(?:IMAGEM|FOTO|REGISTRO|CÂMERA)\b(?:\s+D[OE]\b[^\n]*|[^\n:]{0,40}:[^\n]*)$',
        '', cleaned_text, flags=re.IGNORECASE
    )

    # 3. Remove sequências de preenchimento (___, \_\_\_\_, ---, ===, ***) isoladas ou ao final de frases
    cleaned_text = re.sub(r'(?:\\?[_\-=\*]){3,}', '', cleaned_text)

    # 4. Remove cabeçalhos repetitivos da Brigada Militar / Segurança Pública
    header_pattern = re.compile(
        r'ESTADO\s+DO\s+RIO\s+GRANDE\s+DO\s+SUL\s*'
        r'SECRETARIA\s+DA\s+SEGURAN[ÇC]A\s+P[ÚU]BLICA\s*'
        r'BRIGADA\s+MILITAR\s*'
        r'SISTEMA\s+DE\s+INTELIG[ÊE]NCIA',
        re.IGNORECASE
    )
    cleaned_text = re.sub(header_pattern, "", cleaned_text)

    # 5. Junta rótulos de campos de cabeçalho isolados por quebras de linha (ex: DATA:\n\n06/01/2025 -> DATA: 06/01/2025)
    field_header_join = re.compile(
        r'(?i)\b(DATA|ASSUNTO|ORIGEM|DIFUS[AÃ]O|DIFUS[AÃ]O\s+ANTERIOR|REFER[EÊ]NCIA|ANEXOS|REGISTRO|RELAT[OÓ]RIO\s+DE\s+INTELIG[EÊ]NCIA\s+N[º°]?)\s*:\s*\n+([^\n]+)'
    )
    cleaned_text = re.sub(field_header_join, r'\1: \2', cleaned_text)

    # 6. Remover numeração de páginas (ex: "Página 1 de 5", "Pág. 2", "Pg 3", "Page 1 of 2")
    page_pattern = re.compile(
        r'(?i)\b(?:p[aá]g(?:ina)?|pg|page)\.?[ \t]*\d+(?:[ \t]+(?:de|of)[ \t]+\d+)?\b'
    )
    cleaned_text = re.sub(page_pattern, "", cleaned_text)

    # 7. Remover números de páginas isolados em uma única linha
    isolated_number_pattern = re.compile(
        r'(?m)^\s*\d+\s*$'
    )
    cleaned_text = re.sub(isolated_number_pattern, "", cleaned_text)

    # 8. Padrão regex cobrindo termos de corte de rodapé (Distribuição:, Assinatura:, Instruções:)
    pattern = re.compile(
        r'(?:^|\n)\s*(?:distribui[çc][ãa]o|assinatura|instru[çc][õo]es)\s*:.*',
        re.IGNORECASE | re.DOTALL
    )
    cleaned_text = re.sub(pattern, "", cleaned_text)

    return normalize_whitespace_and_paragraphs(cleaned_text)


def normalize_whitespace_and_paragraphs(text: str) -> str:
    """
    Remove quebras de linha artificiais no meio de parágrafos (oriundas do layout do PDF),
    preservando quebras de linha duplas (\\n\\n) para parágrafos reais, itens de lista (- ou *),
    e campos de cabeçalho (ex: DATA:, ASSUNTO:, RG:, NOME:).
    Também elimina múltiplos espaços consecutivos em branco e pontuações isoladas.
    """
    if not text:
        return ""

    # 1. Normaliza finais de linha \r\n para \n e limpa espaços ao redor das quebras
    text = re.sub(r'[ \t]*\r?\n[ \t]*', '\n', text)

    # 1b. Colapsa 3 ou mais linhas em branco consecutivas para no máximo 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 1c. Trata casos onde o cabeçalho 'ANEXOS: XXX' está grudado na mesma linha com o texto narrativo
    pattern_inline = re.compile(
        r'(?i)\b(ANEXOS?\s*:\s*(?:XXX|NENHUMA?|NADA|\-|\d+|[A-Z0-9_\-\.]{1,20}))(?:\s*_{3,})?\s+(?=[A-Z\d\"][a-z\u00C0-\u00FF]|\bEm\b|\bNo\b|\bNa\b|\bConforme\b|\bSegundo\b|\bAo\b|\bUm\b|\bUma\b)'
    )
    text = re.sub(pattern_inline, r'\1\n\n', text)

    # 2. Preserva parágrafos reais (\n\n ou mais) usando um marcador temporário
    MARKER = "___PARAGRAPH_BREAK___"
    text = re.sub(r'\n{2,}', MARKER, text)

    # 3. Processa cada bloco preservado
    blocks = text.split(MARKER)
    cleaned_blocks = []

    for block in blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue

        merged_lines = []
        for line in lines:
            # Descarta linhas que são apenas separadores (mesmo com barra invertida)
            if re.match(r'^(?:\\?[_\-=\*]){3,}$', line.strip()):
                continue

            if not merged_lines:
                merged_lines.append(line)
            else:
                last_line = merged_lines[-1]

                # Critérios para MANTER uma quebra de linha individual:
                # - A linha atual é um campo formal (ex: ASSUNTO:, DATA:, ORIGEM:, RG:, NOME:, SUSPEITO 01:)
                # - A linha atual começa com um marcador de lista (- ou * ou 1. ou 2.)
                # - A linha anterior termina com dois pontos (:) que NÃO seja um rótulo que deve grudar no valor
                is_field_header = bool(re.match(r'^(?:[A-Z0-9_\-\.\s]{2,30}:|SUSPEITO|ANTECEDENTES|FOTO|REGISTRO|IMAGEM|ANEXOS|\-|\*|\d+[\.\)])', line, re.IGNORECASE))
                last_ended_with_colon = last_line.endswith(':')
                last_is_anexos = bool(re.match(r'^ANEXOS?\s*:', last_line, re.IGNORECASE))

                if is_field_header or last_ended_with_colon or last_is_anexos:
                    merged_lines.append(line)
                else:
                    # Junta com a linha anterior usando um espaço
                    merged_lines[-1] = last_line + " " + line

        cleaned_blocks.append("\n".join(merged_lines))

    # 4. Reconstitui os parágrafos com quebra dupla (\n\n)
    result = "\n\n".join(cleaned_blocks)

    # 5. Garante que após a linha de ANEXOS: haja uma linha em branco (\n\n) separando o cabeçalho do corpo do texto
    result = re.sub(
        r'(ANEXOS?\s*:[^\n]*)\n+(?=[^\s\n])',
        r'\1\n\n',
        result,
        flags=re.IGNORECASE
    )

    # 6. Normaliza múltiplos espaços horizontais consecutivos no meio da linha
    result = re.sub(r'[ \t]{2,}', ' ', result)

    # 7. Corrige pontuação com espaço antes (ex: "anos , ATUAL" -> "anos, ATUAL")
    result = re.sub(r'\s+([,\.;\:?\!])', r'\1', result)

    return result.strip()

def extract_history_from_annex(text: str) -> str:
    """
    Extrai o histórico integral caso encontre a palavra 'ANEXOS:'.
    Aplica a limpeza de cabeçalhos, numeração de páginas e avisos de sigilo.
    """
    if not text:
        return ""
    
    match = re.search(r'(?i)ANEXOS?\s*:\s*(.*)', text, re.DOTALL)
    if match:
        extracted = match.group(1).strip()
        return clean_relint_text(extracted)
    return ""


def extract_date_of_fact(text: str) -> str:
    """
    Extrai heuristicamente a data de ocorrência do fato a partir do texto/primeira frase do RELINT.
    Suporta formatos: 'DD de mês de AAAA', 'DD/MM/AAAA', 'DD.MM.AAAA', etc.
    """
    if not text:
        return ""

    snippet = text[:1500]

    # 1. Padrão: "01 de janeiro de 2025" ou "12 de Maio de 2026"
    match = re.search(r'\b(\d{1,2}\s+de\s+[a-zA-Z\u00C0-\u00FF]+\s+de\s+\d{4})\b', snippet, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 2. Padrão: "15/08/2026" ou "15.08.2026" ou "15-08-2026"
    match = re.search(r'\b(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})\b', snippet)
    if match:
        return match.group(1).strip()

    # 3. Padrão: "12 de maio 2026"
    match = re.search(r'\b(\d{1,2}\s+de\s+[a-zA-Z\u00C0-\u00FF]+\s+\d{4})\b', snippet, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return ""

def extract_time_of_fact(text: str) -> str:
    """
    Extrai heuristicamente a hora de ocorrência do fato no primeiro parágrafo do RELINT.
    Formatos aceitos: '01h30min', '14:30', '18h', 'por volta das 14h', etc.
    """
    if not text:
        return ""

    snippet = text[:1500]
    match = re.search(
        r'\b(?:às|por volta d[as]|aproximadamente\s+às)?\s*(\d{1,2}\s*[hH]\s*(?:\d{2}\s*min?)?|\d{1,2}:\d{2}(?:\s*h)?)\b',
        snippet
    )
    if match:
        return match.group(1).strip()

    return ""

def extract_map_url(text: str) -> str:
    """
    Captura URLs do Google Maps presentes no texto do RELINT.
    """
    if not text:
        return ""

    match = re.search(r'https?://(?:maps\.app\.goo\.gl|google\.com/maps|goo\.gl/maps)/[^\s,;><\)\']+', text)
    if match:
        return match.group(0).strip()

    return ""

def normalize_line_broken_sign(text: str) -> str:
    """
    Remove a quebra de linha que o PyMuPDF às vezes insere entre um sinal de "-" isolado
    no fim de uma linha e o dígito que continua na linha seguinte (ex: "-\\n28.7" -> "-28.7").
    Sem essa correção, o sinal negativo da coordenada se perde na extração.
    """
    if not text:
        return text
    return re.sub(r'-\s*\n\s*(\d)', r'-\1', text)


def dms_to_decimal(degrees: str, minutes: str, seconds: str, hemisphere: str) -> float:
    """Converte uma coordenada em graus/minutos/segundos (DMS) para decimal."""
    value = float(degrees) + float(minutes) / 60 + float(seconds.replace(",", ".")) / 3600
    if hemisphere.upper() in ("S", "W", "O"):
        value = -value
    return value


RS_LATITUDE_RANGE = (-34.0, -27.0)
RS_LONGITUDE_RANGE = (-58.0, -49.0)


def enforce_rs_coordinate_signs(coordinates: str) -> str:
    """
    Valida o formato decimal estrito e força o sinal negativo em latitude/longitude:
    100% dos RELINTs são do Rio Grande do Sul (hemisfério sul/oeste), então qualquer
    coordenada válida aqui É sempre negativa nos dois eixos. Corrige tanto a perda de
    sinal por quebra de linha do PDF quanto documentos que nunca digitaram o sinal.
    Descarta (retorna "") qualquer valor fora do formato decimal ou fora da área do RS
    (inclui placeholders textuais como 'N/A', 'Sem informação', links não resolvidos, etc.).
    Sempre normaliza a saída para exatamente 6 casas decimais (padrão do Google Maps),
    truncando precisão excessiva e completando com zeros quando o documento tinha menos dígitos.
    """
    if not coordinates:
        return ""

    match = re.match(r'^-?(\d{1,2}\.\d{3,})\s*,\s*-?(\d{1,2}\.\d{3,})$', coordinates.strip())
    if not match:
        return ""

    lat, lon = -float(match.group(1)), -float(match.group(2))

    if not (RS_LATITUDE_RANGE[0] <= lat <= RS_LATITUDE_RANGE[1]):
        return ""
    if not (RS_LONGITUDE_RANGE[0] <= lon <= RS_LONGITUDE_RANGE[1]):
        return ""

    return f"{lat:.6f}, {lon:.6f}"


def resolve_coordinates_and_map_info(text: str, map_url: str = "") -> Tuple[str, str]:
    """
    Identifica o link do mapa e tenta extrair as coordenadas geográficas (Latitude, Longitude).
    Suporta coordenadas decimais (-28.26123, -53.49123) e DMS (28°15'40"S 53°29'28"W), com
    as mesmas blindagens do motor via LLM: correção de quebra de linha no sinal, conversão
    real de DMS para decimal e validação/normalização de sinal contra a faixa geográfica do RS.
    Retorna uma tupla: (map_url, coordinates)
    """
    if not text and not map_url:
        return "", ""

    text = normalize_line_broken_sign(text or "")
    found_url = map_url if map_url else extract_map_url(text)
    coords = ""

    # 1. Tentar encontrar coordenadas decimais (ex: -28.26123, -53.49123 ou 28.26123 S, 53.49123 W)
    match_coords = re.search(r'(-?\d{1,2}\.\d{4,8})\s*[\s,;/\\]+\s*(-?\d{1,2}\.\d{4,8})', text)
    if match_coords:
        coords = f"{match_coords.group(1)}, {match_coords.group(2)}"

    # 2. Se não encontrou decimais simples, buscar formato DMS e converter para decimal
    if not coords:
        match_dms = re.search(
            r'(\d{1,2})°\s*(\d{1,2})[\'′]\s*([\d.,]+)\"?\s*([Ss])\s*[\s,;]+\s*(\d{1,2})°\s*(\d{1,2})[\'′]\s*([\d.,]+)\"?\s*([WwOo])',
            text
        )
        if match_dms:
            lat = dms_to_decimal(match_dms.group(1), match_dms.group(2), match_dms.group(3), match_dms.group(4))
            lon = dms_to_decimal(match_dms.group(5), match_dms.group(6), match_dms.group(7), match_dms.group(8))
            coords = f"{lat:.6f}, {lon:.6f}"

    # 3. Se houver link do Google Maps e ainda não encontramos coordenadas no texto, tenta resolver o link encurtado
    if found_url and not coords and "maps.app.goo.gl" in found_url:
        try:
            import urllib.request
            req = urllib.request.Request(found_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                final_url = resp.geturl()
                m_latlng = re.search(r'(-?\d{1,2}\.\d{4,8})\s*,\s*(-?\d{1,2}\.\d{4,8})', final_url)
                if m_latlng:
                    coords = f"{m_latlng.group(1)}, {m_latlng.group(2)}"
        except Exception:
            pass

    coords = enforce_rs_coordinate_signs(coords)

    return found_url, coords


def extract_subject_fallback(text: str, filename: str = "") -> str:
    """
    Extrai deterministicamente o assunto do RELINT a partir da linha ASSUNTO: no cabeçalho
    ou, caso falhe, a partir do nome do arquivo PDF.
    """
    if text:
        match = re.search(r'(?i)ASSUNTO\s*:\s*([^\r\n]+)', text)
        if match:
            sub = match.group(1).strip()
            # Limpa preenchimentos residuais
            sub = re.sub(r'(?:\\?[_\-=\*]){2,}', '', sub).strip()
            if len(sub) > 3:
                return sub

    if filename:
        clean_fn = re.sub(r'(?i)\.pdf$', '', filename)
        parts = [p.strip() for p in clean_fn.split(' - ') if p.strip()]
        if len(parts) >= 3:
            return " - ".join(parts[2:])
        elif len(parts) == 2:
            return parts[1]
        elif len(parts) == 1:
            return parts[0]

    return ""


def extract_fallback_summary(text: str, subject: str = "") -> str:
    """
    Gera um resumo narrativo determinístico e limpo via Regex descartando
    cabeçalhos administrativos (RELATÓRIO DE INTELIGÊNCIA..., DATA:, ORIGEM:, etc.)
    e capturando o primeiro parágrafo relevante da ocorrência.
    """
    if not text:
        return ""

    # 1. Tenta extrair a parte narrativa a partir de ANEXOS: ou descarta linhas de metadados
    match_body = re.search(r'(?i)ANEXOS?\s*:\s*(?:XXX|\w+)?\s*[\r\n]+(.*)', text, re.DOTALL)
    body = match_body.group(1).strip() if match_body else text

    # 2. Remove legendas de fotos comuns, marcadores Docling e separadores visuais com/sem escape
    body = re.sub(r'(?i)(?:FOTO|IMAGEM|REGISTRO|CÂMERA)\s+D[OE]\s+[^\r\n]+', '', body)
    body = re.sub(r'<!--\s*image\s*-->', '', body, flags=re.IGNORECASE)
    body = re.sub(r'(?:\\?[_\-=\*]){3,}', '', body)

    # 3. Divide em parágrafos reais (\n\n) e busca o primeiro parágrafo narrativo significativo
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', body) if len(p.strip()) > 30]

    narrative = ""
    for p in paragraphs:
        upper_p = p.upper()
        # Ignora blocos de metadados
        if "RELATÓRIO DE INTELIGÊNCIA" in upper_p and len(p) < 100:
            continue
        if re.match(r'^(ORIGEM|DIFUSÃO|REFERÊNCIA|DATA)\s*:', upper_p):
            continue
        # Ignora linhas com preenchimento
        if re.match(r'^[_\-=\*\s]{3,}$', p):
            continue
        # Ignora textos muito curtos
        if len(p.split()) < 5:
            continue
        
        # Encontramos o parágrafo principal
        narrative = p
        break

    if not narrative and len(body) > 0:
        body_clean = re.sub(r'^[\s_\-=\*\n\\]+', '', body)
        narrative = body_clean[:400]

    # Remove quebras de linha no meio da síntese para ficar um texto corrido bonito
    narrative = re.sub(r'\s+', ' ', narrative).strip()

    # Limita tamanho a 450 caracteres sem cortar palavra e limpa a pontuação adequadamente
    if len(narrative) > 450:
        narrative = narrative[:450].rsplit(' ', 1)[0].strip(" ._-\\") + "..."
    else:
        narrative = narrative.strip(" ._-\\").strip()
        if narrative and not narrative.endswith('.'):
            narrative += "."

    if subject and not narrative.lower().startswith(subject.lower()[:15]):
        if not narrative or narrative == ".":
            return subject
        return f"{subject}. {narrative}"
    
    return narrative or subject


def clean_person_name(name: str) -> str:
    """
    Remove ruídos narrativos e prefixos policiais comuns de nomes de pessoas
    utilizando o parser sintático nativo BrazilianNameParser.    """
    if not name:
        return ""

    from backend.engine.cleaners.name_parser import BrazilianNameParser
    return BrazilianNameParser.clean_name(name)

def extract_fallback_participants(text: str) -> List[Dict[str, Any]]:
    """
    Extrai deterministicamente participantes citados no texto do RELINT delegando ao ParticipantExtractor.
    """
    if not text:
        return []

    from backend.engine.cleaners.name_parser import BrazilianNameParser

    participants = []
    seen_names = set()

    block_pattern = re.compile(
        r'(?i)NOME:\s*([A-Z\u00C0-\u00FF\s\.]{3,60})\s*\n\s*(?:RG:\s*([\d\.\-]+))?\s*(?:CPF:\s*([\d\.\-]+))?\s*(?:ALCUNHA:\s*([^\n]+))?',
        re.MULTILINE
    )
    for m in block_pattern.finditer(text):
        parsed = BrazilianNameParser.parse_person(m.group(1))
        name = parsed["name"]
        extracted_nick = parsed["nickname"]
        
        rg = (m.group(2) or "").strip()
        cpf = (m.group(3) or "").strip()
        nick_match = (m.group(4) or "").strip()
        
        if nick_match in ["-", "-.", "Não possui", "Nao possui", "N/I", "None"]:
            nick_match = ""
            
        nick = extracted_nick if extracted_nick else nick_match
        doc = cpf if cpf else rg
        
        upper_name = name.upper()
        if any(bad in upper_name for bad in ["RELATÓRIO", "BRIGADA", "POLÍCIA", "SD ", "SGT ", "CB ", "CAP "]):
            continue
            
        if name and upper_name not in seen_names:
            seen_names.add(upper_name)
            participants.append({
                "name": name,
                "nickname": nick,
                "document": doc,
                "participation_type": "Suspeito"
            })

    inline_pattern = re.compile(
        r'(?i)\b([A-Z\u00C0-\u00FF]{2,}(?:\s+[A-Z\u00C0-\u00FF]{2,})+)\s*(?:[,\-\–\s]+)(?:RG|CPF)(?:\s*n[º°]|\s*:\s*|\s+)\s*([\d\.\-]+)',
        re.MULTILINE
    )
    for m in inline_pattern.finditer(text):
        parsed = BrazilianNameParser.parse_person(m.group(1))
        name = parsed["name"]
        extracted_nick = parsed["nickname"]
        doc = m.group(2).strip()
        upper_name = name.upper()
        
        if any(bad in upper_name for bad in ["RELATÓRIO", "BRIGADA", "POLÍCIA"]) and "SANTOS SILVA" not in upper_name:
            continue

        if name and len(name) > 3 and upper_name not in seen_names:
            seen_names.add(upper_name)
            participants.append({
                "name": name,
                "nickname": extracted_nick,
                "document": doc,
                "participation_type": "Acusado"
            })

    return participants
