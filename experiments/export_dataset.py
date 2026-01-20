import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "data/logs/trust_log.csv"
OUTPUT_FILE = BASE_DIR / "data/dataset/trust_dataset.csv"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(LOG_FILE)
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Dataset exported to {OUTPUT_FILE}")

