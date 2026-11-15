# Codex conversation

## User

Faca uma leitura inicial do README.md do desafio pratico da onfly. esta em ~/Downloads/onfly-desafio

## Assistant

Vou localizar o README em `~/Downloads/onfly-desafio` e fazer uma leitura inicial dos requisitos do desafio.

## Activity

    $ rg --files -g 'README*' -g 'AGENTS.md' /Users/joaovictordesousalima/Downloads/onfly-desafio
    /Users/joaovictordesousalima/Downloads/onfly-desafio/README.md
    ✓ • 340ms

## Activity

    $ cat /Users/joaovictordesousalima/Downloads/onfly-desafio/README.md
    # Onfly — Consolidador de reservas de hotel
    
    Você recebeu a exportação de reservas de hotel de uma empresa cliente da Onfly. O CLI deste projeto deveria gerar um relatório JSON consolidado, mas **entrega números errados**.
    
    **Sua tarefa:** encontrar e corrigir os defeitos do CLI, fazer os testes fornecidos passarem e
    entregar o projeto.
    
    ## Como rodar
    
    Requisitos: Python 3.11+ e pytest para os testes (`requirements-dev.txt`).
    
    ```bash
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt
    
    PYTHONPATH=src python -m onfly\_report \\
      --input data/reservas\_hoteis.csv \\
      --rates data/taxas\_cambio.csv \\
      --output output/report.json
    ```
    
    O relatório é gravado em `output/report.json`; o CLI cria o diretório. Um resumo é impresso no
    stdout.
    
    Os testes já estão em `tests/`. No início, todos falham — é esperado. Rode:
    
    ```bash
    pytest -q
    ```
    
    Corrija o código até todos passarem. **Não altere os testes fornecidos.** Se quiser, adicione
    testes novos em arquivos `test\_\*.py`.
    
    ## Estrutura
    
    ```
    .
    ├── README.md              # este arquivo
    ├── pyproject.toml
    ├── requirements\*.txt
    ├── data/
    │   ├── reservas\_hoteis.csv
    │   ├── taxas\_cambio.csv
    │   └── exemplo-validacao.csv
    ├── src/onfly\_report/      # CLI
    ├── tests/                 # testes fornecidos
    ├── entrega/               # sua entrega
    └── output/                # relatório gerado
    ```
    
    ## Regras de negócio
    
    Os dados fornecidos estão consistentes, os defeitos estão no CLI.
    
    As colunas do CSV são autoexplicativas. O relatório usa hotel, check-in, check-out, quartos, status, moeda e valor; as demais colunas não afetam os totais.
    
    ### Status
    
    * Só `CONFIRMED` é faturável.
    * `CANCELLED` e `NO\_SHOW` contam em `total\_reservations` e nas contagens por status, mas não entram
    em noites, valores, `by\_month` nem `top\_hotels`.
    
    ### Noites
    
    ```
    room\_nights = (checkout\_date - checkin\_date).days \* rooms
    ```
    
    A diferença é não inclusiva: check-in 10/01 e check-out 13/01 = 3 noites. Vale também na virada de
    mês/ano.
    
    ### Câmbio
    
    * `amount` está na moeda de `currency`.
    * Converta com `amount \* rate\_to\_brl`, usando a tabela `data/taxas\_cambio.csv`.
    * Todas as moedas do dataset têm taxa.
    
    ### Totais
    
    * `total\_reservations` = número de reservas no arquivo.
    * `confirmed\_reservations`, `cancelled\_reservations` e `no\_show\_reservations` = contagens por status.
    * `total\_room\_nights`, `total\_amount\_brl` e `average\_nightly\_rate\_brl` usam apenas `CONFIRMED`.
    
    ### Ordem do processamento
    
    ```
    ler → converter tipos → contar status → filtrar CONFIRMED → agregar
    ```
    
    ### Exatidão
    
    * Use `Decimal`, nunca `float`, no dinheiro.
    * Some os valores exatos e arredonde **só na serialização**, para 2 casas, com half-up.
    * `average\_nightly\_rate\_brl = total\_amount\_brl / total\_room\_nights`; sem noites, `"0.00"`.
    * Check-in/check-out são datas civis (`YYYY-MM-DD`).
    * `generated\_at` usa offset fixo `-03:00` e é ignorado na comparação.
    
    ### Ordenação
    
    * `by\_month`: `month` ascendente.
    * `top\_hotels`: `total\_brl` decrescente; empate por `hotel\_id` ascendente.
    
    ## Contrato do CLI
    
    ```bash
    python -m onfly\_report \\
      --input data/reservas\_hoteis.csv \\
      --rates data/taxas\_cambio.csv \\
      --output output/report.json \\
      --top 5
    ```
    
    |Argumento|Obrigatório|Padrão|
    |-|-|-|
    |`--input`|sim|—|
    |`--rates`|sim|—|
    |`--output`|não|`output/report.json`|
    |`--top`|não|`5` (inteiro ≥ 1)|
    
    Códigos de saída: `0` sucesso, `2` entrada/argumento inválido, `1` erro inesperado.
    
    O relatório deve ter exatamente este formato:
    
    ```json
    {
      "report\_version": "1.0",
      "generated\_at": "2025-07-01T10:00:00-03:00",
      "summary": {
        "total\_reservations": 0,
        "confirmed\_reservations": 0,
        "cancelled\_reservations": 0,
        "no\_show\_reservations": 0,
        "total\_room\_nights": 0,
        "total\_amount\_brl": "0.00",
        "average\_nightly\_rate\_brl": "0.00"
      },
      "by\_month": \[
        {"month": "2025-01", "reservations": 0, "room\_nights": 0, "total\_brl": "0.00"}
      ],
      "top\_hotels": \[
        {"hotel\_id": "H01", "hotel\_name": "Hotel Exemplo", "room\_nights": 0, "total\_brl": "0.00"}
      ]
    }
    ```
    
    * Dinheiro é string com exatamente 2 casas (`"1234.50"`), sem separador de milhar.
    * `report\_version` é sempre `"1.0"`.
    * `top\_hotels` tem `--top` itens (ou menos, se houver menos hotéis).
    * `by\_month` usa o mês do check-in.
    * Não altere nomes, tipos ou semântica dos campos.
    
    ## Amostra de validação
    
    Rode o CLI na amostra e compare com o resultado abaixo:
    
    ```bash
    PYTHONPATH=src python -m onfly\_report \\
      --input data/exemplo-validacao.csv \\
      --rates data/taxas\_cambio.csv \\
      --output output/exemplo.json
    ```
    
    <!-- AMOSTRA:INICIO -->
    
    |Campo|Valor esperado|
    |-|-|
    |`total\_reservations`|12|
    |`confirmed\_reservations`|9|
    |`cancelled\_reservations`|2|
    |`no\_show\_reservations`|1|
    |`total\_room\_nights`|28|
    |`total\_amount\_brl`|7566.00|
    |`average\_nightly\_rate\_brl`|270.21|
    
    |`month`|`reservations`|`room\_nights`|`total\_brl`|
    |-|-|-|-|
    |2025-01|8|25|6684.00|
    |2025-02|1|3|882.00|
    
    |`hotel\_id`|`hotel\_name`|`room\_nights`|`total\_brl`|
    |-|-|-|-|
    |H01|Hotel Aurora Paulista|3|1200.00|
    |H02|Hotel Mirante|2|1084.00|
    |H12|Hotel Miami Beach|1|1000.00|
    |H10|Hotel Madrid, Gran Vía|4|900.00|
    |H09|Hotel Lisboa, Centro|3|882.00|
    
    <!-- AMOSTRA:FIM -->
    
    A amostra cobre apenas parte dos cenários; use as regras acima para os demais.
    
    ## Entrega
    
    Suba o projeto, incluindo a pasta `entrega/`, em um repositório público no GitHub e compartilhe o
    acesso com nosso time via forms.
    
    ```
    entrega/
    ├── README-ENTREGA.md
    └── uso-de-ia/                 # apenas se usou IA
        ├── sessao.md (ou .txt/.jsonl; várias: sessao-01.md, sessao-02.md...)
        └── declaracao.md
    ```
    
    **`README-ENTREGA.md`** deve ter: defeitos corrigidos, causa raiz em uma frase por defeito, como
    investigou/abordou o problema, como validar e resultado do `pytest`.
    
    **Caminho com IA:** use assistentes de IA se quiser. Se usar, inclua a exportação da(s) sessão(ões)
    no formato nativo da ferramenta (`/export` do Claude Code, export/JSON de outros assistentes, ou log
    consolidado de prompts e respostas) e uma `declaracao.md` com:
    
    * ferramenta e modelo usados;
    * o que a IA fez e o que você fez.
    
    **Caminho sem IA:** não é necessária sessão nem declaração. A investigação fica no
    `entrega/README-ENTREGA.md`.
    
    ## O que não pode mudar
    
    * O comando e os argumentos do CLI.
    * O schema e a semântica do relatório acima.
    * Os arquivos `data/reservas\_hoteis.csv` e `data/taxas\_cambio.csv`.
    
    Você pode reorganizar o código interno, adicionar arquivos, melhorar logs e adicionar testes. Os
    testes fornecidos devem permanecer inalterados.
    
    ## Como será avaliado
    
    A correção verifica se o relatório segue este documento, se os defeitos foram corrigidos e se os
    testes fornecidos passam sem alteração. Testes adicionais são considerados.
    
    ## Checklist
    
    * \[ ] O CLI roda com Python 3.11 (`PYTHONPATH=src python -m onfly\_report ...`).
    * \[ ] O comando de execução gera `output/report.json` sem erro.
    * \[ ] O relatório segue o contrato acima.
    * \[ ] `pytest -q` passa com os testes fornecidos.
    * \[ ] `entrega/README-ENTREGA.md` preenchido.
    * \[ ] Sessão + declaração apenas no caminho com IA; investigação no README-ENTREGA nos dois caminhos.
    * \[ ] Repositório público no GitHub com o projeto e o link enviado.
    
    ✓ • 0ms

## Assistant

Li o [README.md](/Users/joaovictordesousalima/Downloads/onfly-desafio/README.md). O desafio é **investigar e corrigir um CLI Python que consolida reservas de hotéis e gera totais incorretos**.

Os requisitos centrais são:

- **Contagens:** todas as reservas entram no total e nas contagens por status.
- **Faturamento:** apenas `CONFIRMED` entra nos valores, noites, agrupamento mensal e ranking de hotéis.
- **Noites:** diferença entre check-out e check-in, multiplicada pelo número de quartos.
- **Câmbio:** valor original multiplicado pela taxa para BRL.
- **Precisão:** usar `Decimal`, acumular valores exatos e arredondar somente na serialização, com duas casas e `ROUND_HALF_UP`.
- **Agrupamento mensal:** usar o mês do check-in.
- **Ordenação:** meses em ordem crescente; hotéis por valor decrescente, com desempate pelo identificador crescente.

O contrato exige preservar argumentos, nomes, tipos e significado dos campos do JSON. Também define códigos de saída: `0` para sucesso, `2` para entrada ou argumento inválido e `1` para erro inesperado.

**Não podem ser alterados:** os testes fornecidos, os dois CSVs principais e o contrato do CLI. É permitido reorganizar o código e adicionar testes.

A amostra de validação deve resultar em **12 reservas, 9 confirmadas, 28 diárias de quartos, R$ 7.566,00 e média de R$ 270,21**.

A entrega inclui o projeto em repositório público e `entrega/README-ENTREGA.md`, com defeitos, causas, investigação, validação e resultado do pytest. Como estamos usando IA, também será necessário incluir o registro da sessão e a declaração de ferramenta/modelo e responsabilidades.

Até aqui, fiz apenas a leitura do README, sem analisar ou modificar o código. O próximo passo é examinar a implementação e executar os testes para estabelecer o diagnóstico inicial.

## User

voce leu tambem que a leitura para em 200 reservas, quando na verdade deveria ir ate 300?

## Assistant

Não. O README que li **não menciona o limite de 200 nem o total de 300 reservas**. Ele exige que `total_reservations` corresponda a todas as reservas do arquivo.

Como ainda não examinei o código nem os dados, não identifiquei esse possível corte na leitura. Se o arquivo tem 300 reservas e o CLI processa só 200, isso viola o requisito.

## User

ok, pode ler o projeto completo para entender melhor, os testes e todos os arquivos.

## Assistant

Vou ler a estrutura, o código, os testes e os arquivos de dados para entender o projeto completo, incluindo o possível corte em 200 reservas. Nesta etapa, não vou alterar os arquivos.

## Activity

    $ ls -la /Users/joaovictordesousalima/Downloads/onfly-desafio
    total 48
    drwxr-xr-x@  12 joaovictordesousalima  staff    384 Nov 15 19:14 .
    drwx------+ 675 joaovictordesousalima  staff  21600 Nov 15 19:14 ..
    -rw-rw-r--@   1 joaovictordesousalima  staff    182 Nov  4 11:16 .gitignore
    -rw-rw-r--@   1 joaovictordesousalima  staff   7517 Nov  4 11:21 README.md
    drwxr-xr-x@   5 joaovictordesousalima  staff    160 Nov 15 19:14 data
    drwxr-xr-x@   3 joaovictordesousalima  staff     96 Nov 15 19:14 entrega
    drwxr-xr-x@   3 joaovictordesousalima  staff     96 Nov 15 19:14 output
    -rw-rw-r--@   1 joaovictordesousalima  staff    335 Nov  4 11:16 pyproject.toml
    -rw-rw-r--@   1 joaovictordesousalima  staff     26 Nov  4 11:16 requirements-dev.txt
    -rw-rw-r--@   1 joaovictordesousalima  staff    107 Nov  4 11:16 requirements.txt
    drwxr-xr-x@   3 joaovictordesousalima  staff     96 Nov 15 19:14 src
    drwxr-xr-x@   8 joaovictordesousalima  staff    256 Nov 15 19:14 tests
    ✓ • 0ms

## Activity

    $ rg --files --hidden -g '!.git/**' /Users/joaovictordesousalima/Downloads/onfly-desafio
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/row_parser.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/stay_calculator.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/__init__.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/currency_converter.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/status_policy.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/report_builder.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/__main__.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/exceptions.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/cli.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/repositories/csv_reservation_repository.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/repositories/__init__.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/repositories/csv_rate_repository.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/__init__.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/models.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/logging_config.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/data/taxas_cambio.csv
    /Users/joaovictordesousalima/Downloads/onfly-desafio/data/exemplo-validacao.csv
    /Users/joaovictordesousalima/Downloads/onfly-desafio/data/reservas_hoteis.csv
    /Users/joaovictordesousalima/Downloads/onfly-desafio/.gitignore
    /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements-dev.txt
    /Users/joaovictordesousalima/Downloads/onfly-desafio/README.md
    /Users/joaovictordesousalima/Downloads/onfly-desafio/output/.gitkeep
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/helpers.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_currency.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_status_rules.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_top_hotels.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_nights.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_regression_report.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/entrega/.gitkeep
    /Users/joaovictordesousalima/Downloads/onfly-desafio/pyproject.toml
    /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements.txt
    ✓ • 0ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        root = Path('/Users/joaovictordesousalima/Downloads/onfly-desafio')
        for p in sorted((root / 'data').iterdir()):
            if p.is_file():
                print(f'\nFILE: {p.relative_to(root)}')
                for n, line in enumerate(p.read_text().splitlines(), 1):
                    print(f'{n:4}: {line}')
        PY
    
    FILE: data/exemplo-validacao.csv
       1: reservation_id,traveler_name,company_id,hotel_id,hotel_name,city,country,checkin_date,checkout_date,rooms,status,currency,amount,payment_method,booked_at
       2: EX-01,Pessoa Fictícia,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-01-10,2025-01-13,1,CONFIRMED,BRL,1200.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
       3: EX-02,Pessoa Fictícia,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-01-20,2025-01-22,1,CONFIRMED,USD,200.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
       4: EX-03,Pessoa Fictícia,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-01-28,2025-02-02,2,CONFIRMED,BRL,800.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
       5: EX-04,Pessoa Fictícia,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-01-05,2025-01-07,1,CANCELLED,BRL,500.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
       6: EX-05,Pessoa Fictícia,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-01-06,2025-01-07,1,NO_SHOW,BRL,300.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
       7: EX-06,Pessoa Fictícia,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-01-07,2025-01-09,1,CANCELLED,BRL,250.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
       8: EX-07,Pessoa Fictícia,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-01-08,2025-01-10,1,CONFIRMED,BRL,600.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
       9: EX-08,Pessoa Fictícia,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-01-09,2025-01-10,1,CONFIRMED,BRL,400.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
      10: EX-09,Pessoa Fictícia,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-02-05,2025-02-08,1,CONFIRMED,EUR,150.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
      11: EX-10,Pessoa Fictícia,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-01-12,2025-01-16,1,CONFIRMED,BRL,900.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
      12: EX-11,Pessoa Fictícia,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-01-14,2025-01-16,1,CONFIRMED,BRL,700.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
      13: EX-12,Pessoa Fictícia,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-01-15,2025-01-16,1,CONFIRMED,BRL,1000.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    
    FILE: data/reservas_hoteis.csv
       1: reservation_id,traveler_name,company_id,hotel_id,hotel_name,city,country,checkin_date,checkout_date,rooms,status,currency,amount,payment_method,booked_at
       2: RSV-0001,Hugo Siqueira,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-06-29,2025-07-03,1,CANCELLED,BRL,1457.41,INVOICE,2025-06-21T17:02:00-03:00
       3: RSV-0002,Felipe Martins,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-01-30,2025-02-04,1,CONFIRMED,BRL,1551.16,INVOICE,2024-12-31T15:04:00-03:00
       4: RSV-0003,Diego Monteiro,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-01-31,2025-02-06,1,CONFIRMED,EUR,233.79,PIX,2025-01-11T16:18:00-03:00
       5: RSV-0004,Olívia Prado,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-01-04,2025-01-11,1,NO_SHOW,BRL,2116.06,INVOICE,2024-12-28T14:28:00-03:00
       6: RSV-0005,Elisa Queiroz,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-04-04,2025-04-07,1,NO_SHOW,BRL,974.48,CORPORATE_CARD,2025-03-30T18:59:00-03:00
       7: RSV-0006,Jonas Neves,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2024-12-30,2025-01-01,2,NO_SHOW,USD,502.12,PIX,2024-12-12T08:37:00-03:00
       8: RSV-0007,Wagner Lopes,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-01-22,2025-01-29,1,NO_SHOW,USD,106.75,CORPORATE_CARD,2025-01-12T17:19:00-03:00
       9: RSV-0008,Rafael Cardoso,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-02-27,2025-03-02,2,CONFIRMED,BRL,2421.16,PIX,2025-02-15T09:48:00-03:00
      10: RSV-0009,Rafael Cardoso,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-04-20,2025-04-25,1,CONFIRMED,USD,93.65,CORPORATE_CARD,2025-03-21T18:53:00-03:00
      11: RSV-0010,Eduarda Alves,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2024-12-10,2024-12-13,1,NO_SHOW,BRL,2481.16,CORPORATE_CARD,2024-11-21T18:25:00-03:00
      12: RSV-0011,Ursula Gomes,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-01-31,2025-02-03,1,CONFIRMED,BRL,1185.20,PIX,2025-01-19T12:46:00-03:00
      13: RSV-0012,Camila Farias,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-01-31,2025-02-02,1,CANCELLED,BRL,1435.63,INVOICE,2025-01-17T15:38:00-03:00
      14: RSV-0013,Carla Dias,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-05-30,2025-06-01,1,NO_SHOW,USD,388.43,CORPORATE_CARD,2025-05-13T18:19:00-03:00
      15: RSV-0014,Ana Souza,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-05-29,2025-06-02,3,CONFIRMED,BRL,2222.19,INVOICE,2025-05-19T13:07:00-03:00
      16: RSV-0015,Carla Dias,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-02-28,2025-03-03,1,NO_SHOW,BRL,2325.19,INVOICE,2025-02-25T14:55:00-03:00
      17: RSV-0016,Zélia Correia,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2024-12-11,2024-12-16,1,NO_SHOW,BRL,2088.27,CORPORATE_CARD,2024-11-27T12:07:00-03:00
      18: RSV-0017,Breno Carvalho,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-02-20,2025-02-24,2,CONFIRMED,BRL,565.92,PIX,2025-01-23T09:15:00-03:00
      19: RSV-0018,Henrique Costa,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-01-10,2025-01-16,1,NO_SHOW,BRL,2258.84,PIX,2025-01-07T16:40:00-03:00
      20: RSV-0019,João Pereira,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-03-21,2025-03-28,1,CONFIRMED,BRL,708.79,PIX,2025-03-14T10:38:00-03:00
      21: RSV-0020,Lívia Moura,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2024-12-21,2024-12-25,1,CONFIRMED,BRL,2211.70,PIX,2024-12-06T18:59:00-03:00
      22: RSV-0021,Rafael Cardoso,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-05-21,2025-05-24,1,CONFIRMED,BRL,1498.86,PIX,2025-04-30T12:50:00-03:00
      23: RSV-0022,Felipe Martins,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2024-12-10,2024-12-14,1,CONFIRMED,BRL,1253.41,PIX,2024-11-30T09:41:00-03:00
      24: RSV-0023,Mariana Castro,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-04-18,2025-04-25,2,CONFIRMED,EUR,263.39,INVOICE,2025-03-23T17:41:00-03:00
      25: RSV-0024,Lucas Barbosa,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-05-29,2025-06-03,1,NO_SHOW,BRL,2756.84,CORPORATE_CARD,2025-05-26T16:41:00-03:00
      26: RSV-0025,Vitor Sampaio,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-04-17,2025-04-22,1,CONFIRMED,USD,273.88,PIX,2025-04-07T14:26:00-03:00
      27: RSV-0026,Natália Campos,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-06-03,2025-06-06,1,CANCELLED,USD,281.01,CORPORATE_CARD,2025-05-25T19:54:00-03:00
      28: RSV-0027,Felipe Martins,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-05-12,2025-05-15,3,CONFIRMED,USD,424.31,INVOICE,2025-05-07T17:45:00-03:00
      29: RSV-0028,Breno Carvalho,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-06-05,2025-06-11,2,CONFIRMED,USD,598.53,PIX,2025-05-06T16:05:00-03:00
      30: RSV-0029,Sofia Ribeiro,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-03-07,2025-03-10,3,CONFIRMED,EUR,152.56,CORPORATE_CARD,2025-03-02T10:04:00-03:00
      31: RSV-0030,Lucas Barbosa,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-05-17,2025-05-18,1,CANCELLED,EUR,126.35,PIX,2025-05-04T10:10:00-03:00
      32: RSV-0031,Camila Farias,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-02-02,2025-02-06,1,CONFIRMED,BRL,931.95,CORPORATE_CARD,2025-01-18T17:18:00-03:00
      33: RSV-0032,Sofia Ribeiro,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-03-16,2025-03-23,1,CONFIRMED,EUR,477.27,INVOICE,2025-03-01T15:49:00-03:00
      34: RSV-0033,Gabriela Nunes,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-04-07,2025-04-14,1,CONFIRMED,BRL,477.84,PIX,2025-03-22T13:35:00-03:00
      35: RSV-0034,Olívia Prado,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-01-29,2025-02-02,1,CONFIRMED,BRL,711.00,INVOICE,2025-01-15T09:58:00-03:00
      36: RSV-0035,Ursula Gomes,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-01-13,2025-01-18,1,NO_SHOW,BRL,2786.59,CORPORATE_CARD,2025-01-01T11:01:00-03:00
      37: RSV-0036,Elisa Queiroz,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-06-05,2025-06-07,1,CANCELLED,BRL,2055.38,INVOICE,2025-05-31T20:45:00-03:00
      38: RSV-0037,Sofia Ribeiro,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-01-29,2025-02-01,1,CONFIRMED,EUR,331.82,CORPORATE_CARD,2025-01-15T09:49:00-03:00
      39: RSV-0038,Bruno Lima,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-01-31,2025-02-06,1,CONFIRMED,BRL,2399.88,PIX,2025-01-15T17:34:00-03:00
      40: RSV-0039,Felipe Martins,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-02-10,2025-02-14,1,CONFIRMED,USD,205.09,PIX,2025-01-27T10:42:00-03:00
      41: RSV-0040,Yuri Fernandes,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-01-18,2025-01-23,2,CONFIRMED,BRL,1707.67,INVOICE,2025-01-05T15:02:00-03:00
      42: RSV-0041,Vitor Sampaio,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-01-03,2025-01-06,1,CONFIRMED,BRL,1889.23,CORPORATE_CARD,2024-12-09T17:47:00-03:00
      43: RSV-0042,Lucas Barbosa,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2024-12-21,2024-12-23,2,CANCELLED,BRL,1488.33,CORPORATE_CARD,2024-11-28T15:40:00-03:00
      44: RSV-0043,Thiago Araújo,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2024-12-15,2024-12-16,1,CONFIRMED,BRL,2288.22,PIX,2024-11-16T08:20:00-03:00
      45: RSV-0044,Vitor Sampaio,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-05-02,2025-05-09,1,CONFIRMED,USD,265.63,INVOICE,2025-04-07T08:55:00-03:00
      46: RSV-0045,Fábio Bezerra,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2024-12-13,2024-12-19,1,CONFIRMED,BRL,1180.64,INVOICE,2024-12-07T15:44:00-03:00
      47: RSV-0046,Ursula Gomes,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-05-29,2025-06-03,1,CONFIRMED,BRL,2787.99,CORPORATE_CARD,2025-05-23T16:18:00-03:00
      48: RSV-0047,Carla Dias,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2024-12-10,2024-12-14,1,NO_SHOW,USD,166.66,PIX,2024-11-25T13:28:00-03:00
      49: RSV-0048,Giovana Pires,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-03-14,2025-03-17,1,NO_SHOW,USD,119.02,PIX,2025-02-21T14:23:00-03:00
      50: RSV-0049,Yuri Fernandes,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-01-31,2025-02-05,1,CANCELLED,BRL,928.19,PIX,2025-01-10T13:23:00-03:00
      51: RSV-0050,Ursula Gomes,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2024-12-30,2025-01-03,1,CONFIRMED,USD,378.44,PIX,2024-12-13T13:25:00-03:00
      52: RSV-0051,Camila Farias,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-01-29,2025-02-03,1,CONFIRMED,BRL,638.51,CORPORATE_CARD,2025-01-04T12:45:00-03:00
      53: RSV-0052,Felipe Martins,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-03-16,2025-03-18,1,CANCELLED,USD,315.06,PIX,2025-02-15T19:28:00-03:00
      54: RSV-0053,Lucas Barbosa,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-03-23,2025-03-24,1,CONFIRMED,BRL,2533.76,INVOICE,2025-02-23T10:45:00-03:00
      55: RSV-0054,Jonas Neves,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-01-05,2025-01-07,2,CONFIRMED,USD,267.67,CORPORATE_CARD,2024-12-17T13:29:00-03:00
      56: RSV-0055,Eduarda Alves,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-01-30,2025-02-04,1,CONFIRMED,EUR,424.04,INVOICE,2025-01-27T10:20:00-03:00
      57: RSV-0056,Henrique Costa,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-05-18,2025-05-24,1,CONFIRMED,BRL,1409.91,PIX,2025-04-18T08:53:00-03:00
      58: RSV-0057,Mariana Castro,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2024-12-30,2025-01-02,1,NO_SHOW,BRL,2542.57,PIX,2024-12-02T09:16:00-03:00
      59: RSV-0058,Karina Melo,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-03-30,2025-04-05,1,CONFIRMED,BRL,1920.42,PIX,2025-03-11T17:09:00-03:00
      60: RSV-0059,Queila Moraes,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-05-19,2025-05-20,2,CONFIRMED,BRL,549.00,PIX,2025-04-28T20:36:00-03:00
      61: RSV-0060,Paulo Teixeira,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-05-21,2025-05-22,1,CONFIRMED,EUR,304.60,PIX,2025-04-30T12:30:00-03:00
      62: RSV-0061,Ursula Gomes,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-04-28,2025-05-01,1,CONFIRMED,BRL,1487.88,PIX,2025-04-17T17:09:00-03:00
      63: RSV-0062,Rafael Cardoso,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-03-05,2025-03-12,1,CONFIRMED,BRL,610.15,INVOICE,2025-02-25T15:07:00-03:00
      64: RSV-0063,Ursula Gomes,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-01-30,2025-02-05,1,CONFIRMED,USD,503.01,CORPORATE_CARD,2024-12-31T17:46:00-03:00
      65: RSV-0064,Paulo Teixeira,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-04-15,2025-04-19,2,CANCELLED,BRL,406.78,CORPORATE_CARD,2025-04-02T16:29:00-03:00
      66: RSV-0065,Gabriela Nunes,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-01-30,2025-02-05,2,NO_SHOW,BRL,1997.68,INVOICE,2025-01-20T16:00:00-03:00
      67: RSV-0066,Jonas Neves,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2024-12-30,2025-01-04,1,CONFIRMED,USD,106.60,INVOICE,2024-12-12T11:23:00-03:00
      68: RSV-0067,Zélia Correia,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2024-12-18,2024-12-21,2,CANCELLED,USD,433.81,INVOICE,2024-12-14T10:06:00-03:00
      69: RSV-0068,Carla Dias,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-03-12,2025-03-19,1,CONFIRMED,USD,344.74,CORPORATE_CARD,2025-02-23T08:02:00-03:00
      70: RSV-0069,Zélia Correia,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-04-05,2025-04-10,2,CONFIRMED,BRL,1153.52,PIX,2025-03-16T13:10:00-03:00
      71: RSV-0070,Bruno Lima,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-03-17,2025-03-24,1,CONFIRMED,BRL,2086.41,INVOICE,2025-03-07T15:52:00-03:00
      72: RSV-0071,Elisa Queiroz,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-01-19,2025-01-22,2,CONFIRMED,BRL,2486.64,INVOICE,2024-12-29T08:38:00-03:00
      73: RSV-0072,Yuri Fernandes,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-05-02,2025-05-07,1,CANCELLED,BRL,1891.11,CORPORATE_CARD,2025-04-12T20:53:00-03:00
      74: RSV-0073,Nicolas Freitas,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-02-28,2025-03-02,1,CONFIRMED,USD,243.12,INVOICE,2025-02-23T14:44:00-03:00
      75: RSV-0074,Yuri Fernandes,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-05-02,2025-05-08,1,CONFIRMED,BRL,1724.17,INVOICE,2025-04-10T15:33:00-03:00
      76: RSV-0075,Otávio Braga,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-04-11,2025-04-16,1,CONFIRMED,BRL,2017.83,INVOICE,2025-03-16T19:16:00-03:00
      77: RSV-0076,Fábio Bezerra,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2024-12-31,2025-01-04,1,CONFIRMED,BRL,2239.38,INVOICE,2024-12-08T11:44:00-03:00
      78: RSV-0077,Wagner Lopes,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-05-09,2025-05-12,1,CONFIRMED,BRL,1680.82,CORPORATE_CARD,2025-04-10T14:52:00-03:00
      79: RSV-0078,Irene Bastos,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-03-03,2025-03-06,3,CONFIRMED,BRL,978.29,INVOICE,2025-02-15T11:12:00-03:00
      80: RSV-0079,Olívia Prado,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-06-28,2025-07-04,2,CANCELLED,BRL,944.02,CORPORATE_CARD,2025-06-06T16:14:00-03:00
      81: RSV-0080,Elisa Queiroz,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2024-12-16,2024-12-17,1,CONFIRMED,USD,82.69,INVOICE,2024-11-28T10:26:00-03:00
      82: RSV-0081,Carla Dias,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-03-21,2025-03-22,3,CONFIRMED,BRL,1948.13,CORPORATE_CARD,2025-03-13T16:47:00-03:00
      83: RSV-0082,Carla Dias,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-02-02,2025-02-09,1,CONFIRMED,USD,176.88,CORPORATE_CARD,2025-01-09T12:56:00-03:00
      84: RSV-0083,Giovana Pires,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-05-30,2025-06-03,1,CONFIRMED,BRL,1681.09,INVOICE,2025-05-14T10:54:00-03:00
      85: RSV-0084,Lívia Moura,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-01-15,2025-01-21,1,CONFIRMED,BRL,384.51,PIX,2025-01-04T20:18:00-03:00
      86: RSV-0085,Isabela Ramos,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-02-13,2025-02-20,1,CONFIRMED,BRL,562.51,INVOICE,2025-01-22T09:11:00-03:00
      87: RSV-0086,Lívia Moura,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-02-27,2025-03-02,1,CONFIRMED,BRL,2687.39,CORPORATE_CARD,2025-02-17T17:46:00-03:00
      88: RSV-0087,Thiago Araújo,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-03-02,2025-03-08,1,CANCELLED,EUR,138.68,PIX,2025-02-08T16:59:00-03:00
      89: RSV-0088,Natália Campos,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2024-12-10,2024-12-13,1,CONFIRMED,BRL,2695.53,INVOICE,2024-11-24T10:29:00-03:00
      90: RSV-0089,Felipe Martins,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-05-18,2025-05-25,1,CONFIRMED,BRL,2216.56,PIX,2025-04-26T20:38:00-03:00
      91: RSV-0090,João Pereira,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-06-19,2025-06-20,1,CANCELLED,BRL,2562.08,CORPORATE_CARD,2025-06-12T17:34:00-03:00
      92: RSV-0091,Daniel Rocha,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-05-22,2025-05-24,2,CONFIRMED,BRL,572.81,INVOICE,2025-05-05T15:51:00-03:00
      93: RSV-0092,Queila Moraes,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2024-12-19,2024-12-20,1,CONFIRMED,USD,499.60,CORPORATE_CARD,2024-11-25T08:25:00-03:00
      94: RSV-0093,Elisa Queiroz,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-05-30,2025-06-03,2,CANCELLED,BRL,2785.60,CORPORATE_CARD,2025-04-30T09:59:00-03:00
      95: RSV-0094,Felipe Martins,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-02-14,2025-02-17,3,CONFIRMED,USD,313.24,PIX,2025-01-15T14:24:00-03:00
      96: RSV-0095,Ana Souza,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-05-30,2025-06-01,1,CONFIRMED,USD,284.39,CORPORATE_CARD,2025-05-25T19:14:00-03:00
      97: RSV-0096,Mariana Castro,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-04-18,2025-04-22,1,CONFIRMED,USD,208.71,PIX,2025-04-06T10:17:00-03:00
      98: RSV-0097,Carla Dias,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-01-14,2025-01-19,2,CONFIRMED,EUR,173.49,INVOICE,2025-01-11T09:38:00-03:00
      99: RSV-0098,Daniel Rocha,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-06-08,2025-06-14,1,CONFIRMED,BRL,924.13,CORPORATE_CARD,2025-06-01T20:55:00-03:00
     100: RSV-0099,Thiago Araújo,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-03-31,2025-04-06,1,CONFIRMED,BRL,2242.72,CORPORATE_CARD,2025-03-04T13:15:00-03:00
     101: RSV-0100,Breno Carvalho,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-05-30,2025-06-03,1,CONFIRMED,BRL,2505.30,PIX,2025-04-30T10:40:00-03:00
     102: RSV-0101,Yuri Fernandes,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-03-22,2025-03-26,2,CONFIRMED,BRL,2055.96,CORPORATE_CARD,2025-03-08T10:19:00-03:00
     103: RSV-0102,Amanda Pinto,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-04-28,2025-05-02,2,CONFIRMED,USD,499.00,INVOICE,2025-03-29T08:35:00-03:00
     104: RSV-0103,Irene Bastos,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-02-09,2025-02-11,1,CANCELLED,USD,559.56,PIX,2025-01-12T13:05:00-03:00
     105: RSV-0104,Jonas Neves,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-01-31,2025-02-06,1,CONFIRMED,EUR,150.91,CORPORATE_CARD,2025-01-06T17:46:00-03:00
     106: RSV-0105,Paulo Teixeira,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-03-01,2025-03-03,3,NO_SHOW,BRL,637.42,PIX,2025-02-04T15:58:00-03:00
     107: RSV-0106,Thiago Araújo,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-02-08,2025-02-13,1,CONFIRMED,BRL,1282.62,INVOICE,2025-01-21T18:22:00-03:00
     108: RSV-0107,Olívia Prado,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-04-16,2025-04-23,2,CONFIRMED,EUR,229.40,PIX,2025-04-02T08:36:00-03:00
     109: RSV-0108,Lívia Moura,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2024-12-31,2025-01-06,2,CONFIRMED,BRL,723.41,CORPORATE_CARD,2024-12-20T11:24:00-03:00
     110: RSV-0109,Diego Monteiro,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-06-11,2025-06-14,2,CONFIRMED,BRL,2717.95,CORPORATE_CARD,2025-05-21T19:31:00-03:00
     111: RSV-0110,Eduarda Alves,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-03-31,2025-04-06,1,CONFIRMED,BRL,2776.29,PIX,2025-03-29T16:02:00-03:00
     112: RSV-0111,Daniel Rocha,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2024-12-29,2025-01-01,1,CONFIRMED,USD,84.75,PIX,2024-12-12T15:23:00-03:00
     113: RSV-0112,Rafael Cardoso,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-05-22,2025-05-26,1,CONFIRMED,BRL,1701.53,PIX,2025-05-21T08:33:00-03:00
     114: RSV-0113,Paulo Teixeira,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-01-23,2025-01-29,1,CONFIRMED,BRL,612.19,CORPORATE_CARD,2025-01-19T16:09:00-03:00
     115: RSV-0114,Olívia Prado,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-03-09,2025-03-16,1,CONFIRMED,BRL,2700.28,INVOICE,2025-02-22T17:15:00-03:00
     116: RSV-0115,Ana Souza,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-01-21,2025-01-28,1,CONFIRMED,BRL,1279.20,PIX,2025-01-03T15:03:00-03:00
     117: RSV-0116,Carla Dias,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2024-12-14,2024-12-20,2,NO_SHOW,EUR,490.25,CORPORATE_CARD,2024-12-10T16:58:00-03:00
     118: RSV-0117,Carla Dias,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-06-16,2025-06-19,1,CONFIRMED,BRL,2026.85,CORPORATE_CARD,2025-06-07T16:36:00-03:00
     119: RSV-0118,Karina Melo,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-03-29,2025-04-04,1,NO_SHOW,USD,506.87,PIX,2025-02-27T09:19:00-03:00
     120: RSV-0119,Giovana Pires,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-04-18,2025-04-21,1,CANCELLED,USD,152.77,PIX,2025-03-26T19:05:00-03:00
     121: RSV-0120,Bruno Lima,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-01-29,2025-01-31,1,CONFIRMED,BRL,2689.40,PIX,2025-01-16T20:20:00-03:00
     122: RSV-0121,Felipe Martins,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-04-12,2025-04-17,3,CONFIRMED,BRL,805.06,PIX,2025-03-24T18:24:00-03:00
     123: RSV-0122,Ursula Gomes,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-02-03,2025-02-06,1,CONFIRMED,USD,487.62,INVOICE,2025-01-29T19:24:00-03:00
     124: RSV-0123,Camila Farias,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2024-12-30,2025-01-04,1,CANCELLED,BRL,600.47,PIX,2024-12-27T10:27:00-03:00
     125: RSV-0124,Sofia Ribeiro,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-04-28,2025-05-02,1,CONFIRMED,BRL,1815.21,INVOICE,2025-04-17T14:00:00-03:00
     126: RSV-0125,Thiago Araújo,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-01-18,2025-01-20,1,CONFIRMED,BRL,2029.02,INVOICE,2025-01-12T10:17:00-03:00
     127: RSV-0126,Fábio Bezerra,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-01-30,2025-02-04,1,CONFIRMED,USD,267.78,PIX,2025-01-22T19:40:00-03:00
     128: RSV-0127,Vitor Sampaio,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-04-29,2025-05-01,3,CONFIRMED,BRL,2411.95,INVOICE,2025-04-16T20:55:00-03:00
     129: RSV-0128,Ursula Gomes,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-06-05,2025-06-08,1,CONFIRMED,BRL,842.09,INVOICE,2025-05-25T10:25:00-03:00
     130: RSV-0129,Henrique Costa,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-06-19,2025-06-26,1,CONFIRMED,BRL,1036.74,PIX,2025-05-24T14:23:00-03:00
     131: RSV-0130,Camila Farias,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2024-12-06,2024-12-12,2,NO_SHOW,BRL,2684.86,INVOICE,2024-11-21T19:13:00-03:00
     132: RSV-0131,Breno Carvalho,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-01-14,2025-01-20,1,CONFIRMED,BRL,1091.94,INVOICE,2025-01-05T18:09:00-03:00
     133: RSV-0132,Irene Bastos,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2024-12-16,2024-12-21,1,CONFIRMED,BRL,2612.56,CORPORATE_CARD,2024-11-18T19:26:00-03:00
     134: RSV-0133,Wagner Lopes,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-03-18,2025-03-23,1,CONFIRMED,EUR,117.03,CORPORATE_CARD,2025-03-10T18:42:00-03:00
     135: RSV-0134,Gabriela Nunes,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-01-21,2025-01-27,1,CONFIRMED,USD,582.17,INVOICE,2025-01-07T09:00:00-03:00
     136: RSV-0135,Márcio Tavares,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-06-19,2025-06-25,1,CONFIRMED,USD,274.54,PIX,2025-06-04T20:43:00-03:00
     137: RSV-0136,Thiago Araújo,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-03-16,2025-03-17,1,CONFIRMED,EUR,119.91,INVOICE,2025-02-20T10:22:00-03:00
     138: RSV-0137,Carla Dias,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-02-12,2025-02-16,1,CONFIRMED,BRL,2057.07,PIX,2025-02-01T09:19:00-03:00
     139: RSV-0138,Lucas Barbosa,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2024-12-21,2024-12-22,1,NO_SHOW,BRL,2628.31,PIX,2024-11-27T11:33:00-03:00
     140: RSV-0139,Zélia Correia,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2024-12-15,2024-12-17,2,CONFIRMED,BRL,801.91,CORPORATE_CARD,2024-11-24T18:27:00-03:00
     141: RSV-0140,Eduarda Alves,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-02-14,2025-02-18,1,CANCELLED,BRL,854.17,PIX,2025-01-20T19:51:00-03:00
     142: RSV-0141,Ursula Gomes,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2024-12-06,2024-12-09,1,NO_SHOW,BRL,629.19,PIX,2024-11-14T15:33:00-03:00
     143: RSV-0142,Thiago Araújo,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-04-12,2025-04-15,2,CONFIRMED,BRL,772.69,PIX,2025-03-21T19:51:00-03:00
     144: RSV-0143,Amanda Pinto,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-06-28,2025-07-01,1,CONFIRMED,BRL,1264.60,PIX,2025-06-23T16:24:00-03:00
     145: RSV-0144,Karina Melo,EMP-001,H12,Hotel Miami Beach,Miami,US,2024-12-06,2024-12-10,1,CONFIRMED,BRL,2601.94,INVOICE,2024-11-06T10:35:00-03:00
     146: RSV-0145,Yuri Fernandes,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-02-15,2025-02-20,1,CONFIRMED,USD,574.96,PIX,2025-01-30T10:12:00-03:00
     147: RSV-0146,Olívia Prado,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-04-16,2025-04-20,2,CONFIRMED,USD,334.12,INVOICE,2025-04-13T17:01:00-03:00
     148: RSV-0147,Giovana Pires,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2024-12-30,2025-01-02,2,NO_SHOW,BRL,2169.17,CORPORATE_CARD,2024-12-05T15:35:00-03:00
     149: RSV-0148,Breno Carvalho,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-03-12,2025-03-17,2,CONFIRMED,BRL,2212.01,CORPORATE_CARD,2025-02-25T16:13:00-03:00
     150: RSV-0149,Henrique Costa,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-06-10,2025-06-17,3,CONFIRMED,EUR,183.01,CORPORATE_CARD,2025-05-13T09:28:00-03:00
     151: RSV-0150,Nicolas Freitas,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-06-12,2025-06-19,2,CONFIRMED,EUR,254.11,CORPORATE_CARD,2025-05-23T10:50:00-03:00
     152: RSV-0151,Rafael Cardoso,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-05-09,2025-05-14,1,CONFIRMED,EUR,490.97,PIX,2025-04-29T12:36:00-03:00
     153: RSV-0152,Isabela Ramos,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-06-05,2025-06-12,2,CONFIRMED,BRL,2781.59,CORPORATE_CARD,2025-05-08T18:08:00-03:00
     154: RSV-0153,Amanda Pinto,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2024-12-08,2024-12-15,2,CONFIRMED,BRL,1549.17,INVOICE,2024-11-19T18:17:00-03:00
     155: RSV-0154,Fábio Bezerra,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-06-03,2025-06-07,1,CONFIRMED,USD,441.25,INVOICE,2025-05-05T13:29:00-03:00
     156: RSV-0155,Rafael Cardoso,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-06-29,2025-07-03,2,NO_SHOW,BRL,1324.40,INVOICE,2025-06-15T11:31:00-03:00
     157: RSV-0156,Gabriela Nunes,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-03-05,2025-03-10,2,CANCELLED,BRL,2540.68,PIX,2025-02-08T08:02:00-03:00
     158: RSV-0157,Thiago Araújo,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-04-28,2025-05-03,1,CONFIRMED,BRL,845.68,CORPORATE_CARD,2025-04-05T10:56:00-03:00
     159: RSV-0158,Thiago Araújo,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-03-30,2025-04-03,1,NO_SHOW,BRL,2564.31,PIX,2025-03-24T08:25:00-03:00
     160: RSV-0159,Hugo Siqueira,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-02-03,2025-02-09,1,CONFIRMED,EUR,275.03,PIX,2025-01-29T17:14:00-03:00
     161: RSV-0160,Gabriela Nunes,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-01-04,2025-01-11,1,CONFIRMED,USD,328.40,CORPORATE_CARD,2024-12-27T14:05:00-03:00
     162: RSV-0161,Wagner Lopes,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-03-29,2025-04-01,1,CONFIRMED,BRL,370.76,PIX,2025-03-08T10:28:00-03:00
     163: RSV-0162,Henrique Costa,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-06-29,2025-07-05,1,CONFIRMED,BRL,562.39,PIX,2025-06-25T10:48:00-03:00
     164: RSV-0163,Natália Campos,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-03-11,2025-03-18,1,CONFIRMED,EUR,347.19,PIX,2025-03-03T16:38:00-03:00
     165: RSV-0164,Daniel Rocha,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-06-30,2025-07-04,1,CONFIRMED,BRL,1598.33,CORPORATE_CARD,2025-06-06T14:18:00-03:00
     166: RSV-0165,Yuri Fernandes,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-01-31,2025-02-06,1,CONFIRMED,BRL,2767.86,PIX,2025-01-01T13:08:00-03:00
     167: RSV-0166,Daniel Rocha,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-05-16,2025-05-23,1,NO_SHOW,USD,115.12,INVOICE,2025-05-07T11:02:00-03:00
     168: RSV-0167,Rafael Cardoso,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-06-14,2025-06-18,2,CONFIRMED,USD,413.08,CORPORATE_CARD,2025-05-27T17:09:00-03:00
     169: RSV-0168,Eduarda Alves,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-05-05,2025-05-10,1,CONFIRMED,BRL,1904.02,INVOICE,2025-04-08T18:43:00-03:00
     170: RSV-0169,Thiago Araújo,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-06-08,2025-06-09,1,CONFIRMED,BRL,634.17,PIX,2025-05-19T17:03:00-03:00
     171: RSV-0170,Queila Moraes,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-06-28,2025-07-01,2,CONFIRMED,BRL,1566.21,CORPORATE_CARD,2025-06-16T16:33:00-03:00
     172: RSV-0171,Eduarda Alves,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-06-09,2025-06-15,2,CONFIRMED,USD,254.21,INVOICE,2025-05-26T12:33:00-03:00
     173: RSV-0172,Karina Melo,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-05-16,2025-05-20,1,CONFIRMED,BRL,1574.04,INVOICE,2025-04-27T10:23:00-03:00
     174: RSV-0173,Carla Dias,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-05-04,2025-05-06,2,CONFIRMED,BRL,457.89,INVOICE,2025-04-06T08:15:00-03:00
     175: RSV-0174,Paulo Teixeira,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-02-26,2025-03-04,2,CONFIRMED,BRL,2164.63,INVOICE,2025-02-12T11:20:00-03:00
     176: RSV-0175,Hugo Siqueira,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-03-29,2025-04-04,1,CONFIRMED,BRL,1999.65,CORPORATE_CARD,2025-03-27T10:14:00-03:00
     177: RSV-0176,Mariana Castro,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-01-10,2025-01-17,2,CONFIRMED,EUR,107.15,INVOICE,2024-12-26T08:23:00-03:00
     178: RSV-0177,Irene Bastos,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-03-08,2025-03-12,1,CONFIRMED,USD,598.85,CORPORATE_CARD,2025-02-11T11:46:00-03:00
     179: RSV-0178,Ana Souza,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2024-12-01,2024-12-03,1,CANCELLED,EUR,431.02,PIX,2024-11-02T08:21:00-03:00
     180: RSV-0179,Rafael Cardoso,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-06-04,2025-06-06,1,CONFIRMED,BRL,1378.55,CORPORATE_CARD,2025-06-02T10:45:00-03:00
     181: RSV-0180,Gabriela Nunes,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2024-12-31,2025-01-05,2,CONFIRMED,EUR,267.14,PIX,2024-12-07T09:37:00-03:00
     182: RSV-0181,Queila Moraes,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2024-12-03,2024-12-08,1,CONFIRMED,USD,424.47,INVOICE,2024-11-28T11:18:00-03:00
     183: RSV-0182,Márcio Tavares,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-04-11,2025-04-14,1,CONFIRMED,BRL,532.98,CORPORATE_CARD,2025-04-04T10:49:00-03:00
     184: RSV-0183,Thiago Araújo,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2024-12-30,2025-01-03,1,CANCELLED,EUR,224.06,INVOICE,2024-12-05T11:28:00-03:00
     185: RSV-0184,Felipe Martins,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-01-31,2025-02-04,2,CONFIRMED,EUR,329.42,PIX,2025-01-24T13:09:00-03:00
     186: RSV-0185,Jonas Neves,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-03-02,2025-03-08,1,CONFIRMED,BRL,426.15,CORPORATE_CARD,2025-02-17T15:35:00-03:00
     187: RSV-0186,Felipe Martins,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2024-12-29,2024-12-31,1,CONFIRMED,BRL,670.25,PIX,2024-12-02T14:23:00-03:00
     188: RSV-0187,Henrique Costa,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-01-29,2025-02-01,3,CONFIRMED,BRL,2332.78,CORPORATE_CARD,2025-01-26T20:21:00-03:00
     189: RSV-0188,Lucas Barbosa,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-01-31,2025-02-05,2,CONFIRMED,BRL,1565.51,INVOICE,2025-01-18T18:27:00-03:00
     190: RSV-0189,Amanda Pinto,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-02-27,2025-03-02,1,CONFIRMED,USD,400.83,PIX,2025-02-06T12:31:00-03:00
     191: RSV-0190,Bruno Lima,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-01-29,2025-02-03,1,CONFIRMED,BRL,960.41,INVOICE,2025-01-03T16:50:00-03:00
     192: RSV-0191,Ursula Gomes,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-03-16,2025-03-19,3,CONFIRMED,BRL,1137.93,PIX,2025-03-07T10:01:00-03:00
     193: RSV-0192,Paulo Teixeira,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-03-30,2025-04-05,1,CONFIRMED,BRL,2799.03,INVOICE,2025-03-24T09:15:00-03:00
     194: RSV-0193,Paulo Teixeira,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-06-28,2025-07-04,2,CONFIRMED,BRL,1219.27,PIX,2025-06-01T10:11:00-03:00
     195: RSV-0194,Mariana Castro,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-06-19,2025-06-20,2,CONFIRMED,BRL,2671.52,INVOICE,2025-05-31T10:36:00-03:00
     196: RSV-0195,Otávio Braga,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-02-03,2025-02-04,1,CONFIRMED,EUR,78.57,CORPORATE_CARD,2025-01-18T08:21:00-03:00
     197: RSV-0196,Hugo Siqueira,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-03-11,2025-03-12,1,CONFIRMED,BRL,2076.51,INVOICE,2025-03-06T20:07:00-03:00
     198: RSV-0197,Breno Carvalho,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-03-22,2025-03-26,1,CONFIRMED,BRL,1089.32,PIX,2025-03-17T10:46:00-03:00
     199: RSV-0198,Lucas Barbosa,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-06-18,2025-06-24,2,CONFIRMED,BRL,2278.13,INVOICE,2025-06-10T18:37:00-03:00
     200: RSV-0199,Lucas Barbosa,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-06-28,2025-06-30,3,CONFIRMED,EUR,238.39,PIX,2025-06-03T17:02:00-03:00
     201: RSV-0200,Ursula Gomes,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-05-31,2025-06-02,3,CONFIRMED,EUR,212.40,CORPORATE_CARD,2025-05-28T11:22:00-03:00
     202: RSV-0201,Eduarda Alves,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-01-22,2025-01-28,2,CONFIRMED,BRL,1444.24,INVOICE,2025-01-13T11:15:00-03:00
     203: RSV-0202,Yuri Fernandes,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-01-02,2025-01-06,1,CONFIRMED,USD,583.93,INVOICE,2024-12-04T14:31:00-03:00
     204: RSV-0203,Carla Dias,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-01-19,2025-01-25,2,NO_SHOW,EUR,139.94,INVOICE,2025-01-16T20:54:00-03:00
     205: RSV-0204,Felipe Martins,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2024-12-29,2024-12-31,1,CANCELLED,EUR,139.19,INVOICE,2024-12-26T16:57:00-03:00
     206: RSV-0205,Daniel Rocha,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-05-23,2025-05-24,1,NO_SHOW,BRL,754.24,CORPORATE_CARD,2025-04-24T14:10:00-03:00
     207: RSV-0206,Gabriela Nunes,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-02-18,2025-02-24,3,CONFIRMED,BRL,999.90,CORPORATE_CARD,2025-02-08T12:15:00-03:00
     208: RSV-0207,Natália Campos,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-05-05,2025-05-06,1,CONFIRMED,USD,125.57,INVOICE,2025-04-08T18:40:00-03:00
     209: RSV-0208,Elisa Queiroz,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2024-12-29,2025-01-02,3,CONFIRMED,BRL,2417.23,INVOICE,2024-12-19T20:25:00-03:00
     210: RSV-0209,Camila Farias,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-03-31,2025-04-05,1,CONFIRMED,BRL,1255.03,INVOICE,2025-03-16T08:16:00-03:00
     211: RSV-0210,Amanda Pinto,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-03-05,2025-03-12,1,CONFIRMED,USD,124.57,PIX,2025-02-21T20:34:00-03:00
     212: RSV-0211,Paulo Teixeira,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-01-17,2025-01-21,3,NO_SHOW,BRL,2473.89,INVOICE,2025-01-01T17:56:00-03:00
     213: RSV-0212,Henrique Costa,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-04-02,2025-04-07,1,CONFIRMED,USD,496.23,INVOICE,2025-03-11T17:09:00-03:00
     214: RSV-0213,João Pereira,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2024-12-07,2024-12-14,1,CONFIRMED,EUR,252.05,PIX,2024-11-15T14:12:00-03:00
     215: RSV-0214,Diego Monteiro,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-06-03,2025-06-04,1,CONFIRMED,BRL,1702.53,CORPORATE_CARD,2025-05-06T12:33:00-03:00
     216: RSV-0215,Gabriela Nunes,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-05-14,2025-05-15,1,CANCELLED,BRL,1738.16,PIX,2025-04-25T20:06:00-03:00
     217: RSV-0216,Lucas Barbosa,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-03-12,2025-03-16,1,CONFIRMED,BRL,1539.68,INVOICE,2025-02-20T15:02:00-03:00
     218: RSV-0217,Rafael Cardoso,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-05-23,2025-05-27,1,CONFIRMED,BRL,2041.76,INVOICE,2025-05-21T19:30:00-03:00
     219: RSV-0218,Olívia Prado,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2024-12-10,2024-12-13,1,CONFIRMED,BRL,2452.68,CORPORATE_CARD,2024-11-18T09:55:00-03:00
     220: RSV-0219,Amanda Pinto,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-06-11,2025-06-14,2,CONFIRMED,EUR,347.59,PIX,2025-06-04T15:13:00-03:00
     221: RSV-0220,Hugo Siqueira,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-05-02,2025-05-07,2,CONFIRMED,USD,241.78,PIX,2025-04-15T14:08:00-03:00
     222: RSV-0221,Rafael Cardoso,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2024-12-29,2024-12-31,1,CANCELLED,BRL,473.87,INVOICE,2024-12-17T19:12:00-03:00
     223: RSV-0222,Elisa Queiroz,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-05-04,2025-05-10,1,CONFIRMED,USD,334.17,PIX,2025-04-19T10:55:00-03:00
     224: RSV-0223,Nicolas Freitas,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-03-30,2025-04-01,1,CONFIRMED,USD,105.82,CORPORATE_CARD,2025-03-02T17:49:00-03:00
     225: RSV-0224,Lucas Barbosa,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-06-30,2025-07-05,1,NO_SHOW,BRL,371.80,PIX,2025-05-31T10:41:00-03:00
     226: RSV-0225,Diego Monteiro,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-02-27,2025-03-03,1,CONFIRMED,USD,522.82,INVOICE,2025-02-12T12:13:00-03:00
     227: RSV-0226,Natália Campos,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-05-04,2025-05-05,1,CONFIRMED,BRL,2717.89,PIX,2025-04-07T13:35:00-03:00
     228: RSV-0227,Thiago Araújo,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-06-28,2025-07-02,3,CONFIRMED,BRL,1146.59,CORPORATE_CARD,2025-06-19T12:41:00-03:00
     229: RSV-0228,Bruno Lima,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2024-12-02,2024-12-09,2,CANCELLED,BRL,1340.04,PIX,2024-11-21T18:08:00-03:00
     230: RSV-0229,Olívia Prado,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-03-30,2025-04-04,1,CONFIRMED,EUR,320.70,PIX,2025-03-11T11:21:00-03:00
     231: RSV-0230,Sofia Ribeiro,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-04-22,2025-04-25,1,NO_SHOW,BRL,2409.56,CORPORATE_CARD,2025-03-24T16:11:00-03:00
     232: RSV-0231,Thiago Araújo,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-06-30,2025-07-03,3,CONFIRMED,USD,420.31,INVOICE,2025-06-22T13:14:00-03:00
     233: RSV-0232,Márcio Tavares,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-03-19,2025-03-22,1,CONFIRMED,USD,324.68,PIX,2025-02-19T18:37:00-03:00
     234: RSV-0233,João Pereira,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2024-12-17,2024-12-18,2,CONFIRMED,BRL,1648.10,CORPORATE_CARD,2024-12-03T08:55:00-03:00
     235: RSV-0234,Lucas Barbosa,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-03-19,2025-03-23,1,CONFIRMED,EUR,147.55,INVOICE,2025-03-16T15:21:00-03:00
     236: RSV-0235,Felipe Martins,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-01-07,2025-01-14,2,CONFIRMED,USD,477.53,CORPORATE_CARD,2024-12-22T20:48:00-03:00
     237: RSV-0236,Ursula Gomes,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-06-14,2025-06-18,1,CONFIRMED,USD,357.57,PIX,2025-05-21T13:00:00-03:00
     238: RSV-0237,Yuri Fernandes,EMP-001,H12,Hotel Miami Beach,Miami,US,2024-12-21,2024-12-27,1,CONFIRMED,BRL,2498.61,PIX,2024-12-11T10:06:00-03:00
     239: RSV-0238,Breno Carvalho,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-02-26,2025-03-02,3,NO_SHOW,BRL,2133.19,PIX,2025-02-06T16:21:00-03:00
     240: RSV-0239,Bruno Lima,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-03-16,2025-03-19,2,CONFIRMED,BRL,2672.81,CORPORATE_CARD,2025-02-14T20:25:00-03:00
     241: RSV-0240,Yuri Fernandes,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-02-26,2025-03-04,1,CONFIRMED,USD,270.63,PIX,2025-02-05T20:02:00-03:00
     242: RSV-0241,Amanda Pinto,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-05-20,2025-05-21,1,CONFIRMED,BRL,2398.49,INVOICE,2025-05-18T19:07:00-03:00
     243: RSV-0242,Gabriela Nunes,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-05-31,2025-06-03,1,CONFIRMED,BRL,1894.26,PIX,2025-05-21T14:42:00-03:00
     244: RSV-0243,Henrique Costa,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-05-05,2025-05-09,2,CONFIRMED,BRL,1603.38,CORPORATE_CARD,2025-04-15T09:18:00-03:00
     245: RSV-0244,Jonas Neves,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-05-30,2025-06-05,3,NO_SHOW,BRL,2073.42,INVOICE,2025-05-20T10:02:00-03:00
     246: RSV-0245,Fábio Bezerra,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-06-11,2025-06-13,1,CONFIRMED,USD,126.28,CORPORATE_CARD,2025-06-07T17:42:00-03:00
     247: RSV-0246,Daniel Rocha,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-05-31,2025-06-02,3,CONFIRMED,BRL,916.34,CORPORATE_CARD,2025-05-21T12:29:00-03:00
     248: RSV-0247,Carla Dias,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-01-12,2025-01-19,1,CONFIRMED,BRL,2159.42,CORPORATE_CARD,2025-01-08T20:56:00-03:00
     249: RSV-0248,Vitor Sampaio,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-06-11,2025-06-14,2,CONFIRMED,EUR,185.37,CORPORATE_CARD,2025-05-18T09:23:00-03:00
     250: RSV-0249,Karina Melo,EMP-001,H12,Hotel Miami Beach,Miami,US,2024-12-15,2024-12-18,2,CONFIRMED,BRL,2434.15,CORPORATE_CARD,2024-11-19T14:41:00-03:00
     251: RSV-0250,Lucas Barbosa,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2024-12-06,2024-12-07,1,CONFIRMED,EUR,277.55,PIX,2024-11-17T18:28:00-03:00
     252: RSV-0251,Amanda Pinto,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-03-22,2025-03-29,2,CANCELLED,BRL,1533.55,INVOICE,2025-03-06T09:56:00-03:00
     253: RSV-0252,Lívia Moura,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2024-12-30,2025-01-01,2,CONFIRMED,BRL,1635.80,CORPORATE_CARD,2024-12-06T17:46:00-03:00
     254: RSV-0253,Elisa Queiroz,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-06-17,2025-06-22,1,CONFIRMED,BRL,583.34,INVOICE,2025-05-26T19:15:00-03:00
     255: RSV-0254,Fábio Bezerra,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-06-18,2025-06-23,1,CONFIRMED,EUR,471.78,CORPORATE_CARD,2025-06-01T15:54:00-03:00
     256: RSV-0255,Zélia Correia,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2024-12-08,2024-12-11,3,CONFIRMED,EUR,287.98,CORPORATE_CARD,2024-11-20T18:24:00-03:00
     257: RSV-0256,Bruno Lima,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2024-12-19,2024-12-23,1,CONFIRMED,EUR,262.24,CORPORATE_CARD,2024-12-15T15:47:00-03:00
     258: RSV-0257,Giovana Pires,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-01-01,2025-01-08,1,CONFIRMED,BRL,2709.77,PIX,2024-12-11T12:56:00-03:00
     259: RSV-0258,Otávio Braga,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-06-11,2025-06-14,2,CONFIRMED,EUR,433.06,PIX,2025-05-31T16:49:00-03:00
     260: RSV-0259,Sofia Ribeiro,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-06-15,2025-06-16,1,CONFIRMED,USD,195.31,PIX,2025-06-04T13:53:00-03:00
     261: RSV-0260,Otávio Braga,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-06-28,2025-07-03,1,CANCELLED,BRL,2169.15,CORPORATE_CARD,2025-06-14T09:16:00-03:00
     262: RSV-0261,Carla Dias,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2024-12-13,2024-12-15,1,CONFIRMED,EUR,378.22,PIX,2024-12-09T20:26:00-03:00
     263: RSV-0262,Daniel Rocha,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-05-30,2025-06-04,1,CONFIRMED,BRL,679.86,PIX,2025-05-14T08:33:00-03:00
     264: RSV-0263,Isabela Ramos,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-05-17,2025-05-24,3,CONFIRMED,BRL,2044.95,CORPORATE_CARD,2025-05-11T19:52:00-03:00
     265: RSV-0264,Paulo Teixeira,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-05-11,2025-05-16,2,CONFIRMED,EUR,491.19,INVOICE,2025-04-11T19:48:00-03:00
     266: RSV-0265,Thiago Araújo,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-03-15,2025-03-22,1,CONFIRMED,BRL,1826.18,PIX,2025-02-14T19:32:00-03:00
     267: RSV-0266,Isabela Ramos,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-03-18,2025-03-24,1,CANCELLED,USD,404.57,PIX,2025-03-08T18:22:00-03:00
     268: RSV-0267,Amanda Pinto,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-02-11,2025-02-17,1,CONFIRMED,USD,372.39,PIX,2025-01-23T17:42:00-03:00
     269: RSV-0268,Mariana Castro,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-05-30,2025-06-01,1,CONFIRMED,USD,278.05,INVOICE,2025-05-28T18:03:00-03:00
     270: RSV-0269,Carla Dias,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-02-09,2025-02-11,2,CONFIRMED,USD,487.87,INVOICE,2025-02-02T20:34:00-03:00
     271: RSV-0270,Giovana Pires,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-01-22,2025-01-28,1,NO_SHOW,USD,466.05,PIX,2025-01-04T14:15:00-03:00
     272: RSV-0271,Queila Moraes,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-06-29,2025-07-04,1,CONFIRMED,BRL,1116.00,CORPORATE_CARD,2025-06-11T08:00:00-03:00
     273: RSV-0272,Mariana Castro,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-04-21,2025-04-27,2,CONFIRMED,USD,472.66,PIX,2025-04-03T19:38:00-03:00
     274: RSV-0273,Breno Carvalho,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-03-22,2025-03-23,1,NO_SHOW,BRL,2150.94,INVOICE,2025-03-18T14:02:00-03:00
     275: RSV-0274,Ursula Gomes,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-02-27,2025-03-01,1,CONFIRMED,EUR,473.12,PIX,2025-02-25T10:59:00-03:00
     276: RSV-0275,Ursula Gomes,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2024-12-20,2024-12-27,1,CONFIRMED,BRL,2285.28,PIX,2024-12-02T13:04:00-03:00
     277: RSV-0276,Nicolas Freitas,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-02-17,2025-02-19,1,CONFIRMED,BRL,1338.37,PIX,2025-02-05T11:56:00-03:00
     278: RSV-0277,Wagner Lopes,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-03-31,2025-04-06,1,CONFIRMED,BRL,2368.04,INVOICE,2025-03-10T08:07:00-03:00
     279: RSV-0278,Yuri Fernandes,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-06-20,2025-06-22,3,CONFIRMED,EUR,450.83,INVOICE,2025-06-07T20:07:00-03:00
     280: RSV-0279,Mariana Castro,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-03-31,2025-04-04,1,CONFIRMED,BRL,1441.61,INVOICE,2025-03-29T12:57:00-03:00
     281: RSV-0280,Breno Carvalho,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-01-31,2025-02-06,1,CONFIRMED,BRL,866.41,CORPORATE_CARD,2025-01-10T20:13:00-03:00
     282: RSV-0281,Vitor Sampaio,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-06-14,2025-06-20,2,CANCELLED,BRL,2179.88,CORPORATE_CARD,2025-06-09T08:29:00-03:00
     283: RSV-0282,Zélia Correia,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2024-12-30,2025-01-05,1,CONFIRMED,BRL,2581.92,INVOICE,2024-12-16T14:28:00-03:00
     284: RSV-0283,Eduarda Alves,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-04-18,2025-04-19,1,CONFIRMED,BRL,504.93,INVOICE,2025-03-25T17:02:00-03:00
     285: RSV-0284,Bruno Lima,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-01-31,2025-02-04,1,CONFIRMED,USD,477.94,INVOICE,2025-01-16T14:25:00-03:00
     286: RSV-0285,Xênia Duarte,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2024-12-31,2025-01-05,2,CONFIRMED,BRL,1072.70,CORPORATE_CARD,2024-12-10T10:19:00-03:00
     287: RSV-0286,Wagner Lopes,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-05-29,2025-05-31,1,CONFIRMED,BRL,1666.02,CORPORATE_CARD,2025-05-26T12:13:00-03:00
     288: RSV-0287,Lívia Moura,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-06-05,2025-06-07,1,CONFIRMED,BRL,2395.13,CORPORATE_CARD,2025-05-29T09:11:00-03:00
     289: RSV-0288,Fábio Bezerra,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-05-18,2025-05-19,1,CONFIRMED,USD,210.36,INVOICE,2025-05-11T19:37:00-03:00
     290: RSV-0289,Thiago Araújo,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-06-04,2025-06-07,1,CONFIRMED,BRL,1128.58,PIX,2025-05-20T13:39:00-03:00
     291: RSV-0290,Breno Carvalho,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-05-11,2025-05-15,1,CONFIRMED,BRL,953.13,INVOICE,2025-05-03T19:47:00-03:00
     292: RSV-0291,Lucas Barbosa,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-02-11,2025-02-15,1,CONFIRMED,BRL,2248.18,PIX,2025-01-26T16:06:00-03:00
     293: RSV-0292,Bruno Lima,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-03-05,2025-03-10,1,CONFIRMED,BRL,2521.52,PIX,2025-03-02T19:04:00-03:00
     294: RSV-0293,João Pereira,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-05-19,2025-05-21,3,CONFIRMED,BRL,988.51,INVOICE,2025-04-20T16:30:00-03:00
     295: RSV-0294,Paulo Teixeira,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-05-10,2025-05-12,1,CONFIRMED,BRL,571.86,PIX,2025-04-28T16:00:00-03:00
     296: RSV-0295,Elisa Queiroz,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-05-29,2025-06-01,1,CANCELLED,EUR,353.55,INVOICE,2025-05-24T19:46:00-03:00
     297: RSV-0296,Xênia Duarte,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2024-12-08,2024-12-09,1,CONFIRMED,BRL,454.88,INVOICE,2024-12-01T16:58:00-03:00
     298: RSV-0297,Queila Moraes,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-04-02,2025-04-08,1,CONFIRMED,BRL,2722.68,PIX,2025-03-12T12:53:00-03:00
     299: RSV-0298,Zélia Correia,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-02-13,2025-02-16,1,CONFIRMED,USD,348.66,INVOICE,2025-01-31T11:33:00-03:00
     300: RSV-0299,Rafael Cardoso,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-03-16,2025-03-21,1,CONFIRMED,USD,308.75,CORPORATE_CARD,2025-03-08T09:32:00-03:00
     301: RSV-0300,Elisa Queiroz,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2024-12-31,2025-01-02,1,CONFIRMED,BRL,2337.37,INVOICE,2024-12-07T09:30:00-03:00
    
    FILE: data/taxas_cambio.csv
       1: currency,rate_to_brl
       2: BRL,1.000000
       3: USD,5.420000
       4: EUR,5.880000
    ✓ • 69ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        root = Path('/Users/joaovictordesousalima/Downloads/onfly-desafio')
        paths = sorted((root / 'tests').rglob('*')) + [root / n for n in ('.gitignore','pyproject.toml','requirements.txt','requirements-dev.txt','entrega/.gitkeep','output/.gitkeep')]
        for p in paths:
            if p.is_file():
                print(f'\nFILE: {p.relative_to(root)}')
                for n, line in enumerate(p.read_text().splitlines(), 1):
                    print(f'{n:4}: {line}')
        PY
    
    FILE: tests/helpers.py
       1: """Utilitários dos testes fornecidos."""
       2:
       3: from __future__ import annotations
       4:
       5: import csv
       6: import json
       7: import os
       8: import subprocess
       9: import sys
      10: from pathlib import Path
      11:
      12: PROJECT_ROOT = Path(__file__).resolve().parent.parent
      13: SRC_DIR = PROJECT_ROOT / "src"
      14:
      15: COLUMNS = [
      16:     "reservation_id",
      17:     "traveler_name",
      18:     "company_id",
      19:     "hotel_id",
      20:     "hotel_name",
      21:     "city",
      22:     "country",
      23:     "checkin_date",
      24:     "checkout_date",
      25:     "rooms",
      26:     "status",
      27:     "currency",
      28:     "amount",
      29:     "payment_method",
      30:     "booked_at",
      31: ]
      32:
      33: BASE = {
      34:     "reservation_id": "R-1",
      35:     "traveler_name": "Pessoa Teste",
      36:     "company_id": "EMP-001",
      37:     "hotel_id": "H01",
      38:     "hotel_name": "Hotel Teste",
      39:     "city": "Sao Paulo",
      40:     "country": "BR",
      41:     "checkin_date": "2025-01-10",
      42:     "checkout_date": "2025-01-11",
      43:     "rooms": "1",
      44:     "status": "CONFIRMED",
      45:     "currency": "BRL",
      46:     "amount": "100.00",
      47:     "payment_method": "CORPORATE_CARD",
      48:     "booked_at": "2025-01-01T10:00:00-03:00",
      49: }
      50:
      51:
      52: def run_cli(tmp_path: Path, rows: list[dict[str, str]], top: int = 5) -> dict:
      53:     """Executa o CLI sobre um CSV temporário e devolve o relatório."""
      54:     input_path = tmp_path / "reservas.csv"
      55:     rates_path = tmp_path / "rates.csv"
      56:     output_path = tmp_path / "report.json"
      57:
      58:     with input_path.open("w", encoding="utf-8", newline="") as handle:
      59:         writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
      60:         writer.writeheader()
      61:         writer.writerows({**BASE, **row} for row in rows)
      62:
      63:     rates_path.write_text(
      64:         "currency,rate_to_brl\nBRL,1.000000\nUSD,5.420000\nEUR,5.880000\n",
      65:         encoding="utf-8",
      66:     )
      67:
      68:     environment = os.environ.copy()
      69:     for import_root in (SRC_DIR, PROJECT_ROOT):
      70:         if (import_root / "onfly_report").is_dir():
      71:             environment["PYTHONPATH"] = str(import_root) + os.pathsep + environment.get("PYTHONPATH", "")
      72:             break
      73:     environment["PYTHONDONTWRITEBYTECODE"] = "1"
      74:
      75:     process = subprocess.run(
      76:         [
      77:             sys.executable,
      78:             "-m",
      79:             "onfly_report",
      80:             "--input",
      81:             str(input_path),
      82:             "--rates",
      83:             str(rates_path),
      84:             "--output",
      85:             str(output_path),
      86:             "--top",
      87:             str(top),
      88:         ],
      89:         cwd=str(PROJECT_ROOT),
      90:         env=environment,
      91:         capture_output=True,
      92:         text=True,
      93:         timeout=60,
      94:     )
      95:     assert process.returncode == 0, process.stderr
      96:     return json.loads(output_path.read_text(encoding="utf-8"))
    
    FILE: tests/test_currency.py
       1: """Testes fornecidos: câmbio para BRL."""
       2:
       3: from helpers import run_cli
       4:
       5:
       6: def test_currency_conversion_to_brl(tmp_path):
       7:     """Multiplica o valor pela taxa, sem inverter a operação."""
       8:     report = run_cli(
       9:         tmp_path,
      10:         [
      11:             {"reservation_id": "R-1", "currency": "BRL", "amount": "100.00"},
      12:             {"reservation_id": "R-2", "currency": "USD", "amount": "100.00"},
      13:         ],
      14:     )
      15:     assert report["summary"]["total_amount_brl"] == "642.00"
    
    FILE: tests/test_nights.py
       1: """Testes fornecidos: noites de quarto na virada de mês."""
       2:
       3: from helpers import run_cli
       4:
       5:
       6: def test_nights_across_month_boundary(tmp_path):
       7:     """A diferença de datas considera a virada de mês, não o dia do mês."""
       8:     report = run_cli(
       9:         tmp_path,
      10:         [
      11:             {
      12:                 "reservation_id": "R-1",
      13:                 "checkin_date": "2025-01-30",
      14:                 "checkout_date": "2025-02-02",
      15:                 "rooms": "1",
      16:             }
      17:         ],
      18:     )
      19:     assert report["summary"]["total_room_nights"] == 3
    
    FILE: tests/test_regression_report.py
       1: """Testes fornecidos: regressão ponta a ponta."""
       2:
       3: from helpers import run_cli
       4:
       5:
       6: def test_regression_report_on_sample(tmp_path):
       7:     """Relatório completo de uma amostra pequena, com status, noites e câmbio."""
       8:     report = run_cli(
       9:         tmp_path,
      10:         [
      11:             {
      12:                 "reservation_id": "R-1",
      13:                 "amount": "1000.00",
      14:                 "checkin_date": "2025-01-10",
      15:                 "checkout_date": "2025-01-13",
      16:             },
      17:             {"reservation_id": "R-2", "status": "CANCELLED", "amount": "500.00"},
      18:             {
      19:                 "reservation_id": "R-3",
      20:                 "currency": "USD",
      21:                 "amount": "100.00",
      22:                 "checkin_date": "2025-01-20",
      23:                 "checkout_date": "2025-01-22",
      24:             },
      25:         ],
      26:     )
      27:     assert report["summary"] == {
      28:         "total_reservations": 3,
      29:         "confirmed_reservations": 2,
      30:         "cancelled_reservations": 1,
      31:         "no_show_reservations": 0,
      32:         "total_room_nights": 5,
      33:         "total_amount_brl": "1542.00",
      34:         "average_nightly_rate_brl": "308.40",
      35:     }
    
    FILE: tests/test_status_rules.py
       1: """Testes fornecidos: regras de status."""
       2:
       3: from helpers import run_cli
       4:
       5:
       6: def test_status_rules_exclude_cancelled_and_no_show(tmp_path):
       7:     """Somente CONFIRMED entra nos totais financeiros."""
       8:     report = run_cli(
       9:         tmp_path,
      10:         [
      11:             {"reservation_id": "R-1", "status": "CONFIRMED", "amount": "100.00"},
      12:             {"reservation_id": "R-2", "status": "CANCELLED", "amount": "50.00"},
      13:             {"reservation_id": "R-3", "status": "NO_SHOW", "amount": "20.00"},
      14:         ],
      15:     )
      16:     assert report["summary"]["total_reservations"] == 3
      17:     assert report["summary"]["confirmed_reservations"] == 1
      18:     assert report["summary"]["cancelled_reservations"] == 1
      19:     assert report["summary"]["no_show_reservations"] == 1
      20:     assert report["summary"]["total_amount_brl"] == "100.00"
      21:     assert report["summary"]["total_room_nights"] == 1
    
    FILE: tests/test_top_hotels.py
       1: """Testes fornecidos: ranking de hotéis."""
       2:
       3: from helpers import run_cli
       4:
       5:
       6: def test_top_hotels_are_ranked_descending(tmp_path):
       7:     """O ranking mostra os hotéis de maior valor primeiro."""
       8:     report = run_cli(
       9:         tmp_path,
      10:         [
      11:             {"reservation_id": "R-1", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "1000.00"},
      12:             {"reservation_id": "R-2", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "900.00"},
      13:             {"reservation_id": "R-3", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "800.00"},
      14:             {"reservation_id": "R-4", "hotel_id": "H04", "hotel_name": "Hotel D", "amount": "700.00"},
      15:         ],
      16:         top=3,
      17:     )
      18:     assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]
      19:     assert [hotel["total_brl"] for hotel in report["top_hotels"]] == ["1000.00", "900.00", "800.00"]
    
    FILE: .gitignore
       1: __pycache__/
       2: *.py[cod]
       3: .venv/
       4: venv/
       5: .pytest_cache/
       6: .ruff_cache/
       7: .mypy_cache/
       8: .coverage
       9: coverage.xml
      10: htmlcov/
      11: output/*
      12: !output/.gitkeep
      13: dist/
      14: build/
      15: *.egg-info/
      16: .env
      17: .env.*
      18: .DS_Store
    
    FILE: pyproject.toml
       1: [project]
       2: name = "onfly-report"
       3: version = "1.0.0"
       4: description = "Consolidador de reservas de hotel da Onfly"
       5: requires-python = ">=3.11"
       6:
       7: [tool.ruff]
       8: line-length = 120
       9: target-version = "py311"
      10: src = ["src"]
      11:
      12: [tool.ruff.lint]
      13: select = ["E", "F", "I"]
      14:
      15: [tool.pytest.ini_options]
      16: testpaths = ["tests"]
      17: pythonpath = ["src"]
      18: addopts = "-ra"
    
    FILE: requirements.txt
       1: # O CLI usa apenas a biblioteca padrão do Python 3.11.
       2: # Não há dependências de runtime para instalar.
    
    FILE: requirements-dev.txt
       1: pytest==8.3.4
       2: ruff==0.8.4
    
    FILE: entrega/.gitkeep
    
    FILE: output/.gitkeep
    ✓ • 75ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        root = Path('/Users/joaovictordesousalima/Downloads/onfly-desafio')
        for p in sorted((root / 'src').rglob('*')):
            if p.is_file():
                print(f'\nFILE: {p.relative_to(root)}')
                for n, line in enumerate(p.read_text().splitlines(), 1):
                    print(f'{n:4}: {line}')
        PY
    
    FILE: src/onfly_report/__init__.py
       1: """CLI de consolidação de reservas de hotel da Onfly."""
       2:
       3: __version__ = "1.0.0"
    
    FILE: src/onfly_report/__main__.py
       1: from .cli import main
       2:
       3: raise SystemExit(main())
    
    FILE: src/onfly_report/cli.py
       1: """Interface de linha de comando do consolidador."""
       2:
       3: from __future__ import annotations
       4:
       5: import argparse
       6: import json
       7: import logging
       8: from pathlib import Path
       9:
      10: from .exceptions import InputFileError
      11: from .logging_config import configure_logging
      12: from .repositories.csv_rate_repository import CsvRateRepository
      13: from .repositories.csv_reservation_repository import CsvReservationRepository
      14: from .services.report_builder import ReportBuilder
      15:
      16: logger = logging.getLogger("onfly_report")
      17:
      18:
      19: def build_parser() -> argparse.ArgumentParser:
      20:     parser = argparse.ArgumentParser(
      21:         prog="onfly_report",
      22:         description="Consolida a exportação de reservas de hotel em um relatório JSON.",
      23:     )
      24:     parser.add_argument("--input", required=True, help="CSV de reservas")
      25:     parser.add_argument("--rates", required=True, help="CSV de taxas de câmbio para BRL")
      26:     parser.add_argument("--output", default="output/report.json", help="caminho do relatório JSON")
      27:     parser.add_argument("--top", type=int, default=5, help="quantidade de hotéis no ranking")
      28:     return parser
      29:
      30:
      31: def main(argv: list[str] | None = None) -> int:
      32:     configure_logging()
      33:     parser = build_parser()
      34:     args = parser.parse_args(argv)
      35:
      36:     if args.top < 1:
      37:         parser.error("--top deve ser maior ou igual a 1")
      38:
      39:     try:
      40:         report = ReportBuilder(
      41:             reservation_repository=CsvReservationRepository(Path(args.input)),
      42:             rate_repository=CsvRateRepository(Path(args.rates)),
      43:             top_n=args.top,
      44:         ).build()
      45:     except InputFileError as err:
      46:         logger.error("falha ao ler a entrada: %s", err)
      47:         return 2
      48:     except Exception:
      49:         logger.exception("erro inesperado ao gerar o relatório")
      50:         return 1
      51:
      52:     output_path = Path(args.output)
      53:     try:
      54:         output_path.parent.mkdir(parents=True, exist_ok=True)
      55:         output_path.write_text(
      56:             json.dumps(report, ensure_ascii=False, indent=2) + "\n",
      57:             encoding="utf-8",
      58:         )
      59:     except OSError:
      60:         logger.exception("falha ao escrever o relatório em %s", output_path)
      61:         return 1
      62:
      63:     summary = report["summary"]
      64:     print(
      65:         "Reservas: {total} | Confirmadas: {confirmed} | Noites: {nights} | Total BRL: {amount}".format(
      66:             total=summary["total_reservations"],
      67:             confirmed=summary["confirmed_reservations"],
      68:             nights=summary["total_room_nights"],
      69:             amount=summary["total_amount_brl"],
      70:         )
      71:     )
      72:     return 0
      73:
      74:
      75: if __name__ == "__main__":
      76:     raise SystemExit(main())
    
    FILE: src/onfly_report/exceptions.py
       1: """Exceções de domínio do consolidador de reservas."""
       2:
       3:
       4: class DomainError(Exception):
       5:     """Erro base do domínio."""
       6:
       7:
       8: class InputFileError(DomainError):
       9:     """Arquivo de entrada ausente, ilegível ou fora do formato esperado."""
    
    FILE: src/onfly_report/logging_config.py
       1: """Configuração de logging do CLI (sempre em stderr)."""
       2:
       3: from __future__ import annotations
       4:
       5: import logging
       6: import sys
       7:
       8:
       9: def configure_logging(level: str = "INFO") -> None:
      10:     """Configura o logger raiz para stderr, mantendo o stdout para o resumo."""
      11:     logging.basicConfig(
      12:         level=level,
      13:         stream=sys.stderr,
      14:         format="%(asctime)s %(levelname)s %(name)s %(message)s",
      15:     )
    
    FILE: src/onfly_report/models.py
       1: """Modelos de dados do consolidador."""
       2:
       3: from __future__ import annotations
       4:
       5: from dataclasses import dataclass
       6: from datetime import date
       7: from decimal import Decimal
       8:
       9:
      10: @dataclass(frozen=True)
      11: class RawRow:
      12:     """Linha crua lida do CSV, com o número da linha física no arquivo."""
      13:
      14:     line_number: int
      15:     values: dict[str, str]
      16:
      17:
      18: @dataclass(frozen=True)
      19: class Reservation:
      20:     """Reserva já convertida para os tipos do domínio."""
      21:
      22:     reservation_id: str
      23:     traveler_name: str
      24:     company_id: str
      25:     hotel_id: str
      26:     hotel_name: str
      27:     city: str
      28:     country: str
      29:     checkin: date
      30:     checkout: date
      31:     rooms: int
      32:     status: str
      33:     currency: str
      34:     amount: Decimal
      35:     payment_method: str
      36:     line_number: int
    
    FILE: src/onfly_report/repositories/__init__.py
    
    FILE: src/onfly_report/repositories/csv_rate_repository.py
       1: """Leitura da tabela de câmbio para BRL."""
       2:
       3: from __future__ import annotations
       4:
       5: import csv
       6: from decimal import Decimal, InvalidOperation
       7: from pathlib import Path
       8:
       9: from ..exceptions import InputFileError
      10:
      11: REQUIRED_COLUMNS = ("currency", "rate_to_brl")
      12:
      13:
      14: class CsvRateRepository:
      15:     """Carrega moeda -> taxa para BRL a partir de um CSV."""
      16:
      17:     def __init__(self, path: Path) -> None:
      18:         self._path = path
      19:
      20:     def read(self) -> dict[str, Decimal]:
      21:         rates: dict[str, Decimal] = {}
      22:         try:
      23:             with self._path.open("r", encoding="utf-8", newline="") as handle:
      24:                 reader = csv.DictReader(handle)
      25:                 missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
      26:                 if missing:
      27:                     raise InputFileError(f"colunas obrigatórias ausentes em {self._path}: {', '.join(missing)}")
      28:
      29:                 for values in reader:
      30:                     currency = (values.get("currency") or "").strip().upper()
      31:                     raw_rate = (values.get("rate_to_brl") or "").strip()
      32:                     if not currency or not raw_rate:
      33:                         raise InputFileError(f"linha de câmbio incompleta em {self._path}")
      34:                     try:
      35:                         rate = Decimal(raw_rate)
      36:                     except InvalidOperation as err:
      37:                         raise InputFileError(f"taxa inválida para {currency} em {self._path}") from err
      38:                     if rate <= 0:
      39:                         raise InputFileError(f"taxa não positiva para {currency} em {self._path}")
      40:                     rates[currency] = rate
      41:         except FileNotFoundError as err:
      42:             raise InputFileError(f"tabela de câmbio não encontrada: {self._path}") from err
      43:         except (OSError, csv.Error) as err:
      44:             raise InputFileError(f"falha ao ler {self._path}: {err}") from err
      45:
      46:         if not rates:
      47:             raise InputFileError(f"tabela de câmbio vazia: {self._path}")
      48:         return rates
    
    FILE: src/onfly_report/repositories/csv_reservation_repository.py
       1: """Leitura da exportação de reservas em CSV."""
       2:
       3: from __future__ import annotations
       4:
       5: import csv
       6: from pathlib import Path
       7:
       8: from ..exceptions import InputFileError
       9: from ..models import RawRow
      10:
      11: REQUIRED_COLUMNS = (
      12:     "reservation_id",
      13:     "traveler_name",
      14:     "company_id",
      15:     "hotel_id",
      16:     "hotel_name",
      17:     "city",
      18:     "country",
      19:     "checkin_date",
      20:     "checkout_date",
      21:     "rooms",
      22:     "status",
      23:     "currency",
      24:     "amount",
      25:     "payment_method",
      26:     "booked_at",
      27: )
      28:
      29:
      30: class CsvReservationRepository:
      31:     """Lê a exportação de reservas sem aplicar regra de negócio."""
      32:
      33:     def __init__(self, path: Path) -> None:
      34:         self._path = path
      35:
      36:     def read(self) -> list[RawRow]:
      37:         try:
      38:             with self._path.open("r", encoding="utf-8", newline="") as handle:
      39:                 reader = csv.DictReader(handle)
      40:                 missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
      41:                 if missing:
      42:                     raise InputFileError(f"colunas obrigatórias ausentes: {', '.join(missing)}")
      43:
      44:                 rows: list[RawRow] = []
      45:                 for values in reader:
      46:                     rows.append(RawRow(line_number=reader.line_num, values=values))
      47:                     if len(rows) == 200:
      48:                         break
      49:                 return rows
      50:         except FileNotFoundError as err:
      51:             raise InputFileError(f"arquivo de reservas não encontrado: {self._path}") from err
      52:         except (OSError, csv.Error) as err:
      53:             raise InputFileError(f"falha ao ler {self._path}: {err}") from err
    
    FILE: src/onfly_report/services/__init__.py
    
    FILE: src/onfly_report/services/currency_converter.py
       1: """Conversão de valores para BRL."""
       2:
       3: from __future__ import annotations
       4:
       5: from decimal import Decimal
       6:
       7:
       8: def convert_to_brl(amount: Decimal, currency: str, rates: dict[str, Decimal]) -> Decimal:
       9:     """Converte um valor na moeda informada para BRL usando a taxa da tabela."""
      10:     rate = rates[currency]
      11:     return Decimal(str(float(amount) / float(rate)))
    
    FILE: src/onfly_report/services/report_builder.py
       1: """Construção do relatório consolidado."""
       2:
       3: from __future__ import annotations
       4:
       5: from collections import defaultdict
       6: from datetime import datetime, timedelta, timezone
       7: from decimal import ROUND_HALF_UP, Decimal
       8:
       9: from ..repositories.csv_rate_repository import CsvRateRepository
      10: from ..repositories.csv_reservation_repository import CsvReservationRepository
      11: from .currency_converter import convert_to_brl
      12: from .row_parser import RowParser
      13: from .status_policy import is_billable
      14: from .stay_calculator import calculate_room_nights
      15:
      16: MONEY_QUANTUM = Decimal("0.01")
      17: FIXED_OFFSET = timezone(timedelta(hours=-3))
      18:
      19:
      20: def format_money(value: Decimal) -> str:
      21:     """Serializa dinheiro com duas casas, arredondamento half-up."""
      22:     return str(value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP))
      23:
      24:
      25: class ReportBuilder:
      26:     """Orquestra leitura, conversão e agregação."""
      27:
      28:     def __init__(
      29:         self,
      30:         reservation_repository: CsvReservationRepository,
      31:         rate_repository: CsvRateRepository,
      32:         top_n: int = 5,
      33:         now: datetime | None = None,
      34:     ) -> None:
      35:         self._reservation_repository = reservation_repository
      36:         self._rate_repository = rate_repository
      37:         self._top_n = top_n
      38:         self._now = now
      39:
      40:     def build(self) -> dict:
      41:         parser = RowParser()
      42:         reservations = [parser.parse(raw) for raw in self._reservation_repository.read()]
      43:         rates = self._rate_repository.read()
      44:
      45:         status_counts = {"CONFIRMED": 0, "CANCELLED": 0, "NO_SHOW": 0}
      46:         for reservation in reservations:
      47:             status_counts[reservation.status] = status_counts.get(reservation.status, 0) + 1
      48:
      49:         confirmed = [row for row in reservations if is_billable(row.status)]
      50:
      51:         monthly: dict[str, dict] = defaultdict(
      52:             lambda: {"reservations": 0, "room_nights": 0, "amount": Decimal("0")}
      53:         )
      54:         hotels: dict[str, dict] = defaultdict(
      55:             lambda: {"hotel_name": "", "room_nights": 0, "amount": Decimal("0")}
      56:         )
      57:
      58:         total_nights = 0
      59:         total_amount = Decimal("0")
      60:
      61:         for row in confirmed:
      62:             room_nights = calculate_room_nights(row.checkin, row.checkout, row.rooms)
      63:             amount_brl = convert_to_brl(row.amount, row.currency, rates)
      64:
      65:             total_nights += room_nights
      66:             total_amount += amount_brl
      67:
      68:             month_key = row.checkin.strftime("%Y-%m")
      69:             monthly[month_key]["reservations"] += 1
      70:             monthly[month_key]["room_nights"] += room_nights
      71:             monthly[month_key]["amount"] += amount_brl
      72:
      73:             hotels[row.hotel_id]["hotel_name"] = row.hotel_name
      74:             hotels[row.hotel_id]["room_nights"] += room_nights
      75:             hotels[row.hotel_id]["amount"] += amount_brl
      76:
      77:         average_nightly_rate = (
      78:             total_amount / Decimal(total_nights) if total_nights > 0 else Decimal("0")
      79:         )
      80:
      81:         by_month = [
      82:             {
      83:                 "month": month,
      84:                 "reservations": data["reservations"],
      85:                 "room_nights": data["room_nights"],
      86:                 "total_brl": format_money(data["amount"]),
      87:             }
      88:             for month, data in sorted(monthly.items())
      89:         ]
      90:
      91:         ranked_hotels = sorted(hotels.items(), key=lambda item: (item[1]["amount"], item[0]))
      92:         top_hotels = [
      93:             {
      94:                 "hotel_id": hotel_id,
      95:                 "hotel_name": data["hotel_name"],
      96:                 "room_nights": data["room_nights"],
      97:                 "total_brl": format_money(data["amount"]),
      98:             }
      99:             for hotel_id, data in ranked_hotels[: self._top_n]
     100:         ]
     101:
     102:         now = self._now or datetime.now(FIXED_OFFSET)
     103:
     104:         return {
     105:             "report_version": "1.0",
     106:             "generated_at": now.isoformat(timespec="seconds"),
     107:             "summary": {
     108:                 "total_reservations": len(reservations),
     109:                 "confirmed_reservations": status_counts.get("CONFIRMED", 0),
     110:                 "cancelled_reservations": status_counts.get("CANCELLED", 0),
     111:                 "no_show_reservations": status_counts.get("NO_SHOW", 0),
     112:                 "total_room_nights": total_nights,
     113:                 "total_amount_brl": format_money(total_amount),
     114:                 "average_nightly_rate_brl": format_money(average_nightly_rate),
     115:             },
     116:             "by_month": by_month,
     117:             "top_hotels": top_hotels,
     118:         }
    
    FILE: src/onfly_report/services/row_parser.py
       1: """Conversão de uma linha do CSV para o modelo de reserva."""
       2:
       3: from __future__ import annotations
       4:
       5: from datetime import date
       6: from decimal import Decimal, InvalidOperation
       7:
       8: from ..exceptions import InputFileError
       9: from ..models import RawRow, Reservation
      10:
      11:
      12: class RowParser:
      13:     """Converte a linha crua em Reservation.
      14:
      15:     O arquivo de entrada é consistente; falhas de formato são erro de arquivo, não dado a
      16:     ser descartado.
      17:     """
      18:
      19:     def parse(self, raw: RawRow) -> Reservation:
      20:         values = raw.values
      21:         try:
      22:             return Reservation(
      23:                 reservation_id=(values.get("reservation_id") or "").strip(),
      24:                 traveler_name=(values.get("traveler_name") or "").strip(),
      25:                 company_id=(values.get("company_id") or "").strip(),
      26:                 hotel_id=(values.get("hotel_id") or "").strip(),
      27:                 hotel_name=(values.get("hotel_name") or "").strip(),
      28:                 city=(values.get("city") or "").strip(),
      29:                 country=(values.get("country") or "").strip(),
      30:                 checkin=date.fromisoformat((values.get("checkin_date") or "").strip()),
      31:                 checkout=date.fromisoformat((values.get("checkout_date") or "").strip()),
      32:                 rooms=int((values.get("rooms") or "").strip()),
      33:                 status=(values.get("status") or "").strip(),
      34:                 currency=(values.get("currency") or "").strip(),
      35:                 amount=Decimal((values.get("amount") or "").strip()),
      36:                 payment_method=(values.get("payment_method") or "").strip(),
      37:                 line_number=raw.line_number,
      38:             )
      39:         except (ValueError, InvalidOperation) as err:
      40:             raise InputFileError(f"linha {raw.line_number} inválida: {err}") from err
    
    FILE: src/onfly_report/services/status_policy.py
       1: """Política de status das reservas."""
       2:
       3: from __future__ import annotations
       4:
       5:
       6: def is_billable(status: str) -> bool:
       7:     """Indica se a reserva entra nos totais financeiros e de noites."""
       8:     return status != "CANCELLED"
    
    FILE: src/onfly_report/services/stay_calculator.py
       1: """Cálculo de noites ocupadas."""
       2:
       3: from __future__ import annotations
       4:
       5: from datetime import date
       6:
       7:
       8: def calculate_room_nights(checkin: date, checkout: date, rooms: int) -> int:
       9:     """Calcula noites de quarto: diferença de dias (não inclusiva) vezes quartos."""
      10:     return (checkout.day - checkin.day) * rooms
    ✓ • 75ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        root = Path('/Users/joaovictordesousalima/Downloads/onfly-desafio')
        paths = sorted((root / 'tests').glob('*.py')) + [root / n for n in ('.gitignore','pyproject.toml','requirements.txt','requirements-dev.txt','data/exemplo-validacao.csv','data/taxas_cambio.csv')]
        for p in paths:
            print(f'\nFILE: {p.relative_to(root)}\n{p.read_text()}')
        PY
    
    FILE: tests/helpers.py
    """Utilitários dos testes fornecidos."""
    
    from __future__ import annotations
    
    import csv
    import json
    import os
    import subprocess
    import sys
    from pathlib import Path
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    SRC_DIR = PROJECT_ROOT / "src"
    
    COLUMNS = [
        "reservation_id",
        "traveler_name",
        "company_id",
        "hotel_id",
        "hotel_name",
        "city",
        "country",
        "checkin_date",
        "checkout_date",
        "rooms",
        "status",
        "currency",
        "amount",
        "payment_method",
        "booked_at",
    ]
    
    BASE = {
        "reservation_id": "R-1",
        "traveler_name": "Pessoa Teste",
        "company_id": "EMP-001",
        "hotel_id": "H01",
        "hotel_name": "Hotel Teste",
        "city": "Sao Paulo",
        "country": "BR",
        "checkin_date": "2025-01-10",
        "checkout_date": "2025-01-11",
        "rooms": "1",
        "status": "CONFIRMED",
        "currency": "BRL",
        "amount": "100.00",
        "payment_method": "CORPORATE_CARD",
        "booked_at": "2025-01-01T10:00:00-03:00",
    }
    
    
    def run_cli(tmp_path: Path, rows: list[dict[str, str]], top: int = 5) -> dict:
        """Executa o CLI sobre um CSV temporário e devolve o relatório."""
        input_path = tmp_path / "reservas.csv"
        rates_path = tmp_path / "rates.csv"
        output_path = tmp_path / "report.json"
    
        with input_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows({**BASE, **row} for row in rows)
    
        rates_path.write_text(
            "currency,rate_to_brl\nBRL,1.000000\nUSD,5.420000\nEUR,5.880000\n",
            encoding="utf-8",
        )
    
        environment = os.environ.copy()
        for import_root in (SRC_DIR, PROJECT_ROOT):
            if (import_root / "onfly_report").is_dir():
                environment["PYTHONPATH"] = str(import_root) + os.pathsep + environment.get("PYTHONPATH", "")
                break
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
    
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "onfly_report",
                "--input",
                str(input_path),
                "--rates",
                str(rates_path),
                "--output",
                str(output_path),
                "--top",
                str(top),
            ],
            cwd=str(PROJECT_ROOT),
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert process.returncode == 0, process.stderr
        return json.loads(output_path.read_text(encoding="utf-8"))
    
    
    FILE: tests/test_currency.py
    """Testes fornecidos: câmbio para BRL."""
    
    from helpers import run_cli
    
    
    def test_currency_conversion_to_brl(tmp_path):
        """Multiplica o valor pela taxa, sem inverter a operação."""
        report = run_cli(
            tmp_path,
            [
                {"reservation_id": "R-1", "currency": "BRL", "amount": "100.00"},
                {"reservation_id": "R-2", "currency": "USD", "amount": "100.00"},
            ],
        )
        assert report["summary"]["total_amount_brl"] == "642.00"
    
    
    FILE: tests/test_nights.py
    """Testes fornecidos: noites de quarto na virada de mês."""
    
    from helpers import run_cli
    
    
    def test_nights_across_month_boundary(tmp_path):
        """A diferença de datas considera a virada de mês, não o dia do mês."""
        report = run_cli(
            tmp_path,
            [
                {
                    "reservation_id": "R-1",
                    "checkin_date": "2025-01-30",
                    "checkout_date": "2025-02-02",
                    "rooms": "1",
                }
            ],
        )
        assert report["summary"]["total_room_nights"] == 3
    
    
    FILE: tests/test_regression_report.py
    """Testes fornecidos: regressão ponta a ponta."""
    
    from helpers import run_cli
    
    
    def test_regression_report_on_sample(tmp_path):
        """Relatório completo de uma amostra pequena, com status, noites e câmbio."""
        report = run_cli(
            tmp_path,
            [
                {
                    "reservation_id": "R-1",
                    "amount": "1000.00",
                    "checkin_date": "2025-01-10",
                    "checkout_date": "2025-01-13",
                },
                {"reservation_id": "R-2", "status": "CANCELLED", "amount": "500.00"},
                {
                    "reservation_id": "R-3",
                    "currency": "USD",
                    "amount": "100.00",
                    "checkin_date": "2025-01-20",
                    "checkout_date": "2025-01-22",
                },
            ],
        )
        assert report["summary"] == {
            "total_reservations": 3,
            "confirmed_reservations": 2,
            "cancelled_reservations": 1,
            "no_show_reservations": 0,
            "total_room_nights": 5,
            "total_amount_brl": "1542.00",
            "average_nightly_rate_brl": "308.40",
        }
    
    
    FILE: tests/test_status_rules.py
    """Testes fornecidos: regras de status."""
    
    from helpers import run_cli
    
    
    def test_status_rules_exclude_cancelled_and_no_show(tmp_path):
        """Somente CONFIRMED entra nos totais financeiros."""
        report = run_cli(
            tmp_path,
            [
                {"reservation_id": "R-1", "status": "CONFIRMED", "amount": "100.00"},
                {"reservation_id": "R-2", "status": "CANCELLED", "amount": "50.00"},
                {"reservation_id": "R-3", "status": "NO_SHOW", "amount": "20.00"},
            ],
        )
        assert report["summary"]["total_reservations"] == 3
        assert report["summary"]["confirmed_reservations"] == 1
        assert report["summary"]["cancelled_reservations"] == 1
        assert report["summary"]["no_show_reservations"] == 1
        assert report["summary"]["total_amount_brl"] == "100.00"
        assert report["summary"]["total_room_nights"] == 1
    
    
    FILE: tests/test_top_hotels.py
    """Testes fornecidos: ranking de hotéis."""
    
    from helpers import run_cli
    
    
    def test_top_hotels_are_ranked_descending(tmp_path):
        """O ranking mostra os hotéis de maior valor primeiro."""
        report = run_cli(
            tmp_path,
            [
                {"reservation_id": "R-1", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "1000.00"},
                {"reservation_id": "R-2", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "900.00"},
                {"reservation_id": "R-3", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "800.00"},
                {"reservation_id": "R-4", "hotel_id": "H04", "hotel_name": "Hotel D", "amount": "700.00"},
            ],
            top=3,
        )
        assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]
        assert [hotel["total_brl"] for hotel in report["top_hotels"]] == ["1000.00", "900.00", "800.00"]
    
    
    FILE: .gitignore
    __pycache__/
    *.py[cod]
    .venv/
    venv/
    .pytest_cache/
    .ruff_cache/
    .mypy_cache/
    .coverage
    coverage.xml
    htmlcov/
    output/*
    !output/.gitkeep
    dist/
    build/
    *.egg-info/
    .env
    .env.*
    .DS_Store
    
    
    FILE: pyproject.toml
    [project]
    name = "onfly-report"
    version = "1.0.0"
    description = "Consolidador de reservas de hotel da Onfly"
    requires-python = ">=3.11"
    
    [tool.ruff]
    line-length = 120
    target-version = "py311"
    src = ["src"]
    
    [tool.ruff.lint]
    select = ["E", "F", "I"]
    
    [tool.pytest.ini_options]
    testpaths = ["tests"]
    pythonpath = ["src"]
    addopts = "-ra"
    
    
    FILE: requirements.txt
    # O CLI usa apenas a biblioteca padrão do Python 3.11.
    # Não há dependências de runtime para instalar.
    
    
    FILE: requirements-dev.txt
    pytest==8.3.4
    ruff==0.8.4
    
    
    FILE: data/exemplo-validacao.csv
    reservation_id,traveler_name,company_id,hotel_id,hotel_name,city,country,checkin_date,checkout_date,rooms,status,currency,amount,payment_method,booked_at
    EX-01,Pessoa Fictícia,EMP-001,H01,Hotel Aurora Paulista,São Paulo,BR,2025-01-10,2025-01-13,1,CONFIRMED,BRL,1200.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-02,Pessoa Fictícia,EMP-001,H02,Hotel Mirante,Rio de Janeiro,BR,2025-01-20,2025-01-22,1,CONFIRMED,USD,200.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-03,Pessoa Fictícia,EMP-001,H03,Hotel Serra Verde,Belo Horizonte,BR,2025-01-28,2025-02-02,2,CONFIRMED,BRL,800.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-04,Pessoa Fictícia,EMP-001,H04,Hotel Porto Azul,Curitiba,BR,2025-01-05,2025-01-07,1,CANCELLED,BRL,500.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-05,Pessoa Fictícia,EMP-001,H05,Hotel Recife Plaza,Recife,BR,2025-01-06,2025-01-07,1,NO_SHOW,BRL,300.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-06,Pessoa Fictícia,EMP-001,H06,Hotel Salvador Centro,Salvador,BR,2025-01-07,2025-01-09,1,CANCELLED,BRL,250.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-07,Pessoa Fictícia,EMP-001,H07,Hotel Brasília Tower,Brasília,BR,2025-01-08,2025-01-10,1,CONFIRMED,BRL,600.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-08,Pessoa Fictícia,EMP-001,H08,Hotel Iguazu Falls,Foz do Iguaçu,BR,2025-01-09,2025-01-10,1,CONFIRMED,BRL,400.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-09,Pessoa Fictícia,EMP-001,H09,"Hotel Lisboa, Centro",Lisboa,PT,2025-02-05,2025-02-08,1,CONFIRMED,EUR,150.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-10,Pessoa Fictícia,EMP-001,H10,"Hotel Madrid, Gran Vía",Madrid,ES,2025-01-12,2025-01-16,1,CONFIRMED,BRL,900.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-11,Pessoa Fictícia,EMP-001,H11,Hotel Buenos Aires,Buenos Aires,AR,2025-01-14,2025-01-16,1,CONFIRMED,BRL,700.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    EX-12,Pessoa Fictícia,EMP-001,H12,Hotel Miami Beach,Miami,US,2025-01-15,2025-01-16,1,CONFIRMED,BRL,1000.00,CORPORATE_CARD,2025-01-02T10:00:00-03:00
    
    
    FILE: data/taxas_cambio.csv
    currency,rate_to_brl
    BRL,1.000000
    USD,5.420000
    EUR,5.880000
    
    ✓ • 0ms

## Activity

    $ python3 - <<'PY'
        import csv
        from pathlib import Path
        p = Path('/Users/joaovictordesousalima/Downloads/onfly-desafio/data/reservas_hoteis.csv')
        with p.open(newline='') as f:
            rows = list(csv.DictReader(f))
        fields = ['reservation_id','hotel_id','checkin_date','checkout_date','rooms','status','currency','amount']
        print(','.join(fields))
        for r in rows:
            print(','.join(r[k] for k in fields))
        PY
    reservation_id,hotel_id,checkin_date,checkout_date,rooms,status,currency,amount
    RSV-0001,H02,2025-06-29,2025-07-03,1,CANCELLED,BRL,1457.41
    RSV-0002,H02,2025-01-30,2025-02-04,1,CONFIRMED,BRL,1551.16
    RSV-0003,H06,2025-01-31,2025-02-06,1,CONFIRMED,EUR,233.79
    RSV-0004,H09,2025-01-04,2025-01-11,1,NO_SHOW,BRL,2116.06
    RSV-0005,H11,2025-04-04,2025-04-07,1,NO_SHOW,BRL,974.48
    RSV-0006,H06,2024-12-30,2025-01-01,2,NO_SHOW,USD,502.12
    RSV-0007,H12,2025-01-22,2025-01-29,1,NO_SHOW,USD,106.75
    RSV-0008,H06,2025-02-27,2025-03-02,2,CONFIRMED,BRL,2421.16
    RSV-0009,H09,2025-04-20,2025-04-25,1,CONFIRMED,USD,93.65
    RSV-0010,H03,2024-12-10,2024-12-13,1,NO_SHOW,BRL,2481.16
    RSV-0011,H08,2025-01-31,2025-02-03,1,CONFIRMED,BRL,1185.20
    RSV-0012,H05,2025-01-31,2025-02-02,1,CANCELLED,BRL,1435.63
    RSV-0013,H11,2025-05-30,2025-06-01,1,NO_SHOW,USD,388.43
    RSV-0014,H03,2025-05-29,2025-06-02,3,CONFIRMED,BRL,2222.19
    RSV-0015,H11,2025-02-28,2025-03-03,1,NO_SHOW,BRL,2325.19
    RSV-0016,H07,2024-12-11,2024-12-16,1,NO_SHOW,BRL,2088.27
    RSV-0017,H06,2025-02-20,2025-02-24,2,CONFIRMED,BRL,565.92
    RSV-0018,H06,2025-01-10,2025-01-16,1,NO_SHOW,BRL,2258.84
    RSV-0019,H02,2025-03-21,2025-03-28,1,CONFIRMED,BRL,708.79
    RSV-0020,H10,2024-12-21,2024-12-25,1,CONFIRMED,BRL,2211.70
    RSV-0021,H02,2025-05-21,2025-05-24,1,CONFIRMED,BRL,1498.86
    RSV-0022,H01,2024-12-10,2024-12-14,1,CONFIRMED,BRL,1253.41
    RSV-0023,H01,2025-04-18,2025-04-25,2,CONFIRMED,EUR,263.39
    RSV-0024,H06,2025-05-29,2025-06-03,1,NO_SHOW,BRL,2756.84
    RSV-0025,H06,2025-04-17,2025-04-22,1,CONFIRMED,USD,273.88
    RSV-0026,H11,2025-06-03,2025-06-06,1,CANCELLED,USD,281.01
    RSV-0027,H12,2025-05-12,2025-05-15,3,CONFIRMED,USD,424.31
    RSV-0028,H12,2025-06-05,2025-06-11,2,CONFIRMED,USD,598.53
    RSV-0029,H08,2025-03-07,2025-03-10,3,CONFIRMED,EUR,152.56
    RSV-0030,H10,2025-05-17,2025-05-18,1,CANCELLED,EUR,126.35
    RSV-0031,H12,2025-02-02,2025-02-06,1,CONFIRMED,BRL,931.95
    RSV-0032,H11,2025-03-16,2025-03-23,1,CONFIRMED,EUR,477.27
    RSV-0033,H05,2025-04-07,2025-04-14,1,CONFIRMED,BRL,477.84
    RSV-0034,H09,2025-01-29,2025-02-02,1,CONFIRMED,BRL,711.00
    RSV-0035,H07,2025-01-13,2025-01-18,1,NO_SHOW,BRL,2786.59
    RSV-0036,H08,2025-06-05,2025-06-07,1,CANCELLED,BRL,2055.38
    RSV-0037,H12,2025-01-29,2025-02-01,1,CONFIRMED,EUR,331.82
    RSV-0038,H02,2025-01-31,2025-02-06,1,CONFIRMED,BRL,2399.88
    RSV-0039,H06,2025-02-10,2025-02-14,1,CONFIRMED,USD,205.09
    RSV-0040,H09,2025-01-18,2025-01-23,2,CONFIRMED,BRL,1707.67
    RSV-0041,H11,2025-01-03,2025-01-06,1,CONFIRMED,BRL,1889.23
    RSV-0042,H11,2024-12-21,2024-12-23,2,CANCELLED,BRL,1488.33
    RSV-0043,H01,2024-12-15,2024-12-16,1,CONFIRMED,BRL,2288.22
    RSV-0044,H05,2025-05-02,2025-05-09,1,CONFIRMED,USD,265.63
    RSV-0045,H07,2024-12-13,2024-12-19,1,CONFIRMED,BRL,1180.64
    RSV-0046,H10,2025-05-29,2025-06-03,1,CONFIRMED,BRL,2787.99
    RSV-0047,H07,2024-12-10,2024-12-14,1,NO_SHOW,USD,166.66
    RSV-0048,H01,2025-03-14,2025-03-17,1,NO_SHOW,USD,119.02
    RSV-0049,H02,2025-01-31,2025-02-05,1,CANCELLED,BRL,928.19
    RSV-0050,H02,2024-12-30,2025-01-03,1,CONFIRMED,USD,378.44
    RSV-0051,H09,2025-01-29,2025-02-03,1,CONFIRMED,BRL,638.51
    RSV-0052,H02,2025-03-16,2025-03-18,1,CANCELLED,USD,315.06
    RSV-0053,H05,2025-03-23,2025-03-24,1,CONFIRMED,BRL,2533.76
    RSV-0054,H01,2025-01-05,2025-01-07,2,CONFIRMED,USD,267.67
    RSV-0055,H07,2025-01-30,2025-02-04,1,CONFIRMED,EUR,424.04
    RSV-0056,H03,2025-05-18,2025-05-24,1,CONFIRMED,BRL,1409.91
    RSV-0057,H09,2024-12-30,2025-01-02,1,NO_SHOW,BRL,2542.57
    RSV-0058,H09,2025-03-30,2025-04-05,1,CONFIRMED,BRL,1920.42
    RSV-0059,H01,2025-05-19,2025-05-20,2,CONFIRMED,BRL,549.00
    RSV-0060,H11,2025-05-21,2025-05-22,1,CONFIRMED,EUR,304.60
    RSV-0061,H08,2025-04-28,2025-05-01,1,CONFIRMED,BRL,1487.88
    RSV-0062,H09,2025-03-05,2025-03-12,1,CONFIRMED,BRL,610.15
    RSV-0063,H03,2025-01-30,2025-02-05,1,CONFIRMED,USD,503.01
    RSV-0064,H08,2025-04-15,2025-04-19,2,CANCELLED,BRL,406.78
    RSV-0065,H11,2025-01-30,2025-02-05,2,NO_SHOW,BRL,1997.68
    RSV-0066,H07,2024-12-30,2025-01-04,1,CONFIRMED,USD,106.60
    RSV-0067,H10,2024-12-18,2024-12-21,2,CANCELLED,USD,433.81
    RSV-0068,H10,2025-03-12,2025-03-19,1,CONFIRMED,USD,344.74
    RSV-0069,H03,2025-04-05,2025-04-10,2,CONFIRMED,BRL,1153.52
    RSV-0070,H08,2025-03-17,2025-03-24,1,CONFIRMED,BRL,2086.41
    RSV-0071,H12,2025-01-19,2025-01-22,2,CONFIRMED,BRL,2486.64
    RSV-0072,H09,2025-05-02,2025-05-07,1,CANCELLED,BRL,1891.11
    RSV-0073,H08,2025-02-28,2025-03-02,1,CONFIRMED,USD,243.12
    RSV-0074,H04,2025-05-02,2025-05-08,1,CONFIRMED,BRL,1724.17
    RSV-0075,H12,2025-04-11,2025-04-16,1,CONFIRMED,BRL,2017.83
    RSV-0076,H05,2024-12-31,2025-01-04,1,CONFIRMED,BRL,2239.38
    RSV-0077,H11,2025-05-09,2025-05-12,1,CONFIRMED,BRL,1680.82
    RSV-0078,H11,2025-03-03,2025-03-06,3,CONFIRMED,BRL,978.29
    RSV-0079,H04,2025-06-28,2025-07-04,2,CANCELLED,BRL,944.02
    RSV-0080,H03,2024-12-16,2024-12-17,1,CONFIRMED,USD,82.69
    RSV-0081,H02,2025-03-21,2025-03-22,3,CONFIRMED,BRL,1948.13
    RSV-0082,H08,2025-02-02,2025-02-09,1,CONFIRMED,USD,176.88
    RSV-0083,H11,2025-05-30,2025-06-03,1,CONFIRMED,BRL,1681.09
    RSV-0084,H03,2025-01-15,2025-01-21,1,CONFIRMED,BRL,384.51
    RSV-0085,H06,2025-02-13,2025-02-20,1,CONFIRMED,BRL,562.51
    RSV-0086,H05,2025-02-27,2025-03-02,1,CONFIRMED,BRL,2687.39
    RSV-0087,H05,2025-03-02,2025-03-08,1,CANCELLED,EUR,138.68
    RSV-0088,H04,2024-12-10,2024-12-13,1,CONFIRMED,BRL,2695.53
    RSV-0089,H04,2025-05-18,2025-05-25,1,CONFIRMED,BRL,2216.56
    RSV-0090,H09,2025-06-19,2025-06-20,1,CANCELLED,BRL,2562.08
    RSV-0091,H08,2025-05-22,2025-05-24,2,CONFIRMED,BRL,572.81
    RSV-0092,H11,2024-12-19,2024-12-20,1,CONFIRMED,USD,499.60
    RSV-0093,H09,2025-05-30,2025-06-03,2,CANCELLED,BRL,2785.60
    RSV-0094,H07,2025-02-14,2025-02-17,3,CONFIRMED,USD,313.24
    RSV-0095,H09,2025-05-30,2025-06-01,1,CONFIRMED,USD,284.39
    RSV-0096,H04,2025-04-18,2025-04-22,1,CONFIRMED,USD,208.71
    RSV-0097,H01,2025-01-14,2025-01-19,2,CONFIRMED,EUR,173.49
    RSV-0098,H08,2025-06-08,2025-06-14,1,CONFIRMED,BRL,924.13
    RSV-0099,H10,2025-03-31,2025-04-06,1,CONFIRMED,BRL,2242.72
    RSV-0100,H10,2025-05-30,2025-06-03,1,CONFIRMED,BRL,2505.30
    RSV-0101,H06,2025-03-22,2025-03-26,2,CONFIRMED,BRL,2055.96
    RSV-0102,H03,2025-04-28,2025-05-02,2,CONFIRMED,USD,499.00
    RSV-0103,H02,2025-02-09,2025-02-11,1,CANCELLED,USD,559.56
    RSV-0104,H02,2025-01-31,2025-02-06,1,CONFIRMED,EUR,150.91
    RSV-0105,H12,2025-03-01,2025-03-03,3,NO_SHOW,BRL,637.42
    RSV-0106,H05,2025-02-08,2025-02-13,1,CONFIRMED,BRL,1282.62
    RSV-0107,H04,2025-04-16,2025-04-23,2,CONFIRMED,EUR,229.40
    RSV-0108,H05,2024-12-31,2025-01-06,2,CONFIRMED,BRL,723.41
    RSV-0109,H08,2025-06-11,2025-06-14,2,CONFIRMED,BRL,2717.95
    RSV-0110,H09,2025-03-31,2025-04-06,1,CONFIRMED,BRL,2776.29
    RSV-0111,H03,2024-12-29,2025-01-01,1,CONFIRMED,USD,84.75
    RSV-0112,H09,2025-05-22,2025-05-26,1,CONFIRMED,BRL,1701.53
    RSV-0113,H03,2025-01-23,2025-01-29,1,CONFIRMED,BRL,612.19
    RSV-0114,H06,2025-03-09,2025-03-16,1,CONFIRMED,BRL,2700.28
    RSV-0115,H07,2025-01-21,2025-01-28,1,CONFIRMED,BRL,1279.20
    RSV-0116,H10,2024-12-14,2024-12-20,2,NO_SHOW,EUR,490.25
    RSV-0117,H02,2025-06-16,2025-06-19,1,CONFIRMED,BRL,2026.85
    RSV-0118,H12,2025-03-29,2025-04-04,1,NO_SHOW,USD,506.87
    RSV-0119,H12,2025-04-18,2025-04-21,1,CANCELLED,USD,152.77
    RSV-0120,H10,2025-01-29,2025-01-31,1,CONFIRMED,BRL,2689.40
    RSV-0121,H07,2025-04-12,2025-04-17,3,CONFIRMED,BRL,805.06
    RSV-0122,H12,2025-02-03,2025-02-06,1,CONFIRMED,USD,487.62
    RSV-0123,H05,2024-12-30,2025-01-04,1,CANCELLED,BRL,600.47
    RSV-0124,H10,2025-04-28,2025-05-02,1,CONFIRMED,BRL,1815.21
    RSV-0125,H03,2025-01-18,2025-01-20,1,CONFIRMED,BRL,2029.02
    RSV-0126,H02,2025-01-30,2025-02-04,1,CONFIRMED,USD,267.78
    RSV-0127,H06,2025-04-29,2025-05-01,3,CONFIRMED,BRL,2411.95
    RSV-0128,H12,2025-06-05,2025-06-08,1,CONFIRMED,BRL,842.09
    RSV-0129,H07,2025-06-19,2025-06-26,1,CONFIRMED,BRL,1036.74
    RSV-0130,H01,2024-12-06,2024-12-12,2,NO_SHOW,BRL,2684.86
    RSV-0131,H11,2025-01-14,2025-01-20,1,CONFIRMED,BRL,1091.94
    RSV-0132,H09,2024-12-16,2024-12-21,1,CONFIRMED,BRL,2612.56
    RSV-0133,H02,2025-03-18,2025-03-23,1,CONFIRMED,EUR,117.03
    RSV-0134,H06,2025-01-21,2025-01-27,1,CONFIRMED,USD,582.17
    RSV-0135,H08,2025-06-19,2025-06-25,1,CONFIRMED,USD,274.54
    RSV-0136,H02,2025-03-16,2025-03-17,1,CONFIRMED,EUR,119.91
    RSV-0137,H12,2025-02-12,2025-02-16,1,CONFIRMED,BRL,2057.07
    RSV-0138,H03,2024-12-21,2024-12-22,1,NO_SHOW,BRL,2628.31
    RSV-0139,H11,2024-12-15,2024-12-17,2,CONFIRMED,BRL,801.91
    RSV-0140,H04,2025-02-14,2025-02-18,1,CANCELLED,BRL,854.17
    RSV-0141,H08,2024-12-06,2024-12-09,1,NO_SHOW,BRL,629.19
    RSV-0142,H10,2025-04-12,2025-04-15,2,CONFIRMED,BRL,772.69
    RSV-0143,H03,2025-06-28,2025-07-01,1,CONFIRMED,BRL,1264.60
    RSV-0144,H12,2024-12-06,2024-12-10,1,CONFIRMED,BRL,2601.94
    RSV-0145,H06,2025-02-15,2025-02-20,1,CONFIRMED,USD,574.96
    RSV-0146,H08,2025-04-16,2025-04-20,2,CONFIRMED,USD,334.12
    RSV-0147,H10,2024-12-30,2025-01-02,2,NO_SHOW,BRL,2169.17
    RSV-0148,H01,2025-03-12,2025-03-17,2,CONFIRMED,BRL,2212.01
    RSV-0149,H08,2025-06-10,2025-06-17,3,CONFIRMED,EUR,183.01
    RSV-0150,H11,2025-06-12,2025-06-19,2,CONFIRMED,EUR,254.11
    RSV-0151,H06,2025-05-09,2025-05-14,1,CONFIRMED,EUR,490.97
    RSV-0152,H01,2025-06-05,2025-06-12,2,CONFIRMED,BRL,2781.59
    RSV-0153,H07,2024-12-08,2024-12-15,2,CONFIRMED,BRL,1549.17
    RSV-0154,H05,2025-06-03,2025-06-07,1,CONFIRMED,USD,441.25
    RSV-0155,H09,2025-06-29,2025-07-03,2,NO_SHOW,BRL,1324.40
    RSV-0156,H06,2025-03-05,2025-03-10,2,CANCELLED,BRL,2540.68
    RSV-0157,H07,2025-04-28,2025-05-03,1,CONFIRMED,BRL,845.68
    RSV-0158,H11,2025-03-30,2025-04-03,1,NO_SHOW,BRL,2564.31
    RSV-0159,H04,2025-02-03,2025-02-09,1,CONFIRMED,EUR,275.03
    RSV-0160,H03,2025-01-04,2025-01-11,1,CONFIRMED,USD,328.40
    RSV-0161,H10,2025-03-29,2025-04-01,1,CONFIRMED,BRL,370.76
    RSV-0162,H04,2025-06-29,2025-07-05,1,CONFIRMED,BRL,562.39
    RSV-0163,H05,2025-03-11,2025-03-18,1,CONFIRMED,EUR,347.19
    RSV-0164,H10,2025-06-30,2025-07-04,1,CONFIRMED,BRL,1598.33
    RSV-0165,H01,2025-01-31,2025-02-06,1,CONFIRMED,BRL,2767.86
    RSV-0166,H10,2025-05-16,2025-05-23,1,NO_SHOW,USD,115.12
    RSV-0167,H02,2025-06-14,2025-06-18,2,CONFIRMED,USD,413.08
    RSV-0168,H10,2025-05-05,2025-05-10,1,CONFIRMED,BRL,1904.02
    RSV-0169,H07,2025-06-08,2025-06-09,1,CONFIRMED,BRL,634.17
    RSV-0170,H03,2025-06-28,2025-07-01,2,CONFIRMED,BRL,1566.21
    RSV-0171,H01,2025-06-09,2025-06-15,2,CONFIRMED,USD,254.21
    RSV-0172,H01,2025-05-16,2025-05-20,1,CONFIRMED,BRL,1574.04
    RSV-0173,H01,2025-05-04,2025-05-06,2,CONFIRMED,BRL,457.89
    RSV-0174,H12,2025-02-26,2025-03-04,2,CONFIRMED,BRL,2164.63
    RSV-0175,H09,2025-03-29,2025-04-04,1,CONFIRMED,BRL,1999.65
    RSV-0176,H06,2025-01-10,2025-01-17,2,CONFIRMED,EUR,107.15
    RSV-0177,H08,2025-03-08,2025-03-12,1,CONFIRMED,USD,598.85
    RSV-0178,H11,2024-12-01,2024-12-03,1,CANCELLED,EUR,431.02
    RSV-0179,H04,2025-06-04,2025-06-06,1,CONFIRMED,BRL,1378.55
    RSV-0180,H06,2024-12-31,2025-01-05,2,CONFIRMED,EUR,267.14
    RSV-0181,H07,2024-12-03,2024-12-08,1,CONFIRMED,USD,424.47
    RSV-0182,H04,2025-04-11,2025-04-14,1,CONFIRMED,BRL,532.98
    RSV-0183,H09,2024-12-30,2025-01-03,1,CANCELLED,EUR,224.06
    RSV-0184,H12,2025-01-31,2025-02-04,2,CONFIRMED,EUR,329.42
    RSV-0185,H03,2025-03-02,2025-03-08,1,CONFIRMED,BRL,426.15
    RSV-0186,H04,2024-12-29,2024-12-31,1,CONFIRMED,BRL,670.25
    RSV-0187,H08,2025-01-29,2025-02-01,3,CONFIRMED,BRL,2332.78
    RSV-0188,H07,2025-01-31,2025-02-05,2,CONFIRMED,BRL,1565.51
    RSV-0189,H10,2025-02-27,2025-03-02,1,CONFIRMED,USD,400.83
    RSV-0190,H09,2025-01-29,2025-02-03,1,CONFIRMED,BRL,960.41
    RSV-0191,H09,2025-03-16,2025-03-19,3,CONFIRMED,BRL,1137.93
    RSV-0192,H10,2025-03-30,2025-04-05,1,CONFIRMED,BRL,2799.03
    RSV-0193,H07,2025-06-28,2025-07-04,2,CONFIRMED,BRL,1219.27
    RSV-0194,H06,2025-06-19,2025-06-20,2,CONFIRMED,BRL,2671.52
    RSV-0195,H04,2025-02-03,2025-02-04,1,CONFIRMED,EUR,78.57
    RSV-0196,H10,2025-03-11,2025-03-12,1,CONFIRMED,BRL,2076.51
    RSV-0197,H06,2025-03-22,2025-03-26,1,CONFIRMED,BRL,1089.32
    RSV-0198,H10,2025-06-18,2025-06-24,2,CONFIRMED,BRL,2278.13
    RSV-0199,H10,2025-06-28,2025-06-30,3,CONFIRMED,EUR,238.39
    RSV-0200,H03,2025-05-31,2025-06-02,3,CONFIRMED,EUR,212.40
    RSV-0201,H06,2025-01-22,2025-01-28,2,CONFIRMED,BRL,1444.24
    RSV-0202,H07,2025-01-02,2025-01-06,1,CONFIRMED,USD,583.93
    RSV-0203,H04,2025-01-19,2025-01-25,2,NO_SHOW,EUR,139.94
    RSV-0204,H07,2024-12-29,2024-12-31,1,CANCELLED,EUR,139.19
    RSV-0205,H11,2025-05-23,2025-05-24,1,NO_SHOW,BRL,754.24
    RSV-0206,H09,2025-02-18,2025-02-24,3,CONFIRMED,BRL,999.90
    RSV-0207,H07,2025-05-05,2025-05-06,1,CONFIRMED,USD,125.57
    RSV-0208,H08,2024-12-29,2025-01-02,3,CONFIRMED,BRL,2417.23
    RSV-0209,H07,2025-03-31,2025-04-05,1,CONFIRMED,BRL,1255.03
    RSV-0210,H02,2025-03-05,2025-03-12,1,CONFIRMED,USD,124.57
    RSV-0211,H11,2025-01-17,2025-01-21,3,NO_SHOW,BRL,2473.89
    RSV-0212,H09,2025-04-02,2025-04-07,1,CONFIRMED,USD,496.23
    RSV-0213,H01,2024-12-07,2024-12-14,1,CONFIRMED,EUR,252.05
    RSV-0214,H07,2025-06-03,2025-06-04,1,CONFIRMED,BRL,1702.53
    RSV-0215,H03,2025-05-14,2025-05-15,1,CANCELLED,BRL,1738.16
    RSV-0216,H11,2025-03-12,2025-03-16,1,CONFIRMED,BRL,1539.68
    RSV-0217,H06,2025-05-23,2025-05-27,1,CONFIRMED,BRL,2041.76
    RSV-0218,H08,2024-12-10,2024-12-13,1,CONFIRMED,BRL,2452.68
    RSV-0219,H10,2025-06-11,2025-06-14,2,CONFIRMED,EUR,347.59
    RSV-0220,H02,2025-05-02,2025-05-07,2,CONFIRMED,USD,241.78
    RSV-0221,H08,2024-12-29,2024-12-31,1,CANCELLED,BRL,473.87
    RSV-0222,H06,2025-05-04,2025-05-10,1,CONFIRMED,USD,334.17
    RSV-0223,H07,2025-03-30,2025-04-01,1,CONFIRMED,USD,105.82
    RSV-0224,H11,2025-06-30,2025-07-05,1,NO_SHOW,BRL,371.80
    RSV-0225,H07,2025-02-27,2025-03-03,1,CONFIRMED,USD,522.82
    RSV-0226,H11,2025-05-04,2025-05-05,1,CONFIRMED,BRL,2717.89
    RSV-0227,H11,2025-06-28,2025-07-02,3,CONFIRMED,BRL,1146.59
    RSV-0228,H10,2024-12-02,2024-12-09,2,CANCELLED,BRL,1340.04
    RSV-0229,H01,2025-03-30,2025-04-04,1,CONFIRMED,EUR,320.70
    RSV-0230,H03,2025-04-22,2025-04-25,1,NO_SHOW,BRL,2409.56
    RSV-0231,H06,2025-06-30,2025-07-03,3,CONFIRMED,USD,420.31
    RSV-0232,H02,2025-03-19,2025-03-22,1,CONFIRMED,USD,324.68
    RSV-0233,H07,2024-12-17,2024-12-18,2,CONFIRMED,BRL,1648.10
    RSV-0234,H12,2025-03-19,2025-03-23,1,CONFIRMED,EUR,147.55
    RSV-0235,H10,2025-01-07,2025-01-14,2,CONFIRMED,USD,477.53
    RSV-0236,H01,2025-06-14,2025-06-18,1,CONFIRMED,USD,357.57
    RSV-0237,H12,2024-12-21,2024-12-27,1,CONFIRMED,BRL,2498.61
    RSV-0238,H08,2025-02-26,2025-03-02,3,NO_SHOW,BRL,2133.19
    RSV-0239,H03,2025-03-16,2025-03-19,2,CONFIRMED,BRL,2672.81
    RSV-0240,H02,2025-02-26,2025-03-04,1,CONFIRMED,USD,270.63
    RSV-0241,H11,2025-05-20,2025-05-21,1,CONFIRMED,BRL,2398.49
    RSV-0242,H11,2025-05-31,2025-06-03,1,CONFIRMED,BRL,1894.26
    RSV-0243,H02,2025-05-05,2025-05-09,2,CONFIRMED,BRL,1603.38
    RSV-0244,H06,2025-05-30,2025-06-05,3,NO_SHOW,BRL,2073.42
    RSV-0245,H11,2025-06-11,2025-06-13,1,CONFIRMED,USD,126.28
    RSV-0246,H11,2025-05-31,2025-06-02,3,CONFIRMED,BRL,916.34
    RSV-0247,H07,2025-01-12,2025-01-19,1,CONFIRMED,BRL,2159.42
    RSV-0248,H10,2025-06-11,2025-06-14,2,CONFIRMED,EUR,185.37
    RSV-0249,H12,2024-12-15,2024-12-18,2,CONFIRMED,BRL,2434.15
    RSV-0250,H10,2024-12-06,2024-12-07,1,CONFIRMED,EUR,277.55
    RSV-0251,H03,2025-03-22,2025-03-29,2,CANCELLED,BRL,1533.55
    RSV-0252,H11,2024-12-30,2025-01-01,2,CONFIRMED,BRL,1635.80
    RSV-0253,H10,2025-06-17,2025-06-22,1,CONFIRMED,BRL,583.34
    RSV-0254,H11,2025-06-18,2025-06-23,1,CONFIRMED,EUR,471.78
    RSV-0255,H01,2024-12-08,2024-12-11,3,CONFIRMED,EUR,287.98
    RSV-0256,H08,2024-12-19,2024-12-23,1,CONFIRMED,EUR,262.24
    RSV-0257,H10,2025-01-01,2025-01-08,1,CONFIRMED,BRL,2709.77
    RSV-0258,H04,2025-06-11,2025-06-14,2,CONFIRMED,EUR,433.06
    RSV-0259,H11,2025-06-15,2025-06-16,1,CONFIRMED,USD,195.31
    RSV-0260,H12,2025-06-28,2025-07-03,1,CANCELLED,BRL,2169.15
    RSV-0261,H04,2024-12-13,2024-12-15,1,CONFIRMED,EUR,378.22
    RSV-0262,H09,2025-05-30,2025-06-04,1,CONFIRMED,BRL,679.86
    RSV-0263,H03,2025-05-17,2025-05-24,3,CONFIRMED,BRL,2044.95
    RSV-0264,H07,2025-05-11,2025-05-16,2,CONFIRMED,EUR,491.19
    RSV-0265,H07,2025-03-15,2025-03-22,1,CONFIRMED,BRL,1826.18
    RSV-0266,H04,2025-03-18,2025-03-24,1,CANCELLED,USD,404.57
    RSV-0267,H06,2025-02-11,2025-02-17,1,CONFIRMED,USD,372.39
    RSV-0268,H01,2025-05-30,2025-06-01,1,CONFIRMED,USD,278.05
    RSV-0269,H12,2025-02-09,2025-02-11,2,CONFIRMED,USD,487.87
    RSV-0270,H04,2025-01-22,2025-01-28,1,NO_SHOW,USD,466.05
    RSV-0271,H11,2025-06-29,2025-07-04,1,CONFIRMED,BRL,1116.00
    RSV-0272,H06,2025-04-21,2025-04-27,2,CONFIRMED,USD,472.66
    RSV-0273,H03,2025-03-22,2025-03-23,1,NO_SHOW,BRL,2150.94
    RSV-0274,H12,2025-02-27,2025-03-01,1,CONFIRMED,EUR,473.12
    RSV-0275,H08,2024-12-20,2024-12-27,1,CONFIRMED,BRL,2285.28
    RSV-0276,H09,2025-02-17,2025-02-19,1,CONFIRMED,BRL,1338.37
    RSV-0277,H09,2025-03-31,2025-04-06,1,CONFIRMED,BRL,2368.04
    RSV-0278,H11,2025-06-20,2025-06-22,3,CONFIRMED,EUR,450.83
    RSV-0279,H09,2025-03-31,2025-04-04,1,CONFIRMED,BRL,1441.61
    RSV-0280,H02,2025-01-31,2025-02-06,1,CONFIRMED,BRL,866.41
    RSV-0281,H02,2025-06-14,2025-06-20,2,CANCELLED,BRL,2179.88
    RSV-0282,H04,2024-12-30,2025-01-05,1,CONFIRMED,BRL,2581.92
    RSV-0283,H10,2025-04-18,2025-04-19,1,CONFIRMED,BRL,504.93
    RSV-0284,H05,2025-01-31,2025-02-04,1,CONFIRMED,USD,477.94
    RSV-0285,H09,2024-12-31,2025-01-05,2,CONFIRMED,BRL,1072.70
    RSV-0286,H07,2025-05-29,2025-05-31,1,CONFIRMED,BRL,1666.02
    RSV-0287,H10,2025-06-05,2025-06-07,1,CONFIRMED,BRL,2395.13
    RSV-0288,H02,2025-05-18,2025-05-19,1,CONFIRMED,USD,210.36
    RSV-0289,H04,2025-06-04,2025-06-07,1,CONFIRMED,BRL,1128.58
    RSV-0290,H06,2025-05-11,2025-05-15,1,CONFIRMED,BRL,953.13
    RSV-0291,H06,2025-02-11,2025-02-15,1,CONFIRMED,BRL,2248.18
    RSV-0292,H12,2025-03-05,2025-03-10,1,CONFIRMED,BRL,2521.52
    RSV-0293,H09,2025-05-19,2025-05-21,3,CONFIRMED,BRL,988.51
    RSV-0294,H09,2025-05-10,2025-05-12,1,CONFIRMED,BRL,571.86
    RSV-0295,H10,2025-05-29,2025-06-01,1,CANCELLED,EUR,353.55
    RSV-0296,H04,2024-12-08,2024-12-09,1,CONFIRMED,BRL,454.88
    RSV-0297,H12,2025-04-02,2025-04-08,1,CONFIRMED,BRL,2722.68
    RSV-0298,H02,2025-02-13,2025-02-16,1,CONFIRMED,USD,348.66
    RSV-0299,H03,2025-03-16,2025-03-21,1,CONFIRMED,USD,308.75
    RSV-0300,H07,2024-12-31,2025-01-02,1,CONFIRMED,BRL,2337.37
    ✓ • 0ms

## Assistant

Confirmei o corte: o leitor de CSV interrompe o processamento ao chegar a 200 reservas, mas o arquivo contém 300. Também encontrei erros no câmbio, no cálculo de noites, no tratamento de `NO_SHOW` e na ordenação dos hotéis. Vou executar os testes e comparar o relatório atual com um cálculo independente baseado nas regras do README.

## Activity

    $ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
    /Library/Frameworks/Python.framework/Versions/3.13/bin/python3: No module named pytest
    ✗ (1) • 0ms

## Activity

    $ PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 - <<'PY'
        import csv
        import json
        from collections import Counter, defaultdict
        from datetime import date
        from decimal import Decimal, ROUND_HALF_UP
        from pathlib import Path
        from onfly_report.repositories.csv_reservation_repository import CsvReservationRepository
        from onfly_report.repositories.csv_rate_repository import CsvRateRepository
        from onfly_report.services.report_builder import ReportBuilder
        
        def money(x):
            return str(x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        rates = {r['currency']: Decimal(r['rate_to_brl']) for r in csv.DictReader(Path('data/taxas_cambio.csv').open())}
        for name in ('exemplo-validacao.csv', 'reservas_hoteis.csv'):
            path = Path('data') / name
            with path.open(newline='') as f:
                rows = list(csv.DictReader(f))
            confirmed = [r for r in rows if r['status'] == 'CONFIRMED']
            nights = sum((date.fromisoformat(r['checkout_date']) - date.fromisoformat(r['checkin_date'])).days * int(r['rooms']) for r in confirmed)
            total = sum((Decimal(r['amount']) * rates[r['currency']] for r in confirmed), Decimal(0))
            current = ReportBuilder(CsvReservationRepository(path), CsvRateRepository(Path('data/taxas_cambio.csv'))).build()
            hotels = defaultdict(lambda: Decimal(0))
            for r in confirmed:
                hotels[r['hotel_id']] += Decimal(r['amount']) * rates[r['currency']]
            print(json.dumps({'file': name, 'actual_summary': current['summary'], 'expected_from_rules': {'total_reservations':len(rows), 'status_counts': dict(Counter(r['status'] for r in rows)), 'total_room_nights': nights, 'total_amount_brl':money(total), 'average_nightly_rate_brl':money(total / nights) if nights else '0.00', 'top_hotels': [(h, money(v)) for h, v in sorted(hotels.items(),key=lambda x:(-x[1],x[0]))[:5]]}, 'rows_omitted':len(rows)-len(CsvReservationRepository(path).read())}, ensure_ascii=False, indent=2))
        PY
    {
      "file": "exemplo-validacao.csv",
      "actual_summary": {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": -33,
        "total_amount_brl": "5962.41",
        "average_nightly_rate_brl": "0.00"
      },
      "expected_from_rules": {
        "total_reservations": 12,
        "status_counts": {
          "CONFIRMED": 9,
          "CANCELLED": 2,
          "NO_SHOW": 1
        },
        "total_room_nights": 28,
        "total_amount_brl": "7566.00",
        "average_nightly_rate_brl": "270.21",
        "top_hotels": [
          [
            "H01",
            "1200.00"
          ],
          [
            "H02",
            "1084.00"
          ],
          [
            "H12",
            "1000.00"
          ],
          [
            "H10",
            "900.00"
          ],
          [
            "H09",
            "882.00"
          ]
        ]
      },
      "rows_omitted": 0
    }
    {
      "file": "reservas_hoteis.csv",
      "actual_summary": {
        "total_reservations": 200,
        "confirmed_reservations": 153,
        "cancelled_reservations": 22,
        "no_show_reservations": 25,
        "total_room_nights": -1393,
        "total_amount_brl": "193218.53",
        "average_nightly_rate_brl": "0.00"
      },
      "expected_from_rules": {
        "total_reservations": 300,
        "status_counts": {
          "CANCELLED": 31,
          "CONFIRMED": 235,
          "NO_SHOW": 34
        },
        "total_room_nights": 1347,
        "total_amount_brl": "396170.00",
        "average_nightly_rate_brl": "294.11",
        "top_hotels": [
          [
            "H06",
            "45165.46"
          ],
          [
            "H10",
            "45041.69"
          ],
          [
            "H12",
            "41647.69"
          ],
          [
            "H07",
            "39920.52"
          ],
          [
            "H11",
            "37455.69"
          ]
        ]
      },
      "rows_omitted": 100
    }
    ✓ • 161ms

## Activity

    $ command -v python3.11 python3.12 pytest uv pipx
    /usr/local/bin/pipx
    ✗ (1) • 0ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        roots = [Path('/Users/joaovictordesousalima/Desktop/onfly-challenge'), Path('/Users/joaovictordesousalima/Downloads/onfly-desafio'), Path('/opt/homebrew/bin'), Path('/usr/local/bin')]
        for root in roots:
            for pattern in ('.venv/bin/python*', 'venv/bin/python*', 'python3*', 'pytest*'):
                for p in sorted(root.glob(pattern)):
                    print(p)
        PY
    /usr/local/bin/python3
    /usr/local/bin/python3-config
    /usr/local/bin/python3-intel64
    /usr/local/bin/python3.13
    /usr/local/bin/python3.13-config
    /usr/local/bin/python3.13-intel64
    ✓ • 0ms

## Activity

    $ PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python3 - <<'PY'
        import importlib
        import inspect
        import tempfile
        import traceback
        from pathlib import Path
        modules = ['test_currency', 'test_nights', 'test_status_rules', 'test_top_hotels', 'test_regression_report']
        failed = 0
        for name in modules:
            module = importlib.import_module(name)
            for fname, function in inspect.getmembers(module, inspect.isfunction):
                if not fname.startswith('test_'):
                    continue
                with tempfile.TemporaryDirectory(prefix='onfly-read-') as directory:
                    try:
                        function(Path(directory))
                    except AssertionError:
                        failed += 1
                        frame = traceback.extract_tb(__import__('sys').exc_info()[2])[-1]
                        print(f'FAIL {name}.{fname}: {frame.line}')
                    else:
                        print(f'PASS {name}.{fname}')
        print(f'Test functions executed directly (without pytest): 5; failed: {failed}')
        PY
    FAIL test_currency.test_currency_conversion_to_brl: assert report["summary"]["total_amount_brl"] == "642.00"
    FAIL test_nights.test_nights_across_month_boundary: assert report["summary"]["total_room_nights"] == 3
    FAIL test_status_rules.test_status_rules_exclude_cancelled_and_no_show: assert report["summary"]["total_amount_brl"] == "100.00"
    FAIL test_top_hotels.test_top_hotels_are_ranked_descending: assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]
    FAIL test_regression_report.test_regression_report_on_sample: assert report["summary"] == {
    Test functions executed directly (without pytest): 5; failed: 5
    ✓ • 844ms

## Assistant

Li o projeto completo: código, cinco testes, utilitário dos testes, configurações, três CSVs e arquivos de entrega. **Nenhum arquivo foi alterado.**

O fluxo está separado em leitura dos CSVs, conversão de tipos, regras de negócio, agregação e saída pelo CLI. Identifiquei estes defeitos:

| Local | Problema |
|---|---|
| `csv_reservation_repository.py:47` | Interrompe a leitura em **200 reservas**, descartando as últimas 100. |
| `stay_calculator.py:10` | Subtrai apenas o dia do mês, produzindo noites negativas nas viradas de mês ou ano. |
| `currency_converter.py:11` | Divide pela taxa em vez de multiplicar e utiliza `float`, contrariando a precisão exigida. |
| `status_policy.py:8` | Exclui apenas `CANCELLED`, incluindo indevidamente `NO_SHOW` no faturamento e nas noites. |
| `report_builder.py:91` | Ordena hotéis pelo menor valor primeiro. |

**O corte em 200 não é coberto pelos testes fornecidos.** Eles verificam câmbio, virada de mês, status, ranking e uma regressão com três reservas. Também faltam verificações específicas para precisão monetária, desempate e outros pontos do contrato.

Calculei os resultados esperados diretamente dos CSVs, usando as regras do README:

| Indicador do arquivo principal | Resultado atual | Esperado |
|---|---:|---:|
| Reservas | 200 | **300** |
| Confirmadas | 153 | **235** |
| Canceladas | 22 | **31** |
| Não comparecimento | 25 | **34** |
| Noites de quartos | -1393 | **1347** |
| Total BRL | 193218.53 | **396170.00** |
| Média por noite BRL | 0.00 | **294.11** |

O cálculo independente da amostra também coincidiu com os valores publicados no README.

O Python disponível está sem `pytest`. Executei diretamente as cinco funções de teste, preservando os arquivos: **todas falharam nas asserções esperadas**. Isso confirma os problemas, mas ainda não constitui uma execução oficial de `pytest -q`.

As pastas `entrega/` e `output/` contêm somente `.gitkeep`. Ainda não há documentação de entrega nem relatório gerado.

## User

novamente, execute os testes fornecidos e o CLI com a amostra de validação, usando um ambiente adequado ao projeto. Compare o relatório com os valores esperados no README. Apresente as falhas observadas e preserve esse resultado para documentarmos a investigação. Não altere código, testes ou dados nesta etapa

## Assistant

Vou preparar um ambiente isolado com as dependências declaradas, executar `pytest` e o CLI com a amostra de validação. Vou salvar os logs, o relatório e a comparação com o README na pasta de trabalho, sem alterar código, testes ou dados.

## Activity

    $ pwd
    /Users/joaovictordesousalima/Desktop/onfly-challenge
    ✓ • 0ms

## Activity

    $ rg --files --hidden -g '!.git/**' -g '!node_modules/**' -g '!vendor/**' -g 'AGENTS.md' -g 'README*' -g 'pyproject.toml' -g 'requirements*.txt' /Users/joaovictordesousalima/Desktop/onfly-challenge /Users/joaovictordesousalima/Downloads/onfly-desafio
    /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements-dev.txt
    /Users/joaovictordesousalima/Downloads/onfly-desafio/README.md
    /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements.txt
    /Users/joaovictordesousalima/Downloads/onfly-desafio/pyproject.toml
    ✓ • 0ms

## Activity

    $ python3 --version
    Python 3.13.9
    ✓ • 0ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import hashlib, json, tempfile, subprocess, sys
        from datetime import datetime, timezone
        source = Path('/Users/joaovictordesousalima/Downloads/onfly-desafio')
        workspace = Path('/Users/joaovictordesousalima/Desktop/onfly-challenge')
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        evidence = workspace / 'investigacao' / ('onfly-baseline-' + stamp)
        evidence.mkdir(parents=True)
        env_root = Path(tempfile.mkdtemp(prefix='onfly-baseline-'))
        manifest = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.rglob('*')) if p.is_file()}
        (evidence / 'manifesto-antes.json').write_text(json.dumps(manifest, indent=2) + '\n')
        state = {'source': str(source), 'evidence': str(evidence), 'venv': str(env_root / 'venv'), 'created_at_utc': stamp, 'bootstrap_python': sys.version, 'requirements_dev': (source / 'requirements-dev.txt').read_text(), 'pyproject': (source / 'pyproject.toml').read_text()}
        (evidence / 'ambiente.json').write_text(json.dumps(state, indent=2) + '\n')
        print(json.dumps(state, indent=2), flush=True)
        with (evidence / 'venv-setup.log').open('w') as log:
            result = subprocess.run([sys.executable, '-m', 'venv', state['venv']], stdout=log, stderr=subprocess.STDOUT)
        print('venv_exit_code:', result.returncode)
        PY
    {
      "source": "/Users/joaovictordesousalima/Downloads/onfly-desafio",
      "evidence": "/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z",
      "venv": "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv",
      "created_at_utc": "20261115T222717Z",
      "bootstrap_python": "3.13.9 (v3.13.9:8183fa5e3f7, Oct 14 2025, 10:27:13) [Clang 16.0.0 (clang-1600.0.26.6)]",
      "requirements_dev": "pytest==8.3.4\nruff==0.8.4\n",
      "pyproject": "[project]\nname = \"onfly-report\"\nversion = \"1.0.0\"\ndescription = \"Consolidador de reservas de hotel da Onfly\"\nrequires-python = \">=3.11\"\n\n[tool.ruff]\nline-length = 120\ntarget-version = \"py311\"\nsrc = [\"src\"]\n\n[tool.ruff.lint]\nselect = [\"E\", \"F\", \"I\"]\n\n[tool.pytest.ini_options]\ntestpaths = [\"tests\"]\npythonpath = [\"src\"]\naddopts = \"-ra\"\n"
    }
    venv_exit_code: 0
    ✓ • 4.42s

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import json, os, subprocess
        p = Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z')
        s = json.loads((p / 'ambiente.json').read_text())
        command = [str(Path(s['venv']) / 'bin/python'), '-m', 'pip', 'install', '--disable-pip-version-check', '--no-cache-dir', '-r', str(Path(s['source']) / 'requirements-dev.txt')]
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        with (p / 'dependencias-install.log').open('w') as log:
            log.write('Command: ' + ' '.join(command) + '\n')
            log.flush()
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=env)
        print('install_exit_code:', result.returncode)
        print((p / 'dependencias-install.log').read_text())
        PY
    install_exit_code: 1
    Command: /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/python -m pip install --disable-pip-version-check --no-cache-dir -r /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements-dev.txt
    WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x10d19cec0>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known')': /simple/pytest/
    WARNING: Retrying (Retry(total=3, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x10d0b6210>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known')': /simple/pytest/
    WARNING: Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x10d0b6490>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known')': /simple/pytest/
    WARNING: Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x10d0b6710>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known')': /simple/pytest/
    WARNING: Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x10d0b6990>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known')': /simple/pytest/
    ERROR: Could not find a version that satisfies the requirement pytest==8.3.4 (from versions: none)
    ERROR: No matching distribution found for pytest==8.3.4
    
    ✓ • 8.28s

## Activity

    $ curl -fsSL --connect-timeout 15 https://pypi.org/pypi/pytest/8.3.4/json -o /private/tmp/onfly-pytest-8.3.4.json
    ✓ • 74ms

## Assistant

O ambiente isolado já foi criado com Python 3.13.9, compatível com o requisito `>=3.11`. A instalação pelo `pip` falhou por acesso à rede; vou baixar os pacotes separadamente para instalar as versões declaradas e executar o pytest de fato.

## Activity

    $ curl -fsSL --connect-timeout 15 https://pypi.org/pypi/iniconfig/2.0.0/json -o /private/tmp/onfly-iniconfig-2.0.0.json
    ✓ • 71ms

## Activity

    $ curl -fsSL --connect-timeout 15 https://pypi.org/pypi/pluggy/1.5.0/json -o /private/tmp/onfly-pluggy-1.5.0.json
    ✓ • 76ms

## Activity

    $ curl -fsSL --connect-timeout 15 https://pypi.org/pypi/packaging/24.2/json -o /private/tmp/onfly-packaging-24.2.json
    ✓ • 80ms

## Activity

    $ curl -fsSL --connect-timeout 15 https://pypi.org/pypi/ruff/0.8.4/json -o /private/tmp/onfly-ruff-0.8.4.json
    ✓ • 93ms

## Activity

    $ python3 - <<'PY'
        import json, platform
        from pathlib import Path
        p = Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z')
        s = json.loads((p / 'ambiente.json').read_text())
        wheel_dir = Path(s['venv']).parent / 'wheels'
        wheel_dir.mkdir()
        selected = []
        for name, version in [('pytest','8.3.4'),('ruff','0.8.4'),('packaging','24.2'),('iniconfig','2.0.0'),('pluggy','1.5.0')]:
            metadata = json.loads(Path(f'/private/tmp/onfly-{name}-{version}.json').read_text())
            candidates = [u for u in metadata['urls'] if u['filename'].endswith('.whl')]
            if name == 'ruff':
                architecture = 'arm64' if platform.machine() == 'arm64' else 'x86_64'
                candidates = [u for u in candidates if 'macosx' in u['filename'] and architecture in u['filename']]
            assert len(candidates) == 1, [c['filename'] for c in candidates]
            wheel = candidates[0]
            selected.append({'package':name, 'version':version, 'filename':wheel['filename'], 'url':wheel['url'], 'sha256':wheel['digests']['sha256'], 'target':str(wheel_dir / wheel['filename'])})
        (p / 'pacotes-download.json').write_text(json.dumps(selected, indent=2) + '\n')
        print(json.dumps(selected))
        PY
    [{"package": "pytest", "version": "8.3.4", "filename": "pytest-8.3.4-py3-none-any.whl", "url": "https://files.pythonhosted.org/packages/11/92/76a1c94d3afee238333bc0a42b82935dd8f9cf8ce9e336ff87ee14d9e1cf/pytest-8.3.4-py3-none-any.whl", "sha256": "50e16d954148559c9a74109af1eaf0c945ba2d8f30f0a3d3335edde19788b6f6", "target": "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/pytest-8.3.4-py3-none-any.whl"}, {"package": "ruff", "version": "0.8.4", "filename": "ruff-0.8.4-py3-none-macosx_10_12_x86_64.whl", "url": "https://files.pythonhosted.org/packages/eb/7a/5aba20312c73f1ce61814e520d1920edf68ca3b9c507bd84d8546a8ecaa8/ruff-0.8.4-py3-none-macosx_10_12_x86_64.whl", "sha256": "ffb60904651c00a1e0b8df594591770018a0f04587f7deeb3838344fe3adabac", "target": "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/ruff-0.8.4-py3-none-macosx_10_12_x86_64.whl"}, {"package": "packaging", "version": "24.2", "filename": "packaging-24.2-py3-none-any.whl", "url": "https://files.pythonhosted.org/packages/88/ef/eb23f262cca3c0c4eb7ab1933c3b1f03d021f2c48f54763065b6f0e321be/packaging-24.2-py3-none-any.whl", "sha256": "09abb1bccd265c01f4a3aa3f7a7db064b36514d2cba19a2f694fe6150451a759", "target": "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/packaging-24.2-py3-none-any.whl"}, {"package": "iniconfig", "version": "2.0.0", "filename": "iniconfig-2.0.0-py3-none-any.whl", "url": "https://files.pythonhosted.org/packages/ef/a6/62565a6e1cf69e10f5727360368e451d4b7f58beeac6173dc9db836a5b46/iniconfig-2.0.0-py3-none-any.whl", "sha256": "b6a85871a79d2e3b22d2d1b94ac2824226a63c6b741c88f7ae975f18b6778374", "target": "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/iniconfig-2.0.0-py3-none-any.whl"}, {"package": "pluggy", "version": "1.5.0", "filename": "pluggy-1.5.0-py3-none-any.whl", "url": "https://files.pythonhosted.org/packages/88/5f/e351af9a41f866ac3f1fac4ca0613908d9a41741cfcf2228f4ad853b697d/pluggy-1.5.0-py3-none-any.whl", "sha256": "44e1ad92c8ca002de6377e165f3e0f1be63266ab4d554740532335b9d75ea669", "target": "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/pluggy-1.5.0-py3-none-any.whl"}]
    ✓ • 0ms

## Activity

    $ curl -fsSL --connect-timeout 15 'https://files.pythonhosted.org/packages/ef/a6/62565a6e1cf69e10f5727360368e451d4b7f58beeac6173dc9db836a5b46/iniconfig-2.0.0-py3-none-any.whl' -o '/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/iniconfig-2.0.0-py3-none-any.whl'
    ✓ • 0ms

## Activity

    $ curl -fsSL --connect-timeout 15 'https://files.pythonhosted.org/packages/88/5f/e351af9a41f866ac3f1fac4ca0613908d9a41741cfcf2228f4ad853b697d/pluggy-1.5.0-py3-none-any.whl' -o '/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/pluggy-1.5.0-py3-none-any.whl'
    ✓ • 0ms

## Activity

    $ curl -fsSL --connect-timeout 15 'https://files.pythonhosted.org/packages/11/92/76a1c94d3afee238333bc0a42b82935dd8f9cf8ce9e336ff87ee14d9e1cf/pytest-8.3.4-py3-none-any.whl' -o '/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/pytest-8.3.4-py3-none-any.whl'
    ✓ • 17ms

## Activity

    $ curl -fsSL --connect-timeout 15 'https://files.pythonhosted.org/packages/88/ef/eb23f262cca3c0c4eb7ab1933c3b1f03d021f2c48f54763065b6f0e321be/packaging-24.2-py3-none-any.whl' -o '/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/packaging-24.2-py3-none-any.whl'
    ✓ • 0ms

## Activity

    $ curl -fsSL --connect-timeout 15 'https://files.pythonhosted.org/packages/eb/7a/5aba20312c73f1ce61814e520d1920edf68ca3b9c507bd84d8546a8ecaa8/ruff-0.8.4-py3-none-macosx_10_12_x86_64.whl' -o '/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/ruff-0.8.4-py3-none-macosx_10_12_x86_64.whl'
    ✓ • 361ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import hashlib, json, os, subprocess
        p = Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z')
        s = json.loads((p / 'ambiente.json').read_text())
        for wheel in json.loads((p / 'pacotes-download.json').read_text()):
            assert hashlib.sha256(Path(wheel['target']).read_bytes()).hexdigest() == wheel['sha256'], wheel['filename']
        python = str(Path(s['venv']) / 'bin/python')
        command = [python, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-index', '--find-links', str(Path(s['venv']).parent / 'wheels'), '-r', str(Path(s['source']) / 'requirements-dev.txt')]
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        result = subprocess.run(command, capture_output=True, text=True, env=env)
        (p / 'dependencias-offline.log').write_text('Command: ' + ' '.join(command) + '\n' + result.stdout + result.stderr)
        print('install_exit_code:',result.returncode)
        print(result.stdout, result.stderr)
        if result.returncode:
            raise SystemExit(result.returncode)
        freeze = subprocess.run([python, '-m', 'pip', 'freeze'], capture_output=True, text=True, check=True, env=env)
        (p / 'requirements-executados.txt').write_text(freeze.stdout)
        print(freeze.stdout)
        PY
    install_exit_code: 0
    Looking in links: /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels
    Processing /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/pytest-8.3.4-py3-none-any.whl (from -r /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements-dev.txt (line 1))
    Processing /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/ruff-0.8.4-py3-none-macosx_10_12_x86_64.whl (from -r /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements-dev.txt (line 2))
    Processing /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/iniconfig-2.0.0-py3-none-any.whl (from pytest==8.3.4->-r /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements-dev.txt (line 1))
    Processing /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/packaging-24.2-py3-none-any.whl (from pytest==8.3.4->-r /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements-dev.txt (line 1))
    Processing /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/wheels/pluggy-1.5.0-py3-none-any.whl (from pytest==8.3.4->-r /Users/joaovictordesousalima/Downloads/onfly-desafio/requirements-dev.txt (line 1))
    Installing collected packages: ruff, pluggy, packaging, iniconfig, pytest
    
    Successfully installed iniconfig-2.0.0 packaging-24.2 pluggy-1.5.0 pytest-8.3.4 ruff-0.8.4
     WARNING: The directory '/Users/joaovictordesousalima/Library/Caches/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
    
    iniconfig==2.0.0
    packaging==24.2
    pluggy==1.5.0
    pytest==8.3.4
    ruff==0.8.4
    
    ✓ • 1.95s

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import json, os, subprocess
        p = Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z')
        s = json.loads((p / 'ambiente.json').read_text())
        python = str(Path(s['venv']) / 'bin/python')
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        command = [python, '-m', 'onfly_report', '--input', 'data/exemplo-validacao.csv', '--rates', 'data/taxas_cambio.csv', '--output', str(p / 'exemplo-observado.json')]
        env['PYTHONPATH'] = str(Path(s['source']) / 'src')
        result = subprocess.run(command, cwd=s['source'], env=env, capture_output=True, text=True, timeout=120)
        (p / 'cli-amostra.stdout.log').write_text(result.stdout)
        (p / 'cli-amostra.stderr.log').write_text(result.stderr)
        meta = {'command':command, 'cwd':s['source'], 'exit_code':result.returncode, 'environment':{key:env[key] for key in ('PYTHONDONTWRITEBYTECODE','PYTHONPATH','PYTEST_DISABLE_PLUGIN_AUTOLOAD') if key in env}}
        (p / 'cli-amostra.execucao.json').write_text(json.dumps(meta, indent=2) + '\n')
        print(json.dumps(meta, indent=2))
        print(result.stdout)
        print(result.stderr)
        PY
    {
      "command": [
        "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/python",
        "-m",
        "onfly_report",
        "--input",
        "data/exemplo-validacao.csv",
        "--rates",
        "data/taxas_cambio.csv",
        "--output",
        "/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/exemplo-observado.json"
      ],
      "cwd": "/Users/joaovictordesousalima/Downloads/onfly-desafio",
      "exit_code": 0,
      "environment": {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": "/Users/joaovictordesousalima/Downloads/onfly-desafio/src"
      }
    }
    Reservas: 12 | Confirmadas: 9 | Noites: -33 | Total BRL: 5962.41
    
    
    ✓ • 142ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import json, os, subprocess
        p = Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z')
        s = json.loads((p / 'ambiente.json').read_text())
        python = str(Path(s['venv']) / 'bin/python')
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        command = [python, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', '--basetemp', str(Path(s['venv']).parent / 'pytest-temp'), '--junitxml', str(p / 'pytest.xml')]
        env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
        result = subprocess.run(command, cwd=s['source'], env=env, capture_output=True, text=True, timeout=120)
        (p / 'pytest.stdout.log').write_text(result.stdout)
        (p / 'pytest.stderr.log').write_text(result.stderr)
        meta = {'command':command, 'cwd':s['source'], 'exit_code':result.returncode, 'environment':{key:env[key] for key in ('PYTHONDONTWRITEBYTECODE','PYTHONPATH','PYTEST_DISABLE_PLUGIN_AUTOLOAD') if key in env}}
        (p / 'pytest.execucao.json').write_text(json.dumps(meta, indent=2) + '\n')
        print(json.dumps(meta, indent=2))
        print(result.stdout)
        print(result.stderr)
        PY
    {
      "command": [
        "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/python",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "--basetemp",
        "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/pytest-temp",
        "--junitxml",
        "/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/pytest.xml"
      ],
      "cwd": "/Users/joaovictordesousalima/Downloads/onfly-desafio",
      "exit_code": 1,
      "environment": {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"
      }
    }
    FFFFF                                                                    [100%]
    =================================== FAILURES ===================================
    _______________________ test_currency_conversion_to_brl ________________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/pytest-temp/test_currency_conversion_to_br0')
    
        def test_currency_conversion_to_brl(tmp_path):
            """Multiplica o valor pela taxa, sem inverter a operação."""
            report = run_cli(
                tmp_path,
                [
                    {"reservation_id": "R-1", "currency": "BRL", "amount": "100.00"},
                    {"reservation_id": "R-2", "currency": "USD", "amount": "100.00"},
                ],
            )
    >       assert report["summary"]["total_amount_brl"] == "642.00"
    E       AssertionError: assert '118.45' == '642.00'
    E
    E         - 642.00
    E         + 118.45
    
    tests/test_currency.py:15: AssertionError
    ______________________ test_nights_across_month_boundary _______________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/pytest-temp/test_nights_across_month_bound0')
    
        def test_nights_across_month_boundary(tmp_path):
            """A diferença de datas considera a virada de mês, não o dia do mês."""
            report = run_cli(
                tmp_path,
                [
                    {
                        "reservation_id": "R-1",
                        "checkin_date": "2025-01-30",
                        "checkout_date": "2025-02-02",
                        "rooms": "1",
                    }
                ],
            )
    >       assert report["summary"]["total_room_nights"] == 3
    E       assert -28 == 3
    
    tests/test_nights.py:19: AssertionError
    _______________________ test_regression_report_on_sample _______________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/pytest-temp/test_regression_report_on_samp0')
    
        def test_regression_report_on_sample(tmp_path):
            """Relatório completo de uma amostra pequena, com status, noites e câmbio."""
            report = run_cli(
                tmp_path,
                [
                    {
                        "reservation_id": "R-1",
                        "amount": "1000.00",
                        "checkin_date": "2025-01-10",
                        "checkout_date": "2025-01-13",
                    },
                    {"reservation_id": "R-2", "status": "CANCELLED", "amount": "500.00"},
                    {
                        "reservation_id": "R-3",
                        "currency": "USD",
                        "amount": "100.00",
                        "checkin_date": "2025-01-20",
                        "checkout_date": "2025-01-22",
                    },
                ],
            )
    >       assert report["summary"] == {
                "total_reservations": 3,
                "confirmed_reservations": 2,
                "cancelled_reservations": 1,
                "no_show_reservations": 0,
                "total_room_nights": 5,
                "total_amount_brl": "1542.00",
                "average_nightly_rate_brl": "308.40",
            }
    E       AssertionError: assert {'average_nig...ions': 0, ...} == {'average_nig...ions': 0, ...}
    E
    E         Omitting 5 identical items, use -vv to show
    E         Differing items:
    E         {'average_nightly_rate_brl': '203.69'} != {'average_nightly_rate_brl': '308.40'}
    E         {'total_amount_brl': '1018.45'} != {'total_amount_brl': '1542.00'}
    E         Use -v to get more diff
    
    tests/test_regression_report.py:27: AssertionError
    _______________ test_status_rules_exclude_cancelled_and_no_show ________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/pytest-temp/test_status_rules_exclude_canc0')
    
        def test_status_rules_exclude_cancelled_and_no_show(tmp_path):
            """Somente CONFIRMED entra nos totais financeiros."""
            report = run_cli(
                tmp_path,
                [
                    {"reservation_id": "R-1", "status": "CONFIRMED", "amount": "100.00"},
                    {"reservation_id": "R-2", "status": "CANCELLED", "amount": "50.00"},
                    {"reservation_id": "R-3", "status": "NO_SHOW", "amount": "20.00"},
                ],
            )
            assert report["summary"]["total_reservations"] == 3
            assert report["summary"]["confirmed_reservations"] == 1
            assert report["summary"]["cancelled_reservations"] == 1
            assert report["summary"]["no_show_reservations"] == 1
    >       assert report["summary"]["total_amount_brl"] == "100.00"
    E       AssertionError: assert '120.00' == '100.00'
    E
    E         - 100.00
    E         ?  ^
    E         + 120.00
    E         ?  ^
    
    tests/test_status_rules.py:20: AssertionError
    ____________________ test_top_hotels_are_ranked_descending _____________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/pytest-temp/test_top_hotels_are_ranked_des0')
    
        def test_top_hotels_are_ranked_descending(tmp_path):
            """O ranking mostra os hotéis de maior valor primeiro."""
            report = run_cli(
                tmp_path,
                [
                    {"reservation_id": "R-1", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "1000.00"},
                    {"reservation_id": "R-2", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "900.00"},
                    {"reservation_id": "R-3", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "800.00"},
                    {"reservation_id": "R-4", "hotel_id": "H04", "hotel_name": "Hotel D", "amount": "700.00"},
                ],
                top=3,
            )
    >       assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]
    E       AssertionError: assert ['H04', 'H03', 'H02'] == ['H01', 'H02', 'H03']
    E
    E         At index 0 diff: 'H04' != 'H01'
    E         Use -v to get more diff
    
    tests/test_top_hotels.py:18: AssertionError
    - generated xml file: /Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/pytest.xml -
    =========================== short test summary info ============================
    FAILED tests/test_currency.py::test_currency_conversion_to_brl - AssertionErr...
    FAILED tests/test_nights.py::test_nights_across_month_boundary - assert -28 == 3
    FAILED tests/test_regression_report.py::test_regression_report_on_sample - As...
    FAILED tests/test_status_rules.py::test_status_rules_exclude_cancelled_and_no_show
    FAILED tests/test_top_hotels.py::test_top_hotels_are_ranked_descending - Asse...
    5 failed in 0.68s
    
    
    ✓ • 1.04s

## Activity

    $ cat /Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/exemplo-observado.json
    {
      "report_version": "1.0",
      "generated_at": "2026-11-15T19:28:44-03:00",
      "summary": {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": -33,
        "total_amount_brl": "5962.41",
        "average_nightly_rate_brl": "0.00"
      },
      "by_month": [
        {
          "month": "2025-01",
          "reservations": 9,
          "room_nights": -36,
          "total_brl": "5936.90"
        },
        {
          "month": "2025-02",
          "reservations": 1,
          "room_nights": 3,
          "total_brl": "25.51"
        }
      ],
      "top_hotels": [
        {
          "hotel_id": "H09",
          "hotel_name": "Hotel Lisboa, Centro",
          "room_nights": 3,
          "total_brl": "25.51"
        },
        {
          "hotel_id": "H02",
          "hotel_name": "Hotel Mirante",
          "room_nights": 2,
          "total_brl": "36.90"
        },
        {
          "hotel_id": "H05",
          "hotel_name": "Hotel Recife Plaza",
          "room_nights": 1,
          "total_brl": "300.00"
        },
        {
          "hotel_id": "H08",
          "hotel_name": "Hotel Iguazu Falls",
          "room_nights": 1,
          "total_brl": "400.00"
        },
        {
          "hotel_id": "H07",
          "hotel_name": "Hotel Brasília Tower",
          "room_nights": 2,
          "total_brl": "600.00"
        }
      ]
    }
    ✓ • 0ms

## Assistant

O pytest executou os cinco testes: todos falharam. O CLI da amostra terminou com código `0`, mas gerou `-33` noites e total de `5962.41`, contra `28` noites e `7566.00` esperados. Estou registrando também as divergências por mês e no ranking, além de verificar a integridade dos arquivos originais.

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        from datetime import datetime, timedelta
        import hashlib, json, re, shlex, shutil
        import xml.etree.ElementTree as ET
        p = Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z')
        s = json.loads((p / 'ambiente.json').read_text())
        source = Path(s['source'])
        readme = (source / 'README.md').read_text()
        (p / 'README-referencia.md').write_text(readme)
        block = readme.split('<!-- AMOSTRA:INICIO -->')[1].split('<!-- AMOSTRA:FIM -->')[0]
        tables = re.findall(r'(?:^\|[^\n]*\n?)+', block, re.MULTILINE)
        assert len(tables) == 3
        
        def table(raw):
            return [[cell.strip().replace('`','').replace('\\','') for cell in line.strip().strip('|').split('|')] for line in raw.strip().splitlines()]
        summary = {key:int(value) if '.' not in value else value for key,value in table(tables[0])[2:]}
        months = [{'month':v[0], 'reservations':int(v[1]), 'room_nights':int(v[2]), 'total_brl':v[3]} for v in table(tables[1])[2:]]
        hotels = [{'hotel_id':v[0], 'hotel_name':v[1], 'room_nights':int(v[2]), 'total_brl':v[3]} for v in table(tables[2])[2:]]
        expected = {'report_version':'1.0', 'summary':summary, 'by_month':months, 'top_hotels':hotels}
        (p / 'exemplo-esperado-readme.json').write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n')
        observed = json.loads((p / 'exemplo-observado.json').read_text())
        comparable = {key:value for key,value in observed.items() if key != 'generated_at'}
        differences = []
        def compare(wanted, actual, path='$'):
            if type(wanted) is not type(actual):
                differences.append({'path':path, 'expected':wanted, 'observed':actual, 'reason':'type'})
            elif isinstance(wanted,dict):
                for key in wanted.keys() | actual.keys():
                    if key not in wanted or key not in actual:
                        differences.append({'path':path+'.'+key, 'expected':wanted.get(key), 'observed':actual.get(key), 'reason':'missing_or_extra_field'})
                    else:
                        compare(wanted[key], actual[key], path+'.'+key)
            elif isinstance(wanted,list):
                if len(wanted) != len(actual):
                    differences.append({'path':path+'.length','expected':len(wanted),'observed':len(actual)})
                for index,(a,b) in enumerate(zip(wanted,actual)):
                    compare(a,b,f'{path}[{index}]')
            elif wanted != actual:
                differences.append({'path':path, 'expected':wanted, 'observed':actual})
        compare(expected, comparable)
        differences.sort(key=lambda d:d['path'])
        offset_ok = datetime.fromisoformat(observed['generated_at']).utcoffset() == timedelta(hours=-3)
        comparison = {'reference':'README.md, AMOSTRA:INICIO..AMOSTRA:FIM; report_version from CLI contract', 'ignored':['generated_at value'], 'generated_at_offset_minus_03':offset_ok, 'matches':not differences, 'difference_count':len(differences), 'differences':differences}
        (p / 'comparacao.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + '\n')
        shutil.copytree(Path(s['venv']).parent / 'pytest-temp', p / 'casos-pytest')
        before = json.loads((p / 'manifesto-antes.json').read_text())
        after = {f.relative_to(source).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(source.rglob('*')) if f.is_file()}
        (p / 'manifesto-depois.json').write_text(json.dumps(after, indent=2) + '\n')
        integrity = {'algorithm':'SHA-256', 'files_before':len(before), 'files_after':len(after), 'modified':[k for k in before.keys() & after.keys() if before[k] != after[k]], 'added':sorted(after.keys()-before.keys()), 'removed':sorted(before.keys()-after.keys()), 'identical':before==after}
        (p / 'integridade.json').write_text(json.dumps(integrity, indent=2) + '\n')
        assert integrity['identical'], integrity
        suite = ET.parse(p / 'pytest.xml').getroot().find('testsuite')
        pytest_meta = json.loads((p / 'pytest.execucao.json').read_text())
        cli_meta = json.loads((p / 'cli-amostra.execucao.json').read_text())
        lines = [
        '# Investigação inicial — Onfly', '',
        f"Execução UTC: {s['created_at_utc']}. Projeto original: `{source}`.", '',
        '## Ambiente e escopo', '',
        'Python 3.13.9 em venv isolado, compatível com `requires-python = ">=3.11"` do pyproject.toml. Não é uma validação específica com Python 3.11.',
        'Instalados pytest==8.3.4 e ruff==0.8.4, exatamente como requirements-dev.txt. Versões transitivas em requirements-executados.txt.',
        'O primeiro pip install falhou por resolução/acesso de rede. Os wheels foram baixados do PyPI via curl, conferidos por SHA-256 e instalados sem índice. Logs e URLs estão preservados.',
        'Nenhum arquivo do projeto original foi alterado, adicionado ou removido: os manifestos SHA-256 de todos os 31 arquivos são idênticos. Os resultados ficam nesta pasta de investigação, fora do projeto original.',
        'Cache do pytest e bytecode foram desabilitados; temporários, XML e saída do CLI foram direcionados para fora do projeto original.', '',
        '## Comandos executados', '',
        'Executados no diretório original. As opções adicionais do pytest controlam somente cache, temporários e a gravação do XML.', '',
        '```sh',
        'PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 ' + shlex.join(pytest_meta['command']),
        'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src ' + shlex.join(cli_meta['command']),
        '```', '',
        '## Testes fornecidos', '',
        f"Resultado real do pytest: {suite.attrib['tests']} testes, {suite.attrib['failures']} falhas, {suite.attrib['errors']} erros; código de saída {pytest_meta['exit_code']}. Consulte pytest.stdout.log e pytest.xml.", '',
        '| Teste | Esperado | Observado |', '|---|---|---|',
        '| Câmbio | 642.00 BRL | 118.45 BRL |',
        '| Noites na virada de mês | 3 | -28 |',
        '| Regressão: total / média | 1542.00 / 308.40 | 1018.45 / 203.69 |',
        '| Status: total faturável | 100.00 BRL | 120.00 BRL |',
        '| Ranking | H01, H02, H03 | H04, H03, H02 |', '',
        '## CLI com a amostra de validação', '',
        f"Código de saída: {cli_meta['exit_code']}; stderr vazio: {not bool((p / 'cli-amostra.stderr.log').read_text())}. O comando conclui, porém gera números incorretos.", '',
        '```text', (p / 'cli-amostra.stdout.log').read_text().strip(), '```', '',
        '### Resumo', '', '| Campo | Esperado no README | Observado | Resultado |', '|---|---:|---:|---|'
        ]
        for key,value in expected['summary'].items():
            actual = observed['summary'][key]
            lines.append(f"| {key} | {value} | {actual} | {'OK' if value==actual else 'FALHA'} |")
        lines += ['', '### Agrupamento por mês', '', '| Mês | Reservas esperado / observado | Noites esperado / observado | BRL esperado / observado |', '|---|---|---|---|']
        for wanted,actual in zip(expected['by_month'], observed['by_month']):
            lines.append(f"| {wanted['month']} | {wanted['reservations']} / {actual['reservations']} | {wanted['room_nights']} / {actual['room_nights']} | {wanted['total_brl']} / {actual['total_brl']} |")
        lines += ['', '### Ranking de hotéis', '', '| Posição | Hotel esperado | Noites / BRL esperados | Hotel observado | Noites / BRL observados |', '|---|---|---|---|---|']
        for index,(wanted,actual) in enumerate(zip(expected['top_hotels'], observed['top_hotels']),1):
            lines.append(f"| {index} | {wanted['hotel_id']} — {wanted['hotel_name']} | {wanted['room_nights']} / {wanted['total_brl']} | {actual['hotel_id']} — {actual['hotel_name']} | {actual['room_nights']} / {actual['total_brl']} |")
        lines += ['', f"Comparação recursiva: {len(differences)} valores divergentes, detalhados em comparacao.json. A referência foi extraída diretamente das três tabelas da amostra no README. report_version é 1.0; generated_at tem offset -03:00 e seu valor foi ignorado conforme o contrato.", '',
        '## Causas identificadas por leitura do código', '',
        '- Câmbio: currency_converter.py:11 divide pela taxa e converte por float.',
        '- Noites: stay_calculator.py:10 subtrai números dos dias do mês em vez das datas completas.',
        '- Status: status_policy.py:8 aceita NO_SHOW ao excluir somente CANCELLED. A amostra inclui indevidamente H05 e uma reserva adicional em janeiro.',
        '- Ranking: report_builder.py:91 ordena o total em ordem crescente.',
        '- Corte de leitura: csv_reservation_repository.py:47-48 interrompe ao chegar a 200 registros. Este defeito não é exercitado pela amostra de 12 reservas nem pelos cinco testes fornecidos. Sua correção não pode ser comprovada por estas execuções.', '',
        '## Evidências preservadas', '',
        '- Logs completos e códigos de saída: pytest.* e cli-amostra.*.',
        '- Relatório real: exemplo-observado.json; referência do README: exemplo-esperado-readme.json; diferenças: comparacao.json.',
        '- Cópia do README usado: README-referencia.md.',
        '- Entradas e relatórios temporários dos cinco testes: casos-pytest/.',
        '- Ambiente e dependências: ambiente.json, requirements-executados.txt, pacotes-download.json e logs de instalação.',
        '- Integridade: manifesto-antes.json, manifesto-depois.json e integridade.json.', '',
        'Nenhuma correção foi realizada nesta etapa.', ''
        ]
        # Use the measured file count rather than a hard-coded count.
        lines = [line.replace('todos os 31 arquivos', f"todos os {len(before)} arquivos") for line in lines]
        (p / 'INVESTIGACAO.md').write_text('\n'.join(lines))
        print(json.dumps({'pytest':suite.attrib, 'comparison':comparison, 'integrity':integrity}, ensure_ascii=False, indent=2))
        print('\nReport:',p / 'INVESTIGACAO.md')
        PY
    {
      "pytest": {
        "name": "pytest",
        "errors": "0",
        "failures": "5",
        "skipped": "0",
        "tests": "5",
        "time": "0.678",
        "timestamp": "2026-11-15T19:28:45.149494-03:00",
        "hostname": "192.168.0.18"
      },
      "comparison": {
        "reference": "README.md, AMOSTRA:INICIO..AMOSTRA:FIM; report_version from CLI contract",
        "ignored": [
          "generated_at value"
        ],
        "generated_at_offset_minus_03": true,
        "matches": false,
        "difference_count": 22,
        "differences": [
          {
            "path": "$.by_month[0].reservations",
            "expected": 8,
            "observed": 9
          },
          {
            "path": "$.by_month[0].room_nights",
            "expected": 25,
            "observed": -36
          },
          {
            "path": "$.by_month[0].total_brl",
            "expected": "6684.00",
            "observed": "5936.90"
          },
          {
            "path": "$.by_month[1].total_brl",
            "expected": "882.00",
            "observed": "25.51"
          },
          {
            "path": "$.summary.average_nightly_rate_brl",
            "expected": "270.21",
            "observed": "0.00"
          },
          {
            "path": "$.summary.total_amount_brl",
            "expected": "7566.00",
            "observed": "5962.41"
          },
          {
            "path": "$.summary.total_room_nights",
            "expected": 28,
            "observed": -33
          },
          {
            "path": "$.top_hotels[0].hotel_id",
            "expected": "H01",
            "observed": "H09"
          },
          {
            "path": "$.top_hotels[0].hotel_name",
            "expected": "Hotel Aurora Paulista",
            "observed": "Hotel Lisboa, Centro"
          },
          {
            "path": "$.top_hotels[0].total_brl",
            "expected": "1200.00",
            "observed": "25.51"
          },
          {
            "path": "$.top_hotels[1].total_brl",
            "expected": "1084.00",
            "observed": "36.90"
          },
          {
            "path": "$.top_hotels[2].hotel_id",
            "expected": "H12",
            "observed": "H05"
          },
          {
            "path": "$.top_hotels[2].hotel_name",
            "expected": "Hotel Miami Beach",
            "observed": "Hotel Recife Plaza"
          },
          {
            "path": "$.top_hotels[2].total_brl",
            "expected": "1000.00",
            "observed": "300.00"
          },
          {
            "path": "$.top_hotels[3].hotel_id",
            "expected": "H10",
            "observed": "H08"
          },
          {
            "path": "$.top_hotels[3].hotel_name",
            "expected": "Hotel Madrid, Gran Vía",
            "observed": "Hotel Iguazu Falls"
          },
          {
            "path": "$.top_hotels[3].room_nights",
            "expected": 4,
            "observed": 1
          },
          {
            "path": "$.top_hotels[3].total_brl",
            "expected": "900.00",
            "observed": "400.00"
          },
          {
            "path": "$.top_hotels[4].hotel_id",
            "expected": "H09",
            "observed": "H07"
          },
          {
            "path": "$.top_hotels[4].hotel_name",
            "expected": "Hotel Lisboa, Centro",
            "observed": "Hotel Brasília Tower"
          },
          {
            "path": "$.top_hotels[4].room_nights",
            "expected": 3,
            "observed": 2
          },
          {
            "path": "$.top_hotels[4].total_brl",
            "expected": "882.00",
            "observed": "600.00"
          }
        ]
      },
      "integrity": {
        "algorithm": "SHA-256",
        "files_before": 31,
        "files_after": 31,
        "modified": [],
        "added": [],
        "removed": [],
        "identical": true
      }
    }
    
    Report: /Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/INVESTIGACAO.md
    ✓ • 637ms

## Assistant

Executei em um ambiente virtual isolado com **Python 3.13.9 e pytest 8.3.4**, respeitando o requisito Python ≥ 3.11 e as dependências declaradas.

**Testes fornecidos: 5 falharam, nenhum passou.** O pytest terminou com código `1`.

| Teste | Esperado | Observado |
|---|---|---|
| Câmbio | `642.00` | `118.45` |
| Noites na virada de mês | `3` | `-28` |
| Regressão: total / média | `1542.00 / 308.40` | `1018.45 / 203.69` |
| Status: total faturável | `100.00` | `120.00` |
| Ranking | H01, H02, H03 | H04, H03, H02 |

O **CLI com a amostra terminou com código `0`**, mas produziu valores incorretos:

| Indicador | Esperado no README | Observado |
|---|---:|---:|
| Reservas / confirmadas / canceladas / NO_SHOW | 12 / 9 / 2 / 1 | 12 / 9 / 2 / 1 |
| Noites de quartos | 28 | -33 |
| Total BRL | 7566.00 | 5962.41 |
| Média por noite BRL | 270.21 | 0.00 |

Janeiro apresentou 9 reservas faturáveis em vez de 8, noites negativas e total incorreto. Fevereiro apresentou `25.51` BRL em vez de `882.00`. O ranking também divergiu e incluiu um hotel com reserva `NO_SHOW`.

Preservei o registro completo em [INVESTIGACAO.md](/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/INVESTIGACAO.md), acompanhado dos logs do pytest, relatório observado, referência extraída do README, comparação detalhada e versões instaladas.

**Os 31 arquivos originais permaneceram idênticos**, confirmado por SHA-256 antes e depois. Código, testes e dados não foram alterados.

## User

Ok, com base nos resultados e nos defeitos identificados na leitura, percorra o fluxo do CSV até o JSON. Para cada defeito, mostre a regra do README, o trecho responsável, a causa raiz e o efeito no relatório. Diferencie o que foi comprovado por execução do que foi identificado pela leitura. Ainda não faça alterações

## Assistant

Vou percorrer o fluxo da leitura do CSV até a gravação do JSON e relacionar cada defeito à regra do README e às evidências salvas. Vou separar o que foi observado em execução do que a leitura do código permite concluir, sem alterar arquivos.

## Activity

    $ nl -ba /Users/joaovictordesousalima/Downloads/onfly-desafio/README.md
         1    # Onfly — Consolidador de reservas de hotel
         2
         3    Você recebeu a exportação de reservas de hotel de uma empresa cliente da Onfly. O CLI deste projeto deveria gerar um relatório JSON consolidado, mas **entrega números errados**.
         4
         5    **Sua tarefa:** encontrar e corrigir os defeitos do CLI, fazer os testes fornecidos passarem e
         6    entregar o projeto.
         7
         8    ## Como rodar
         9
        10    Requisitos: Python 3.11+ e pytest para os testes (`requirements-dev.txt`).
        11
        12    ```bash
        13    python3.11 -m venv .venv
        14    source .venv/bin/activate
        15    pip install -r requirements-dev.txt
        16
        17    PYTHONPATH=src python -m onfly\_report \\
        18      --input data/reservas\_hoteis.csv \\
        19      --rates data/taxas\_cambio.csv \\
        20      --output output/report.json
        21    ```
        22
        23    O relatório é gravado em `output/report.json`; o CLI cria o diretório. Um resumo é impresso no
        24    stdout.
        25
        26    Os testes já estão em `tests/`. No início, todos falham — é esperado. Rode:
        27
        28    ```bash
        29    pytest -q
        30    ```
        31
        32    Corrija o código até todos passarem. **Não altere os testes fornecidos.** Se quiser, adicione
        33    testes novos em arquivos `test\_\*.py`.
        34
        35    ## Estrutura
        36
        37    ```
        38    .
        39    ├── README.md              # este arquivo
        40    ├── pyproject.toml
        41    ├── requirements\*.txt
        42    ├── data/
        43    │   ├── reservas\_hoteis.csv
        44    │   ├── taxas\_cambio.csv
        45    │   └── exemplo-validacao.csv
        46    ├── src/onfly\_report/      # CLI
        47    ├── tests/                 # testes fornecidos
        48    ├── entrega/               # sua entrega
        49    └── output/                # relatório gerado
        50    ```
        51
        52    ## Regras de negócio
        53
        54    Os dados fornecidos estão consistentes, os defeitos estão no CLI.
        55
        56    As colunas do CSV são autoexplicativas. O relatório usa hotel, check-in, check-out, quartos, status, moeda e valor; as demais colunas não afetam os totais.
        57
        58    ### Status
        59
        60    * Só `CONFIRMED` é faturável.
        61    * `CANCELLED` e `NO\_SHOW` contam em `total\_reservations` e nas contagens por status, mas não entram
        62    em noites, valores, `by\_month` nem `top\_hotels`.
        63
        64    ### Noites
        65
        66    ```
        67    room\_nights = (checkout\_date - checkin\_date).days \* rooms
        68    ```
        69
        70    A diferença é não inclusiva: check-in 10/01 e check-out 13/01 = 3 noites. Vale também na virada de
        71    mês/ano.
        72
        73    ### Câmbio
        74
        75    * `amount` está na moeda de `currency`.
        76    * Converta com `amount \* rate\_to\_brl`, usando a tabela `data/taxas\_cambio.csv`.
        77    * Todas as moedas do dataset têm taxa.
        78
        79    ### Totais
        80
        81    * `total\_reservations` = número de reservas no arquivo.
        82    * `confirmed\_reservations`, `cancelled\_reservations` e `no\_show\_reservations` = contagens por status.
        83    * `total\_room\_nights`, `total\_amount\_brl` e `average\_nightly\_rate\_brl` usam apenas `CONFIRMED`.
        84
        85    ### Ordem do processamento
        86
        87    ```
        88    ler → converter tipos → contar status → filtrar CONFIRMED → agregar
        89    ```
        90
        91    ### Exatidão
        92
        93    * Use `Decimal`, nunca `float`, no dinheiro.
        94    * Some os valores exatos e arredonde **só na serialização**, para 2 casas, com half-up.
        95    * `average\_nightly\_rate\_brl = total\_amount\_brl / total\_room\_nights`; sem noites, `"0.00"`.
        96    * Check-in/check-out são datas civis (`YYYY-MM-DD`).
        97    * `generated\_at` usa offset fixo `-03:00` e é ignorado na comparação.
        98
        99    ### Ordenação
       100
       101    * `by\_month`: `month` ascendente.
       102    * `top\_hotels`: `total\_brl` decrescente; empate por `hotel\_id` ascendente.
       103
       104    ## Contrato do CLI
       105
       106    ```bash
       107    python -m onfly\_report \\
       108      --input data/reservas\_hoteis.csv \\
       109      --rates data/taxas\_cambio.csv \\
       110      --output output/report.json \\
       111      --top 5
       112    ```
       113
       114    |Argumento|Obrigatório|Padrão|
       115    |-|-|-|
       116    |`--input`|sim|—|
       117    |`--rates`|sim|—|
       118    |`--output`|não|`output/report.json`|
       119    |`--top`|não|`5` (inteiro ≥ 1)|
       120
       121    Códigos de saída: `0` sucesso, `2` entrada/argumento inválido, `1` erro inesperado.
       122
       123    O relatório deve ter exatamente este formato:
       124
       125    ```json
       126    {
       127      "report\_version": "1.0",
       128      "generated\_at": "2025-07-01T10:00:00-03:00",
       129      "summary": {
       130        "total\_reservations": 0,
       131        "confirmed\_reservations": 0,
       132        "cancelled\_reservations": 0,
       133        "no\_show\_reservations": 0,
       134        "total\_room\_nights": 0,
       135        "total\_amount\_brl": "0.00",
       136        "average\_nightly\_rate\_brl": "0.00"
       137      },
       138      "by\_month": \[
       139        {"month": "2025-01", "reservations": 0, "room\_nights": 0, "total\_brl": "0.00"}
       140      ],
       141      "top\_hotels": \[
       142        {"hotel\_id": "H01", "hotel\_name": "Hotel Exemplo", "room\_nights": 0, "total\_brl": "0.00"}
       143      ]
       144    }
       145    ```
       146
       147    * Dinheiro é string com exatamente 2 casas (`"1234.50"`), sem separador de milhar.
       148    * `report\_version` é sempre `"1.0"`.
       149    * `top\_hotels` tem `--top` itens (ou menos, se houver menos hotéis).
       150    * `by\_month` usa o mês do check-in.
       151    * Não altere nomes, tipos ou semântica dos campos.
       152
       153    ## Amostra de validação
       154
       155    Rode o CLI na amostra e compare com o resultado abaixo:
       156
       157    ```bash
       158    PYTHONPATH=src python -m onfly\_report \\
       159      --input data/exemplo-validacao.csv \\
       160      --rates data/taxas\_cambio.csv \\
       161      --output output/exemplo.json
       162    ```
       163
       164    <!-- AMOSTRA:INICIO -->
       165
       166    |Campo|Valor esperado|
       167    |-|-|
       168    |`total\_reservations`|12|
       169    |`confirmed\_reservations`|9|
       170    |`cancelled\_reservations`|2|
       171    |`no\_show\_reservations`|1|
       172    |`total\_room\_nights`|28|
       173    |`total\_amount\_brl`|7566.00|
       174    |`average\_nightly\_rate\_brl`|270.21|
       175
       176    |`month`|`reservations`|`room\_nights`|`total\_brl`|
       177    |-|-|-|-|
       178    |2025-01|8|25|6684.00|
       179    |2025-02|1|3|882.00|
       180
       181    |`hotel\_id`|`hotel\_name`|`room\_nights`|`total\_brl`|
       182    |-|-|-|-|
       183    |H01|Hotel Aurora Paulista|3|1200.00|
       184    |H02|Hotel Mirante|2|1084.00|
       185    |H12|Hotel Miami Beach|1|1000.00|
       186    |H10|Hotel Madrid, Gran Vía|4|900.00|
       187    |H09|Hotel Lisboa, Centro|3|882.00|
       188
       189    <!-- AMOSTRA:FIM -->
       190
       191    A amostra cobre apenas parte dos cenários; use as regras acima para os demais.
       192
       193    ## Entrega
       194
       195    Suba o projeto, incluindo a pasta `entrega/`, em um repositório público no GitHub e compartilhe o
       196    acesso com nosso time via forms.
       197
       198    ```
       199    entrega/
       200    ├── README-ENTREGA.md
       201    └── uso-de-ia/                 # apenas se usou IA
       202        ├── sessao.md (ou .txt/.jsonl; várias: sessao-01.md, sessao-02.md...)
       203        └── declaracao.md
       204    ```
       205
       206    **`README-ENTREGA.md`** deve ter: defeitos corrigidos, causa raiz em uma frase por defeito, como
       207    investigou/abordou o problema, como validar e resultado do `pytest`.
       208
       209    **Caminho com IA:** use assistentes de IA se quiser. Se usar, inclua a exportação da(s) sessão(ões)
       210    no formato nativo da ferramenta (`/export` do Claude Code, export/JSON de outros assistentes, ou log
       211    consolidado de prompts e respostas) e uma `declaracao.md` com:
       212
       213    * ferramenta e modelo usados;
       214    * o que a IA fez e o que você fez.
       215
       216    **Caminho sem IA:** não é necessária sessão nem declaração. A investigação fica no
       217    `entrega/README-ENTREGA.md`.
       218
       219    ## O que não pode mudar
       220
       221    * O comando e os argumentos do CLI.
       222    * O schema e a semântica do relatório acima.
       223    * Os arquivos `data/reservas\_hoteis.csv` e `data/taxas\_cambio.csv`.
       224
       225    Você pode reorganizar o código interno, adicionar arquivos, melhorar logs e adicionar testes. Os
       226    testes fornecidos devem permanecer inalterados.
       227
       228    ## Como será avaliado
       229
       230    A correção verifica se o relatório segue este documento, se os defeitos foram corrigidos e se os
       231    testes fornecidos passam sem alteração. Testes adicionais são considerados.
       232
       233    ## Checklist
       234
       235    * \[ ] O CLI roda com Python 3.11 (`PYTHONPATH=src python -m onfly\_report ...`).
       236    * \[ ] O comando de execução gera `output/report.json` sem erro.
       237    * \[ ] O relatório segue o contrato acima.
       238    * \[ ] `pytest -q` passa com os testes fornecidos.
       239    * \[ ] `entrega/README-ENTREGA.md` preenchido.
       240    * \[ ] Sessão + declaração apenas no caminho com IA; investigação no README-ENTREGA nos dois caminhos.
       241    * \[ ] Repositório público no GitHub com o projeto e o link enviado.
       242
    ✓ • 0ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        root=Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z')
        for name in ['INVESTIGACAO.md','cli-amostra.execucao.json','exemplo-observado.json','integridade.json']:
            print('\nFILE:',name)
            print((root/name).read_text())
        PY
    
    FILE: INVESTIGACAO.md
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
    
    
    FILE: cli-amostra.execucao.json
    {
      "command": [
        "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/python",
        "-m",
        "onfly_report",
        "--input",
        "data/exemplo-validacao.csv",
        "--rates",
        "data/taxas_cambio.csv",
        "--output",
        "/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/exemplo-observado.json"
      ],
      "cwd": "/Users/joaovictordesousalima/Downloads/onfly-desafio",
      "exit_code": 0,
      "environment": {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": "/Users/joaovictordesousalima/Downloads/onfly-desafio/src"
      }
    }
    
    
    FILE: exemplo-observado.json
    {
      "report_version": "1.0",
      "generated_at": "2026-11-15T19:28:44-03:00",
      "summary": {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": -33,
        "total_amount_brl": "5962.41",
        "average_nightly_rate_brl": "0.00"
      },
      "by_month": [
        {
          "month": "2025-01",
          "reservations": 9,
          "room_nights": -36,
          "total_brl": "5936.90"
        },
        {
          "month": "2025-02",
          "reservations": 1,
          "room_nights": 3,
          "total_brl": "25.51"
        }
      ],
      "top_hotels": [
        {
          "hotel_id": "H09",
          "hotel_name": "Hotel Lisboa, Centro",
          "room_nights": 3,
          "total_brl": "25.51"
        },
        {
          "hotel_id": "H02",
          "hotel_name": "Hotel Mirante",
          "room_nights": 2,
          "total_brl": "36.90"
        },
        {
          "hotel_id": "H05",
          "hotel_name": "Hotel Recife Plaza",
          "room_nights": 1,
          "total_brl": "300.00"
        },
        {
          "hotel_id": "H08",
          "hotel_name": "Hotel Iguazu Falls",
          "room_nights": 1,
          "total_brl": "400.00"
        },
        {
          "hotel_id": "H07",
          "hotel_name": "Hotel Brasília Tower",
          "room_nights": 2,
          "total_brl": "600.00"
        }
      ]
    }
    
    
    FILE: integridade.json
    {
      "algorithm": "SHA-256",
      "files_before": 31,
      "files_after": 31,
      "modified": [],
      "added": [],
      "removed": [],
      "identical": true
    }
    
    ✓ • 46ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        root=Path('/Users/joaovictordesousalima/Downloads/onfly-desafio')
        paths=['src/onfly_report/cli.py','src/onfly_report/repositories/csv_reservation_repository.py','src/onfly_report/repositories/csv_rate_repository.py','src/onfly_report/services/row_parser.py','src/onfly_report/services/status_policy.py','src/onfly_report/services/stay_calculator.py','src/onfly_report/services/currency_converter.py','src/onfly_report/services/report_builder.py']
        for name in paths:
            print('\nFILE:',name)
            for n,line in enumerate((root/name).read_text().splitlines(),1):
                print(f'{n}: {line}')
        PY
    
    FILE: src/onfly_report/cli.py
    1: """Interface de linha de comando do consolidador."""
    2:
    3: from __future__ import annotations
    4:
    5: import argparse
    6: import json
    7: import logging
    8: from pathlib import Path
    9:
    10: from .exceptions import InputFileError
    11: from .logging_config import configure_logging
    12: from .repositories.csv_rate_repository import CsvRateRepository
    13: from .repositories.csv_reservation_repository import CsvReservationRepository
    14: from .services.report_builder import ReportBuilder
    15:
    16: logger = logging.getLogger("onfly_report")
    17:
    18:
    19: def build_parser() -> argparse.ArgumentParser:
    20:     parser = argparse.ArgumentParser(
    21:         prog="onfly_report",
    22:         description="Consolida a exportação de reservas de hotel em um relatório JSON.",
    23:     )
    24:     parser.add_argument("--input", required=True, help="CSV de reservas")
    25:     parser.add_argument("--rates", required=True, help="CSV de taxas de câmbio para BRL")
    26:     parser.add_argument("--output", default="output/report.json", help="caminho do relatório JSON")
    27:     parser.add_argument("--top", type=int, default=5, help="quantidade de hotéis no ranking")
    28:     return parser
    29:
    30:
    31: def main(argv: list[str] | None = None) -> int:
    32:     configure_logging()
    33:     parser = build_parser()
    34:     args = parser.parse_args(argv)
    35:
    36:     if args.top < 1:
    37:         parser.error("--top deve ser maior ou igual a 1")
    38:
    39:     try:
    40:         report = ReportBuilder(
    41:             reservation_repository=CsvReservationRepository(Path(args.input)),
    42:             rate_repository=CsvRateRepository(Path(args.rates)),
    43:             top_n=args.top,
    44:         ).build()
    45:     except InputFileError as err:
    46:         logger.error("falha ao ler a entrada: %s", err)
    47:         return 2
    48:     except Exception:
    49:         logger.exception("erro inesperado ao gerar o relatório")
    50:         return 1
    51:
    52:     output_path = Path(args.output)
    53:     try:
    54:         output_path.parent.mkdir(parents=True, exist_ok=True)
    55:         output_path.write_text(
    56:             json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    57:             encoding="utf-8",
    58:         )
    59:     except OSError:
    60:         logger.exception("falha ao escrever o relatório em %s", output_path)
    61:         return 1
    62:
    63:     summary = report["summary"]
    64:     print(
    65:         "Reservas: {total} | Confirmadas: {confirmed} | Noites: {nights} | Total BRL: {amount}".format(
    66:             total=summary["total_reservations"],
    67:             confirmed=summary["confirmed_reservations"],
    68:             nights=summary["total_room_nights"],
    69:             amount=summary["total_amount_brl"],
    70:         )
    71:     )
    72:     return 0
    73:
    74:
    75: if __name__ == "__main__":
    76:     raise SystemExit(main())
    
    FILE: src/onfly_report/repositories/csv_reservation_repository.py
    1: """Leitura da exportação de reservas em CSV."""
    2:
    3: from __future__ import annotations
    4:
    5: import csv
    6: from pathlib import Path
    7:
    8: from ..exceptions import InputFileError
    9: from ..models import RawRow
    10:
    11: REQUIRED_COLUMNS = (
    12:     "reservation_id",
    13:     "traveler_name",
    14:     "company_id",
    15:     "hotel_id",
    16:     "hotel_name",
    17:     "city",
    18:     "country",
    19:     "checkin_date",
    20:     "checkout_date",
    21:     "rooms",
    22:     "status",
    23:     "currency",
    24:     "amount",
    25:     "payment_method",
    26:     "booked_at",
    27: )
    28:
    29:
    30: class CsvReservationRepository:
    31:     """Lê a exportação de reservas sem aplicar regra de negócio."""
    32:
    33:     def __init__(self, path: Path) -> None:
    34:         self._path = path
    35:
    36:     def read(self) -> list[RawRow]:
    37:         try:
    38:             with self._path.open("r", encoding="utf-8", newline="") as handle:
    39:                 reader = csv.DictReader(handle)
    40:                 missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
    41:                 if missing:
    42:                     raise InputFileError(f"colunas obrigatórias ausentes: {', '.join(missing)}")
    43:
    44:                 rows: list[RawRow] = []
    45:                 for values in reader:
    46:                     rows.append(RawRow(line_number=reader.line_num, values=values))
    47:                     if len(rows) == 200:
    48:                         break
    49:                 return rows
    50:         except FileNotFoundError as err:
    51:             raise InputFileError(f"arquivo de reservas não encontrado: {self._path}") from err
    52:         except (OSError, csv.Error) as err:
    53:             raise InputFileError(f"falha ao ler {self._path}: {err}") from err
    
    FILE: src/onfly_report/repositories/csv_rate_repository.py
    1: """Leitura da tabela de câmbio para BRL."""
    2:
    3: from __future__ import annotations
    4:
    5: import csv
    6: from decimal import Decimal, InvalidOperation
    7: from pathlib import Path
    8:
    9: from ..exceptions import InputFileError
    10:
    11: REQUIRED_COLUMNS = ("currency", "rate_to_brl")
    12:
    13:
    14: class CsvRateRepository:
    15:     """Carrega moeda -> taxa para BRL a partir de um CSV."""
    16:
    17:     def __init__(self, path: Path) -> None:
    18:         self._path = path
    19:
    20:     def read(self) -> dict[str, Decimal]:
    21:         rates: dict[str, Decimal] = {}
    22:         try:
    23:             with self._path.open("r", encoding="utf-8", newline="") as handle:
    24:                 reader = csv.DictReader(handle)
    25:                 missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
    26:                 if missing:
    27:                     raise InputFileError(f"colunas obrigatórias ausentes em {self._path}: {', '.join(missing)}")
    28:
    29:                 for values in reader:
    30:                     currency = (values.get("currency") or "").strip().upper()
    31:                     raw_rate = (values.get("rate_to_brl") or "").strip()
    32:                     if not currency or not raw_rate:
    33:                         raise InputFileError(f"linha de câmbio incompleta em {self._path}")
    34:                     try:
    35:                         rate = Decimal(raw_rate)
    36:                     except InvalidOperation as err:
    37:                         raise InputFileError(f"taxa inválida para {currency} em {self._path}") from err
    38:                     if rate <= 0:
    39:                         raise InputFileError(f"taxa não positiva para {currency} em {self._path}")
    40:                     rates[currency] = rate
    41:         except FileNotFoundError as err:
    42:             raise InputFileError(f"tabela de câmbio não encontrada: {self._path}") from err
    43:         except (OSError, csv.Error) as err:
    44:             raise InputFileError(f"falha ao ler {self._path}: {err}") from err
    45:
    46:         if not rates:
    47:             raise InputFileError(f"tabela de câmbio vazia: {self._path}")
    48:         return rates
    
    FILE: src/onfly_report/services/row_parser.py
    1: """Conversão de uma linha do CSV para o modelo de reserva."""
    2:
    3: from __future__ import annotations
    4:
    5: from datetime import date
    6: from decimal import Decimal, InvalidOperation
    7:
    8: from ..exceptions import InputFileError
    9: from ..models import RawRow, Reservation
    10:
    11:
    12: class RowParser:
    13:     """Converte a linha crua em Reservation.
    14:
    15:     O arquivo de entrada é consistente; falhas de formato são erro de arquivo, não dado a
    16:     ser descartado.
    17:     """
    18:
    19:     def parse(self, raw: RawRow) -> Reservation:
    20:         values = raw.values
    21:         try:
    22:             return Reservation(
    23:                 reservation_id=(values.get("reservation_id") or "").strip(),
    24:                 traveler_name=(values.get("traveler_name") or "").strip(),
    25:                 company_id=(values.get("company_id") or "").strip(),
    26:                 hotel_id=(values.get("hotel_id") or "").strip(),
    27:                 hotel_name=(values.get("hotel_name") or "").strip(),
    28:                 city=(values.get("city") or "").strip(),
    29:                 country=(values.get("country") or "").strip(),
    30:                 checkin=date.fromisoformat((values.get("checkin_date") or "").strip()),
    31:                 checkout=date.fromisoformat((values.get("checkout_date") or "").strip()),
    32:                 rooms=int((values.get("rooms") or "").strip()),
    33:                 status=(values.get("status") or "").strip(),
    34:                 currency=(values.get("currency") or "").strip(),
    35:                 amount=Decimal((values.get("amount") or "").strip()),
    36:                 payment_method=(values.get("payment_method") or "").strip(),
    37:                 line_number=raw.line_number,
    38:             )
    39:         except (ValueError, InvalidOperation) as err:
    40:             raise InputFileError(f"linha {raw.line_number} inválida: {err}") from err
    
    FILE: src/onfly_report/services/status_policy.py
    1: """Política de status das reservas."""
    2:
    3: from __future__ import annotations
    4:
    5:
    6: def is_billable(status: str) -> bool:
    7:     """Indica se a reserva entra nos totais financeiros e de noites."""
    8:     return status != "CANCELLED"
    
    FILE: src/onfly_report/services/stay_calculator.py
    1: """Cálculo de noites ocupadas."""
    2:
    3: from __future__ import annotations
    4:
    5: from datetime import date
    6:
    7:
    8: def calculate_room_nights(checkin: date, checkout: date, rooms: int) -> int:
    9:     """Calcula noites de quarto: diferença de dias (não inclusiva) vezes quartos."""
    10:     return (checkout.day - checkin.day) * rooms
    
    FILE: src/onfly_report/services/currency_converter.py
    1: """Conversão de valores para BRL."""
    2:
    3: from __future__ import annotations
    4:
    5: from decimal import Decimal
    6:
    7:
    8: def convert_to_brl(amount: Decimal, currency: str, rates: dict[str, Decimal]) -> Decimal:
    9:     """Converte um valor na moeda informada para BRL usando a taxa da tabela."""
    10:     rate = rates[currency]
    11:     return Decimal(str(float(amount) / float(rate)))
    
    FILE: src/onfly_report/services/report_builder.py
    1: """Construção do relatório consolidado."""
    2:
    3: from __future__ import annotations
    4:
    5: from collections import defaultdict
    6: from datetime import datetime, timedelta, timezone
    7: from decimal import ROUND_HALF_UP, Decimal
    8:
    9: from ..repositories.csv_rate_repository import CsvRateRepository
    10: from ..repositories.csv_reservation_repository import CsvReservationRepository
    11: from .currency_converter import convert_to_brl
    12: from .row_parser import RowParser
    13: from .status_policy import is_billable
    14: from .stay_calculator import calculate_room_nights
    15:
    16: MONEY_QUANTUM = Decimal("0.01")
    17: FIXED_OFFSET = timezone(timedelta(hours=-3))
    18:
    19:
    20: def format_money(value: Decimal) -> str:
    21:     """Serializa dinheiro com duas casas, arredondamento half-up."""
    22:     return str(value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP))
    23:
    24:
    25: class ReportBuilder:
    26:     """Orquestra leitura, conversão e agregação."""
    27:
    28:     def __init__(
    29:         self,
    30:         reservation_repository: CsvReservationRepository,
    31:         rate_repository: CsvRateRepository,
    32:         top_n: int = 5,
    33:         now: datetime | None = None,
    34:     ) -> None:
    35:         self._reservation_repository = reservation_repository
    36:         self._rate_repository = rate_repository
    37:         self._top_n = top_n
    38:         self._now = now
    39:
    40:     def build(self) -> dict:
    41:         parser = RowParser()
    42:         reservations = [parser.parse(raw) for raw in self._reservation_repository.read()]
    43:         rates = self._rate_repository.read()
    44:
    45:         status_counts = {"CONFIRMED": 0, "CANCELLED": 0, "NO_SHOW": 0}
    46:         for reservation in reservations:
    47:             status_counts[reservation.status] = status_counts.get(reservation.status, 0) + 1
    48:
    49:         confirmed = [row for row in reservations if is_billable(row.status)]
    50:
    51:         monthly: dict[str, dict] = defaultdict(
    52:             lambda: {"reservations": 0, "room_nights": 0, "amount": Decimal("0")}
    53:         )
    54:         hotels: dict[str, dict] = defaultdict(
    55:             lambda: {"hotel_name": "", "room_nights": 0, "amount": Decimal("0")}
    56:         )
    57:
    58:         total_nights = 0
    59:         total_amount = Decimal("0")
    60:
    61:         for row in confirmed:
    62:             room_nights = calculate_room_nights(row.checkin, row.checkout, row.rooms)
    63:             amount_brl = convert_to_brl(row.amount, row.currency, rates)
    64:
    65:             total_nights += room_nights
    66:             total_amount += amount_brl
    67:
    68:             month_key = row.checkin.strftime("%Y-%m")
    69:             monthly[month_key]["reservations"] += 1
    70:             monthly[month_key]["room_nights"] += room_nights
    71:             monthly[month_key]["amount"] += amount_brl
    72:
    73:             hotels[row.hotel_id]["hotel_name"] = row.hotel_name
    74:             hotels[row.hotel_id]["room_nights"] += room_nights
    75:             hotels[row.hotel_id]["amount"] += amount_brl
    76:
    77:         average_nightly_rate = (
    78:             total_amount / Decimal(total_nights) if total_nights > 0 else Decimal("0")
    79:         )
    80:
    81:         by_month = [
    82:             {
    83:                 "month": month,
    84:                 "reservations": data["reservations"],
    85:                 "room_nights": data["room_nights"],
    86:                 "total_brl": format_money(data["amount"]),
    87:             }
    88:             for month, data in sorted(monthly.items())
    89:         ]
    90:
    91:         ranked_hotels = sorted(hotels.items(), key=lambda item: (item[1]["amount"], item[0]))
    92:         top_hotels = [
    93:             {
    94:                 "hotel_id": hotel_id,
    95:                 "hotel_name": data["hotel_name"],
    96:                 "room_nights": data["room_nights"],
    97:                 "total_brl": format_money(data["amount"]),
    98:             }
    99:             for hotel_id, data in ranked_hotels[: self._top_n]
    100:         ]
    101:
    102:         now = self._now or datetime.now(FIXED_OFFSET)
    103:
    104:         return {
    105:             "report_version": "1.0",
    106:             "generated_at": now.isoformat(timespec="seconds"),
    107:             "summary": {
    108:                 "total_reservations": len(reservations),
    109:                 "confirmed_reservations": status_counts.get("CONFIRMED", 0),
    110:                 "cancelled_reservations": status_counts.get("CANCELLED", 0),
    111:                 "no_show_reservations": status_counts.get("NO_SHOW", 0),
    112:                 "total_room_nights": total_nights,
    113:                 "total_amount_brl": format_money(total_amount),
    114:                 "average_nightly_rate_brl": format_money(average_nightly_rate),
    115:             },
    116:             "by_month": by_month,
    117:             "top_hotels": top_hotels,
    118:         }
    ✓ • 47ms

## Assistant

O fluxo está em [ReportBuilder.build()](/Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/report_builder.py:40):

`CSV → RawRow → Reservation → contagem de status → filtro faturável → noites e câmbio → agregação → ordenação → formatação → JSON`

Há **seis defeitos em cinco pontos do código**. Abaixo, separo os resultados observados das conclusões obtidas por leitura. Nenhum arquivo foi alterado nesta etapa.

1. **Leitura do CSV interrompida em 200 reservas**

   **Regra:** o [README](/Users/joaovictordesousalima/Downloads/onfly-desafio/README.md:81) define `total_reservations` como o número de reservas no arquivo, sem limite fixo.

   **Trecho responsável — [csv_reservation_repository.py](/Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/repositories/csv_reservation_repository.py:45):**

   ```python
   for values in reader:
       rows.append(RawRow(line_number=reader.line_num, values=values))
       if len(rows) == 200:
           break
   ```

   **Causa raiz:** uma condição fixa encerra a leitura antes do fim do arquivo.

   **Efeito:** as últimas 100 reservas do arquivo principal nunca chegam ao parser. Contagens, noites, valores, meses e hotéis passam a considerar apenas parte dos dados. Trocar o limite por 300 continuaria contrariando a regra para arquivos maiores.

   **Evidência:** identificado pela leitura e observado na execução exploratória anterior do `ReportBuilder`, que retornou 200 reservas para o arquivo principal. **Os cinco testes e a execução preservada da amostra de 12 reservas não exercitam esse corte.**

2. **Filtro inclui `NO_SHOW` como faturável**

   **Regra:** pelo [README](/Users/joaovictordesousalima/Downloads/onfly-desafio/README.md:60), somente `CONFIRMED` participa de noites, valores, meses e ranking. Todos os status continuam nas contagens.

   **Trecho responsável — [status_policy.py](/Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/status_policy.py:6):**

   ```python
   def is_billable(status: str) -> bool:
       return status != "CANCELLED"
   ```

   **Causa raiz:** o filtro exclui um status específico, permitindo a entrada de `NO_SHOW`.

   **Efeito:** a lista chamada `confirmed` contém reservas não faturáveis. Suas noites e valores contaminam todas as agregações. As contagens por status permanecem corretas para as linhas carregadas, pois são feitas antes desse filtro.

   **Comprovado por execução:** o teste de status gerou `120.00`, contra `100.00`. Na amostra, janeiro apresentou **9 reservas faturáveis em vez de 8**, e H05, cuja reserva é `NO_SHOW`, apareceu no ranking.

3. **Noites calculadas pelos dias do mês**

   **Regra:** o [README](/Users/joaovictordesousalima/Downloads/onfly-desafio/README.md:64) exige `(checkout_date - checkin_date).days * rooms`, inclusive nas viradas de mês e ano.

   **Trecho responsável — [stay_calculator.py](/Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/stay_calculator.py:8):**

   ```python
   return (checkout.day - checkin.day) * rooms
   ```

   **Causa raiz:** a operação descarta mês e ano, embora o parser já tenha convertido corretamente as datas para `date`.

   **Efeito:** uma estadia de 30/01 a 02/02 vira `2 - 30 = -28`, em vez de 3 noites. Isso afeta o resumo, os meses, os hotéis e o denominador da média.

   **Comprovado por execução:** o teste retornou **-28**, contra 3. A amostra apresentou **-33 noites**, contra 28.

4. **Conversão cambial usa divisão**

   **Regra:** o [README](/Users/joaovictordesousalima/Downloads/onfly-desafio/README.md:73) exige `amount * rate_to_brl`.

   **Trecho responsável — [currency_converter.py](/Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/currency_converter.py:8):**

   ```python
   rate = rates[currency]
   return Decimal(str(float(amount) / float(rate)))
   ```

   **Causa raiz:** a operação de conversão foi invertida. A taxa representa BRL por unidade da moeda original.

   **Efeito:** valores em USD e EUR são subestimados, afetando totais, média e posições no ranking.

   **Comprovado por execução:** o teste de câmbio retornou **118.45**, contra `642.00`. Na amostra, H02 apresentou **36.90**, contra `1084.00`, e H09 apresentou **25.51**, contra `882.00`.

5. **Dinheiro passa por `float`**

   **Regra:** o [README](/Users/joaovictordesousalima/Downloads/onfly-desafio/README.md:91) determina `Decimal`, sem `float`, com soma exata e arredondamento somente na serialização.

   **Trecho responsável:** as chamadas `float(amount)` e `float(rate)` no mesmo conversor acima.

   **Causa raiz:** valores originalmente lidos como `Decimal` passam para representação binária aproximada. Reconverter o resultado com `Decimal(str(...))` não recupera a exatidão perdida.

   **Efeito:** pode introduzir diferenças de centavos em somas e arredondamentos, mesmo depois de corrigida a operação cambial.

   **Identificado pela leitura:** a violação é explícita no código. **As execuções realizadas não isolam uma divergência causada exclusivamente por `float`**, pois o erro de divisão ocorre na mesma expressão.

6. **Ranking ordenado por valor crescente**

   **Regra:** o [README](/Users/joaovictordesousalima/Downloads/onfly-desafio/README.md:99) exige total decrescente, com desempate por `hotel_id` crescente.

   **Trecho responsável — [report_builder.py](/Users/joaovictordesousalima/Downloads/onfly-desafio/src/onfly_report/services/report_builder.py:91):**

   ```python
   ranked_hotels = sorted(
       hotels.items(),
       key=lambda item: (item[1]["amount"], item[0])
   )
   ```

   **Causa raiz:** `sorted` usa ordem crescente para ambos os componentes. O desempate está na direção exigida; o valor principal está invertido.

   **Efeito:** o recorte `[:self._top_n]` seleciona os hotéis de menor faturamento.

   **Comprovado por execução:** o teste retornou **H04, H03, H02**, contra H01, H02, H03. Na amostra, o primeiro hotel foi H09 com `25.51`, enquanto o esperado era H01 com `1200.00`.

Depois desses pontos, a agregação apenas propaga os resultados recebidos. A média usa `total_amount / total_nights` quando há noites positivas; como a amostra chega com noites negativas, o código produz `0.00`. **Esse zero é uma consequência do cálculo de noites**, não uma causa independente identificada.

A formatação usa `quantize(..., ROUND_HALF_UP)` ao montar a saída, e o CLI grava esse conteúdo com `json.dumps`. Na execução da amostra, foram observados dinheiro como string com duas casas, `report_version: "1.0"` e offset `-03:00`. O JSON foi gravado e o CLI retornou `0`, mesmo com os valores de negócio incorretos.

As evidências de execução permanecem no [registro da investigação](/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-baseline-20261115T222717Z/INVESTIGACAO.md): **cinco testes falhando e a comparação completa da amostra com o README**.

## User

Fiz o commit e push do projeto inicial, em ~/Downloads/onfly-desafio. Faremos todas as correções por la. Corrija primeiro a leitura incompleta das reservas e a seleção dos status faturáveis. O arquivo inteiro deve ser processado; todos os status devem ser contados, mas somente CONFIRMED pode alimentar noites, valores, meses e ranking. Faça alterações pequenas, preserve os testes fornecidos e execute a validação relevante. Mostre o diff e explique por que cada mudança resolve a causa.

## Assistant

Vou conferir o estado do repositório em `~/Downloads/onfly-desafio`, remover o corte de leitura e restringir o faturamento a `CONFIRMED`. Vou preservar os testes fornecidos e validar a leitura completa e o efeito dos status no relatório, considerando que câmbio, noites e ordenação ainda têm correções pendentes.

## Activity

    $ git status --short
    ✓ • 0ms

## Activity

    $ rg --files --hidden -g '!.git/**' -g '!.venv/**' -g '!__pycache__/**' -g '!*.pyc' -g 'AGENTS.md' -g '*test*' -g 'pyproject.toml' /Users/joaovictordesousalima/Downloads/onfly-desafio
    /Users/joaovictordesousalima/Downloads/onfly-desafio/pyproject.toml
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_currency.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_status_rules.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_top_hotels.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_nights.py
    /Users/joaovictordesousalima/Downloads/onfly-desafio/tests/test_regression_report.py
    ✓ • 0ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        r=Path('/Users/joaovictordesousalima/Downloads/onfly-desafio')
        for name in ['AGENTS.md','src/onfly_report/repositories/csv_reservation_repository.py','src/onfly_report/services/status_policy.py','tests/test_status_rules.py','tests/helpers.py','pyproject.toml']:
            p=r/name
            if p.exists():
                print('\nFILE:',name)
                print(p.read_text())
        for p in [r.parent/'AGENTS.md',r.parent.parent/'AGENTS.md']:
            if p.exists():
                print('\nFILE:',p)
                print(p.read_text())
        PY
    
    FILE: src/onfly_report/repositories/csv_reservation_repository.py
    """Leitura da exportação de reservas em CSV."""
    
    from __future__ import annotations
    
    import csv
    from pathlib import Path
    
    from ..exceptions import InputFileError
    from ..models import RawRow
    
    REQUIRED_COLUMNS = (
        "reservation_id",
        "traveler_name",
        "company_id",
        "hotel_id",
        "hotel_name",
        "city",
        "country",
        "checkin_date",
        "checkout_date",
        "rooms",
        "status",
        "currency",
        "amount",
        "payment_method",
        "booked_at",
    )
    
    
    class CsvReservationRepository:
        """Lê a exportação de reservas sem aplicar regra de negócio."""
    
        def __init__(self, path: Path) -> None:
            self._path = path
    
        def read(self) -> list[RawRow]:
            try:
                with self._path.open("r", encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle)
                    missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
                    if missing:
                        raise InputFileError(f"colunas obrigatórias ausentes: {', '.join(missing)}")
    
                    rows: list[RawRow] = []
                    for values in reader:
                        rows.append(RawRow(line_number=reader.line_num, values=values))
                        if len(rows) == 200:
                            break
                    return rows
            except FileNotFoundError as err:
                raise InputFileError(f"arquivo de reservas não encontrado: {self._path}") from err
            except (OSError, csv.Error) as err:
                raise InputFileError(f"falha ao ler {self._path}: {err}") from err
    
    
    FILE: src/onfly_report/services/status_policy.py
    """Política de status das reservas."""
    
    from __future__ import annotations
    
    
    def is_billable(status: str) -> bool:
        """Indica se a reserva entra nos totais financeiros e de noites."""
        return status != "CANCELLED"
    
    
    FILE: tests/test_status_rules.py
    """Testes fornecidos: regras de status."""
    
    from helpers import run_cli
    
    
    def test_status_rules_exclude_cancelled_and_no_show(tmp_path):
        """Somente CONFIRMED entra nos totais financeiros."""
        report = run_cli(
            tmp_path,
            [
                {"reservation_id": "R-1", "status": "CONFIRMED", "amount": "100.00"},
                {"reservation_id": "R-2", "status": "CANCELLED", "amount": "50.00"},
                {"reservation_id": "R-3", "status": "NO_SHOW", "amount": "20.00"},
            ],
        )
        assert report["summary"]["total_reservations"] == 3
        assert report["summary"]["confirmed_reservations"] == 1
        assert report["summary"]["cancelled_reservations"] == 1
        assert report["summary"]["no_show_reservations"] == 1
        assert report["summary"]["total_amount_brl"] == "100.00"
        assert report["summary"]["total_room_nights"] == 1
    
    
    FILE: tests/helpers.py
    """Utilitários dos testes fornecidos."""
    
    from __future__ import annotations
    
    import csv
    import json
    import os
    import subprocess
    import sys
    from pathlib import Path
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    SRC_DIR = PROJECT_ROOT / "src"
    
    COLUMNS = [
        "reservation_id",
        "traveler_name",
        "company_id",
        "hotel_id",
        "hotel_name",
        "city",
        "country",
        "checkin_date",
        "checkout_date",
        "rooms",
        "status",
        "currency",
        "amount",
        "payment_method",
        "booked_at",
    ]
    
    BASE = {
        "reservation_id": "R-1",
        "traveler_name": "Pessoa Teste",
        "company_id": "EMP-001",
        "hotel_id": "H01",
        "hotel_name": "Hotel Teste",
        "city": "Sao Paulo",
        "country": "BR",
        "checkin_date": "2025-01-10",
        "checkout_date": "2025-01-11",
        "rooms": "1",
        "status": "CONFIRMED",
        "currency": "BRL",
        "amount": "100.00",
        "payment_method": "CORPORATE_CARD",
        "booked_at": "2025-01-01T10:00:00-03:00",
    }
    
    
    def run_cli(tmp_path: Path, rows: list[dict[str, str]], top: int = 5) -> dict:
        """Executa o CLI sobre um CSV temporário e devolve o relatório."""
        input_path = tmp_path / "reservas.csv"
        rates_path = tmp_path / "rates.csv"
        output_path = tmp_path / "report.json"
    
        with input_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows({**BASE, **row} for row in rows)
    
        rates_path.write_text(
            "currency,rate_to_brl\nBRL,1.000000\nUSD,5.420000\nEUR,5.880000\n",
            encoding="utf-8",
        )
    
        environment = os.environ.copy()
        for import_root in (SRC_DIR, PROJECT_ROOT):
            if (import_root / "onfly_report").is_dir():
                environment["PYTHONPATH"] = str(import_root) + os.pathsep + environment.get("PYTHONPATH", "")
                break
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
    
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "onfly_report",
                "--input",
                str(input_path),
                "--rates",
                str(rates_path),
                "--output",
                str(output_path),
                "--top",
                str(top),
            ],
            cwd=str(PROJECT_ROOT),
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert process.returncode == 0, process.stderr
        return json.loads(output_path.read_text(encoding="utf-8"))
    
    
    FILE: pyproject.toml
    [project]
    name = "onfly-report"
    version = "1.0.0"
    description = "Consolidador de reservas de hotel da Onfly"
    requires-python = ">=3.11"
    
    [tool.ruff]
    line-length = 120
    target-version = "py311"
    src = ["src"]
    
    [tool.ruff.lint]
    select = ["E", "F", "I"]
    
    [tool.pytest.ini_options]
    testpaths = ["tests"]
    pythonpath = ["src"]
    addopts = "-ra"
    
    ✓ • 55ms

## Assistant

A edição em `~/Downloads/onfly-desafio` foi rejeitada pelo controle de permissões: esta sessão só permite escrita na pasta de trabalho atual e em diretórios temporários. Vou preparar e validar o patch em uma cópia temporária, para deixá-lo revisável. A aplicação no repositório original ficará pendente até essa pasta ser aberta como área de trabalho.

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        from datetime import datetime, timezone
        import hashlib, json, shutil, subprocess, tempfile
        source=Path('/Users/joaovictordesousalima/Downloads/onfly-desafio')
        evidence=Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao')/('onfly-leitura-status-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        evidence.mkdir(parents=True)
        root=Path(tempfile.mkdtemp(prefix='onfly-leitura-status-'))
        original=root/'original'
        candidate=root/'candidate'
        shutil.copytree(source,original,ignore=shutil.ignore_patterns('.git','.venv','__pycache__','.pytest_cache'))
        shutil.copytree(original,candidate)
        manifest={str(f.relative_to(source)):hashlib.sha256(f.read_bytes()).hexdigest() for f in source.rglob('*') if f.is_file() and '.git' not in f.relative_to(source).parts}
        (evidence/'manifesto-original.json').write_text(json.dumps(manifest,indent=2)+'\n')
        state={'source':str(source),'original':str(original),'candidate':str(candidate),'evidence':str(evidence),'python':'/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/python','git_head':subprocess.run(['git','rev-parse','HEAD'],cwd=source,capture_output=True,text=True,check=True).stdout.strip(),'application_status':'Not applied: patch rejected outside writable workspace'}
        (evidence/'execucao.json').write_text(json.dumps(state,indent=2)+'\n')
        p=candidate/'src/onfly_report/repositories/csv_reservation_repository.py'
        text=p.read_text()
        old='                    if len(rows) == 200:\n                        break\n'
        assert text.count(old)==1
        p.write_text(text.replace(old,''))
        p=candidate/'src/onfly_report/services/status_policy.py'
        text=p.read_text()
        assert text.count('return status != "CANCELLED"')==1
        p.write_text(text.replace('return status != "CANCELLED"','return status == "CONFIRMED"'))
        print(json.dumps(state,indent=2))
        PY
    {
      "source": "/Users/joaovictordesousalima/Downloads/onfly-desafio",
      "original": "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-leitura-status-t6fsr3g5/original",
      "candidate": "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-leitura-status-t6fsr3g5/candidate",
      "evidence": "/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z",
      "python": "/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/python",
      "git_head": "9f8d8f733a88bbd3dc5b63a948c0f359958694b0",
      "application_status": "Not applied: patch rejected outside writable workspace"
    }
    ✓ • 138ms

## Activity

    file changes: Completed · 1 changes
    Add: /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-leitura-status-t6fsr3g5/candidate/tests/test_reading_and_billing.py
    """Regressões para leitura completa e agregação somente de confirmadas."""
    
    import pytest
    
    from helpers import run_cli
    
    
    @pytest.mark.parametrize("reservation_count", [201, 300, 303])
    def test_cli_reads_every_reservation(tmp_path, reservation_count):
        statuses = ("CONFIRMED", "CANCELLED", "NO_SHOW")
        rows = [
            {"reservation_id": f"R-{index}", "status": statuses[index % 3]}
            for index in range(reservation_count)
        ]
    
        report = run_cli(tmp_path, rows)
        per_status = reservation_count // 3
    
        assert report["summary"] == {
            "total_reservations": reservation_count,
            "confirmed_reservations": per_status,
            "cancelled_reservations": per_status,
            "no_show_reservations": per_status,
            "total_room_nights": per_status,
            "total_amount_brl": f"{per_status * 100}.00",
            "average_nightly_rate_brl": "100.00",
        }
    
    
    def test_only_confirmed_reservations_feed_all_aggregates(tmp_path):
        report = run_cli(
            tmp_path,
            [
                {
                    "reservation_id": "CONFIRMED-1",
                    "checkin_date": "2025-01-10",
                    "checkout_date": "2025-01-13",
                    "rooms": "2",
                },
                {
                    "reservation_id": "CANCELLED-1",
                    "status": "CANCELLED",
                    "hotel_id": "H02",
                    "checkin_date": "2025-02-10",
                    "checkout_date": "2025-02-13",
                    "amount": "900.00",
                },
                {
                    "reservation_id": "NO-SHOW-1",
                    "status": "NO_SHOW",
                    "hotel_id": "H03",
                    "checkin_date": "2025-03-10",
                    "checkout_date": "2025-03-13",
                    "amount": "800.00",
                },
            ],
        )
    
        assert report["summary"] == {
            "total_reservations": 3,
            "confirmed_reservations": 1,
            "cancelled_reservations": 1,
            "no_show_reservations": 1,
            "total_room_nights": 6,
            "total_amount_brl": "100.00",
            "average_nightly_rate_brl": "16.67",
        }
        assert report["by_month"] == [
            {"month": "2025-01", "reservations": 1, "room_nights": 6, "total_brl": "100.00"}
        ]
        assert report["top_hotels"] == [
            {"hotel_id": "H01", "hotel_name": "Hotel Teste", "room_nights": 6, "total_brl": "100.00"}
        ]

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import difflib, json, shutil
        p=Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z')
        s=json.loads((p/'execucao.json').read_text())
        original=Path(s['original']); candidate=Path(s['candidate'])
        baseline=original.parent/'baseline-with-regressions'
        shutil.copytree(original,baseline)
        shutil.copy2(candidate/'tests/test_reading_and_billing.py',baseline/'tests/test_reading_and_billing.py')
        s['baseline_with_regressions']=str(baseline)
        (p/'execucao.json').write_text(json.dumps(s,indent=2)+'\n')
        patch=[]
        for name in ['src/onfly_report/repositories/csv_reservation_repository.py','src/onfly_report/services/status_policy.py','tests/test_reading_and_billing.py']:
            old=original/name; new=candidate/name
            patch.extend(difflib.unified_diff(old.read_text().splitlines(keepends=True) if old.exists() else [],new.read_text().splitlines(keepends=True),fromfile='a/'+name if old.exists() else '/dev/null',tofile='b/'+name))
        (p/'correcao.patch').write_text(''.join(patch))
        print(''.join(patch))
        PY
    --- a/src/onfly_report/repositories/csv_reservation_repository.py
    +++ b/src/onfly_report/repositories/csv_reservation_repository.py
    @@ -44,8 +44,6 @@
                     rows: list[RawRow] = []
                     for values in reader:
                         rows.append(RawRow(line_number=reader.line_num, values=values))
    -                    if len(rows) == 200:
    -                        break
                     return rows
             except FileNotFoundError as err:
                 raise InputFileError(f"arquivo de reservas não encontrado: {self._path}") from err
    --- a/src/onfly_report/services/status_policy.py
    +++ b/src/onfly_report/services/status_policy.py
    @@ -5,4 +5,4 @@
    
     def is_billable(status: str) -> bool:
         """Indica se a reserva entra nos totais financeiros e de noites."""
    -    return status != "CANCELLED"
    +    return status == "CONFIRMED"
    --- /dev/null
    +++ b/tests/test_reading_and_billing.py
    @@ -0,0 +1,73 @@
    +"""Regressões para leitura completa e agregação somente de confirmadas."""
    +
    +import pytest
    +
    +from helpers import run_cli
    +
    +
    +@pytest.mark.parametrize("reservation_count", [201, 300, 303])
    +def test_cli_reads_every_reservation(tmp_path, reservation_count):
    +    statuses = ("CONFIRMED", "CANCELLED", "NO_SHOW")
    +    rows = [
    +        {"reservation_id": f"R-{index}", "status": statuses[index % 3]}
    +        for index in range(reservation_count)
    +    ]
    +
    +    report = run_cli(tmp_path, rows)
    +    per_status = reservation_count // 3
    +
    +    assert report["summary"] == {
    +        "total_reservations": reservation_count,
    +        "confirmed_reservations": per_status,
    +        "cancelled_reservations": per_status,
    +        "no_show_reservations": per_status,
    +        "total_room_nights": per_status,
    +        "total_amount_brl": f"{per_status * 100}.00",
    +        "average_nightly_rate_brl": "100.00",
    +    }
    +
    +
    +def test_only_confirmed_reservations_feed_all_aggregates(tmp_path):
    +    report = run_cli(
    +        tmp_path,
    +        [
    +            {
    +                "reservation_id": "CONFIRMED-1",
    +                "checkin_date": "2025-01-10",
    +                "checkout_date": "2025-01-13",
    +                "rooms": "2",
    +            },
    +            {
    +                "reservation_id": "CANCELLED-1",
    +                "status": "CANCELLED",
    +                "hotel_id": "H02",
    +                "checkin_date": "2025-02-10",
    +                "checkout_date": "2025-02-13",
    +                "amount": "900.00",
    +            },
    +            {
    +                "reservation_id": "NO-SHOW-1",
    +                "status": "NO_SHOW",
    +                "hotel_id": "H03",
    +                "checkin_date": "2025-03-10",
    +                "checkout_date": "2025-03-13",
    +                "amount": "800.00",
    +            },
    +        ],
    +    )
    +
    +    assert report["summary"] == {
    +        "total_reservations": 3,
    +        "confirmed_reservations": 1,
    +        "cancelled_reservations": 1,
    +        "no_show_reservations": 1,
    +        "total_room_nights": 6,
    +        "total_amount_brl": "100.00",
    +        "average_nightly_rate_brl": "16.67",
    +    }
    +    assert report["by_month"] == [
    +        {"month": "2025-01", "reservations": 1, "room_nights": 6, "total_brl": "100.00"}
    +    ]
    +    assert report["top_hotels"] == [
    +        {"hotel_id": "H01", "hotel_name": "Hotel Teste", "room_nights": 6, "total_brl": "100.00"}
    +    ]
    
    ✓ • 30ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import json, os, subprocess
        p=Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z')
        s=json.loads((p/'execucao.json').read_text())
        env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
        command=[s['python'],'-m','pytest','-q','-p','no:cacheprovider','--junitxml',str(p/'regressoes-antes.xml')]+["tests/test_reading_and_billing.py"]
        r=subprocess.run(command,cwd=s['baseline_with_regressions'],env=env,capture_output=True,text=True,timeout=120)
        (p/'regressoes-antes.log').write_text(r.stdout+r.stderr)
        (p/'regressoes-antes.execucao.json').write_text(json.dumps({'command':command,'cwd':s['baseline_with_regressions'],'exit_code':r.returncode},indent=2)+'\n')
        print('exit_code:',r.returncode)
        print(r.stdout+r.stderr)
        PY
    exit_code: 1
    FFFF                                                                     [100%]
    =================================== FAILURES ===================================
    ____________________ test_cli_reads_every_reservation[201] _____________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/pytest-of-joaovictordesousalima/pytest-0/test_cli_reads_every_reservati0')
    reservation_count = 201
    
        @pytest.mark.parametrize("reservation_count", [201, 300, 303])
        def test_cli_reads_every_reservation(tmp_path, reservation_count):
            statuses = ("CONFIRMED", "CANCELLED", "NO_SHOW")
            rows = [
                {"reservation_id": f"R-{index}", "status": statuses[index % 3]}
                for index in range(reservation_count)
            ]
    
            report = run_cli(tmp_path, rows)
            per_status = reservation_count // 3
    
    >       assert report["summary"] == {
                "total_reservations": reservation_count,
                "confirmed_reservations": per_status,
                "cancelled_reservations": per_status,
                "no_show_reservations": per_status,
                "total_room_nights": per_status,
                "total_amount_brl": f"{per_status * 100}.00",
                "average_nightly_rate_brl": "100.00",
            }
    E       AssertionError: assert {'average_nig...ons': 66, ...} == {'average_nig...ons': 67, ...}
    E
    E         Omitting 3 identical items, use -vv to show
    E         Differing items:
    E         {'total_amount_brl': '13300.00'} != {'total_amount_brl': '6700.00'}
    E         {'total_reservations': 200} != {'total_reservations': 201}
    E         {'no_show_reservations': 66} != {'no_show_reservations': 67}
    E         {'total_room_nights': 133} != {'total_room_nights': 67}
    E         Use -v to get more diff
    
    tests/test_reading_and_billing.py:19: AssertionError
    ____________________ test_cli_reads_every_reservation[300] _____________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/pytest-of-joaovictordesousalima/pytest-0/test_cli_reads_every_reservati1')
    reservation_count = 300
    
        @pytest.mark.parametrize("reservation_count", [201, 300, 303])
        def test_cli_reads_every_reservation(tmp_path, reservation_count):
            statuses = ("CONFIRMED", "CANCELLED", "NO_SHOW")
            rows = [
                {"reservation_id": f"R-{index}", "status": statuses[index % 3]}
                for index in range(reservation_count)
            ]
    
            report = run_cli(tmp_path, rows)
            per_status = reservation_count // 3
    
    >       assert report["summary"] == {
                "total_reservations": reservation_count,
                "confirmed_reservations": per_status,
                "cancelled_reservations": per_status,
                "no_show_reservations": per_status,
                "total_room_nights": per_status,
                "total_amount_brl": f"{per_status * 100}.00",
                "average_nightly_rate_brl": "100.00",
            }
    E       AssertionError: assert {'average_nig...ons': 66, ...} == {'average_nig...ns': 100, ...}
    E
    E         Omitting 1 identical items, use -vv to show
    E         Differing items:
    E         {'total_amount_brl': '13300.00'} != {'total_amount_brl': '10000.00'}
    E         {'cancelled_reservations': 67} != {'cancelled_reservations': 100}
    E         {'total_room_nights': 133} != {'total_room_nights': 100}
    E         {'confirmed_reservations': 67} != {'confirmed_reservations': 100}...
    E
    E         ...Full output truncated (3 lines hidden), use '-vv' to show
    
    tests/test_reading_and_billing.py:19: AssertionError
    ____________________ test_cli_reads_every_reservation[303] _____________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/pytest-of-joaovictordesousalima/pytest-0/test_cli_reads_every_reservati2')
    reservation_count = 303
    
        @pytest.mark.parametrize("reservation_count", [201, 300, 303])
        def test_cli_reads_every_reservation(tmp_path, reservation_count):
            statuses = ("CONFIRMED", "CANCELLED", "NO_SHOW")
            rows = [
                {"reservation_id": f"R-{index}", "status": statuses[index % 3]}
                for index in range(reservation_count)
            ]
    
            report = run_cli(tmp_path, rows)
            per_status = reservation_count // 3
    
    >       assert report["summary"] == {
                "total_reservations": reservation_count,
                "confirmed_reservations": per_status,
                "cancelled_reservations": per_status,
                "no_show_reservations": per_status,
                "total_room_nights": per_status,
                "total_amount_brl": f"{per_status * 100}.00",
                "average_nightly_rate_brl": "100.00",
            }
    E       AssertionError: assert {'average_nig...ons': 66, ...} == {'average_nig...ns': 101, ...}
    E
    E         Omitting 1 identical items, use -vv to show
    E         Differing items:
    E         {'total_amount_brl': '13300.00'} != {'total_amount_brl': '10100.00'}
    E         {'cancelled_reservations': 67} != {'cancelled_reservations': 101}
    E         {'total_room_nights': 133} != {'total_room_nights': 101}
    E         {'confirmed_reservations': 67} != {'confirmed_reservations': 101}...
    E
    E         ...Full output truncated (3 lines hidden), use '-vv' to show
    
    tests/test_reading_and_billing.py:19: AssertionError
    _____________ test_only_confirmed_reservations_feed_all_aggregates _____________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/pytest-of-joaovictordesousalima/pytest-0/test_only_confirmed_reservatio0')
    
        def test_only_confirmed_reservations_feed_all_aggregates(tmp_path):
            report = run_cli(
                tmp_path,
                [
                    {
                        "reservation_id": "CONFIRMED-1",
                        "checkin_date": "2025-01-10",
                        "checkout_date": "2025-01-13",
                        "rooms": "2",
                    },
                    {
                        "reservation_id": "CANCELLED-1",
                        "status": "CANCELLED",
                        "hotel_id": "H02",
                        "checkin_date": "2025-02-10",
                        "checkout_date": "2025-02-13",
                        "amount": "900.00",
                    },
                    {
                        "reservation_id": "NO-SHOW-1",
                        "status": "NO_SHOW",
                        "hotel_id": "H03",
                        "checkin_date": "2025-03-10",
                        "checkout_date": "2025-03-13",
                        "amount": "800.00",
                    },
                ],
            )
    
    >       assert report["summary"] == {
                "total_reservations": 3,
                "confirmed_reservations": 1,
                "cancelled_reservations": 1,
                "no_show_reservations": 1,
                "total_room_nights": 6,
                "total_amount_brl": "100.00",
                "average_nightly_rate_brl": "16.67",
            }
    E       AssertionError: assert {'average_nig...ions': 1, ...} == {'average_nig...ions': 1, ...}
    E
    E         Omitting 4 identical items, use -vv to show
    E         Differing items:
    E         {'average_nightly_rate_brl': '100.00'} != {'average_nightly_rate_brl': '16.67'}
    E         {'total_amount_brl': '900.00'} != {'total_amount_brl': '100.00'}
    E         {'total_room_nights': 9} != {'total_room_nights': 6}
    E         Use -v to get more diff
    
    tests/test_reading_and_billing.py:59: AssertionError
    - generated xml file: /Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z/regressoes-antes.xml -
    =========================== short test summary info ============================
    FAILED tests/test_reading_and_billing.py::test_cli_reads_every_reservation[201]
    FAILED tests/test_reading_and_billing.py::test_cli_reads_every_reservation[300]
    FAILED tests/test_reading_and_billing.py::test_cli_reads_every_reservation[303]
    FAILED tests/test_reading_and_billing.py::test_only_confirmed_reservations_feed_all_aggregates
    4 failed in 0.81s
    
    ✓ • 1.25s

## Activity

    $ /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/ruff check --no-cache tests/test_reading_and_billing.py
    tests/test_reading_and_billing.py:3:1: I001 [*] Import block is un-sorted or un-formatted
       |
     1 |   """Regressões para leitura completa e agregação somente de confirmadas."""
     2 |
     3 | / import pytest
     4 | |
     5 | | from helpers import run_cli
     6 | |
     7 | |
     8 | | @pytest.mark.parametrize("reservation_count", [201, 300, 303])
       | |_^ I001
     9 |   def test_cli_reads_every_reservation(tmp_path, reservation_count):
    10 |       statuses = ("CONFIRMED", "CANCELLED", "NO_SHOW")
       |
       = help: Organize imports
    
    Found 1 error.
    [*] 1 fixable with the `--fix` option.
    ✗ (1) • 764ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import json, os, subprocess
        p=Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z')
        s=json.loads((p/'execucao.json').read_text())
        env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
        command=[s['python'],'-m','pytest','-q','-p','no:cacheprovider','--junitxml',str(p/'suite-depois.xml')]+[]
        r=subprocess.run(command,cwd=s['candidate'],env=env,capture_output=True,text=True,timeout=120)
        (p/'suite-depois.log').write_text(r.stdout+r.stderr)
        (p/'suite-depois.execucao.json').write_text(json.dumps({'command':command,'cwd':s['candidate'],'exit_code':r.returncode},indent=2)+'\n')
        print('exit_code:',r.returncode)
        print(r.stdout+r.stderr)
        PY
    exit_code: 1
    FF....F.F                                                                [100%]
    =================================== FAILURES ===================================
    _______________________ test_currency_conversion_to_brl ________________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/pytest-of-joaovictordesousalima/pytest-1/test_currency_conversion_to_br0')
    
        def test_currency_conversion_to_brl(tmp_path):
            """Multiplica o valor pela taxa, sem inverter a operação."""
            report = run_cli(
                tmp_path,
                [
                    {"reservation_id": "R-1", "currency": "BRL", "amount": "100.00"},
                    {"reservation_id": "R-2", "currency": "USD", "amount": "100.00"},
                ],
            )
    >       assert report["summary"]["total_amount_brl"] == "642.00"
    E       AssertionError: assert '118.45' == '642.00'
    E
    E         - 642.00
    E         + 118.45
    
    tests/test_currency.py:15: AssertionError
    ______________________ test_nights_across_month_boundary _______________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/pytest-of-joaovictordesousalima/pytest-1/test_nights_across_month_bound0')
    
        def test_nights_across_month_boundary(tmp_path):
            """A diferença de datas considera a virada de mês, não o dia do mês."""
            report = run_cli(
                tmp_path,
                [
                    {
                        "reservation_id": "R-1",
                        "checkin_date": "2025-01-30",
                        "checkout_date": "2025-02-02",
                        "rooms": "1",
                    }
                ],
            )
    >       assert report["summary"]["total_room_nights"] == 3
    E       assert -28 == 3
    
    tests/test_nights.py:19: AssertionError
    _______________________ test_regression_report_on_sample _______________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/pytest-of-joaovictordesousalima/pytest-1/test_regression_report_on_samp0')
    
        def test_regression_report_on_sample(tmp_path):
            """Relatório completo de uma amostra pequena, com status, noites e câmbio."""
            report = run_cli(
                tmp_path,
                [
                    {
                        "reservation_id": "R-1",
                        "amount": "1000.00",
                        "checkin_date": "2025-01-10",
                        "checkout_date": "2025-01-13",
                    },
                    {"reservation_id": "R-2", "status": "CANCELLED", "amount": "500.00"},
                    {
                        "reservation_id": "R-3",
                        "currency": "USD",
                        "amount": "100.00",
                        "checkin_date": "2025-01-20",
                        "checkout_date": "2025-01-22",
                    },
                ],
            )
    >       assert report["summary"] == {
                "total_reservations": 3,
                "confirmed_reservations": 2,
                "cancelled_reservations": 1,
                "no_show_reservations": 0,
                "total_room_nights": 5,
                "total_amount_brl": "1542.00",
                "average_nightly_rate_brl": "308.40",
            }
    E       AssertionError: assert {'average_nig...ions': 0, ...} == {'average_nig...ions': 0, ...}
    E
    E         Omitting 5 identical items, use -vv to show
    E         Differing items:
    E         {'average_nightly_rate_brl': '203.69'} != {'average_nightly_rate_brl': '308.40'}
    E         {'total_amount_brl': '1018.45'} != {'total_amount_brl': '1542.00'}
    E         Use -v to get more diff
    
    tests/test_regression_report.py:27: AssertionError
    ____________________ test_top_hotels_are_ranked_descending _____________________
    
    tmp_path = PosixPath('/private/var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/pytest-of-joaovictordesousalima/pytest-1/test_top_hotels_are_ranked_des0')
    
        def test_top_hotels_are_ranked_descending(tmp_path):
            """O ranking mostra os hotéis de maior valor primeiro."""
            report = run_cli(
                tmp_path,
                [
                    {"reservation_id": "R-1", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "1000.00"},
                    {"reservation_id": "R-2", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "900.00"},
                    {"reservation_id": "R-3", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "800.00"},
                    {"reservation_id": "R-4", "hotel_id": "H04", "hotel_name": "Hotel D", "amount": "700.00"},
                ],
                top=3,
            )
    >       assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]
    E       AssertionError: assert ['H04', 'H03', 'H02'] == ['H01', 'H02', 'H03']
    E
    E         At index 0 diff: 'H04' != 'H01'
    E         Use -v to get more diff
    
    tests/test_top_hotels.py:18: AssertionError
    - generated xml file: /Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z/suite-depois.xml -
    =========================== short test summary info ============================
    FAILED tests/test_currency.py::test_currency_conversion_to_brl - AssertionErr...
    FAILED tests/test_nights.py::test_nights_across_month_boundary - assert -28 == 3
    FAILED tests/test_regression_report.py::test_regression_report_on_sample - As...
    FAILED tests/test_top_hotels.py::test_top_hotels_are_ranked_descending - Asse...
    4 failed, 5 passed in 1.63s
    
    ✓ • 2.11s

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-leitura-status-t6fsr3g5/candidate/tests/test_reading_and_billing.py
    @@ -3,3 +3,2 @@
     import pytest
    -
     from helpers import run_cli

## Activity

    $ /var/folders/2b/tk8q97s15t5ct94xt5fcxvf00000gn/T/onfly-baseline-s8hn7ifh/venv/bin/ruff check --no-cache tests/test_reading_and_billing.py
    All checks passed!
    ✓ • 0ms

## Assistant

Na cópia temporária, as correções passaram pelos testes de leitura com 201, 300 e 303 reservas e pela verificação de que canceladas e `NO_SHOW` ficam fora de todas as agregações. O teste de status fornecido também passou. A suíte completa ficou com 5 aprovados e 4 falhas nos pontos ainda pendentes: câmbio, noites, regressão financeira e ordenação.

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import difflib, hashlib, json, os, subprocess
        p=Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z')
        s=json.loads((p/'execucao.json').read_text())
        candidate=Path(s['candidate']); original=Path(s['original']); source=Path(s['source'])
        env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'; env['PYTHONPATH']=str(candidate/'src')
        command=[s['python'],'-m','pytest','-q','-p','no:cacheprovider','tests/test_status_rules.py','tests/test_reading_and_billing.py']
        r=subprocess.run(command,cwd=candidate,env=env,capture_output=True,text=True,timeout=120)
        (p/'validacao-relevante.log').write_text(r.stdout+r.stderr)
        print(r.stdout+r.stderr)
        assert r.returncode==0
        for name in ['reservas_hoteis.csv','exemplo-validacao.csv']:
            output=p/(name.replace('.csv','')+'-observado.json')
            command=[s['python'],'-m','onfly_report','--input','data/'+name,'--rates','data/taxas_cambio.csv','--output',str(output)]
            r=subprocess.run(command,cwd=candidate,env=env,capture_output=True,text=True,timeout=120)
            (p/(name+'.execucao.json')).write_text(json.dumps({'command':command,'cwd':str(candidate),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n')
            assert r.returncode==0
            report=json.loads(output.read_text())
            print(name, json.dumps(report['summary']))
        main=json.loads((p/'reservas_hoteis-observado.json').read_text())['summary']
        assert {k:main[k] for k in ['total_reservations','confirmed_reservations','cancelled_reservations','no_show_reservations']}=={'total_reservations':300,'confirmed_reservations':235,'cancelled_reservations':31,'no_show_reservations':34}
        patch=[]
        for name in ['src/onfly_report/repositories/csv_reservation_repository.py','src/onfly_report/services/status_policy.py','tests/test_reading_and_billing.py']:
            old=original/name; new=candidate/name
            patch.extend(difflib.unified_diff(old.read_text().splitlines(keepends=True) if old.exists() else [],new.read_text().splitlines(keepends=True),fromfile='a/'+name if old.exists() else '/dev/null',tofile='b/'+name))
        (p/'correcao.patch').write_text(''.join(patch))
        check=subprocess.run(['git','apply','--check',str(p/'correcao.patch')],cwd=source,capture_output=True,text=True)
        (p/'patch-check.log').write_text(f'exit_code: {check.returncode}\n'+check.stdout+check.stderr)
        assert check.returncode==0,check.stderr
        before=json.loads((p/'manifesto-original.json').read_text())
        after={str(f.relative_to(source)):hashlib.sha256(f.read_bytes()).hexdigest() for f in source.rglob('*') if f.is_file() and '.git' not in f.relative_to(source).parts}
        assert before==after
        for group in ['tests','data']:
            for f in (original/group).rglob('*'):
                if f.is_file():
                    assert f.read_bytes()==(candidate/f.relative_to(original)).read_bytes(),f
        status=subprocess.run(['git','status','--short'],cwd=source,capture_output=True,text=True,check=True).stdout
        (p/'integridade.json').write_text(json.dumps({'original_unchanged':before==after,'provided_tests_unchanged':True,'data_unchanged':True,'git_status':status,'patch_applies_cleanly':check.returncode==0},indent=2)+'\n')
        report='''# Correção proposta: leitura completa e status faturável
        
        Status: patch preparado e validado em cópia temporária. Não aplicado ao repositório em Downloads: a ferramenta de edição rejeitou a escrita fora da área de trabalho permitida pela sessão.
        
        Mudanças de produção: remover o break ao atingir 200 reservas e aceitar exclusivamente status == CONFIRMED. A contagem por status no ReportBuilder já precede o filtro e não precisa ser alterada.
        
        Testes fornecidos e dados preservados byte a byte. Novo arquivo de testes com quatro casos: CSVs de 201, 300 e 303 reservas; exclusão de canceladas/NO_SHOW do resumo financeiro, noites, meses e hotéis, mantendo todas as contagens.
        
        Validação no Python 3.13.9 / pytest 8.3.4:
        - As quatro regressões adicionais falham contra o código original.
        - Testes relevantes após o patch: 5 aprovados.
        - Suíte completa após o patch: 5 aprovados e 4 falhas já existentes em câmbio, noites, regressão financeira e ordenação.
        - Ruff no novo arquivo de testes: aprovado.
        - CLI no dataset principal: 300 reservas, 235 confirmadas, 31 canceladas e 34 NO_SHOW.
        - CLI na amostra executado; relatório preservado. Totais financeiros/noites ainda divergem pelos defeitos fora do escopo desta alteração.
        - git apply --check aprovado no repositório original; git status permanece limpo.
        
        Arquivos: correcao.patch, logs de execução, XML antes/depois, relatórios do CLI e integridade.json.
        '''
        (p/'RESULTADO.md').write_text(report)
        print('patch_check: OK; original unchanged; tests/data preserved; git_status:',repr(status))
        print('Patch:',p/'correcao.patch')
        PY
    .....                                                                    [100%]
    5 passed in 0.73s
    
    reservas_hoteis.csv {"total_reservations": 300, "confirmed_reservations": 235, "cancelled_reservations": 31, "no_show_reservations": 34, "total_room_nights": -1639, "total_amount_brl": "237031.25", "average_nightly_rate_brl": "0.00"}
    exemplo-validacao.csv {"total_reservations": 12, "confirmed_reservations": 9, "cancelled_reservations": 2, "no_show_reservations": 1, "total_room_nights": -34, "total_amount_brl": "5662.41", "average_nightly_rate_brl": "0.00"}
    Traceback (most recent call last):
      File "<stdin>", line 27, in <module>
      File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/subprocess.py", line 554, in run
        with Popen(*popenargs, **kwargs) as process:
             ~~~~~^^^^^^^^^^^^^^^^^^^^^^
      File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/subprocess.py", line 1039, in __init__
        self._execute_child(args, executable, preexec_fn, close_fds,
        ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                            pass_fds, cwd, env,
                            ^^^^^^^^^^^^^^^^^^^
        ...<5 lines>...
                            gid, gids, uid, umask,
                            ^^^^^^^^^^^^^^^^^^^^^^
                            start_new_session, process_group)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/subprocess.py", line 1972, in _execute_child
        raise child_exception_type(errno_num, err_msg, err_filename)
    FileNotFoundError: [Errno 2] No such file or directory: PosixPath('/Users/joaovictordesousalima/Downloads/onfly-desafio')
    ✗ (1) • 1.40s

## Activity

    $ pwd
    /Users/joaovictordesousalima/Desktop/onfly-challenge
    ✓ • 0ms

## Activity

    $ ls -ld /Users/joaovictordesousalima/Downloads/onfly-desafio /Users/joaovictordesousalima/Desktop/onfly-challenge /Users/joaovictordesousalima/Desktop/onfly-desafio
    ls: /Users/joaovictordesousalima/Downloads/onfly-desafio: No such file or directory
    drwxr-xr-x   3 joaovictordesousalima  staff   96 Nov 15 19:27 /Users/joaovictordesousalima/Desktop/onfly-challenge
    drwxr-xr-x@ 13 joaovictordesousalima  staff  416 Nov 15 19:36 /Users/joaovictordesousalima/Desktop/onfly-desafio
    ✗ (1) • 0ms

## Activity

    $ rg --files --hidden -g '!.git/**' -g '!investigacao/**' -g '!node_modules/**' -g 'csv_reservation_repository.py' -g 'status_policy.py' /Users/joaovictordesousalima/Desktop/onfly-challenge
    ✗ (1) • 0ms

## Activity

    $ git status --short
    ✓ • 0ms

## Activity

    $ git rev-parse HEAD
    9f8d8f733a88bbd3dc5b63a948c0f359958694b0
    ✓ • 0ms

## Activity

    $ git apply --check /Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z/correcao.patch
    ✓ • 0ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        import hashlib, json, subprocess
        p=Path('/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z')
        s=json.loads((p/'execucao.json').read_text())
        source=Path('/Users/joaovictordesousalima/Desktop/onfly-desafio')
        original=Path(s['original']); candidate=Path(s['candidate'])
        before=json.loads((p/'manifesto-original.json').read_text())
        after={str(f.relative_to(source)):hashlib.sha256(f.read_bytes()).hexdigest() for f in source.rglob('*') if f.is_file() and '.git' not in f.relative_to(source).parts}
        assert before==after
        for group in ['tests','data']:
            for f in (original/group).rglob('*'):
                if f.is_file():
                    assert f.read_bytes()==(candidate/f.relative_to(original)).read_bytes(),f
        check=subprocess.run(['git','apply','--check',str(p/'correcao.patch')],cwd=source,capture_output=True,text=True,check=True)
        status=subprocess.run(['git','status','--short'],cwd=source,capture_output=True,text=True,check=True).stdout
        (p/'patch-check.log').write_text('cwd: '+str(source)+'\nexit_code: 0\n'+check.stdout+check.stderr)
        (p/'integridade.json').write_text(json.dumps({'original_unchanged':before==after,'provided_tests_unchanged':True,'data_unchanged':True,'source_observed_at_end':str(source),'git_status':status,'patch_applies_cleanly':True},indent=2)+'\n')
        s['source_observed_at_end']=str(source)
        (p/'execucao.json').write_text(json.dumps(s,indent=2)+'\n')
        (p/'RESULTADO.md').write_text('''# Correção proposta: leitura completa e status faturável
        
        Status: patch preparado e validado em cópia temporária. Não aplicado ao repositório: a ferramenta de edição rejeitou escrita fora da área de trabalho permitida pela sessão.
        
        Durante a execução, ~/Downloads/onfly-desafio deixou de existir. O mesmo repositório foi localizado em ~/Desktop/onfly-desafio, com HEAD 9f8d8f733a88bbd3dc5b63a948c0f359958694b0, estado limpo e os mesmos arquivos verificados por SHA-256. Esta pasta também está fora da raiz gravável da sessão.
        
        Mudanças de produção: remover o break ao atingir 200 reservas e aceitar exclusivamente status == CONFIRMED. A contagem por status no ReportBuilder já precede o filtro e não precisa ser alterada.
        
        Testes fornecidos e dados preservados byte a byte. Novo arquivo de testes com quatro casos: CSVs de 201, 300 e 303 reservas; exclusão de canceladas/NO_SHOW do resumo financeiro, noites, meses e hotéis, mantendo todas as contagens.
        
        Validação no Python 3.13.9 / pytest 8.3.4:
        - As quatro regressões adicionais falham contra o código original.
        - Testes relevantes após o patch: 5 aprovados.
        - Suíte completa após o patch: 5 aprovados e 4 falhas já existentes em câmbio, noites, regressão financeira e ordenação.
        - Ruff no novo arquivo de testes: aprovado.
        - CLI no dataset principal: 300 reservas, 235 confirmadas, 31 canceladas e 34 NO_SHOW.
        - CLI na amostra executado; relatório preservado. Valores e noites ainda divergem pelos defeitos fora do escopo desta alteração.
        - git apply --check aprovado no repositório localizado no Desktop; git status permanece limpo.
        
        Arquivos: correcao.patch, logs de execução, XML antes/depois, relatórios do CLI e integridade.json.
        ''')
        print('Evidence:',p/'RESULTADO.md')
        print('integrity: OK; source unchanged; patch applies cleanly')
        PY
    Evidence: /Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z/RESULTADO.md
    integrity: OK; source unchanged; patch applies cleanly
    ✓ • 212ms

## Assistant

Preparei e validei o patch em uma cópia temporária. **Ele ainda não foi aplicado ao seu repositório.**

O diff de produção é:

```diff
--- a/src/onfly_report/repositories/csv_reservation_repository.py
+++ b/src/onfly_report/repositories/csv_reservation_repository.py
@@
                 for values in reader:
                     rows.append(RawRow(line_number=reader.line_num, values=values))
-                    if len(rows) == 200:
-                        break
                 return rows

--- a/src/onfly_report/services/status_policy.py
+++ b/src/onfly_report/services/status_policy.py
@@
-    return status != "CANCELLED"
+    return status == "CONFIRMED"
```

Remover o `break` permite percorrer o CSV até o fim, sem substituir o limite por outro. A comparação explícita com `CONFIRMED` impede que `NO_SHOW` alimente noites, valores, meses e ranking. A contagem de todos os status já ocorre antes do filtro e permanece preservada.

Incluí no [patch completo](/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z/correcao.patch) quatro casos adicionais: leitura de 201, 300 e 303 reservas e exclusão dos status não faturáveis de todas as agregações. Os testes fornecidos foram preservados.

Validação na cópia corrigida:

- **Testes relevantes: 5 passaram.**
- **Suíte completa: 5 passaram, 4 falharam**, nos defeitos ainda pendentes.
- CLI principal: **300 reservas, 235 confirmadas, 31 canceladas e 34 `NO_SHOW`**.
- `git apply --check`: aprovado.

Os [resultados e logs](/Users/joaovictordesousalima/Desktop/onfly-challenge/investigacao/onfly-leitura-status-20261115T224407Z/RESULTADO.md) estão preservados. Durante o trabalho, localizei o mesmo repositório em `~/Desktop/onfly-desafio`; o caminho em Downloads deixou de existir. Confirmei o mesmo commit, arquivos idênticos e estado limpo.

O controle automático de aprovação rejeitou a edição por estar fora da área gravável desta sessão. Para aplicar a correção diretamente, abra `~/Desktop/onfly-desafio` como pasta de trabalho.

## User

pronto, movi a pasta com o desafio para /Users/joaovictordesousalima/Desktop/onfly-desafio

## Assistant

Vou conferir o repositório nesse caminho e tentar aplicar o patch já validado. Depois, executarei novamente a validação das duas correções.

## Activity

    $ git status --short
    ✓ • 0ms

## Activity

    $ git rev-parse HEAD
    9f8d8f733a88bbd3dc5b63a948c0f359958694b0
    ✓ • 0ms

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        root=Path('/Users/joaovictordesousalima/Desktop/onfly-desafio')
        for p in [root/'AGENTS.md',root/'src/onfly_report/repositories/csv_reservation_repository.py',root/'src/onfly_report/services/status_policy.py']:
            if p.is_file():
                print('\nFILE:',p)
                print(p.read_text())
        PY
    
    FILE: /Users/joaovictordesousalima/Desktop/onfly-desafio/src/onfly_report/repositories/csv_reservation_repository.py
    """Leitura da exportação de reservas em CSV."""
    
    from __future__ import annotations
    
    import csv
    from pathlib import Path
    
    from ..exceptions import InputFileError
    from ..models import RawRow
    
    REQUIRED_COLUMNS = (
        "reservation_id",
        "traveler_name",
        "company_id",
        "hotel_id",
        "hotel_name",
        "city",
        "country",
        "checkin_date",
        "checkout_date",
        "rooms",
        "status",
        "currency",
        "amount",
        "payment_method",
        "booked_at",
    )
    
    
    class CsvReservationRepository:
        """Lê a exportação de reservas sem aplicar regra de negócio."""
    
        def __init__(self, path: Path) -> None:
            self._path = path
    
        def read(self) -> list[RawRow]:
            try:
                with self._path.open("r", encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle)
                    missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
                    if missing:
                        raise InputFileError(f"colunas obrigatórias ausentes: {', '.join(missing)}")
    
                    rows: list[RawRow] = []
                    for values in reader:
                        rows.append(RawRow(line_number=reader.line_num, values=values))
                        if len(rows) == 200:
                            break
                    return rows
            except FileNotFoundError as err:
                raise InputFileError(f"arquivo de reservas não encontrado: {self._path}") from err
            except (OSError, csv.Error) as err:
                raise InputFileError(f"falha ao ler {self._path}: {err}") from err
    
    
    FILE: /Users/joaovictordesousalima/Desktop/onfly-desafio/src/onfly_report/services/status_policy.py
    """Política de status das reservas."""
    
    from __future__ import annotations
    
    
    def is_billable(status: str) -> bool:
        """Indica se a reserva entra nos totais financeiros e de noites."""
        return status != "CANCELLED"
    
    ✓ • 43ms

## Assistant

Confirmei o repositório em `~/Desktop/onfly-desafio`, com o mesmo commit e sem alterações.

Esta sessão continua vinculada a `~/Desktop/onfly-challenge`. Abra **`~/Desktop/onfly-desafio` como pasta de trabalho no Codex** para que eu possa aplicar o patch já preparado e validado.

A aprovação automática rejeitou novamente a edição por estar fora da área gravável da sessão. Nenhum arquivo foi alterado.
