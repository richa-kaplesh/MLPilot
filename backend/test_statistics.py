import pandas as pd
from agents.data_intelligence.statistics import run_full_statistics
import json

df = pd.read_csv(r"C:\Users\kaplesh\MLPilot\backend\agents\data_intelligence\train (2).csv")

result = run_full_statistics(
    df=df,
    problem_statement="Predict whether a passenger survived the Titanic disaster",
    target_col="Survived"
)

print(json.dumps(result, indent=2))