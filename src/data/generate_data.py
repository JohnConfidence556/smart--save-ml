import numpy as np
import pandas as pd
import os

np.random.seed(42)

N_USERS = 5000
N_MONTHS = 12
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))



# 1USERS TABLE


def generate_users(n_users):

    users = pd.DataFrame({
        "user_id": np.arange(1, n_users + 1),
        "age": np.random.randint(21, 60, n_users),
        "income": np.random.normal(250000, 80000, n_users).clip(80000, 800000).astype(int),
    })

    return users



# BEHAVIOR SIMULATION


def simulate_behavior(users):

    transactions_rows = []
    engagement_rows = []
    nudge_rows = []

    for _, user in users.iterrows():

        engagement_score = np.random.uniform(0.4, 0.9)
        deposit_propensity = np.random.uniform(0.3, 0.9)
        churn_risk = np.random.uniform(-3, -1)
        churned = False
        decay_counter = 0
        balance = np.random.uniform(5000, 20000)

        for month in range(1, N_MONTHS + 1):

            # If already churned → gradual decay
            if churned:
                engagement_score *= 0.5
                deposit_propensity *= 0.3
                decay_counter += 1

            # Engagement evolution
            engagement_score += np.random.normal(0, 0.05)
            engagement_score = np.clip(engagement_score, 0, 1)

            login_count = int(engagement_score * np.random.randint(5, 20))
            session_duration = round(np.random.normal(engagement_score * 10, 2), 2)

            # Deposit behavior depends on engagement + income
            base_deposit = user["income"] * 0.05
            deposit_amount = base_deposit * engagement_score * deposit_propensity
            deposit_amount += np.random.normal(0, 2000)
            deposit_amount = max(deposit_amount, 0)

            withdrawal_amount = deposit_amount * np.random.uniform(0.3, 0.7)

            balance += deposit_amount - withdrawal_amount

            # Churn risk increases if low engagement
            if engagement_score < 0.3:
                churn_risk += 0.5
            else:
                churn_risk -= 0.2

            churn_probability = sigmoid(churn_risk)

            if not churned:
                churn_event = np.random.binomial(1, churn_probability)
                if churn_event == 1:
                    churned = True

            # Nudge logic
            nudge_sent = 1 if engagement_score < 0.4 else 0
            responded = 0
            deposit_after_nudge = deposit_amount

            if nudge_sent and not churned:
                response_prob = 0.3 + engagement_score
                responded = np.random.binomial(1, min(response_prob, 0.9))
                if responded:
                    uplift = np.random.normal(3000, 1000)
                    deposit_after_nudge += max(uplift, 0)

            # Save transactions
            transactions_rows.append([
                user["user_id"],
                month,
                round(deposit_amount, 2),
                round(withdrawal_amount, 2),
                round(balance, 2),
                int(churned)
            ])

            # Save engagement
            engagement_rows.append([
                user["user_id"],
                month,
                login_count,
                session_duration,
                round(engagement_score, 3)
            ])

            # Save nudges
            nudge_rows.append([
                user["user_id"],
                month,
                nudge_sent,
                responded,
                round(deposit_after_nudge, 2)
            ])

    transactions = pd.DataFrame(transactions_rows, columns=[
        "user_id", "month", "deposit_amount",
        "withdrawal_amount", "balance", "churned"
    ])

    engagement = pd.DataFrame(engagement_rows, columns=[
        "user_id", "month", "login_count",
        "session_duration", "engagement_score"
    ])

    nudges = pd.DataFrame(nudge_rows, columns=[
        "user_id", "month", "nudge_sent",
        "responded", "deposit_after_nudge"
    ])

    return transactions, engagement, nudges


# MAIN


if __name__ == "__main__":

    print("Generating users...")
    users = generate_users(N_USERS)

    print("Simulating behavior...")
    transactions, engagement, nudges = simulate_behavior(users)

    users.to_csv(f"{OUTPUT_DIR}/users.csv", index=False)
    transactions.to_csv(f"{OUTPUT_DIR}/transactions.csv", index=False)
    engagement.to_csv(f"{OUTPUT_DIR}/engagement.csv", index=False)
    nudges.to_csv(f"{OUTPUT_DIR}/nudges.csv", index=False)

    print("Level 2 behavioral datasets generated.")