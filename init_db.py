"""
Database Initialization Script
Sets up schemas and populates realistic customer and transaction datasets
supporting:
- Module 2.38 (SQL Business Metrics Query Design: uses NOW() - INTERVAL '12 months')
- Module: SQL Filtering, Grouping & Aggregation (WHERE vs HAVING: uses DATE '2024-01-01')
"""
import os
import duckdb
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'business_metrics.duckdb')

def init_database(db_path=DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)
    
    # 1. Create Tables
    con.execute("""
    CREATE OR REPLACE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_type VARCHAR NOT NULL,
        industry VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        created_at TIMESTAMP NOT NULL
    );

    CREATE OR REPLACE TABLE transactions (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        customer_type VARCHAR NOT NULL,
        amount DOUBLE NOT NULL,
        transaction_status VARCHAR NOT NULL,
        transaction_date TIMESTAMP NOT NULL
    );

    CREATE OR REPLACE TABLE users (
        user_id INTEGER PRIMARY KEY,
        created_at TIMESTAMP NOT NULL,
        email_verified_at TIMESTAMP,
        first_purchase_at TIMESTAMP
    );
    """)

    # 2. Seed Realistic Customer Records (104 Enterprise, 115 SMB)
    industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing']
    customer_rows = []
    
    for i in range(1, 105):
        c_type = 'Enterprise'
        ind = industries[i % len(industries)]
        name = f"Enterprise Client {i}"
        created = datetime(2023, 6, 1) + timedelta(days=(i * 2))
        customer_rows.append((i, c_type, ind, name, created))

    for i in range(105, 220):
        c_type = 'SMB'
        ind = industries[i % len(industries)]
        name = f"SMB Client {i}"
        created = datetime(2023, 8, 1) + timedelta(days=i)
        customer_rows.append((i, c_type, ind, name, created))

    con.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customer_rows)

    # 3. Seed Transactions: Spanning both 2024+ and the past 12 months
    transaction_rows = []
    order_id = 1000

    # Enterprise transactions (high volume, large amounts)
    for c_id in range(1, 105):
        for tx_idx in range(6):
            order_id += 1
            amount = round(random.uniform(2500.0, 8000.0), 2)
            # Mix of recent dates (past months) and 2024
            offset_days = (tx_idx * 45) + (c_id % 15)
            tx_date = datetime.now() - timedelta(days=offset_days)
            transaction_rows.append((order_id, c_id, 'Enterprise', amount, 'completed', tx_date))
        
        # A few pending / refunded records to verify WHERE clause filtering
        order_id += 1
        transaction_rows.append((order_id, c_id, 'Enterprise', -200.0, 'refunded', datetime.now() - timedelta(days=60)))
        order_id += 1
        transaction_rows.append((order_id, c_id, 'Enterprise', 1500.0, 'pending', datetime.now() - timedelta(days=30)))

    # SMB transactions
    for c_id in range(105, 220):
        for tx_idx in range(4):
            order_id += 1
            amount = round(random.uniform(180.0, 950.0), 2)
            offset_days = (tx_idx * 50) + (c_id % 20)
            tx_date = datetime.now() - timedelta(days=offset_days)
            transaction_rows.append((order_id, c_id, 'SMB', amount, 'completed', tx_date))

    con.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)", transaction_rows)

    # 4. Seed Users Funnel
    con.execute("""
    INSERT INTO users VALUES
    (1, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', NOW() - INTERVAL '4 days'),
    (2, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', NULL),
    (3, NOW() - INTERVAL '5 days', NULL, NULL),
    (4, NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '9 days'),
    (5, NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '8 days'),
    (6, NOW() - INTERVAL '10 days', NULL, NULL),
    (7, NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '19 days'),
    (8, NOW() - INTERVAL '20 days', NOW() - INTERVAL '19 days', NULL),
    (9, NOW() - INTERVAL '45 days', NOW() - INTERVAL '45 days', NOW() - INTERVAL '44 days'),
    (10, NOW() - INTERVAL '45 days', NULL, NULL);
    """)

    con.close()
    print(f"Database initialized and populated at: {db_path}")

if __name__ == '__main__':
    init_database()
