from ucimlrepo import fetch_ucirepo
import pandas as pd
import json
import os
import datetime

os.makedirs('data/industrial/uci_steel', exist_ok=True)

print("Fetching dataset 851...")
steel_industry = fetch_ucirepo(id=851)
df = steel_industry.data.original

csv_path = 'data/industrial/uci_steel/raw_data.csv'
df.to_csv(csv_path, index=False)

metadata = {
    "dataset_name": steel_industry.metadata.name,
    "source": "UCI Machine Learning Repository",
    "uci_id": 851,
    "license": "CC BY 4.0",
    "citation": "D. Sathishkumar, C. Bogos, Steel Industry Energy Consumption Dataset, UCI Machine Learning Repository, 2021.",
    "download_timestamp": datetime.datetime.now().isoformat(),
    "row_count": len(df),
    "columns": list(df.columns),
    "time_range": f"{df['date'].min()} to {df['date'].max()}",
    "target_variable": "Usage_kWh",
    "preprocessing_version": "1.0"
}

with open('data/industrial/uci_steel/dataset_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=4)

print(f"Saved raw dataset to {csv_path} and metadata.")
