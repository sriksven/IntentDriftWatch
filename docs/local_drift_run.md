# Local Drift Generation Guide

## 1. Activate environment
```
cd IntentDriftWatch
conda activate intentdriftwatch   # OR your virtualenv
# OR:
# source intentdriftwatch/bin/activate
```

## 2. Run data collection (optional)
```
python data_pipeline/collect/run_collect.py
```

## 3. Run preprocessing
```
python data_pipeline/preprocess/run_preprocess.py
```

## 4. Generate embeddings
```
python data_pipeline/embeddings/run_embeddings.py
```

## 5. Generate semantic drift
```
python drift/semantic/run_semantic_drift.py
```

## 6. Generate concept drift
```
python drift/concept/run_concept_drift.py
```

## 7. Generate final drift summary
```
python drift/summary/run_summary.py
```

## 8. Optional: Generate alerts
```
python drift/alerts/run_alerts.py
```

## 9. View summaries
```
ls drift_reports/summaries/
```

## 10. Push updates
```
git add .
git commit -m "New drift summaries"
git push
```

## Full Pipeline
```
conda activate intentdriftwatch

python data_pipeline/collect/run_collect.py
python data_pipeline/preprocess/run_preprocess.py
python data_pipeline/embeddings/run_embeddings.py

python drift/semantic/run_semantic_drift.py
python drift/concept/run_concept_drift.py

python drift/summary/run_summary.py
python drift/alerts/run_alerts.py



python monitoring/full_pipeline.py - main 

```
