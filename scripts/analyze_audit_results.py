# -*- coding: utf-8 -*-
"""Agrega data/audit_results.json em estatisticas para o relatorio de auditoria."""
import json
from collections import Counter, defaultdict
from pathlib import Path

RESULTS_PATH = Path(__file__).resolve().parent.parent / "data" / "audit_results.json"

data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
total = len(data)
print(f"Total de RELINTs analisados: {total}\n")

print("=" * 70)
print("ESTAGIO 1 - Campos com evidencia textual esperada")
print("=" * 70)
stage1_fields = ["endereco", "municipio", "unidade_policial", "coordenadas",
                  "numero_registro", "orgao_registro", "ano_registro",
                  "data_fato", "hora_fato", "location_types"]

for field in stage1_fields:
    preenchidos = 0
    suspeitos = []
    for entry in data:
        info = entry["estagio1"].get(field, {})
        if not info.get("preenchido"):
            continue
        preenchidos += 1
        if field == "unidade_policial":
            if info.get("suspeito"):
                suspeitos.append((entry["id"], entry["arquivo_origem"], info.get("valor")))
        elif field == "location_types":
            if info.get("sem_evidencia"):
                suspeitos.append((entry["id"], entry["arquivo_origem"], info.get("sem_evidencia")))
        else:
            if not info.get("evidencia_literal"):
                suspeitos.append((entry["id"], entry["arquivo_origem"], info.get("valor")))

    pct = (len(suspeitos) / preenchidos * 100) if preenchidos else 0
    print(f"\n{field}: {preenchidos}/{total} preenchidos, {len(suspeitos)} suspeitos ({pct:.0f}%)")
    for rid, fname, val in suspeitos[:8]:
        print(f"    id={rid} | {str(val)[:60]!r} | {fname[:60]}")
    if len(suspeitos) > 8:
        print(f"    ... e mais {len(suspeitos) - 8}")

print("\n" + "=" * 70)
print("Repeticao de valores suspeitos (possivel vies de ancora)")
print("=" * 70)
addr_counter = Counter()
for entry in data:
    info = entry["estagio1"].get("endereco", {})
    if info.get("preenchido") and not info.get("evidencia_literal"):
        addr_counter[info.get("valor")] += 1
for val, count in addr_counter.most_common(10):
    if count > 1:
        print(f"  {count}x: {val}")

print("\n" + "=" * 70)
print("ESTAGIO 2 - Campos narrativos/classificatorios/especialidade (LLM)")
print("=" * 70)
stage2_stats = defaultdict(lambda: {"total": 0, "inconsistente": 0, "sem_sustentacao": 0, "exemplos": []})
erros_llm = 0
for entry in data:
    if "estagio2_erro" in entry:
        erros_llm += 1
        continue
    for v in entry.get("estagio2", []):
        campo = v.get("campo", "?")
        veredito = v.get("veredito", "?")
        stage2_stats[campo]["total"] += 1
        if veredito == "inconsistente":
            stage2_stats[campo]["inconsistente"] += 1
            stage2_stats[campo]["exemplos"].append((entry["id"], entry["arquivo_origem"], v.get("motivo")))
        elif veredito == "sem_sustentacao":
            stage2_stats[campo]["sem_sustentacao"] += 1

print(f"\nErros de chamada ao Ollama (audit stage 2 falhou): {erros_llm}/{total}\n")

for campo, stats in sorted(stage2_stats.items(), key=lambda kv: -kv[1]["inconsistente"]):
    total_campo = stats["total"]
    inc = stats["inconsistente"]
    pct = (inc / total_campo * 100) if total_campo else 0
    print(f"{campo}: {total_campo} avaliados, {inc} inconsistentes ({pct:.0f}%), {stats['sem_sustentacao']} sem sustentacao")

print("\n" + "=" * 70)
print("DESTAQUE: Grupo BM (classificacao de especialidade) - todas as inconsistencias")
print("=" * 70)
for rid, fname, motivo in stage2_stats.get("bm_group", {}).get("exemplos", []):
    print(f"  id={rid} | {fname[:70]}\n      motivo: {motivo}")

print("\n" + "=" * 70)
print("DESTAQUE: Tipo de RELINT - todas as inconsistencias")
print("=" * 70)
for rid, fname, motivo in stage2_stats.get("relint_type", {}).get("exemplos", []):
    print(f"  id={rid} | {fname[:70]}\n      motivo: {motivo}")
