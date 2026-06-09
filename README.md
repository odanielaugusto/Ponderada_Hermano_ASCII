# ASCII Art CI/CD

Projeto pequeno para testar uma CLI de ASCII art e usar o GitHub Actions como
experimento de metricas de CI/CD.

## Como testar o ASCII art

No terminal, a partir da raiz do repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m ascii_art
```

Digite uma palavra ou frase quando o terminal pedir. O texto sera renderizado em
ASCII art linha por linha.

Tambem da para passar o texto direto:

```powershell
ascii-art --text "Inteli CI" --fill "#"
ascii-art --text "Pipeline" --fill "*" --no-animate
```

## Comandos de desenvolvimento

```powershell
ruff check .
pytest --junitxml=artifacts/junit.xml
```

## Experimento de CI/CD

O workflow esta em:

- `.github/workflows/ci.yml`
- Link esperado no GitHub: https://github.com/odanielaugusto/Ponderada_Hermano_ASCII/blob/main/.github/workflows/ci.yml

O pipeline executa:

1. checkout do codigo;
2. instalacao de dependencias;
3. lint com Ruff;
4. testes automatizados com Pytest;
5. geracao de artefatos com JUnit XML e metadados;
6. coleta posterior de metricas via script Python.

As variacoes controladas ficam em `experiment/profile.json` e tambem podem
envolver mudancas no proprio workflow, como cache e paralelismo dos jobs.

## Coletar metricas reais

Depois de executar o workflow no GitHub Actions pelo menos 12 vezes:

```powershell
python scripts/collect_metrics.py `
  --repo odanielaugusto/Ponderada_Hermano_ASCII `
  --workflow ci.yml `
  --limit 30 `
  --out entregaveis/metricas_pipeline.csv
```

Se o GitHub pedir autenticacao para baixar artefatos, defina um token com acesso
ao repositorio:

```powershell
$env:GITHUB_TOKEN="seu_token"
```

## Gerar graficos

```powershell
python scripts/generate_charts.py `
  --input entregaveis/metricas_pipeline.csv `
  --out-dir entregaveis/graficos
```

Graficos esperados:

- `tempo_total_por_execucao.png`
- `tempo_por_job.png`
- `taxa_sucesso_falha.png`
- `testes_vs_duracao.png`

## Entregaveis

Os arquivos finais ficam em `entregaveis/`:

- `metricas_pipeline.csv`
- `graficos/`
- `relatorio.md`
- `README.md`
