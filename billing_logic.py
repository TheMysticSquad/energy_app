from datetime import datetime, timedelta
import pandas as pd


def last_day_of_month(d):
    next_month = d.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


def month_diff(start, end):
    """Month count with partial month rule."""
    if start.day == last_day_of_month(start).day:
        return (end.year - start.year) * 12 + (end.month - start.month)
    else:
        return (end.year - start.year) * 12 + (end.month - start.month) + 1


def calc_fc(dis_date, agr_date, load, fc_rate):
    agr_exp = agr_date.replace(year=agr_date.year + 1)

    months_agreement = month_diff(dis_date, agr_exp)
    months_90 = month_diff(dis_date, dis_date + timedelta(days=90))

    months = max(months_agreement, months_90)

    amount = load * fc_rate * months
    return amount, months


def calc_dps(days):
    slabs = days // 32
    rate = slabs * 1.5
    return rate


def calculate_ht_bill(inputs):
    # Extract inputs
    curr = inputs["current"]
    prev = inputs["previous"]
    mf = inputs["mf"]
    rates = inputs["rates"]

    # Slot-wise EC
    ec_h1 = (curr["H1"] - prev["H1"]) * mf * rates["H1"]
    ec_h2 = (curr["H2"] - prev["H2"]) * mf * rates["H2"]
    ec_h3 = (curr["H3"] - prev["H3"]) * mf * rates["H3"]

    ec_total = ec_h1 + ec_h2 + ec_h3

    # FC
    fc, fc_months = calc_fc(
        inputs["disconnection_date"],
        inputs["agreement_date"],
        inputs["load"],
        rates["FC"]
    )

    # Subsidy
    subsidy = (curr["kVAh"] - prev["kVAh"]) * mf * rates["subsidy"]

    # ED
    ed = 0.06 * ec_total

    # Rental
    bill_months = month_diff(inputs["bill_prev_date"], inputs["bill_curr_date"])
    rental = 0.75 * (ec_total + fc) * bill_months

    # DPS
    days = (inputs["bill_curr_date"] - inputs["bill_prev_date"]).days
    dps_rate = calc_dps(days)
    dps = (ec_total + ed) * dps_rate / 100

    # Prepare table
    df = pd.DataFrame({
        "Head": [
            "EC - H1", "EC - H2", "EC - H3", "EC TOTAL",
            f"FC (Months={fc_months})",
            "Subsidy",
            "ED @6%",
            f"Rental (Months={bill_months})",
            f"DPS ({days} Days, {dps_rate}%)",
            "TOTAL BILL"
        ],
        "Amount": [
            ec_h1, ec_h2, ec_h3, ec_total,
            fc,
            subsidy,
            ed,
            rental,
            dps,
            ec_total + fc + subsidy + ed + rental + dps
        ]
    })

    return df
