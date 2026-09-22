# Join Strategy & Architecture Documentation
## Module 2.40: SQL Joins & Multi-Table Analysis

---

### 1. Schema & Table Lineage

| Table Name | Role | Primary Key | Foreign Keys | Row Count |
| :--- | :--- | :--- | :--- | :--- |
| **`customers`** | Base Dimension | `customer_id` | *None* | 220 |
| **`orders`** | Transactional Fact | `order_id` | `customer_id` -> `customers.customer_id` | 479 |
| **`order_items`** | Line-Item Fact | `item_id` | `order_id`, `product_id` | 479 |
| **`products`** | Dimension Catalog | `product_id` | *None* | 10 |

---

### 2. Architectural Join Decisions

#### Decision 1: `customers` LEFT JOIN `orders`
- **Purpose**: Retrieve the full customer roster with their lifetime purchase activity.
- **Row Count Transformation**:
  - Base Customers: 220
  - Raw unaggregated join rows: 504 rows
  - Grouped summary rows: 220 (100% customer retention)
- **Multiplication Factor**: 129.1% expansion due to repeat orders per customer.
- **Unmatched Records**: 40 customers have placed zero orders. Retained with `NULL` order data.
- **Business Use Case**: Customer Lifetime Value (CLV), churn detection, inactive account reactivation.

#### Decision 2: `orders` LEFT JOIN `customers` (Orphaned Record Audit)
- **Purpose**: Audit referential integrity to ensure every transaction links to a registered customer.
- **Audit Findings**: 15 orders found with `customer_id = 9999` where `c.customer_id IS NULL`.
- **Root Cause Analysis**: Orders generated from legacy guest checkout or data ingestion sync gaps.
- **Action**: Flagged for reconciliation before financial book closing.

#### Decision 3: Multi-Table Lineage (`customers` -> `orders` -> `order_items` -> `products`)
- **Purpose**: Connect customer segment cohorts (Enterprise vs. SMB) to specific catalog products and line-item revenues.
- **Validation**:
  - `Enterprise Line Total`: **$249,640.00**
  - `Expected Direct Total`: **$249,640.00**
  - **Discrepancy**: **$0.00** (proves 0% duplication / zero fan-out error).

#### Decision 4: Join Order Impact
- **Rule**: Table sequence matters. Starting with `customers` as the leftmost table and chaining `LEFT JOIN` operations guarantees no customer is dropped, even if they have no orders or line items.
- If an `INNER JOIN` was positioned in the middle (e.g. `orders INNER JOIN order_items`), it would silently turn the preceding `LEFT JOIN` into an inner join if unmatched orders existed.

---

### 3. Join Comparison Summary

```text
Table: customers (220 rows) ─────────┬───────── Table: orders (479 rows)
                                     │
    ┌────────────────────────────────┼────────────────────────────────┐
    │                                │                                │
INNER JOIN: 464 rows           LEFT JOIN: 504 rows           FULL OUTER JOIN: 519 rows
- 464 valid matched orders     - 464 matched orders          - 464 matched orders
- Excludes 40 inactive users   - 40 inactive customers       - 40 inactive customers
- Excludes 15 orphaned orders  - Excludes 15 orphaned orders - 15 orphaned orders
```
