# -*- coding: utf-8 -*-
"""
Auditoria de consistência: compara os campos extraídos e gravados no banco contra a
transcrição literal (relints.conteudo) de cada RELINT. Só leitura — não altera o banco.

Estágio 1 (determinístico): campos com evidência textual esperada (endereço, município,
unidade policial, coordenadas, registro, data/hora, location_types) são checados por
match literal tolerante (mesma função text_contains() já usada no LocationExtractor).

Estágio 2 (LLM via Ollama): campos narrativos/classificatórios (assunto, resumo,
fato_principal, grupo_bm, tipo_relint) e de especialidade não têm "match literal" como
critério — pedem julgamento semântico. Cada RELINT recebe UMA chamada ao Ollama com o
texto + os valores gravados relevantes, pedindo um veredito por campo.

Uso:
    python scripts/audit_extracted_fields.py --limit 5      # teste rápido
    python scripts/audit_extracted_fields.py                # roda os 602 completos
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

from backend.database.sqlite_repo import SqliteRepo
from backend.engine.extractors.llm.extractors.location_extractor import (
    text_contains, resolve_battalion_by_municipality, extract_battalion_mentions,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "relints.db"
RESULTS_PATH = Path(__file__).resolve().parent.parent / "data" / "audit_results.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:latest"
MAX_CONTENT_CHARS = 15000  # RELINTs muito longos são truncados só para a chamada de auditoria

# --- Estágio 1: campos com evidência textual esperada ---
GROUNDED_FIELDS = [
    ("address", "endereco"),
    ("municipality", "municipio"),
    ("police_unit", "unidade_policial"),
    ("coordinates", "coordenadas"),
    ("registry_number", "numero_registro"),
    ("registry_agency", "orgao_registro"),
    ("registry_year", "ano_registro"),
    ("date_of_fact", "data_fato"),
    ("time_of_fact", "hora_fato"),
]

# --- Estágio 2: campos narrativos/classificatórios, sempre auditados ---
NARRATIVE_FIELDS = ["subject", "summary", "main_fact", "bm_group", "relint_type"]

# --- Estágio 2: campos de especialidade, condicionais ao bm_group ---
SPECIALTY_FIELDS_BY_GROUP = {
    "Homicídio": ["fact_type", "motivation"],
    "Prisão por Tráfico": ["drug_quantity", "drug_types"],
    "Roubo a Estabelecimento": ["establishment_type", "location_type", "injured_victims", "hostage_victim"],
    "Roubo a Residência": ["location_type", "injured_victims", "hostage_victim"],
    "Roubo de Veículo": ["vehicle_model", "license_plate", "recovered", "recovery_location"],
    "Roubo a Pedestre": ["injured_victims", "weapon_used", "stolen_object"],
    "Furto de Veículo": ["vehicle_model", "license_plate", "recovered", "recovery_location"],
}

FIELD_LABELS = {
    "subject": "Assunto", "summary": "Resumo", "main_fact": "Fato Principal",
    "bm_group": "Grupo BM (classificação de especialidade)", "relint_type": "Tipo de RELINT",
    "fact_type": "Tipo de Fato", "motivation": "Motivação",
    "drug_quantity": "Quantidade de Drogas", "drug_types": "Tipos de Drogas",
    "establishment_type": "Tipo de Estabelecimento", "location_type": "Local (Urbano/Rural)",
    "injured_victims": "Vítimas Lesionadas", "hostage_victim": "Refém",
    "vehicle_model": "Modelo do Veículo", "license_plate": "Placa",
    "recovered": "Veículo Recuperado", "recovery_location": "Local de Recuperação",
    "weapon_used": "Arma Utilizada", "stolen_object": "Objeto Roubado",
}


def audit_stage1(report) -> Dict[str, Dict[str, Any]]:
    """Retorna, por campo, se está preenchido e se tem evidência literal no texto."""
    content = report.content or ""
    result = {}
    for attr, label in GROUNDED_FIELDS:
        value = getattr(report, attr, None)
        value = str(value).strip() if value else ""
        if not value:
            result[label] = {"preenchido": False, "evidencia_literal": None}
            continue

        if label == "unidade_policial":
            # Campo é 100% determinístico (tabela município->BPM) desde melhorias-extracao-geo.md —
            # "sem evidência literal" é o comportamento ESPERADO quando o valor vem da tabela sem
            # menção no texto (inferência territorial). O sinal real de problema é DIVERGIR da tabela
            # sem nenhuma menção literal que justifique (ver seção 6.3 daquele documento).
            mentions = extract_battalion_mentions(content)
            table_value = resolve_battalion_by_municipality(getattr(report, "municipality", "") or "")
            bate_com_tabela = bool(table_value) and (table_value in value)
            mencionado = any(m in value for m in mentions)
            result[label] = {
                "preenchido": True,
                "evidencia_literal": mencionado,
                "bate_com_tabela_municipio": bate_com_tabela,
                "valor": value,
                "suspeito": not (bate_com_tabela or mencionado),
            }
            continue

        result[label] = {"preenchido": True, "evidencia_literal": text_contains(value, content), "valor": value}

    loc_types = getattr(report, "location_types", None) or []
    tipos_sem_evidencia = [t for t in loc_types if t and not text_contains(t, content)]
    result["location_types"] = {
        "preenchido": bool(loc_types),
        "evidencia_literal": (len(tipos_sem_evidencia) == 0) if loc_types else None,
        "valor": loc_types,
        "sem_evidencia": tipos_sem_evidencia,
    }
    return result


def _build_audit_prompt(report, fields_to_audit: List[str]) -> str:
    content = (report.content or "")[:MAX_CONTENT_CHARS]
    valores = []
    for field in fields_to_audit:
        value = getattr(report, field, None)
        if value in (None, "", [], 0) and field not in ("injured_victims", "hostage_victim", "recovered"):
            continue
        label = FIELD_LABELS.get(field, field)
        valores.append(f'- {label} ({field}): "{value}"')

    campos_str = "\n".join(valores) if valores else "(nenhum campo preenchido para auditar)"

    return f"""Você é um auditor de qualidade de dados. Abaixo está o texto literal de um RELINT
(boletim de inteligência policial) e uma lista de campos que um sistema automático já
extraiu e classificou a partir desse texto.

Para cada campo, julgue se a informação gravada é CONSISTENTE com o que o texto realmente
diz. Um resumo/classificação não precisa ser cópia literal do texto (paráfrase é normal),
mas não pode inventar, trocar ou contradizer um fato (nome, número, motivo, tipo de crime
etc.) que o texto descreve de forma diferente.

TEXTO LITERAL DO RELINT:
\"\"\"
{content}
\"\"\"

CAMPOS EXTRAÍDOS PARA AUDITAR:
{campos_str}

Responda em JSON estrito, no formato:
{{"veredictos": [{{"campo": "<chave do campo, ex: bm_group>", "veredito": "consistente" | "inconsistente" | "sem_sustentacao", "motivo": "<1 frase curta explicando, em português>"}}]}}

"sem_sustentacao" = o texto não tem informação suficiente pra confirmar nem contradizer o valor.
Responda só o JSON, um veredicto por campo da lista acima."""


def audit_stage2(report) -> List[Dict[str, str]]:
    bm_group = str(getattr(report, "bm_group", "") or "")
    fields_to_audit = list(NARRATIVE_FIELDS) + SPECIALTY_FIELDS_BY_GROUP.get(bm_group, [])
    prompt = _build_audit_prompt(report, fields_to_audit)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0},
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=180)
    response.raise_for_status()
    raw = response.json().get("response", "{}")
    try:
        parsed = json.loads(raw)
        veredictos = parsed.get("veredictos", [])
        if isinstance(veredictos, list):
            return veredictos
    except (json.JSONDecodeError, AttributeError):
        pass
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Auditar só os N primeiros RELINTs (teste)")
    parser.add_argument("--skip-llm", action="store_true", help="Roda só o Estágio 1 (determinístico)")
    args = parser.parse_args()

    repo = SqliteRepo(DB_PATH)
    reports = repo.get_all()
    if args.limit:
        reports = reports[: args.limit]

    print(f"Auditando {len(reports)} RELINTs...")
    results = []
    start = time.time()
    for i, report in enumerate(reports, 1):
        entry = {
            "id": report.id,
            "arquivo_origem": report.source_file,
            "bm_group": str(getattr(report, "bm_group", "")),
            "estagio1": audit_stage1(report),
        }
        if not args.skip_llm:
            try:
                entry["estagio2"] = audit_stage2(report)
            except Exception as e:
                entry["estagio2_erro"] = str(e)
        results.append(entry)

        if i % 10 == 0 or i == len(reports):
            elapsed = time.time() - start
            print(f"  {i}/{len(reports)} processados ({elapsed:.0f}s, ~{elapsed/i:.1f}s/RELINT)")
            RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Concluído. Resultados salvos em {RESULTS_PATH}")


if __name__ == "__main__":
    main()
