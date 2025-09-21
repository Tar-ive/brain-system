# Temporal Modeling & Behavioral Analytics Trace

Key research papers, articles, and tools to inform the MVP’s statistical backbone for intentionality tracking.

## 1. Forecasting Foundations
- **Prophet: Forecasting at Scale** — Sean J. Taylor & Benjamin Letham, Facebook Research (2017).  
  Introduces additive trend + seasonality model with holiday regressors; fast to prototype for daily behavior series.
- **Bayesian Structural Time Series (BSTS)** — Kay H. Brodersen et al., *Annals of Applied Statistics* (2015).  
  Bayesian state-space framework excellent for counterfactual impact (e.g., “did late nights hurt next-day productivity?”).
- **Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting** — Bryan Lim & Sercan Ö. Arık, *NeurIPS* (2021).  
  Attention over static & temporal covariates with built-in variable importance; candidate for multi-signal behavioral trends.
- **Dynamic Time Warping Averaging of Time Series** — François Petitjean et al., *Pattern Recognition* (2014).  
  Useful for clustering similar days or routines even when time-alignments shift.

## 2. Behavior & Habit Analytics
- **Computational Behavior Change** — B. A. Consolvo & E. Bianchi (CHI workshops, 2014–2019).  
  Design patterns for persuasive tech; good lens for “nudge vs. nag”.
- **Just-in-Time Adaptive Interventions (JITAI)** — Nahum-Shani et al., *Annual Review of Clinical Psychology* (2018).  
  Framework for triggering support at high-risk moments—maps directly to late-night decision coaching.
- **Habit Formation and Tracking with Wearables** — P. Ghosh et al., *IEEE Pervasive Computing* (2020).  
  Surveys lag features (moving averages, streaks) for predicting adherence.

## 3. Signal Processing Enhancers
- **Exponential Weighted Moving Average Control Charts** — S. W. Roberts (1959).  
  Provides lightweight anomaly detection for mood/intention drift without heavy ML.
- **State Space Models with Kalman Filtering** — Maybe start with Meinhold & Singpurwalla (1983).  
  Great for smoothing noisy mood observations.
- **Change Point Detection with Bayesian Online Change Detection** — Adams & MacKay (2007).  
  Enables real-time alerts when behavior regimes shift.

## 4. Tooling & Libraries
- **`river` (Online ML)** — incremental stats for streaming daily entries; supports EWMA, ADWIN drift detection.
- **`neuralprophet`** — easier multi-season forecasting; integrates with PyTorch for future expansions.
- **`greykite`** — LinkedIn’s forecasting framework with interpretable decomposition.

## 5. Suggested Reading Plan
1. **Week 1:** Prophet + BSTS papers — prototype baseline forecasts and intervention counterfactuals.
2. **Week 2:** JITAI & behavior-change literature — craft trigger logic for assistant nudges.
3. **Week 3:** Temporal Fusion Transformer — assess if worth fine-tuning once dataset grows (>90 days).
4. **Week 4:** Online drift detection (river, BOCPD) — move toward real-time guardrails.

## 6. Notes & Open Problems
- Need to evaluate data volume to justify heavy neural models; start with interpretable stats to maintain trust.
- Combine streak metrics with emotional variance to predict burnout windows.
- Investigate persona-specific embeddings so assistant references “past Saksham” voice authentically.

Document last updated: 2025-09-21.
