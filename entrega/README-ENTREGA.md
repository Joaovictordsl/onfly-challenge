# Entrega — consolidador de reservas de hotel

As correções funcionais estão no commit `961c080`, revisado contra o projeto original `9f8d8f7`. Os cinco testes fornecidos passam sem alteração. A suíte completa, incluindo 16 casos adicionais, tem **21 testes aprovados**, tanto no Python 3.13.9 quanto no **Python 3.11.18 em contêiner Linux**.

Nesta revisão final não foram alterados código de produção, testes nem dados. Foram preparados a documentação, os registros de IA e as evidências abaixo. Não foi feito commit ou push nesta etapa.

## Defeitos corrigidos e causas raiz

| Defeito | Causa raiz | Correção |
|---|---|---|
| Apenas 200 das 300 reservas eram lidas | Um `break` condicionado a `len(rows) == 200` encerrava a leitura antes do fim do CSV. | Removido o limite em `csv_reservation_repository.py`; o arquivo inteiro é processado. |
| `NO_SHOW` entrava no faturamento | O predicado excluía somente `CANCELLED`, aceitando qualquer outro status como faturável. | `status_policy.py` aceita exclusivamente `CONFIRMED`; todas as reservas continuam contadas antes do filtro. |
| Noites negativas nas viradas de mês/ano | O cálculo subtraía somente os atributos `.day`, descartando mês e ano. | `stay_calculator.py` usa `(checkout - checkin).days * rooms`. |
| Conversão cambial invertida | O conversor dividia pela taxa expressa em BRL por unidade da moeda original. | `currency_converter.py` multiplica `amount * rate`. |
| Perda de precisão financeira | O conversor transformava os operandos `Decimal` em `float` e reconvertia o resultado aproximado. | Removida a passagem por `float`; leitura, conversão, soma e média usam `Decimal`. O `ROUND_HALF_UP` existente continua apenas na serialização para duas casas. |
| Ranking selecionava os menores totais | A chave de ordenação usava o total em ordem crescente. | `report_builder.py` usa `(-amount, hotel_id)` sobre o total exato, antes da formatação, e aplica `[:top_n]` depois. |

O [diff acumulado de produção e testes adicionais](evidencias/revisao-codigo.patch) contém as mudanças efetivas. São seis defeitos em cinco pontos da implementação; o conversor concentrava dois deles. Os argumentos do CLI, o schema do relatório e os CSVs foram preservados.

## Investigação e abordagem

Primeiro foram lidos README, implementação, testes e CSVs. A execução inicial em ambiente virtual isolado reproduziu **cinco falhas nos cinco testes fornecidos**. O CLI da amostra retornava sucesso, mas produzia `-33` noites, total `5962.41` e média `0.00`, contra `28`, `7566.00` e `270.21` publicados no README.

O fluxo foi percorrido da leitura ao JSON, distinguindo resultados de execução das conclusões por inspeção. O corte de 200 reservas não era coberto pelos testes fornecidos. A violação de precisão por `float` era visível no código, mas não havia sido isolada pela execução inicial, pois ocorria na mesma expressão do câmbio invertido.

As correções foram feitas por etapas: leitura/status; noites/câmbio/precisão; ranking. Foram adicionados testes em arquivos novos para leitura com 201/300/303 reservas, exclusão dos status não faturáveis de todas as agregações, viradas de mês/ano, ano bissexto, quartos, precisão decimal, arredondamento após a soma, desempate e `--top`. Os defeitos ainda pendentes em cada etapa permaneceram visíveis nas suítes intermediárias.

Na revisão final, o diff acumulado foi inspecionado e as evidências anteriores foram reaproveitadas. A suíte em Python 3.13 e as verificações do contrato já concluídas não foram repetidas sem mudança de contexto. A nova execução integral foi justificada pelo ambiente Python 3.11 ainda não validado. Também foi acrescentado um cálculo independente do relatório principal.

## Resultados reais de validação

| Etapa | Resultado | Evidência |
|---|---|---|
| Baseline, Python 3.13.9 / pytest 8.3.4 | 5 falhas, saída 1 | [pytest inicial](evidencias/anteriores/baseline/pytest.stdout.log), [comparação inicial da amostra](evidencias/anteriores/baseline/comparacao.json) |
| Após leitura/status | 5 aprovados, 4 falhas ainda esperadas | [suíte intermediária](evidencias/anteriores/leitura-status/suite-completa-depois.log) |
| Após noites/câmbio | 15 aprovados, 1 falha de ranking | [suíte intermediária](evidencias/anteriores/noites-cambio/suite-completa-depois.log) |
| Após ranking, Python 3.13.9 / pytest 8.3.4 | 21 aprovados em 2.60 s, saída 0 | [suíte completa](evidencias/anteriores/ranking/suite-completa-depois.log) |
| Python 3.11.18 / pytest 8.3.4, Linux isolado | 21 aprovados em 7.58 s, saída 0 | [suíte 3.11](evidencias/python311/pytest.log), [versões](evidencias/python311/versoes.log) |
| Amostra completa versus README | Igualdade de versão, resumo, meses e ranking; `generated_at` excluído da igualdade, mas formato/offset validados | [comparação](evidencias/anteriores/ranking/comparacao-readme.json), [referência extraída do README](evidencias/anteriores/ranking/referencia-readme.json), [amostra 3.11](evidencias/python311/exemplo.json) |
| Dataset principal versus cálculo independente | Todos os campos comparados coincidem, nos dois interpretadores | [comparação 3.13](evidencias/comparacao-principal.json), [comparação 3.11](evidencias/python311/comparacao-principal.json) |
| Integridade | Três CSVs e seis arquivos fornecidos de testes/utilitários idênticos ao commit original | [hashes e comparação byte a byte](evidencias/integridade-final.json) |

O Ruff 0.8.4 (`ruff check --no-cache src tests`) e `git diff --check` foram aprovados na etapa de ranking. Os logs históricos foram copiados sem alterações: [origens e hashes](evidencias/anteriores/origens.json). Seus documentos descrevem o estado da época; a ausência de Python 3.11 registrada anteriormente foi resolvida nesta etapa.

## Dataset principal e cálculo independente

O CLI gerou `output/report.json` com código 0. Como `output/` é ignorado pelo Git, a cópia revisável está em [relatorio-principal.json](evidencias/relatorio-principal.json). O [registro da execução](evidencias/execucoes-finais.json) preserva os comandos exatos, stdout, stderr e códigos de saída.

O [verificador independente](evidencias/conferir_relatorio.py) usa apenas a biblioteca padrão e **não importa `onfly_report`**. Ele lê os CSVs diretamente, usa `Fraction` para representar dinheiro como números racionais exatos, datas convertidas em ordinais e arredondamento half-up por divisão inteira. Agrupa por mês de check-in e por hotel, usa ordenação estável para o desempate e compara versão, resumo, meses e ranking. O timestamp é validado separadamente pelo offset `-03:00`.

| Indicador | CLI e cálculo independente |
|---|---:|
| Reservas | 300 |
| Confirmadas | 235 |
| Canceladas | 31 |
| NO_SHOW | 34 |
| Noites de quartos | 1347 |
| Total BRL | 396170.00 |
| Média por noite BRL | 294.11 |

| Mês | Reservas confirmadas | Noites | Total BRL |
|---|---:|---:|---:|
| 2024-12 | 35 | 174 | 61335.80 |
| 2025-01 | 37 | 235 | 64662.89 |
| 2025-02 | 26 | 138 | 45991.09 |
| 2025-03 | 39 | 215 | 65984.99 |
| 2025-04 | 21 | 146 | 31335.97 |
| 2025-05 | 39 | 196 | 63507.98 |
| 2025-06 | 38 | 243 | 63351.29 |

Os valores de cada agregado são arredondados separadamente na saída. Por isso, a soma dos meses já serializados é `396170.01`, enquanto o total exato agregado e então serializado é `396170.00`; essa diferença de um centavo é compatível com a regra do README.

| Ranking | Hotel | Noites | Total BRL |
|---|---|---:|---:|
| 1 | H06 — Hotel Salvador Centro | 160 | 45165.46 |
| 2 | H10 — Hotel Madrid, Gran Vía | 120 | 45041.69 |
| 3 | H12 — Hotel Miami Beach | 106 | 41647.69 |
| 4 | H07 — Hotel Brasília Tower | 148 | 39920.52 |
| 5 | H11 — Hotel Buenos Aires | 102 | 37455.69 |

A [referência independente completa](evidencias/referencia-independente.json) e o [log do cálculo](evidencias/calculo-independente.log) ficam versionáveis junto desta documentação.

## Amostra do README

O relatório completo corresponde às tabelas publicadas: 12 reservas, 9 confirmadas, 2 canceladas, 1 NO_SHOW, 28 noites, total BRL `7566.00` e média `270.21`. Janeiro tem 8 reservas, 25 noites e `6684.00`; fevereiro tem 1 reserva, 3 noites e `882.00`.

| Hotel, na ordem esperada e observada | Noites | Total BRL |
|---|---:|---:|
| H01 — Hotel Aurora Paulista | 3 | 1200.00 |
| H02 — Hotel Mirante | 2 | 1084.00 |
| H12 — Hotel Miami Beach | 1 | 1000.00 |
| H10 — Hotel Madrid, Gran Vía | 4 | 900.00 |
| H09 — Hotel Lisboa, Centro | 3 | 882.00 |

## Revisão do contrato

Foram verificados: processamento integral; contagens de todos os status antes do filtro; faturamento exclusivo de `CONFIRMED`; datas civis e quartos; câmbio multiplicativo; precisão e arredondamento; média sem noites; agrupamento pelo check-in; ordenação dos meses; ranking exato, desempate e limites; chaves e tipos do JSON; dinheiro como string; versão `1.0`; timestamp `-03:00`; argumentos obrigatórios e padrões; criação dos diretórios; resumo no stdout e erros no stderr; códigos de saída 0/2/1.

Os [21 comandos de verificação do CLI](evidencias/anteriores/ranking/execucoes-cli.json) incluem entradas vazias, apenas status não faturáveis, estadia sem noites, argumentos inválidos, arquivos ausentes, colunas/tipos/taxa inválidos e falha de escrita. Uma exceção inesperada também foi injetada para verificar o retorno 1. Isso cobre os cenários registrados; não é uma alegação de validação exaustiva de todo CSV malformado possível.

## Como reproduzir

Na raiz do projeto, com Python 3.11 instalado:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q -p no:cacheprovider
PYTHONPATH=src .venv/bin/python -m onfly_report \
  --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv \
  --output output/report.json
.venv/bin/python entrega/evidencias/conferir_relatorio.py \
  --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv \
  --report output/report.json \
  --reference output/referencia-independente.json \
  --comparison output/comparacao-principal.json
PYTHONPATH=src .venv/bin/python -m onfly_report \
  --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv \
  --output output/exemplo.json
```

Esses são comandos de reprodução local; os comandos efetivamente usados nesta máquina estão nos registros de execução vinculados acima.

### Validação efetivamente realizada em Python 3.11

Não havia interpretador 3.11 nativo nos locais verificados. Foi usada a imagem oficial `python:3.11-slim`, fixada pelo digest `sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535`, que executou **Python 3.11.18**, Linux x86_64. O projeto ficou somente para leitura, a rede do contêiner desativada e apenas o diretório de evidências gravável. Um venv temporário recebeu pytest 8.3.4 e suas dependências a partir de wheels locais; Ruff foi verificado no host, não instalado nesse contêiner.

O [script do ambiente](evidencias/validar_python311.py), os [resultados](evidencias/python311/resultado.json) e os [comandos com saídas reais](evidencias/python311/execucoes.json) permitem inspecionar o que foi executado. Para reproduzir esse ambiente com Docker disponível:

```bash
mkdir -p /tmp/onfly-wheels entrega/evidencias/python311
python3 -m pip download --dest /tmp/onfly-wheels \
  pytest==8.3.4 iniconfig==2.0.0 packaging==24.2 pluggy==1.5.0
docker run --rm --network none --read-only --tmpfs /tmp \
  --mount "type=bind,src=$(pwd),dst=/workspace,readonly" \
  --mount "type=bind,src=$(pwd)/entrega/evidencias/python311,dst=/evidence" \
  --mount type=bind,src=/tmp/onfly-wheels,dst=/wheels,readonly \
  --workdir /workspace --env PYTHONDONTWRITEBYTECODE=1 \
  python:3.11-slim@sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535 \
  python entrega/evidencias/validar_python311.py
```

Não permanece uma lacuna de execução com Python 3.11. A execução nativa no macOS não foi realizada; o ambiente validado foi o contêiner descrito.

## Uso de IA e pendências

Consulte a [declaração de uso de IA](uso-de-ia/declaracao.md) e o [índice dos registros reais](uso-de-ia/README.md). Foi incluída também a conversa de planejamento que ajudou a estruturar os prompts, sem atribuir ao candidato sua autoria exclusiva.

O [repositório público](https://github.com/Joaovictordsl/onfly-challenge) teve a visibilidade confirmada por consulta somente de leitura ao GitHub: [evidência](evidencias/repositorio-publico.json). Estes novos arquivos ainda precisam ser revisados, adicionados, commitados e enviados; nada disso foi executado nesta etapa. O envio do link pelo formulário da Onfly não foi verificado.

A sessão desta revisão está em andamento durante a extração: o registro consolidado termina no corte indicado em sua proveniência e precisa de uma exportação final após a resposta de encerramento. Não foi fabricada uma resposta futura para preencher essa lacuna.
