# Data Storage Guide

## Folder structure
- `data/raw/`: immutable source datasets received from experiments, vendors, or automated exports. Files in this stage are never modified once recorded.
- `data/interim/`: transformed snapshots that capture cleaned or merged subsets used for modeling pipelines. Intermediate artifacts here are timestamped and versioned to preserve reproducibility.
- `data/processed/`: distilled outputs ready for analysis or reporting, such as feature tables or model-ready feeds.

## Data flow
1. Collect raw observations into `data/raw/`.
2. Apply cleaning, validation, and enrichment routines and write stable intermediate artifacts to `data/interim/`.
3. Materialize finalized tables, aggregates, or synthetic datasets in `data/processed/` for downstream consumption.

## Industry-standard conventions
- Treat data files as immutable; append new files rather than editing in place.
- Use descriptive filenames with timestamps (e.g., `20250204_experiment.csv`) so lineage is obvious.
- Keep massive artifacts out of version control by relying on `.gitignore` entries, while tracking metadata or `.gitkeep` placeholders for directory structure.
