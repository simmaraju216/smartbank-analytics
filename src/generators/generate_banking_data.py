
import os
import random
import argparse

from datetime import timedelta, timezone

import pandas as pd
import numpy as np

from faker import Faker


# ==================================================
# CONFIGURATION
# ==================================================

OUTPUT_DIR = "data/raw"

NUM_BRANCHES = 10
NUM_MERCHANTS = 100

TRANSACTION_TYPES = [
    "UPI",
    "NEFT",
    "RTGS",
    "IMPS",
    "ATM_WITHDRAWAL",
    "DEBIT_CARD",
    "CREDIT_CARD",
    "CASH_DEPOSIT"
]

TRANSACTION_STATUSES = [
    "SUCCESS",
    "FAILED",
    "PENDING",
    "REVERSED"
]

MERCHANT_CATEGORIES = [
    "GROCERY",
    "RESTAURANT",
    "SHOPPING",
    "TRAVEL",
    "FUEL",
    "ELECTRONICS"
]


# ==================================================
# MAIN DATA GENERATOR
# ==================================================

def generate_banking_data(
    num_customers=500,
    num_transactions=1000,
    seed=42,
    output_dir=None
):

    # Initialize reproducible random generators.
    random.seed(seed)
    np.random.seed(seed)

    fake = Faker("en_IN")
    fake.seed_instance(seed)

    # Use the provided output directory or default.
    save_dir = output_dir or OUTPUT_DIR

    print("\nGenerating SmartBank banking datasets...")
    print("=" * 60)
    print(f"Output directory: {save_dir}")

    # --------------------------------------------------
    # 1. CUSTOMERS
    # --------------------------------------------------

    customers = []

    for i in range(1, num_customers + 1):

        customers.append({
            "customer_id": f"CUST{i:06d}",
            "customer_name": fake.name(),
            "email": fake.email(),
            "city": fake.city(),
            "state": fake.state()
        })

    customers_df = pd.DataFrame(customers)

    print(f"Customers generated: {len(customers_df)}")

    # --------------------------------------------------
    # 2. BRANCHES
    # --------------------------------------------------

    branches = []

    for i in range(1, NUM_BRANCHES + 1):

        branches.append({
            "branch_id": f"BR{i:04d}",
            "branch_name": f"SmartBank Branch {i}",
            "city": fake.city(),
            "state": fake.state()
        })

    branches_df = pd.DataFrame(branches)

    print(f"Branches generated: {len(branches_df)}")

    # --------------------------------------------------
    # 3. ACCOUNTS
    # --------------------------------------------------

    accounts = []

    customer_ids = customers_df["customer_id"].tolist()
    branch_ids = branches_df["branch_id"].tolist()

    num_accounts = num_customers + max(
        250, num_customers // 2
    )

    for i in range(1, num_accounts + 1):

        accounts.append({
            "account_id": f"ACC{i:07d}",
            "customer_id": random.choice(customer_ids),
            "branch_id": random.choice(branch_ids),
            "account_type": random.choice([
                "SAVINGS",
                "CURRENT",
                "SALARY"
            ]),
            "balance": round(
                random.uniform(1000, 500000), 2
            )
        })

    accounts_df = pd.DataFrame(accounts)

    print(f"Accounts generated: {len(accounts_df)}")

    # --------------------------------------------------
    # 4. MERCHANTS
    # --------------------------------------------------

    merchants = []

    for i in range(1, NUM_MERCHANTS + 1):

        merchants.append({
            "merchant_id": f"MER{i:05d}",
            "merchant_name": fake.company(),
            "category": random.choice(MERCHANT_CATEGORIES)
        })

    merchants_df = pd.DataFrame(merchants)

    print(f"Merchants generated: {len(merchants_df)}")

    # --------------------------------------------------
    # 5. CARDS
    # --------------------------------------------------

    cards = []

    for i in range(1, num_customers + 1):

        cards.append({
            "card_id": f"CARD{i:07d}",
            "customer_id": customers_df.iloc[i - 1][
                "customer_id"
            ],
            "card_type": random.choice([
                "DEBIT",
                "CREDIT"
            ]),
            "card_status": random.choice([
                "ACTIVE",
                "BLOCKED"
            ])
        })

    cards_df = pd.DataFrame(cards)

    print(f"Cards generated: {len(cards_df)}")

    # --------------------------------------------------
    # 6. TRANSACTIONS
    # --------------------------------------------------

    transactions = []

    account_ids = accounts_df["account_id"].tolist()
    merchant_ids = merchants_df["merchant_id"].tolist()
    card_ids = cards_df["card_id"].tolist()

    for i in range(1, num_transactions + 1):

        transaction_type = random.choice(
            TRANSACTION_TYPES
        )

        # Merchant is optional for some transaction types.
        merchant_id = (
            random.choice(merchant_ids)
            if transaction_type in [
                "UPI",
                "DEBIT_CARD",
                "CREDIT_CARD"
            ]
            else None
        )

        # Card is optional for some transaction types.
        card_id = (
            random.choice(card_ids)
            if transaction_type in [
                "ATM_WITHDRAWAL",
                "DEBIT_CARD",
                "CREDIT_CARD"
            ]
            else None
        )

        # Actual transaction event time (UTC).
        event_timestamp = fake.date_time_between(
            start_date="-365d",
            end_date="now"
        ).replace(tzinfo=timezone.utc)

        # Simulate delivery delay between 0 and 72 hours.
        arrival_delay_hours = random.randint(0, 72)

        # Simulated ingestion/arrival time.
        ingestion_timestamp = (
            event_timestamp
            + timedelta(hours=arrival_delay_hours)
        )

        transactions.append({

            "transaction_id": f"TXN{i:010d}",

            "account_id": random.choice(account_ids),

            "merchant_id": merchant_id,

            "card_id": card_id,

            "transaction_type": transaction_type,

            "transaction_amount": round(
                random.uniform(10, 100000), 2
            ),

            "transaction_status": random.choice(
                TRANSACTION_STATUSES
            ),

            "transaction_timestamp": event_timestamp.isoformat(),

            "ingested_at": ingestion_timestamp.isoformat()

        })

    transactions_df = pd.DataFrame(transactions)

    # Sort by arrival time.
    # Event timestamps can still appear out of order.
    transactions_df = (
        transactions_df
        .sort_values("ingested_at", kind="stable")
        .reset_index(drop=True)
    )

    print(
        f"Transactions generated: {len(transactions_df)}"
    )

    print(
        "Arrival timestamp range:",
        f"{transactions_df['ingested_at'].min()} to "
        f"{transactions_df['ingested_at'].max()}"
    )

    # --------------------------------------------------
    # 7. FRAUD ALERTS
    # --------------------------------------------------

    fraud_alerts = []

    # Generate alerts for approximately 5% of transactions.
    num_alerts = int(num_transactions * 0.05)

    if num_alerts > 0:

        alerted_transactions = transactions_df.sample(
            n=num_alerts,
            random_state=seed
        )

        for i, (_, transaction) in enumerate(
            alerted_transactions.iterrows(),
            start=1
        ):

            fraud_alerts.append({

                "alert_id": f"ALERT{i:07d}",

                "transaction_id": transaction[
                    "transaction_id"
                ],

                "alert_type": random.choice([
                    "HIGH_AMOUNT",
                    "UNUSUAL_ACTIVITY",
                    "SUSPICIOUS_MERCHANT",
                    "MULTIPLE_TRANSACTIONS"
                ]),

                "risk_score": round(
                    random.uniform(0.60, 0.99), 2
                )

            })

    fraud_alerts_df = pd.DataFrame(
        fraud_alerts,
        columns=[
            "alert_id",
            "transaction_id",
            "alert_type",
            "risk_score"
        ]
    )

    print(
        f"Fraud alerts generated: {len(fraud_alerts_df)}"
    )

    # --------------------------------------------------
    # 8. SAVE DATASETS
    # --------------------------------------------------

    os.makedirs(save_dir, exist_ok=True)

    datasets = {
        "customers": customers_df,
        "branches": branches_df,
        "accounts": accounts_df,
        "merchants": merchants_df,
        "cards": cards_df,
        "transactions": transactions_df,
        "fraud_alerts": fraud_alerts_df
    }

    print("\nSaving CSV files...")
    print("-" * 60)

    for name, df in datasets.items():

        file_path = os.path.join(
            save_dir,
            f"{name}.csv"
        )

        df.to_csv(file_path, index=False)

        print(
            f"{name}.csv: {len(df)} records saved"
        )

    print("-" * 60)
    print("All banking datasets generated successfully!")

    return datasets


# ==================================================
# COMMAND LINE ARGUMENTS
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "SmartBank Synthetic Banking Data Generator"
        )
    )

    parser.add_argument(
        "--transactions",
        type=int,
        default=1000,
        help="Number of transactions to generate"
    )

    parser.add_argument(
        "--customers",
        type=int,
        default=None,
        help="Number of customers to generate"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=OUTPUT_DIR,
        help="Directory where generated CSV files will be saved"
    )

    args = parser.parse_args()

    if args.transactions < 1:
        parser.error(
            "--transactions must be greater than zero"
        )

    if args.customers is not None and args.customers < 1:
        parser.error(
            "--customers must be greater than zero"
        )

    # Automatically scale customers when not specified.
    if args.customers is None:
        num_customers = max(
            500,
            args.transactions // 20
        )
    else:
        num_customers = args.customers

    print("\nSMARTBANK ANALYTICS")
    print("-" * 40)
    print(f"Transaction count : {args.transactions:,}")
    print(f"Customer count    : {num_customers:,}")
    print(f"Random seed       : {args.seed}")
    print(f"Output directory  : {args.output_dir}")
    print("-" * 40)

    generate_banking_data(
        num_customers=num_customers,
        num_transactions=args.transactions,
        seed=args.seed,
        output_dir=args.output_dir
    )


# ==================================================
# PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()
