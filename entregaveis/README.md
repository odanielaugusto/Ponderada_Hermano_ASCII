# Entregaveis

- Repositorio: https://github.com/odanielaugusto/Ponderada_Hermano_ASCII
- Workflow: `.github/workflows/ci.yml`
- Script de coleta: `scripts/collect_metrics.py`
- Base de dados: `entregaveis/metricas_pipeline.csv`
- Graficos: `entregaveis/graficos/`
- Relatorio: `entregaveis/relatorio.md`

## Reproduzir

```powershell
pip install -e ".[dev]"
ruff check .
pytest
python scripts/collect_metrics.py `
  --repo odanielaugusto/Ponderada_Hermano_ASCII `
  --workflow ci.yml `
  --limit 12 `
  --out entregaveis/metricas_pipeline.csv
python scripts/generate_charts.py `
  --input entregaveis/metricas_pipeline.csv `
  --out-dir entregaveis/graficos
```
