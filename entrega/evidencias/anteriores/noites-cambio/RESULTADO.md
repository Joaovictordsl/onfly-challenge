# Correção de noites e câmbio

Estado inicial: commit 7c8238a, com as correções de leitura e status já versionadas e árvore de trabalho limpa.

## Alterações e causas

- Noites: substituída a subtração dos dias do mês pela diferença entre datas completas, multiplicada por rooms. Isso considera viradas de mês/ano e anos bissextos.
- Câmbio: substituída a divisão com float por amount * rate. Os operandos já são Decimal, lidos diretamente dos CSVs; agregações, média e formatação também usam Decimal.
- ReportBuilder não foi alterado. O arredondamento existente continua apenas na montagem da saída, com duas casas e ROUND_HALF_UP. A correção do ranking foi reservada à próxima etapa.
- Novo tests/test_nights_and_money.py: três cenários de datas/quartos, dois de precisão decimal e dois de soma e arredondamento na saída.

## Validação

Ambiente reutilizado: Python 3.13.9, pytest 8.3.4 e ruff 0.8.4. Não houve execução específica com Python 3.11.
Comando relevante: python -m pytest -q -p no:cacheprovider tests/test_nights.py tests/test_currency.py tests/test_regression_report.py tests/test_nights_and_money.py
Comando da suíte: python -m pytest -q -p no:cacheprovider
Ambos com PYTHONDONTWRITEBYTECODE=1 e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1.

- Antes: 9 falhas e 1 aprovação nos testes relevantes (testes-antes.log).
- Depois: 10 aprovações nos testes relevantes (testes-relevantes-depois.log).
- Suíte completa: 15 aprovações e 1 falha no teste fornecido de ranking (suite-completa-depois.log).
- Ruff nos dois módulos alterados e no teste novo: aprovado. git diff --check: aprovado.

## Comparação da amostra com o README

A referência foi extraída das tabelas entre AMOSTRA:INICIO e AMOSTRA:FIM e preservada em referencia-readme.json. Todos os comandos e códigos de saída do CLI estão em execucoes-cli.json; todos terminaram com código 0.

| Campo | Esperado | Observado |
|---|---:|---:|
| total_reservations | 12 | 12 |
| confirmed_reservations | 9 | 9 |
| cancelled_reservations | 2 | 2 |
| no_show_reservations | 1 | 1 |
| total_room_nights | 28 | 28 |
| total_amount_brl | 7566.00 | 7566.00 |
| average_nightly_rate_brl | 270.21 | 270.21 |

| Mês | Reservas esperado/observado | Noites esperado/observado | BRL esperado/observado |
|---|---|---|---|
| 2025-01 | 8/8 | 25/25 | 6684.00/6684.00 |
| 2025-02 | 1/1 | 3/3 | 882.00/882.00 |

Ranking esperado: H01, H02, H12, H10, H09. Observado: H08, H07, H11, H03, H09. A seleção/ordenação permanece incorreta, como previsto para esta etapa.
Uma execução adicional com --top 100 permitiu verificar os valores e as noites dos cinco hotéis publicados no README: todos correspondem. Consulte exemplo-todos-hoteis.json e comparacao-readme.json.

## Dataset principal e integridade

CLI principal: 300 reservas, 235 confirmadas, 31 canceladas, 34 NO_SHOW, 1347 noites, BRL 396170.00 e média BRL 294.11. Esses valores coincidem com a referência calculada na investigação inicial. Ranking ainda pendente.
Os três CSVs e os seis arquivos fornecidos de testes/utilitários são idênticos ao commit original 9f8d8f7 por comparação byte a byte. Todos os arquivos de testes preexistentes, inclusive os da etapa anterior, preservaram seus hashes.
Entre os arquivos preexistentes de src, tests e data, apenas currency_converter.py e stay_calculator.py foram alterados; hashes registrados antes/depois. O teste novo é um arquivo adicional.

correcao.patch contém o diff completo de produção e dos testes adicionados. Alterações locais, sem commit ou push. Estes registros ficam em output/, ignorado pelo Git.
