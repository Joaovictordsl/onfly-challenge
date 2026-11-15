# Investigação inicial — Onfly

Execução UTC: 20261115T222717Z. Projeto original: `/Users/joaovictordesousalima/Downloads/onfly-desafio`.

## Ambiente e escopo

Python 3.13.9 em venv isolado, compatível com `requires-python = ">=3.11"` do pyproject.toml. Não é uma validação específica com Python 3.11.
Instalados pytest==8.3.4 e ruff==0.8.4, exatamente como requirements-dev.txt. Versões transitivas em requirements-executados.txt.
O primeiro pip install falhou por resolução/acesso de rede. Os wheels foram baixados do PyPI via curl, conferidos por SHA-256 e instalados sem índice. Logs e URLs estão preservados.
Nenhum arquivo do projeto original foi alterado, adicionado ou removido: os manifestos SHA-256 de todos os 31 arquivos são idênticos. Os resultados ficam nesta pasta de investigação, fora do projeto original.
Cache do pytest e bytecode foram desabilitados; temporários, XML e saída do CLI foram direcionados para fora do projeto original.

## Comandos executados

Executados no diretório original. As opções adicionais do pytest controlam somente cache, temporários e a gravação do XML.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/pytest-temp --junitxml /Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/pytest.xml
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/python -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output /Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/exemplo-observado.json
```

## Testes fornecidos

Resultado real do pytest: 5 testes, 5 falhas, 0 erros; código de saída 1. Consulte pytest.stdout.log e pytest.xml.

| Teste | Esperado | Observado |
|---|---|---|
| Câmbio | 642.00 BRL | 118.45 BRL |
| Noites na virada de mês | 3 | -28 |
| Regressão: total / média | 1542.00 / 308.40 | 1018.45 / 203.69 |
| Status: total faturável | 100.00 BRL | 120.00 BRL |
| Ranking | H01, H02, H03 | H04, H03, H02 |

## CLI com a amostra de validação

Código de saída: 0; stderr vazio: True. O comando conclui, porém gera números incorretos.

```text
Reservas: 12 | Confirmadas: 9 | Noites: -33 | Total BRL: 5962.41
```

### Resumo

| Campo | Esperado no README | Observado | Resultado |
|---|---:|---:|---|
| total_reservations | 12 | 12 | OK |
| confirmed_reservations | 9 | 9 | OK |
| cancelled_reservations | 2 | 2 | OK |
| no_show_reservations | 1 | 1 | OK |
| total_room_nights | 28 | -33 | FALHA |
| total_amount_brl | 7566.00 | 5962.41 | FALHA |
| average_nightly_rate_brl | 270.21 | 0.00 | FALHA |

### Agrupamento por mês

| Mês | Reservas esperado / observado | Noites esperado / observado | BRL esperado / observado |
|---|---|---|---|
| 2025-01 | 8 / 9 | 25 / -36 | 6684.00 / 5936.90 |
| 2025-02 | 1 / 1 | 3 / 3 | 882.00 / 25.51 |

### Ranking de hotéis

| Posição | Hotel esperado | Noites / BRL esperados | Hotel observado | Noites / BRL observados |
|---|---|---|---|---|
| 1 | H01 — Hotel Aurora Paulista | 3 / 1200.00 | H09 — Hotel Lisboa, Centro | 3 / 25.51 |
| 2 | H02 — Hotel Mirante | 2 / 1084.00 | H02 — Hotel Mirante | 2 / 36.90 |
| 3 | H12 — Hotel Miami Beach | 1 / 1000.00 | H05 — Hotel Recife Plaza | 1 / 300.00 |
| 4 | H10 — Hotel Madrid, Gran Vía | 4 / 900.00 | H08 — Hotel Iguazu Falls | 1 / 400.00 |
| 5 | H09 — Hotel Lisboa, Centro | 3 / 882.00 | H07 — Hotel Brasília Tower | 2 / 600.00 |

Comparação recursiva: 22 valores divergentes, detalhados em comparacao.json. A referência foi extraída diretamente das três tabelas da amostra no README. report_version é 1.0; generated_at tem offset -03:00 e seu valor foi ignorado conforme o contrato.

## Causas identificadas por leitura do código

- Câmbio: currency_converter.py:11 divide pela taxa e converte por float.
- Noites: stay_calculator.py:10 subtrai números dos dias do mês em vez das datas completas.
- Status: status_policy.py:8 aceita NO_SHOW ao excluir somente CANCELLED. A amostra inclui indevidamente H05 e uma reserva adicional em janeiro.
- Ranking: report_builder.py:91 ordena o total em ordem crescente.
- Corte de leitura: csv_reservation_repository.py:47-48 interrompe ao chegar a 200 registros. Este defeito não é exercitado pela amostra de 12 reservas nem pelos cinco testes fornecidos. Sua correção não pode ser comprovada por estas execuções.

## Evidências preservadas

- Logs completos e códigos de saída: pytest.* e cli-amostra.*.
- Relatório real: exemplo-observado.json; referência do README: exemplo-esperado-readme.json; diferenças: comparacao.json.
- Cópia do README usado: README-referencia.md.
- Entradas e relatórios temporários dos cinco testes: casos-pytest/.
- Ambiente e dependências: ambiente.json, requirements-executados.txt, pacotes-download.json e logs de instalação.
- Integridade: manifesto-antes.json, manifesto-depois.json e integridade.json.

Nenhuma correção foi realizada nesta etapa.
