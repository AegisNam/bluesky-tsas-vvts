## Study design (recommended)

To evaluate TSAS clearly and reproducibly, set up two scenario groups and run each at multiple demand levels.

- Scenario groups (minimum)
  - Baseline — no TSAS (reference)
  - TSAS-enabled — scheduling/dispatching with TSAS logic

- Demand levels to test
  - Low, Medium, High, Overloaded
  - Run Monte Carlo trials for each demand level to estimate metric distributions and confidence intervals

### Metrics to collect
- Average delay per flight
- Total system delay
- Taxi-out / taxi-in time
- Runway throughput (flights/hour)
- Queue length at runway / fix / approach
- Conflict rate or number of vectoring/holding events
- Schedule adherence (if sequencing/scheduling is simulated)

### Expected outcome (example phrasing)
- "Under high demand, TSAS reduced average delay by X%, reduced queue length by Y%, and increased throughput by Z% compared to baseline (Monte Carlo mean ± CI)."

### Important caveats to state
- Poisson arrivals are a modelling assumption for random arrivals; actual airport traffic patterns may differ.
- BlueSky provides system-level simulation; the TSAS here is a logical/experimental model, not a full operational TSAS implementation used by ANSPs.
- If real SGN (Tan Son Nhat) operational data are not available, declare that this is a scenario-based simulation study and the goal is to evaluate trends and relative performance, not to produce operational figures.

### Suggested thesis / method wording
- "Simulation-based evaluation of a contingency TSAS for Tan Son Nhat Airport using BlueSky, Poisson arrivals and Monte Carlo analysis."
- Objective: "Assess the potential of TSAS to reduce delay and optimize arrival flow under congested conditions."

### Recommended procedure (Monte Carlo framework)
1. Build Tan Son Nhat layout / scenario in BlueSky.
2. Generate arrivals via a Poisson process for each demand level (use multiple seeds).
3. Implement two control logics: baseline and TSAS-enabled.
4. Run many Monte Carlo trials per demand level.
5. Collect the metrics listed above for each trial.
6. Compute summary statistics (mean, median, CI) and compare baseline vs TSAS.
7. Report where TSAS yields statistically significant improvements and discuss limitations.

### Short conclusion template
- "Using BlueSky with Poisson arrivals and Monte Carlo sampling, TSAS can be shown to reduce average delay and improve flow at high demand. Present results as a simulation-based evaluation and clearly state modelling assumptions and limitations."
