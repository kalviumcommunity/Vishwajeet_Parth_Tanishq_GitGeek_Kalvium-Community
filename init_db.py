"""
Database Initialization Script
Sets up tables (customers, transactions, users) and populates sample data
to power SQL business metrics queries and Python validation.
"""
import os
import duckdb

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'business_metrics.duckdb')

def init_database(db_path=DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)
    
    # 1. Create Schema
    con.execute("""
    CREATE OR REPLACE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_type VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        created_at TIMESTAMP NOT NULL
    );

    CREATE OR REPLACE TABLE transactions (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        customer_type VARCHAR NOT NULL,
        amount DOUBLE NOT NULL,
        transaction_date TIMESTAMP NOT NULL
    );

    CREATE OR REPLACE TABLE users (
        user_id INTEGER PRIMARY KEY,
        created_at TIMESTAMP NOT NULL,
        email_verified_at TIMESTAMP,
        first_purchase_at TIMESTAMP
    );
    """)

    # 2. Seed Customers
    con.execute("""
    INSERT INTO customers VALUES
    (1, 'Enterprise', 'Acme Corp', NOW() - INTERVAL '11 months'),
    (2, 'Enterprise', 'Globex Inc', NOW() - INTERVAL '10 months'),
    (3, 'SMB', 'Initech LLC', NOW() - INTERVAL '8 months'),
    (4, 'SMB', 'Umbrella Tech', NOW() - INTERVAL '6 months'),
    (5, 'SMB', 'Hooli Labs', NOW() - INTERVAL '4 months');
    """)

    # 3. Seed Transactions across past months
    con.execute("""
    INSERT INTO transactions VALUES
    -- Month -1
    (101, 1, 'Enterprise', 4500.00, NOW() - INTERVAL '15 days'),
    (102, 2, 'Enterprise', 6200.00, NOW() - INTERVAL '20 days'),
    (103, 3, 'SMB', 350.00, NOW() - INTERVAL '18 days'),
    (104, 4, 'SMB', 490.00, NOW() - INTERVAL '10 days'),
    -- Month -2
    (105, 1, 'Enterprise', 4500.00, NOW() - INTERVAL '45 days'),
    (106, 3, 'SMB', 320.00, NOW() - INTERVAL '50 days'),
    (107, 5, 'SMB', 780.00, NOW() - INTERVAL '42 days'),
    -- Month -3
    (108, 2, 'Enterprise', 5800.00, NOW() - INTERVAL '75 days'),
    (109, 4, 'SMB', 410.00, NOW() - INTERVAL '80 days'),
    -- Month -4
    (110, 1, 'Enterprise', 4200.00, NOW() - INTERVAL '110 days'),
    (111, 5, 'SMB', 650.00, NOW() - INTERVAL '105 days'),
    -- Month -5
    (112, 2, 'Enterprise', 5100.00, NOW() - INTERVAL '140 days'),
    (113, 3, 'SMB', 290.00, NOW() - INTERVAL '145 days'),
    -- Month -6
    (114, 1, 'Enterprise', 3900.00, NOW() - INTERVAL '170 days'),
    (115, 4, 'SMB', 520.00, NOW() - INTERVAL '175 days');
    """)

    # 4. Seed Users Funnel across past 90 days
    con.execute("""
    INSERT INTO users VALUES
    -- Day 1
    (1, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', NOW() - INTERVAL '4 days'),
    (2, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', NULL),
    (3, NOW() - INTERVAL '5 days', NULL, NULL),
    -- Day 2
    (4, NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '9 days'),
    (5, NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '8 days'),
    (6, NOW() - INTERVAL '10 days', NULL, NULL),
    -- Day 3
    (7, NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '19 days'),
    (8, NOW() - INTERVAL '20 days', NOW() - INTERVAL '19 days', NULL),
    -- Day 4
    (9, NOW() - INTERVAL '45 days', NOW() - INTERVAL '45 days', NOW() - INTERVAL '44 days'),
    (10, NOW() - INTERVAL '45 days', NULL, NULL);
    """)

    con.close()
    print(f"Database initialized and seeded successfully at: {db_path}")

if __name__ == '__main__':
    init_database()
