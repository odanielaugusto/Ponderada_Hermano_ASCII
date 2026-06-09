# Relatorio tecnico do experimento CI/CD

## Contexto

Este repositorio contem uma CLI simples de ASCII art em Python e um pipeline no
GitHub Actions com instalacao de dependencias, lint, testes, artefatos e coleta
de metricas.

## Hipotese inicial

As execucoes com cache devem ser mais rapidas que as execucoes sem cache. Jobs em
paralelo devem reduzir o tempo total quando lint e testes forem independentes. Um
teste lento deve afetar principalmente o job de testes, enquanto aumento de
quantidade de testes deve crescer de forma mais gradual.

## Evidencias reais

Preencher apos a coleta:

- Link do repositorio: https://github.com/odanielaugusto/Ponderada_Hermano_ASCII
- Link do YAML: https://github.com/odanielaugusto/Ponderada_Hermano_ASCII/blob/main/.github/workflows/ci.yml
- IDs reais dos workflows:
- Commits reais usados:
- Links ou prints das execucoes do GitHub Actions:

## Variacoes executadas

Preencher apos os 12 runs:

| Execucao | Commit | Variacao | Resultado esperado |
| --- | --- | --- | --- |
| 1 | | Baseline com testes passando | Sucesso |
| 2 | | Aumento artificial de testes | Sucesso |
| 3 | | Introducao de teste lento | Sucesso mais demorado |
| 4 | | Cache de dependencias alterado | Possivel aumento de tempo |
| 5 | | Cache restaurado | Possivel reducao de tempo |
| 6 | | Falha controlada em teste | Falha |
| 7 | | Correcao da falha controlada | Sucesso |
| 8 | | Jobs sequenciais | Sucesso mais demorado |
| 9 | | Jobs paralelos restaurados | Sucesso mais rapido |
| 10 | | Mais testes gerados | Sucesso |
| 11 | | Teste lento mais intenso | Sucesso mais demorado |
| 12 | | Perfil final estavel | Sucesso |

## Graficos

Gerados a partir de `entregaveis/metricas_pipeline.csv`:

- `graficos/tempo_total_por_execucao.png`
- `graficos/tempo_por_job.png`
- `graficos/taxa_sucesso_falha.png`
- `graficos/testes_vs_duracao.png`

## Analise

### Qual etapa mais contribuiu para o tempo total do pipeline?

Preencher com base no grafico de jobs e nas duracoes de etapas coletadas.

### Houve diferenca significativa entre execucoes com e sem cache?

Preencher comparando as execucoes de cache alterado e cache restaurado.

### O paralelismo reduziu o tempo total? Em que condicoes?

Preencher comparando o run sequencial com o run paralelo.

### Quais falhas foram mais frequentes?

Preencher com base nos status e nos metadados dos testes.

### O pipeline fornece feedback rapido o suficiente para o desenvolvedor?

Preencher com base na mediana de duracao total.

### Que melhorias poderiam ser feitas no pipeline?

Preencher depois da analise dos gargalos reais.

### Quais limitacoes existem nos dados coletados?

Preencher incluindo tamanho pequeno da amostra, variabilidade do ambiente
GitHub-hosted runner e dependencia de artefatos disponiveis.

### Como essa analise poderia apoiar decisoes de engenharia?

Preencher relacionando gargalos, confiabilidade e custo de feedback.

## Resultados inesperados

Preencher pelo menos dois resultados inesperados apos a coleta.

## Comparacao entre hipotese e resultado observado

Preencher apos analisar os graficos.

## Limitacoes do experimento

Preencher apos a coleta final dos dados.
