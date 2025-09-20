# mvp/analytics

Home of the lightweight temporal statistics model:
- `temporal_model.py` – Computes day-over-day deltas, rolling means, z-scores, similarity search.
- `feature_builder.py` – Extracts numeric/text features from daily entries.
- `model_runner.py` – Invoked by GitHub Actions; orchestrates analysis + writes to `mvp/data/`.

Dependencies: `numpy`, `pandas`, and optional `sentence-transformers` (guarded import). Target runtime < 1s on GitHub runners.
