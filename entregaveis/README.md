# Entregaveis

Pasta simples para os artefatos finais da atividade.

- `metricas_pipeline.csv`: base gerada por `scripts/collect_metrics.py`.
- `graficos/`: imagens geradas por `scripts/generate_charts.py`.
- `relatorio.md`: analise tecnica com evidencias reais do GitHub Actions.

Fluxo de reproducao:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
python scripts/collect_metrics.py `
  --repo odanielaugusto/Ponderada_Hermano_ASCII `
  --workflow ci.yml `
  --limit 30 `
  --out entregaveis/metricas_pipeline.csv
python scripts/generate_charts.py `
  --input entregaveis/metricas_pipeline.csv `
  --out-dir entregaveis/graficos
```
