"""Verificação reproduzível do contrato publicado no README."""

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
SAMPLE = ROOT / "data/exemplo-validacao.csv"
RATES = ROOT / "data/taxas_cambio.csv"
EXECUTIONS = []


def invoke(label, arguments, cwd, expected_code=0):
    command = [sys.executable, "-m", "onfly_report", *map(str, arguments)]
    result = subprocess.run(command, cwd=cwd, env=ENV, capture_output=True, text=True, timeout=30)
    EXECUTIONS.append({"case": label, "command": command, "cwd": str(cwd),
                       "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    assert result.returncode == expected_code, EXECUTIONS[-1]
    if expected_code:
        assert result.stderr and not result.stdout, EXECUTIONS[-1]
    return result


readme = (ROOT / "README.md").read_text().replace("\\_", "_").replace("\\[", "[").replace("\\]", "]")
schema = json.loads(re.search(r"```json\s*(.*?)```", readme, re.S)[1])
section = readme.split("<!-- AMOSTRA:INICIO -->")[1].split("<!-- AMOSTRA:FIM -->")[0]
tables = []
for block in section.strip().replace("`", "").split("\n\n"):
    rows = [[cell.strip() for cell in line.strip("|").split("|")]
            for line in block.splitlines() if line.startswith("|")]
    if rows:
        tables.append([dict(zip(rows[0], row)) for row in rows[2:]])
reference = {
    "report_version": "1.0",
    "summary": {row["Campo"]: row["Valor esperado"] if row["Campo"] in
                ("total_amount_brl", "average_nightly_rate_brl") else int(row["Valor esperado"])
                for row in tables[0]},
    "by_month": [{key: int(value) if key in ("reservations", "room_nights") else value
                  for key, value in row.items()} for row in tables[1]],
    "top_hotels": [{key: int(value) if key == "room_nights" else value
                    for key, value in row.items()} for row in tables[2]],
}


def validate_schema(report):
    assert set(report) == set(schema)
    assert report["report_version"] == "1.0"
    assert datetime.fromisoformat(report["generated_at"]).utcoffset() == timedelta(hours=-3)
    for group in ("summary", "by_month", "top_hotels"):
        template = schema[group] if group == "summary" else schema[group][0]
        entries = [report[group]] if group == "summary" else report[group]
        if group != "summary":
            assert type(entries) is list
        for entry in entries:
            assert set(entry) == set(template)
            for field, value in entry.items():
                assert type(value) is type(template[field]), (field, value)
                if field in ("total_amount_brl", "average_nightly_rate_brl", "total_brl"):
                    assert re.fullmatch(r"-?\d+\.\d{2}", value), (field, value)


with tempfile.TemporaryDirectory(prefix="onfly-contrato-") as temporary:
    work = Path(temporary)
    base = ["--input", SAMPLE, "--rates", RATES]
    result = invoke("amostra com output e top padrão", base, work)
    target = work / "output/report.json"
    assert target.exists()
    report = json.loads(target.read_text())
    validate_schema(report)
    assert {key: value for key, value in report.items() if key != "generated_at"} == reference
    assert result.stdout == "Reservas: 12 | Confirmadas: 9 | Noites: 28 | Total BRL: 7566.00\n"
    assert not result.stderr
    (EVIDENCE / "exemplo.json").write_text(target.read_text())
    (EVIDENCE / "referencia-readme.json").write_text(json.dumps(reference, ensure_ascii=False, indent=2) + "\n")
    for top in (1, 2, 100):
        invoke(f"--top {top}", [*base, "--top", top], work)
        ranked = json.loads(target.read_text())
        validate_schema(ranked)
        assert len(ranked["top_hotels"]) == min(top, 9)
        assert ranked["top_hotels"][:min(top, 5)] == reference["top_hotels"][:min(top, 5)]

    invoke("dataset principal e criação de diretórios", ["--input", ROOT / "data/reservas_hoteis.csv",
           "--rates", RATES, "--output", work / "nested/sub/report.json"], work)
    main = json.loads((work / "nested/sub/report.json").read_text())
    validate_schema(main)
    assert main["summary"] == dict(zip(reference["summary"], [300, 235, 31, 34, 1347, "396170.00", "294.11"]))
    assert [entry["month"] for entry in main["by_month"]] == sorted(entry["month"] for entry in main["by_month"])
    (EVIDENCE / "report.json").write_text(json.dumps(main, ensure_ascii=False, indent=2) + "\n")

    with SAMPLE.open(newline="") as handle:
        sample_rows = list(csv.DictReader(handle))
        fields = list(sample_rows[0])

    def write_rows(rows):
        path = work / "reservas.csv"
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return path

    for name, rows in [("arquivo sem reservas", []), ("somente status não faturáveis", sample_rows[3:6]),
                       ("reserva sem noites", [{**sample_rows[0], "checkout_date": sample_rows[0]["checkin_date"]}])]:
        source = write_rows(rows)
        invoke(name, ["--input", source, "--rates", RATES], work)
        empty = json.loads(target.read_text())
        validate_schema(empty)
        assert empty["summary"]["average_nightly_rate_brl"] == "0.00"
        assert empty["summary"]["total_room_nights"] == 0
        if name != "reserva sem noites":
            assert not empty["by_month"] and not empty["top_hotels"]
            assert empty["summary"]["total_amount_brl"] == "0.00"
        if name == "somente status não faturáveis":
            assert empty["summary"]["total_reservations"] == 3
            assert empty["summary"]["cancelled_reservations"] == 2
            assert empty["summary"]["no_show_reservations"] == 1

    for args in ([], ["--input", SAMPLE], ["--rates", RATES],
                 [*base, "--top", 0], [*base, "--top", -1], [*base, "--top", "abc"],
                 ["--input", work / "ausente.csv", "--rates", RATES],
                 ["--input", SAMPLE, "--rates", work / "ausente.csv"]):
        invoke("entrada/argumento inválido", args, work, 2)
    bad_columns = work / "colunas.csv"
    bad_columns.write_text("invalid\nvalue\n")
    invoke("colunas ausentes", ["--input", bad_columns, "--rates", RATES], work, 2)
    source = write_rows([{**sample_rows[0], "rooms": "abc"}])
    invoke("tipo inválido na reserva", ["--input", source, "--rates", RATES], work, 2)
    bad_rates = work / "taxas.csv"
    bad_rates.write_text("currency,rate_to_brl\nBRL,abc\n")
    invoke("taxa inválida", ["--input", SAMPLE, "--rates", bad_rates], work, 2)
    invoke("erro de escrita", [*base, "--output", work], work, 1)
    invoke("ajuda", ["--help"], work)
    sys.path.insert(0, str(ROOT / "src"))
    from onfly_report.cli import main as cli_main
    with patch("onfly_report.cli.ReportBuilder.build", side_effect=RuntimeError("erro injetado no teste")):
        assert cli_main(list(map(str, base))) == 1

before = json.loads((EVIDENCE / "integridade-antes.json").read_text())
changed = [path for path, digest in before.items()
           if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest]
assert changed == ["src/onfly_report/services/report_builder.py"], changed
original_files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "9f8d8f7", "data", "tests"], cwd=ROOT, text=True).splitlines()
for path in original_files:
    assert (ROOT / path).read_bytes() == subprocess.check_output(["git", "show", f"9f8d8f7:{path}"], cwd=ROOT)
(EVIDENCE / "execucoes-cli.json").write_text(json.dumps(EXECUTIONS, ensure_ascii=False, indent=2) + "\n")
(EVIDENCE / "integridade-depois.json").write_text(json.dumps({"arquivos_preexistentes_alterados": changed,
    "arquivos_fornecidos_identicos_ao_original": len(original_files)}, indent=2) + "\n")
print(f"Contrato: {len(EXECUTIONS)} execuções do CLI aprovadas e exceção inesperada verificada por injeção.")
print("Amostra completa corresponde ao README, ignorando apenas generated_at; schema e offset validados.")
print("Dados e testes fornecidos idênticos ao commit original; testes preexistentes preservados.")
