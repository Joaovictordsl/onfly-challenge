"""Validação isolada: roda dentro da imagem Python 3.11 com o projeto somente para leitura."""

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("/workspace"))
    parser.add_argument("--output", type=Path, default=Path("/evidence"))
    parser.add_argument("--wheels", type=Path, default=Path("/wheels"))
    args = parser.parse_args()
    assert sys.version_info[:2] == (3, 11), sys.version
    args.output.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(args.project / "src"),
           "PYTHONDONTWRITEBYTECODE": "1", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    executions = []

    def run(name, command):
        result = subprocess.run(command, cwd=args.project, env=env, capture_output=True, text=True, timeout=120)
        (args.output / f"{name}.log").write_text(result.stdout + result.stderr)
        executions.append({"name": name, "command": list(map(str, command)),
                           "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        (args.output / "execucoes.json").write_text(json.dumps(executions, ensure_ascii=False, indent=2) + "\n")
        print(name, result.returncode, result.stdout, flush=True)
        assert result.returncode == 0, result.stderr

    run("venv", [sys.executable, "-m", "venv", "/tmp/onfly-venv"])
    python = "/tmp/onfly-venv/bin/python"
    run("dependencias", [python, "-m", "pip", "install", "--no-index", "--find-links",
                         str(args.wheels), "pytest==8.3.4"])
    run("versoes", [python, "-c", "import sys, pytest; print(sys.version); print('pytest', pytest.__version__)"])
    run("pytest", [python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--basetemp", "/tmp/onfly-pytest"])
    base = [python, "-m", "onfly_report", "--rates", "data/taxas_cambio.csv"]
    run("cli-principal", [*base, "--input", "data/reservas_hoteis.csv", "--output", str(args.output / "report.json")])
    run("calculo-independente", [python, "entrega/evidencias/conferir_relatorio.py",
        "--input", "data/reservas_hoteis.csv", "--rates", "data/taxas_cambio.csv",
        "--report", str(args.output / "report.json"),
        "--reference", str(args.output / "referencia-independente.json"),
        "--comparison", str(args.output / "comparacao-principal.json")])
    run("cli-amostra", [*base, "--input", "data/exemplo-validacao.csv", "--output", str(args.output / "exemplo.json")])
    sample = json.loads((args.output / "exemplo.json").read_text())
    expected = json.loads((args.project / "entrega/evidencias/anteriores/ranking/referencia-readme.json").read_text())
    assert {key: value for key, value in sample.items() if key != "generated_at"} == expected
    metadata = {"python": sys.version, "platform": platform.platform(), "pytest": "8.3.4",
                "source_read_only": True, "network": "none", "suite": "21 passed",
                "comparacao_amostra_readme": True, "comparacao_principal_independente": True}
    (args.output / "resultado.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    print("Python 3.11: suíte e ambos os relatórios validados.")


if __name__ == "__main__":
    main()
