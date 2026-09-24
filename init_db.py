"""
Database Initialization Script
Sets up schemas and populates realistic datasets supporting:
- Module 2.38 (SQL Business Metrics Query Design)
- Module: SQL Filtering, Grouping & Aggregation (WHERE vs HAVING)
- Module 2.40 (SQL Joins & Multi-Table Analysis)
"""
import os
import duckdb
from datetime import datetime, timedelta, date
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
        signup_date DATE NOT NULL,
        created_at TIMESTAMP NOT NULL
    );

    CREATE OR REPLACE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        customer_type VARCHAR,
        order_amount DOUBLE NOT NULL,
        order_date TIMESTAMP NOT NULL,
        status VARCHAR NOT NULL
    );

    CREATE OR REPLACE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name VARCHAR NOT NULL,
        category VARCHAR NOT NULL,
        unit_price DOUBLE NOT NULL
    );

    CREATE OR REPLACE TABLE order_items (
        item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DOUBLE NOT NULL
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

    # 2. Seed Customers (220 customers: 104 Enterprise, 116 SMB)
    industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing']
    customer_rows = []
    
    for i in range(1, 105):
        c_type = 'Enterprise'
        ind = industries[i % len(industries)]
        name = f"Enterprise Client {i}"
        s_date = date(2023, 1, 1) + timedelta(days=(i * 3))
        created = datetime(2023, 1, 1) + timedelta(days=(i * 3))
        customer_rows.append((i, c_type, ind, name, s_date, created))

    for i in range(105, 221):
        c_type = 'SMB'
        ind = industries[i % len(industries)]
        name = f"SMB Client {i}"
        s_date = date(2023, 6, 1) + timedelta(days=i)
        created = datetime(2023, 6, 1) + timedelta(days=i)
        customer_rows.append((i, c_type, ind, name, s_date, created))

    con.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)", customer_rows)

    # 3. Seed Products (10 catalog products)
    products_data = [
        (1, 'Cloud Enterprise Server', 'Infrastructure', 1200.0),
        (2, 'Database Cluster Node', 'Infrastructure', 850.0),
        (3, 'Security Gateway Suite', 'Security', 450.0),
        (4, 'API Management Platform', 'Software', 300.0),
        (5, 'Analytics Dashboard Pro', 'Software', 150.0),
        (6, 'Standard User License', 'SaaS', 50.0),
        (7, 'Developer Tool Bundle', 'Tools', 120.0),
        (8, 'Premium Support Addon', 'Support', 500.0),
        (9, 'Data Backup Appliance', 'Storage', 350.0),
        (10, 'Monitoring Agent Pack', 'DevOps', 80.0)
    ]
    con.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products_data)

    # 4. Seed Orders & Order Items
    # Note: Customers 1 to 180 have orders (Enterprise 1-104 and SMB 105-180).
    # Customers 181 to 220 have NO orders (40 customers with no orders -> tests Task 2A).
    order_rows = []
    item_rows = []
    order_id = 5000
    item_id = 10000

    for c_id in range(1, 181):
        c_type = 'Enterprise' if c_id <= 104 else 'SMB'
        # 3 orders per Enterprise, 2 orders per active SMB
        num_orders = 3 if c_type == 'Enterprise' else 2
        for o_idx in range(num_orders):
            order_id += 1
            o_date = datetime(2024, 1, 10) + timedelta(days=(o_idx * 45) + (c_id % 20))
            
            # 1 to 2 items per order
            p_id = ((c_id + o_idx) % len(products_data)) + 1
            p_price = products_data[p_id - 1][3]
            qty = 2 if c_type == 'Enterprise' else 1
            line_total = qty * p_price
            
            order_rows.append((order_id, c_id, c_type, line_total, o_date, 'completed'))
            item_id += 1
            item_rows.append((item_id, order_id, p_id, qty, p_price))

    # Orphaned orders: 15 orders with customer_id = 9999 (does NOT exist in customers -> tests Task 2B)
    for orph_idx in range(1, 16):
        order_id += 1
        o_date = datetime(2024, 5, 1) + timedelta(days=orph_idx)
        order_rows.append((order_id, 9999, 'Unknown', 450.0, o_date, 'completed'))
        item_id += 1
        item_rows.append((item_id, order_id, 3, 1, 450.0))

    con.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", order_rows)
    con.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", item_rows)

    # 5. Seed Transactions (for previous modules 2.38 and WHERE/HAVING)
    transaction_rows = []
    tx_id = 1000
    for c_id in range(1, 105):
        for tx_idx in range(6):
            tx_id += 1
            amount = round(random.uniform(2500.0, 8000.0), 2)
            offset_days = (tx_idx * 45) + (c_id % 15)
            tx_date = datetime.now() - timedelta(days=offset_days)
            transaction_rows.append((tx_id, c_id, 'Enterprise', amount, 'completed', tx_date))
        tx_id += 1
        transaction_rows.append((tx_id, c_id, 'Enterprise', -200.0, 'refunded', datetime.now() - timedelta(days=60)))
        tx_id += 1
        transaction_rows.append((tx_id, c_id, 'Enterprise', 1500.0, 'pending', datetime.now() - timedelta(days=30)))

    for c_id in range(105, 221):
        for tx_idx in range(4):
            tx_id += 1
            amount = round(random.uniform(180.0, 950.0), 2)
            offset_days = (tx_idx * 50) + (c_id % 20)
            tx_date = datetime.now() - timedelta(days=offset_days)
            transaction_rows.append((tx_id, c_id, 'SMB', amount, 'completed', tx_date))

    con.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)", transaction_rows)

    # 6. Seed Users Funnel
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

    # 7. Seed Customer Revenue Distribution (Module 2.28: Distribution Analysis)
    # Model a realistic business revenue dataset:
    # 80% SMB customers with revenue < $500 (median ~$450)
    # 20% Enterprise customers spending up to $50,000 (mean ~$5,000)
    con.execute("""
    CREATE OR REPLACE TABLE customer_revenue (
        customer_id INTEGER PRIMARY KEY,
        customer_name VARCHAR NOT NULL,
        customer_type VARCHAR NOT NULL,
        revenue DOUBLE NOT NULL,
        orders_count INTEGER NOT NULL,
        signup_date DATE NOT NULL
    );
    """)

    import numpy as np
    np.random.seed(42)
    n_smb = 800
    n_ent = 200
    total_customers = n_smb + n_ent

    smb_rev = np.random.normal(loc=445.0, scale=30.0, size=n_smb)
    smb_rev = np.clip(smb_rev, 100.0, 499.0)

    ent_rev = np.random.uniform(low=12000.0, high=50000.0, size=n_ent)
    target_ent_mean = (5000.0 * total_customers - smb_rev.sum()) / n_ent
    ent_rev = ent_rev - ent_rev.mean() + target_ent_mean

    rev_rows = []
    base_date = date(2023, 1, 1)

    for i in range(n_smb):
        c_id = i + 1
        name = f"SMB Customer {c_id}"
        c_type = "Small Business"
        r_val = round(float(smb_rev[i]), 2)
        orders = random.randint(1, 4)
        s_date = base_date + timedelta(days=i % 365)
        rev_rows.append((c_id, name, c_type, r_val, orders, s_date))

    for j in range(n_ent):
        c_id = n_smb + j + 1
        name = f"Enterprise Customer {c_id}"
        c_type = "Enterprise"
        r_val = round(float(ent_rev[j]), 2)
        orders = random.randint(10, 50)
        s_date = base_date + timedelta(days=(j * 3) % 365)
        rev_rows.append((c_id, name, c_type, r_val, orders, s_date))

    con.executemany("INSERT INTO customer_revenue VALUES (?, ?, ?, ?, ?, ?)", rev_rows)

    # Export to CSV for standalone convenience
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'customer_revenue.csv')
    con.execute(f"COPY customer_revenue TO '{csv_path}' (HEADER, DELIMITER ',')")

    # 8. Seed Customer Churn & Segment Analysis (Module 2.30: GroupBy Aggregation)
    # Model:
    # - Enterprise: 5% of base (100 customers), 1% churn, 70% of total revenue
    # - SMB: 40% of base (800 customers), 12% churn, low revenue share
    # - Startup: 55% of base (1100 customers), 8% churn, moderate revenue share
    con.execute("""
    CREATE OR REPLACE TABLE customer_churn_segments (
        customer_id INTEGER PRIMARY KEY,
        customer_name VARCHAR NOT NULL,
        customer_type VARCHAR NOT NULL,
        product VARCHAR NOT NULL,
        region VARCHAR NOT NULL,
        revenue DOUBLE NOT NULL,
        churn INTEGER NOT NULL,
        signup_date DATE NOT NULL
    );
    """)

    np.random.seed(42)
    n_seg_ent = 100
    n_seg_smb = 800
    n_seg_stu = 1100
    products = ['Cloud Platform', 'Analytics Pro', 'Security Suite', 'Developer Tools']
    regions = ['North America', 'EMEA', 'APAC', 'LATAM']

    churn_rows = []
    
    # 1. Enterprise (100 customers, 1% churn -> 1 churned)
    for i in range(n_seg_ent):
        c_id = i + 1
        name = f"Enterprise Client {c_id}"
        c_type = "Enterprise"
        churn_val = 1 if i == 0 else 0
        raw_rev = float(np.random.uniform(40000.0, 100000.0))
        prod = str(np.random.choice(products, p=[0.45, 0.25, 0.20, 0.10]))
        reg = str(np.random.choice(regions, p=[0.50, 0.30, 0.15, 0.05]))
        s_date = base_date + timedelta(days=(i * 3) % 365)
        churn_rows.append((c_id, name, c_type, prod, reg, raw_rev, churn_val, s_date))

    # 2. SMB (800 customers, 12% churn -> 96 churned)
    for i in range(n_seg_smb):
        c_id = n_seg_ent + i + 1
        name = f"SMB Client {c_id}"
        c_type = "SMB"
        churn_val = 1 if i < 96 else 0
        raw_rev = float(np.random.uniform(800.0, 3500.0))
        prod = str(np.random.choice(products, p=[0.25, 0.35, 0.15, 0.25]))
        reg = str(np.random.choice(regions, p=[0.40, 0.30, 0.20, 0.10]))
        s_date = base_date + timedelta(days=i % 365)
        churn_rows.append((c_id, name, c_type, prod, reg, raw_rev, churn_val, s_date))

    # 3. Startup (1100 customers, 8% churn -> 88 churned)
    for i in range(n_seg_stu):
        c_id = n_seg_ent + n_seg_smb + i + 1
        name = f"Startup Client {c_id}"
        c_type = "Startup"
        churn_val = 1 if i < 88 else 0
        raw_rev = float(np.random.uniform(300.0, 2500.0))
        prod = str(np.random.choice(products, p=[0.20, 0.20, 0.10, 0.50]))
        reg = str(np.random.choice(regions, p=[0.35, 0.30, 0.25, 0.10]))
        s_date = base_date + timedelta(days=(i * 2) % 365)
        churn_rows.append((c_id, name, c_type, prod, reg, raw_rev, churn_val, s_date))

    # Scale enterprise revenue so that enterprise represents exactly 70.0% of total revenue
    smb_and_stu_rev = sum(r[5] for r in churn_rows if r[2] != 'Enterprise')
    current_ent_rev = sum(r[5] for r in churn_rows if r[2] == 'Enterprise')
    target_ent_rev = (0.70 / 0.30) * smb_and_stu_rev
    scale_factor = target_ent_rev / current_ent_rev

    final_churn_rows = []
    for r in churn_rows:
        rev = round(r[5] * scale_factor, 2) if r[2] == 'Enterprise' else round(r[5], 2)
        final_churn_rows.append((r[0], r[1], r[2], r[3], r[4], rev, r[6], r[7]))

    con.executemany("INSERT INTO customer_churn_segments VALUES (?, ?, ?, ?, ?, ?, ?, ?)", final_churn_rows)

    churn_csv_path = os.path.join(os.path.dirname(__file__), 'data', 'customer_churn_segments.csv')
    con.execute(f"COPY customer_churn_segments TO '{churn_csv_path}' (HEADER, DELIMITER ',')")

    con.close()
    print(f"Database initialized and populated at: {db_path}")
    print(f"Customer revenue distribution data exported to: {csv_path}")
    print(f"Customer churn segments data exported to: {churn_csv_path}")

if __name__ == '__main__':
    init_database()
