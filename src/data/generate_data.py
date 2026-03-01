import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)
random.seed(42)

# CONFIG

NUM_USERS = 5000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)
DATE_RANGE = (END_DATE - START_DATE).days

# Generate Users

archetypes = [
    "salary_earner",
    "gig_worker",
    "student",
    "intentional_saver",
    "passive_user"
]

users = []

for user_id in range(1, NUM_USERS + 1):
    archetype = random.choices(
        archetypes,
        weights=[0.35, 0.25, 0.15, 0.15, 0.10]
    )[0]

    users.append({
        "user_id": user_id,
        "age": random.randint(18, 55),
        "archetype": archetype,
        "signup_date": fake.date_between(start_date="-2y", end_date="today")
    })

users_df = pd.DataFrame(users)


# Generate Transactions

transactions = []
transaction_id = 1

categories = ["food", "transport", "rent", "entertainment", "utilities", "airtime"]

for _, user in users_df.iterrows():
    balance = random.randint(10000, 50000)

    for day_offset in range(DATE_RANGE):
        current_date = START_DATE + timedelta(days=day_offset)

        # Salary earners get paid monthly
        if user["archetype"] in ["salary_earner", "intentional_saver"]:
            if current_date.day == 25:
                salary = random.randint(120000, 350000)
                balance += salary
                transactions.append({
                    "transaction_id": transaction_id,
                    "user_id": user["user_id"],
                    "date": current_date,
                    "amount": salary,
                    "type": "credit",
                    "category": "salary",
                    "balance_after": balance
                })
                transaction_id += 1

        # Gig workers random credits
        if user["archetype"] == "gig_worker":
            if random.random() < 0.05:
                income = random.randint(20000, 100000)
                balance += income
                transactions.append({
                    "transaction_id": transaction_id,
                    "user_id": user["user_id"],
                    "date": current_date,
                    "amount": income,
                    "type": "credit",
                    "category": "gig_income",
                    "balance_after": balance
                })
                transaction_id += 1

        # Daily expenses
        if random.random() < 0.6:
            expense = random.randint(1000, 15000)
            category = random.choice(categories)

            if balance - expense > 0:
                balance -= expense
                transactions.append({
                    "transaction_id": transaction_id,
                    "user_id": user["user_id"],
                    "date": current_date,
                    "amount": expense,
                    "type": "debit",
                    "category": category,
                    "balance_after": balance
                })
                transaction_id += 1

transactions_df = pd.DataFrame(transactions)


# Generate Engagement Data


engagement = []

for _, user in users_df.iterrows():
    for day_offset in range(DATE_RANGE):
        current_date = START_DATE + timedelta(days=day_offset)

        login_prob = 0.6

        if user["archetype"] == "passive_user":
            login_prob = 0.2

        if user["archetype"] == "intentional_saver":
            login_prob = 0.8

        login = 1 if random.random() < login_prob else 0
        push_open = 1 if random.random() < (login_prob * 0.7) else 0

        engagement.append({
            "user_id": user["user_id"],
            "date": current_date,
            "login_flag": login,
            "push_open_flag": push_open
        })

engagement_df = pd.DataFrame(engagement)


# Generate Churn Labels

# Churn = no login in last 30 days of year

churn_labels = []

for user_id in users_df["user_id"]:
    user_engagement = engagement_df[
        (engagement_df["user_id"] == user_id) &
        (engagement_df["date"] >= END_DATE - timedelta(days=30))
    ]

    churn_flag = 1 if user_engagement["login_flag"].sum() == 0 else 0

    churn_labels.append({
        "user_id": user_id,
        "churn_flag": churn_flag
    })

churn_df = pd.DataFrame(churn_labels)


# SAVE FILES

users_df.to_csv("users.csv", index=False)
transactions_df.to_csv("transactions.csv", index=False)
engagement_df.to_csv("engagement.csv", index=False)
churn_df.to_csv("churn_labels.csv", index=False)

print("Synthetic dataset generated successfully!")