# Prepaid Electricity Management System - Project Overview

## Objective

The objective of this project is to develop a **prepaid electricity management system** that allows administrators and consumers to manage prepaid accounts, simulate daily consumption, handle recharges, and generate daily billing sheets. The system provides insights into consumer usage, balance, and alerts for low balance or disconnection, while supporting future expansion for full operational readiness.

## Project Scope

* Consumer management: create, view, and update consumer details.
* Billing and tariff management: compute energy charges, fixed charges, and subsidies.
* Consumption simulation: process multiple random consumption records for testing.
* Recharge functionality: update balance dynamically and recalculate billing.
* Daily billing sheet: detailed records including consumption, charges, balance before/after, and status.
* Streamlit-based frontend for easy interaction and visualization.

## Current Status

| Feature                              | Status        |
| ------------------------------------ | ------------- |
| Consumer Management                  | ✅ Implemented |
| Billing Logic (EC, FC, Subsidy)      | ✅ Implemented |
| Daily Billing Sheet                  | ✅ Implemented |
| Recharge Handling                    | ✅ Implemented |
| Streamlit Frontend                   | ✅ Implemented |
| Batch Consumption Simulation         | ✅ Implemented |
| Defaulter List / Daily Disconnection | ❌ Pending     |
| Postpaid → Prepaid Conversion        | ❌ Pending     |
| Alerts / Notifications               | ❌ Pending     |
| User Portal with Payment Integration | ❌ Pending     |
| Live Meter Integration               | ❌ Pending     |

## Upcoming Development / Roadmap

1. Implement **daily defaulter list generation** and integrate with AMISP API.
2. Enable **postpaid → prepaid conversion** for existing consumers.
3. Build **user portal with payment gateway** for online recharge.
4. Add **alerts / notifications** for low balance and pending disconnection.
5. Integrate **live meter data ingestion** for automated consumption updates.
6. Add **adjustment / billing correction** interface for admin.

## Process Flow

```
                            +----------------------+
                            |  Consumer / User     |
                            | (Web / Mobile Portal)|
                            +----------+-----------+
                                       |
                                       | Recharge / Payment
                                       v
+-------------------+        +---------------------+
|   Consumer Class  | <----> |   Billing Logic     |
|  (Attributes,     |        | (EC, FC, Subsidy,  |
|   Balance, Status)|        |  Total Deduction,  |
+--------+----------+        |  Low Balance Alerts)|
         |                   +----------+----------+
         | Consumption / Billing Data
         v
+---------------------+
| Daily Billing Sheet  |
| (EC, FC, Subsidy,   |
|  Balance Before/After,
|  Status)            |
+----------+----------+
           |
           v
+---------------------+       +---------------------+
| Defaulter List /    | ----> | AMISP System        |
| Disconnection Job   |       | (Disconnect /       |
| Generation          |       | Reconnect)          |
+---------------------+       +---------------------+
```

**Legend:**

* ✅ Implemented
* ❌ Pending / Upcoming
