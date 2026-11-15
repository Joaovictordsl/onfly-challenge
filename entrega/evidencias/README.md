# Evidências preservadas para a entrega

Estes arquivos foram colocados em `entrega/` porque `output/` é ignorado pelo Git. São evidências de execuções reais; os documentos em `anteriores/` descrevem os estados históricos e não substituem o resultado final.

| Arquivos/diretórios | Finalidade |
|---|---|
| [revisao-codigo.patch](revisao-codigo.patch) | Diff acumulado de `src/` e testes adicionais entre o commit original `9f8d8f7` e `961c080`. |
| [relatorio-principal.json](relatorio-principal.json), [execucoes-finais.json](execucoes-finais.json), [cli-principal.log](cli-principal.log) | Relatório principal gerado nesta revisão em Python 3.13.9 e registros de execução. |
| [conferir_relatorio.py](conferir_relatorio.py), [referencia-independente.json](referencia-independente.json), [comparacao-principal.json](comparacao-principal.json), [calculo-independente.log](calculo-independente.log) | Cálculo independente com frações racionais, ordinais de datas e arredondamento por divisão inteira; comparação integral dos campos de negócio. |
| [validar_python311.py](validar_python311.py), [python311/resultado.json](python311/resultado.json), [python311/execucoes.json](python311/execucoes.json) | Ambiente Python 3.11.18, venv e pytest 8.3.4 em contêiner; saídas reais da suíte, dos dois relatórios e da conferência independente. |
| [python311/pytest.log](python311/pytest.log), [python311/versoes.log](python311/versoes.log), [python311/dependencias.log](python311/dependencias.log) | Resultado de 21 aprovações, versão efetiva e dependências instaladas a partir de wheels locais. |
| [anteriores/baseline/](anteriores/baseline/) | Cinco testes inicialmente falhando e relatório incorreto da amostra, antes das correções. |
| [anteriores/leitura-status/](anteriores/leitura-status/), [anteriores/noites-cambio/](anteriores/noites-cambio/) | Evidências intermediárias das correções em etapas. |
| [anteriores/ranking/](anteriores/ranking/) | Suíte final em Python 3.13, referência da amostra extraída do README, comparação completa e 21 cenários do CLI. |
| [anteriores/origens.json](anteriores/origens.json) | Origem de cada arquivo histórico copiado e respectivo SHA-256; conteúdo preservado. |
| [integridade-final.json](integridade-final.json) | Identidade dos dados e testes fornecidos com o commit original e ausência de novas alterações em produção/testes nesta revisão. |
| [repositorio-publico.json](repositorio-publico.json) | Campos relevantes da consulta somente de leitura ao GitHub que confirmou a visibilidade pública do repositório. |

Os comandos nos JSONs históricos conservam os caminhos e diretórios temporários usados no momento da execução, que podem não existir em outra máquina. Os comandos de reprodução portáveis estão no [README de entrega](../README-ENTREGA.md).

O `verificar_contrato.py` histórico assume que está dentro de `output/investigacao-ranking/`, como na execução original. A cópia em `anteriores/ranking/` foi mantida sem modificações como evidência, não deve ser executada diretamente deste novo caminho. Para inspecionar o resultado use seus registros, ou para repetir essa verificação coloque a cópia novamente em `output/investigacao-ranking/`. Os dois scripts novos na raiz deste diretório têm comandos de reprodução documentados.

Nenhum teste ou dado fornecido foi alterado para produzir estes resultados. O traceback da exceção injetada na revisão do contrato foi um cenário deliberado para verificar o código de saída 1, não uma falha da execução normal.
