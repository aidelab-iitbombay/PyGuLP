# PyGuLP Worked Examples

This directory contains three worked examples demonstrating weighted goal linear programming with PyGuLP.

Each example includes:

- a Jupyter notebook (`.ipynb`) containing the constructed example data and explanatory context; and
- a runnable Python script (`.py`) containing the corresponding PyGuLP model.

The numerical datasets are constructed examples for demonstrating modelling patterns and should not be interpreted as estimates from a specific hospital, insurer, or health system.

---

## 1. Hospital waiting-time allocation

Files:

- [`HospitalWaitingTime.ipynb`](HospitalWaitingTime.ipynb)
- [`HospitalWaitingTime.py`](HospitalWaitingTime.py)

### Reference solution

```text
Status: Optimal
------------------------------
Scheduling Results:
Group      | Time Band  | Scheduled  | Target     | Goal Met?
Punctual   | 30         | 114        | 114        | YES
Punctual   | 45         | 114        | 120        | NO
Late       | 30         | 18         | 18         | YES
Late       | 45         | 36         | 60         | NO
------------------------------
Total Punctual Scheduled: 114.0 / 120
Total Late Scheduled:     36.0 / 60
Total Slots Used:         150.0 / 150
```

The corresponding weighted under-achievement objective is **30**.

This model has multiple equivalent optimal allocations because the remaining 45-minute capacity can be redistributed between the two groups without changing the optimal weighted objective. Therefore, an alternative allocation with the same objective value and satisfied hard constraints may also be optimal.

---

## 2. Outpatient chemotherapy resource allocation and turnaround time

Files:

- [`TATChemo.ipynb`](TATChemo.ipynb)
- [`TATChemo.py`](TATChemo.py)

### Reference solution


```text
Status: Optimal
Objective value: 116.0400
Total cost: 4040.00 (budget 6000.00)
Served patients: 60.00
Effective infusion staff: 5.00
Infusion capacity: 80.00
```

Staffing:

```text
Unit           Staff
Triage           3.0
Consultation     4.0
Infusion         5.0
```

Selected options:

```text
Option_ID                 Selected
INF_TEMPLATE_BASE            1
INF_TEMPLATE_EXTENDED        0
INF_OVERFLOW_BEDS            0
```

Class outcomes:

```text
Class          Service_Prop   Served   TAT    TAT_Target   TAT_Overrun   Access_Shortfall
Chemo_Long        1.0         10.0    288.0      270.0         18.0             0.0
Chemo_Short       1.0         20.0    202.0      180.0         22.0             0.0
Followup          1.0         30.0    104.0       90.0         14.0             0.0
```

The objective is:

```text
TAT deviation component:
3 × 18 + 2 × 22 + 1 × 14 = 112

Cost component:
0.001 × 4040 = 4.04

Total objective:
112 + 4.04 = 116.04
```

---

## 3. Subsidized health-insurance premium design

Files:

- [`Insurance_Premium_Calculation.ipynb`](Insurance_Premium_Calculation.ipynb)
- [`Insurance_Premium_Calculation.py`](Insurance_Premium_Calculation.py)

### Reference solution

```text
Status: Optimal
Objective value: 0.260220

Selected premium/subsidy packages:
                   Segment Option_ID Enrollee_Premium Subsidy_per_Enrollee Expected_TakeUp Expected_Enrollees Claim_Cost_per_Enrollee Expected_Surplus
    Informal_Young_LowRisk      IY_B            2,500                4,000           84.0%              1,008                   4,700        1,008,000
Informal_Family_MediumRisk      IF_B            4,000                7,000           82.0%                820                   8,500        1,312,000
   SelfEmployed_MiddleRisk      SE_C           12,000                  500           69.0%                621                  11,400           62,100
Salaried_Family_MediumRisk      SF_B           14,500                    0           89.0%              1,157                  12,600          925,600
            Older_HighRisk      OH_B           11,000               19,000           86.0%                516                  25,500        1,599,600

Portfolio outcomes:
  Expected enrollees:         4,122 / 5,000
  Overall coverage:           82.44% (target 82%)
  Vulnerable coverage:        83.09% (target 88%)
  High-risk coverage:         86.00% (target 86%)
  Subsidy spend:              19,886,500.00 (budget 20,000,000.00)
  Expected revenue:           55,591,000.00
  Expected claims:            46,523,200.00
  Expected admin cost:        4,160,500.00
  Expected portfolio surplus: 4,907,300.00 (target 5,000,000.00)
  Vulnerable premium burden:  1.52% (target <= 1.7%)

Normalized goal deviations:
  Overall_Coverage             d_minus=0.000000, d_plus=0.005366
  Vulnerable_Coverage          d_minus=0.055785, d_plus=0.000000
  HighRisk_Coverage            d_minus=0.000000, d_plus=0.000000
  Portfolio_Surplus            d_minus=0.018540, d_plus=0.000000
  Vulnerable_Affordability     d_minus=0.108734, d_plus=0.000000
```

The non-zero objective is intentional: under the stated subsidy budget and policy targets, the model cannot attain every aspirational target simultaneously.

---

## Interpreting the reference solutions

The reference results above provide benchmark outputs for the stated constructed datasets and default weights.

For models with multiple equivalent optima, a solver may return a different decision-variable allocation with the same optimal objective and feasibility conditions.
