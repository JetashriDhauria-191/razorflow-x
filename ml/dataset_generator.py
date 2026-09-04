import random
import pandas as pd
import numpy as np
from pathlib import Path

def generate_synthetic_dataset(num_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic transaction dataset representing normal payments,
    transient network failures, high-risk fraudulent bursts, bank downtimes, and auth errors.
    """
    np.random.seed(seed)
    random.seed(seed)

    records = []
    
    for _ in range(num_samples):
        # 1. Generate base profile
        is_fraud_burst = (random.random() < 0.08) # 8% suspicious burst attacks
        is_bank_downtime = (random.random() < 0.07) # 7% bank outage windows
        is_poor_network = (random.random() < 0.12) # 12% unstable mobile/gateway timeouts
        
        if is_fraud_burst:
            amount = float(np.random.choice([45000, 75000, 95000, 150000]) + np.random.randint(100, 999))
            retry_count = np.random.randint(3, 8)
            failure_count = np.random.randint(4, 10)
            frequency = np.random.randint(5, 20)
            hour = int(np.random.choice([1, 2, 3, 4, 23])) # Late night / unusual hours
            prev_success_rate = round(float(np.random.uniform(0.05, 0.40)), 3)
            velocity = round(float(np.random.uniform(3.5, 9.0)), 2)
            device_trust = round(float(np.random.uniform(0.05, 0.35)), 2)
            
            failed = 1
            risk_score = min(100.0, round(float(75 + velocity * 2.5 + (1.0 - device_trust) * 15 + np.random.uniform(-5, 5)), 1))
            failure_category = "AUTHENTICATION_FAILURE" if random.random() < 0.6 else "DUPLICATE_TRANSACTION"

        elif is_bank_downtime:
            amount = float(np.random.exponential(scale=2500) + 150)
            retry_count = np.random.randint(1, 4)
            failure_count = np.random.randint(1, 4)
            frequency = np.random.randint(1, 4)
            hour = np.random.randint(9, 21)
            prev_success_rate = round(float(np.random.uniform(0.70, 0.95)), 3)
            velocity = round(float(np.random.uniform(0.8, 2.0)), 2)
            device_trust = round(float(np.random.uniform(0.70, 0.98)), 2)
            
            failed = 1
            risk_score = round(float(np.random.uniform(25, 45)), 1)
            failure_category = "BANK_FAILURE" if random.random() < 0.7 else "GATEWAY_FAILURE"

        elif is_poor_network:
            amount = float(np.random.exponential(scale=1800) + 99)
            retry_count = np.random.randint(1, 3)
            failure_count = np.random.randint(1, 3)
            frequency = np.random.randint(1, 3)
            hour = np.random.randint(8, 23)
            prev_success_rate = round(float(np.random.uniform(0.80, 0.99)), 3)
            velocity = round(float(np.random.uniform(0.5, 1.5)), 2)
            device_trust = round(float(np.random.uniform(0.80, 1.0)), 2)
            
            failed = 1
            risk_score = round(float(np.random.uniform(15, 35)), 1)
            failure_category = "TIMEOUT" if random.random() < 0.65 else "NETWORK_FAILURE"

        else: # Normal healthy transaction
            amount = float(np.random.exponential(scale=1200) + 49)
            retry_count = 0 if random.random() < 0.85 else 1
            failure_count = 0 if random.random() < 0.90 else 1
            frequency = 1 if random.random() < 0.8 else 2
            hour = np.random.randint(6, 23)
            prev_success_rate = round(float(np.random.uniform(0.88, 1.0)), 3)
            velocity = round(float(np.random.uniform(0.2, 1.2)), 2)
            device_trust = round(float(np.random.uniform(0.85, 1.0)), 2)
            
            # 96% success in normal segment
            if random.random() < 0.96:
                failed = 0
                risk_score = round(float(np.random.uniform(5, 25)), 1)
                failure_category = "SUCCESS"
            else:
                failed = 1
                risk_score = round(float(np.random.uniform(20, 38)), 1)
                failure_category = "INSUFFICIENT_FUNDS"

        records.append({
            "amount": round(amount, 2),
            "retry_count": retry_count,
            "failure_count": failure_count,
            "transaction_frequency_10min": frequency,
            "hour_of_day": hour,
            "previous_success_rate": prev_success_rate,
            "velocity_score": velocity,
            "device_trust_score": device_trust,
            "risk_score": risk_score,
            "failed": failed,
            "failure_category": failure_category
        })

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    df = generate_synthetic_dataset(5000)
    out_csv = out_dir / "dataset.csv"
    df.to_csv(out_csv, index=False)
    print(f"Generated {len(df)} records saved to {out_csv}")
    print(df.head())
