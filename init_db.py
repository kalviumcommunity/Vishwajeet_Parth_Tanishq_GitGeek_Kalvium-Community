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
import numpy as np

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

    # 9. Seed Funnel & Drop-Off Detection (Module 2.33: Funnel Analysis)
    # 10,000 users initiate sign up
    # 8,000 enter email (20% loss)
    # 6,000 create password (25% loss)
    # 5,000 verify email (16.7% loss)
    # 4,000 add payment method (20% loss)
    # 2,000 complete first purchase (50% loss -> biggest bottleneck)
    con.execute("""
    CREATE OR REPLACE TABLE user_funnel (
        user_id INTEGER PRIMARY KEY,
        session_id VARCHAR NOT NULL,
        traffic_source VARCHAR NOT NULL,
        device_type VARCHAR NOT NULL,
        signup_clicked INTEGER NOT NULL,
        email_entered INTEGER NOT NULL,
        password_created INTEGER NOT NULL,
        email_verified INTEGER NOT NULL,
        payment_added INTEGER NOT NULL,
        first_purchase INTEGER NOT NULL,
        purchase_amount DOUBLE NOT NULL,
        created_at TIMESTAMP NOT NULL
    );
    """)

    traffic_sources = ['Organic Search', 'Paid Ad', 'Referral', 'Social Media']
    devices = ['Desktop', 'Mobile', 'Tablet']
    funnel_rows = []

    for uid in range(1, 10001):
        sess = f"sess_{uid:05d}"
        source = traffic_sources[uid % len(traffic_sources)]
        device = devices[uid % len(devices)]
        
        signup_clicked = 1
        email_entered = 1 if uid <= 8000 else 0
        password_created = 1 if uid <= 6000 else 0
        email_verified = 1 if uid <= 5000 else 0
        payment_added = 1 if uid <= 4000 else 0
        first_purchase = 1 if uid <= 2000 else 0
        purchase_amount = round(float(np.random.normal(150.0, 25.0)), 2) if first_purchase == 1 else 0.0
        c_time = datetime(2024, 1, 1) + timedelta(minutes=(uid * 15))

        funnel_rows.append((
            uid, sess, source, device,
            signup_clicked, email_entered, password_created,
            email_verified, payment_added, first_purchase,
            purchase_amount, c_time
        ))

    con.executemany("INSERT INTO user_funnel VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", funnel_rows)

    funnel_csv_path = os.path.join(os.path.dirname(__file__), 'data', 'funnel_events.csv')
    con.execute(f"COPY user_funnel TO '{funnel_csv_path}' (HEADER, DELIMITER ',')")

    # 10. Seed Hourly KPI Metrics & Anomaly Detection (Module 2.36: Anomaly Detection)
    con.execute("""
    CREATE OR REPLACE TABLE hourly_kpi_metrics (
        metric_id INTEGER PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL,
        date DATE NOT NULL,
        hour INTEGER NOT NULL,
        revenue DOUBLE NOT NULL,
        transaction_count INTEGER NOT NULL,
        signup_count INTEGER NOT NULL,
        active_users INTEGER NOT NULL,
        is_anomaly BOOLEAN NOT NULL,
        anomaly_type VARCHAR
    );
    """)

    np.random.seed(101)
    kpi_rows = []
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    total_hours = 30 * 24  # 720 hours (30 days)

    for h_idx in range(total_hours):
        current_time = start_time + timedelta(hours=h_idx)
        cur_date = current_time.date()
        cur_hour = current_time.hour
        day_num = (h_idx // 24) + 1  # Day 1 to 30

        # Normal diurnal baseline:
        # Peak around 14:00 (2 PM), low around 03:00 (3 AM)
        diurnal_factor = 0.5 * (1 + np.sin((cur_hour - 8) * np.pi / 12))  # ranges [0, 1]
        
        base_rev = 14000.0 + diurnal_factor * 11000.0 + np.random.normal(0, 800.0)
        base_tx = int(180 + diurnal_factor * 160 + np.random.normal(0, 15.0))
        base_signups = int(18 + diurnal_factor * 16 + np.random.normal(0, 3.0))
        base_active = int(1000 + diurnal_factor * 1000 + np.random.normal(0, 75.0))

        rev = max(base_rev, 1000.0)
        tx = max(base_tx, 10)
        signups = max(base_signups, 1)
        active = max(base_active, 50)
        is_anom = False
        anom_desc = "Normal"

        # Injected Anomaly 1: Payment Processing Outage on Day 28, Hours 14 and 15
        if day_num == 28 and cur_hour in (14, 15):
            rev = 0.0
            tx = 0
            is_anom = True
            anom_desc = "Payment Gateway Outage"
        
        # Injected Anomaly 2: Bot Attack / Fake Signups on Day 15, Hour 3
        elif day_num == 15 and cur_hour == 3:
            signups = 260  # 10x normal rate of ~22
            is_anom = True
            anom_desc = "Bot Attack (Signup Surge)"

        # Injected Anomaly 3: Pricing Glitch / 4x Transaction Surge on Day 22, Hour 18
        elif day_num == 22 and cur_hour == 18:
            tx = 1350  # ~4x normal of ~320
            rev = 1485.0  # Glitch price ($1.10/tx instead of ~$75/tx)
            is_anom = True
            anom_desc = "Pricing Glitch Surge"

        kpi_rows.append((
            h_idx + 1,
            current_time,
            cur_date,
            cur_hour,
            round(float(rev), 2),
            int(tx),
            int(signups),
            int(active),
            is_anom,
            anom_desc
        ))

    con.executemany("INSERT INTO hourly_kpi_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", kpi_rows)

    kpi_csv_path = os.path.join(os.path.dirname(__file__), 'data', 'hourly_kpi_metrics.csv')
    con.execute(f"COPY hourly_kpi_metrics TO '{kpi_csv_path}' (HEADER, DELIMITER ',')")

    # 11. Seed High-Volume Warehouse Tables for Query Optimization (Module: Query Optimization)
    con.execute("""
    CREATE OR REPLACE TABLE customers_expanded (
        customer_id INTEGER PRIMARY KEY,
        customer_name VARCHAR NOT NULL,
        country VARCHAR NOT NULL,
        region VARCHAR NOT NULL,
        tier VARCHAR NOT NULL,
        signup_year INTEGER NOT NULL,
        lifetime_value DOUBLE NOT NULL,
        email VARCHAR NOT NULL,
        phone VARCHAR NOT NULL,
        address VARCHAR NOT NULL
    );

    CREATE OR REPLACE TABLE warehouse_transactions (
        transaction_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        transaction_year INTEGER NOT NULL,
        transaction_date DATE NOT NULL,
        amount DOUBLE NOT NULL,
        payment_method VARCHAR NOT NULL,
        card_type VARCHAR NOT NULL,
        currency VARCHAR NOT NULL,
        status VARCHAR NOT NULL,
        store_id INTEGER NOT NULL,
        channel VARCHAR NOT NULL,
        ip_address VARCHAR NOT NULL,
        user_agent VARCHAR NOT NULL,
        device_fingerprint VARCHAR NOT NULL,
        session_id VARCHAR NOT NULL,
        payload_json VARCHAR NOT NULL,
        billing_address VARCHAR NOT NULL,
        shipping_address VARCHAR NOT NULL,
        tax_amount DOUBLE NOT NULL,
        discount_amount DOUBLE NOT NULL,
        is_fraud_flagged BOOLEAN NOT NULL,
        risk_score DOUBLE NOT NULL,
        processor_response_code VARCHAR NOT NULL,
        metadata_notes VARCHAR NOT NULL,
        created_at TIMESTAMP NOT NULL
    );
    """)

    # Seed 2,000 customers
    np.random.seed(2024)
    countries = ['United States', 'Germany', 'United Kingdom', 'Canada', 'France', 'Japan', 'India', 'Australia']
    regions = ['North America', 'EMEA', 'APAC', 'LATAM']
    tiers = ['Standard', 'Silver', 'Gold', 'Platinum']
    
    cust_expanded_rows = []
    for c_id in range(1, 2001):
        c_name = f"Customer {c_id}"
        cntry = countries[c_id % len(countries)]
        reg = regions[c_id % len(regions)]
        tier = tiers[c_id % len(tiers)]
        s_year = 2020 + (c_id % 5)
        ltv = round(float(np.random.uniform(500.0, 50000.0)), 2)
        email = f"user_{c_id}@enterprise-client-{c_id % 100}.com"
        phone = f"+1-555-{c_id:04d}"
        addr = f"{c_id * 17} Tech Innovation Blvd, Suite {c_id % 50}, Metropolis"
        cust_expanded_rows.append((c_id, c_name, cntry, reg, tier, s_year, ltv, email, phone, addr))

    con.executemany("INSERT INTO customers_expanded VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", cust_expanded_rows)

    # Seed 50,000 warehouse transactions across 2021-2024 (with ~10,000 in 2024)
    # 25 wide columns to emulate bloated analytical warehouse schema
    methods = ['Credit Card', 'Wire Transfer', 'ACH', 'PayPal', 'Corporate Net30']
    cards = ['Visa Corporate', 'Mastercard World', 'Amex Platinum', 'Discover Business']
    statuses = ['completed', 'completed', 'completed', 'refunded', 'cancelled']
    channels = ['Web Portal', 'Mobile App', 'API Integration', 'Partner Gateway']

    wh_tx_rows = []

    for tx_id in range(1, 50001):
        cust_id = (tx_id % 2000) + 1
        year_rand = tx_id % 100
        if year_rand < 15:
            tx_year = 2021
            d_offset = (tx_id % 365)
            tx_date = date(2021, 1, 1) + timedelta(days=d_offset)
        elif year_rand < 40:
            tx_year = 2022
            d_offset = (tx_id % 365)
            tx_date = date(2022, 1, 1) + timedelta(days=d_offset)
        elif year_rand < 80:
            tx_year = 2023
            d_offset = (tx_id % 365)
            tx_date = date(2023, 1, 1) + timedelta(days=d_offset)
        else:
            tx_year = 2024
            d_offset = (tx_id % 270)
            tx_date = date(2024, 1, 1) + timedelta(days=d_offset)

        amt = round(float(np.random.exponential(scale=350.0) + 25.0), 2)
        pm = methods[tx_id % len(methods)]
        card = cards[tx_id % len(cards)]
        curr = 'USD'
        st = statuses[tx_id % len(statuses)]
        store = (tx_id % 45) + 1
        chnl = channels[tx_id % len(channels)]
        ip = f"192.168.{(tx_id // 256) % 255}.{tx_id % 254 + 1}"
        u_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        d_fingerprint = f"fp_hash_{tx_id:08x}_{cust_id:04x}"
        sess_id = f"session_guid_{tx_id:08d}"
        payload = f'{{"cart_items": {(tx_id % 8) + 1}, "checkout_latency_ms": {(tx_id % 400) + 120}, "ip_geo": "US-EAST", "promo_applied": false}}'
        b_addr = f"{cust_id} Commerce Plaza, Floor {(cust_id % 12) + 1}, New York, NY"
        s_addr = f"{cust_id} Enterprise Distribution Ctr, Dock {(cust_id % 8) + 1}, Chicago, IL"
        tax = round(amt * 0.0825, 2)
        discount = round(amt * 0.05, 2) if (tx_id % 7 == 0) else 0.0
        fraud = True if (tx_id % 997 == 0) else False
        risk = round(float(np.random.uniform(0.01, 0.45)), 4)
        proc_code = "AUTH_200_SUCCESS" if st == 'completed' else "ERR_DECLINED_402"
        notes = f"Transaction processed through standard gateway routing node-{(tx_id % 10) + 1}"
        c_time = datetime(tx_date.year, tx_date.month, tx_date.day, (tx_id % 24), (tx_id % 60))

        wh_tx_rows.append((
            tx_id, cust_id, tx_year, tx_date, amt, pm, card, curr, st, store,
            chnl, ip, u_agent, d_fingerprint, sess_id, payload, b_addr, s_addr,
            tax, discount, fraud, risk, proc_code, notes, c_time
        ))

    con.executemany("INSERT INTO warehouse_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", wh_tx_rows)

    con.close()
    print(f"Database initialized and populated at: {db_path}")
    print(f"Customer revenue distribution data exported to: {csv_path}")
    print(f"Customer churn segments data exported to: {churn_csv_path}")
    print(f"User funnel events data exported to: {funnel_csv_path}")
    print(f"Hourly KPI metrics data exported to: {kpi_csv_path}")
    print(f"Warehouse transactions populated: 50,000 records with 25 wide columns.")
    print(f"Customers expanded populated: 2,000 records.")

if __name__ == '__main__':
    init_database()
