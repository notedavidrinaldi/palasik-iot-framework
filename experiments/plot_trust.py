import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Load dataset
# =========================
CSV_PATH = "data/logs/trust_log.csv"
df = pd.read_csv(CSV_PATH)

# =========================
# Normalize & prepare
# =========================
df["timestamp"] = pd.to_datetime(df["timestamp"])

# =========================
# Plot trust per device
# =========================
plt.figure(figsize=(12, 6))

for device_ip in df["ip"].unique():
    d = df[df["ip"] == device_ip]
    plt.plot(
        d["timestamp"],
        d["trust_score"],
        marker="o",
        linewidth=2,
        label=device_ip
    )

# =========================
# Policy thresholds
# =========================
plt.axhline(0.8, color="green", linestyle="--", label="SAFE (>0.8)")
plt.axhline(0.5, color="orange", linestyle="--", label="MONITOR (0.5–0.8)")
plt.axhline(0.3, color="red", linestyle="--", label="DANGER (<0.5)")

# =========================
# Styling
# =========================
plt.title("PALASIK — Trust Score per Device Over Time")
plt.xlabel("Time")
plt.ylabel("Trust Score")
plt.ylim(0, 1.05)
plt.legend(title="Device IP")
plt.grid(alpha=0.3)
plt.tight_layout()

OUTPUT_PATH = "experiments/output/trust_per_device.png"
plt.savefig(OUTPUT_PATH, dpi=300)

plt.show()

