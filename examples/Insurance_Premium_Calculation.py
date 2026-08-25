"""
Weighted goal-programming example for subsidized health-insurance design.

The numerical values in this example are synthetic. They are constructed to
represent health-economic trade-offs documented in the literature: premium
sensitivity, adverse selection, affordability, subsidy requirements, access
for high-risk members, and portfolio financial sustainability.

For each population segment, the model selects exactly one premium/subsidy
package. Hard constraints define the feasible policy space; weighted goals
then determine how competing policy aspirations are balanced.
"""

import pandas as pd
import pulp

from pygulp.constraint import Constraint
from pygulp.core import GLPModel
from pygulp.enums import ConstraintSense, GoalSense
from pygulp.goal import Goal


# -------------------------------------------------
# 1. Eligible population segments
# -------------------------------------------------

segments = pd.DataFrame(
    {
        "Segment": [
            "Informal_Young_LowRisk",
            "Informal_Family_MediumRisk",
            "SelfEmployed_MiddleRisk",
            "Salaried_Family_MediumRisk",
            "Older_HighRisk",
        ],
        "Employment_Type": [
            "Informal",
            "Informal",
            "Self-employed",
            "Salaried",
            "Retired/Older",
        ],
        "Income_Band": [
            "Low",
            "Low",
            "Middle",
            "Middle-High",
            "Low-Middle",
        ],
        "Risk_Band": [
            "Low",
            "Medium",
            "Medium",
            "Medium",
            "High",
        ],
        "Vulnerable_Group": [1, 1, 0, 0, 0],
        "High_Risk_Group": [0, 0, 0, 0, 1],
        "Eligible_Lives": [1200, 1000, 900, 1300, 600],
        "Annual_Income_Proxy": [
            180000.0,
            240000.0,
            420000.0,
            720000.0,
            300000.0,
        ],
        "Admin_Cost_per_Enrollee": [
            800.0,
            900.0,
            1000.0,
            1100.0,
            1400.0,
        ],
    }
)


# -------------------------------------------------
# 2. Candidate premium / subsidy packages
# -------------------------------------------------
#
# Lower enrollee contributions generally increase expected take-up but
# require more subsidy. Higher enrollee contributions reduce take-up and
# increase expected claims among those who remain enrolled, representing
# adverse selection.

price_options = pd.DataFrame(
    {
        "Segment": [
            "Informal_Young_LowRisk",
            "Informal_Young_LowRisk",
            "Informal_Young_LowRisk",
            "Informal_Young_LowRisk",
            "Informal_Family_MediumRisk",
            "Informal_Family_MediumRisk",
            "Informal_Family_MediumRisk",
            "Informal_Family_MediumRisk",
            "SelfEmployed_MiddleRisk",
            "SelfEmployed_MiddleRisk",
            "SelfEmployed_MiddleRisk",
            "SelfEmployed_MiddleRisk",
            "Salaried_Family_MediumRisk",
            "Salaried_Family_MediumRisk",
            "Salaried_Family_MediumRisk",
            "Salaried_Family_MediumRisk",
            "Older_HighRisk",
            "Older_HighRisk",
            "Older_HighRisk",
            "Older_HighRisk",
        ],
        "Option_ID": [
            "IY_A", "IY_B", "IY_C", "IY_D",
            "IF_A", "IF_B", "IF_C", "IF_D",
            "SE_A", "SE_B", "SE_C", "SE_D",
            "SF_A", "SF_B", "SF_C", "SF_D",
            "OH_A", "OH_B", "OH_C", "OH_D",
        ],
        "Enrollee_Premium": [
            1500.0, 2500.0, 3500.0, 4500.0,
            2500.0, 4000.0, 5500.0, 7000.0,
            9000.0, 10500.0, 12000.0, 13500.0,
            13000.0, 14500.0, 16000.0, 18000.0,
            8000.0, 11000.0, 14000.0, 17000.0,
        ],
        "Subsidy_per_Enrollee": [
            5000.0, 4000.0, 3000.0, 2000.0,
            8500.0, 7000.0, 5500.0, 4000.0,
            2500.0, 1500.0, 500.0, 0.0,
            0.0, 0.0, 0.0, 0.0,
            22000.0, 19000.0, 16000.0, 13000.0,
        ],
        "Expected_TakeUp": [
            0.92, 0.84, 0.72, 0.58,
            0.90, 0.82, 0.70, 0.55,
            0.88, 0.80, 0.69, 0.56,
            0.94, 0.89, 0.80, 0.68,
            0.93, 0.86, 0.74, 0.60,
        ],
        "Expected_Claim_Cost_per_Enrollee": [
            4300.0, 4700.0, 5200.0, 6000.0,
            7800.0, 8500.0, 9400.0, 10500.0,
            10000.0, 10600.0, 11400.0, 12500.0,
            12200.0, 12600.0, 13400.0, 14600.0,
            24000.0, 25500.0, 27500.0, 30000.0,
        ],
    }
)


# -------------------------------------------------
# 3. Derived option-level economics
# -------------------------------------------------

option_data = price_options.merge(
    segments[
        [
            "Segment",
            "Eligible_Lives",
            "Annual_Income_Proxy",
            "Admin_Cost_per_Enrollee",
            "Vulnerable_Group",
            "High_Risk_Group",
        ]
    ],
    on="Segment",
    how="left",
)

option_data["Gross_Premium_Received"] = (
    option_data["Enrollee_Premium"]
    + option_data["Subsidy_per_Enrollee"]
)
option_data["Expected_Enrollees"] = (
    option_data["Eligible_Lives"] * option_data["Expected_TakeUp"]
)
option_data["Expected_Subsidy_Spend"] = (
    option_data["Expected_Enrollees"] * option_data["Subsidy_per_Enrollee"]
)
option_data["Expected_Revenue"] = (
    option_data["Expected_Enrollees"] * option_data["Gross_Premium_Received"]
)
option_data["Expected_Claims"] = (
    option_data["Expected_Enrollees"]
    * option_data["Expected_Claim_Cost_per_Enrollee"]
)
option_data["Expected_Admin_Cost"] = (
    option_data["Expected_Enrollees"]
    * option_data["Admin_Cost_per_Enrollee"]
)
option_data["Expected_Surplus"] = (
    option_data["Expected_Revenue"]
    - option_data["Expected_Claims"]
    - option_data["Expected_Admin_Cost"]
)
option_data["Premium_Income_Ratio"] = (
    option_data["Enrollee_Premium"] / option_data["Annual_Income_Proxy"]
)


# -------------------------------------------------
# 4. Portfolio constraints and aspirational goals
# -------------------------------------------------

global_params = {
    # Hard constraints / policy guardrails
    "Subsidy_Budget": 20_000_000.0,
    "Min_Portfolio_Surplus": 0.0,
    "Max_Vulnerable_Premium_Income_Ratio": 0.03,
    "Min_Vulnerable_Coverage_Floor": 0.60,
    "Min_HighRisk_Coverage_Floor": 0.60,

    # Aspirational goals
    "Target_Overall_Coverage": 0.82,
    "Target_Vulnerable_Coverage": 0.88,
    "Target_HighRisk_Coverage": 0.86,
    "Target_Portfolio_Surplus": 5_000_000.0,
    "Target_Avg_Vulnerable_Premium_Income_Ratio": 0.017,
}


# -------------------------------------------------
# 5. Helpers
# -------------------------------------------------

S = segments["Segment"].tolist()
K = price_options["Option_ID"].tolist()

segment_stats = segments.set_index("Segment").to_dict("index")
option_stats = option_data.set_index("Option_ID").to_dict("index")

options_by_segment = {
    s: option_data.loc[option_data["Segment"] == s, "Option_ID"].tolist()
    for s in S
}

vulnerable_segments = [
    s for s in S if segment_stats[s]["Vulnerable_Group"] == 1
]

high_risk_segments = [
    s for s in S if segment_stats[s]["High_Risk_Group"] == 1
]

total_eligible_lives = float(segments["Eligible_Lives"].sum())

vulnerable_eligible_lives = float(
    segments.loc[
        segments["Vulnerable_Group"] == 1,
        "Eligible_Lives",
    ].sum()
)

high_risk_eligible_lives = float(
    segments.loc[
        segments["High_Risk_Group"] == 1,
        "Eligible_Lives",
    ].sum()
)


# -------------------------------------------------
# 6. Build GLP model
# -------------------------------------------------

model = GLPModel(
    name="Subsidized_Health_Insurance_Design",
    minimize=True,
)

# y[k] = 1 if premium/subsidy package k is selected.
y = {
    k: model.add_variable(
        f"select_{k}",
        low_bound=0,
        up_bound=1,
        cat="Binary",
    )
    for k in K
}


# -------------------------------------------------
# 7. Portfolio expressions
# -------------------------------------------------

total_enrollees_expr = pulp.lpSum(
    option_stats[k]["Expected_Enrollees"] * y[k] for k in K
)

total_subsidy_expr = pulp.lpSum(
    option_stats[k]["Expected_Subsidy_Spend"] * y[k] for k in K
)

total_surplus_expr = pulp.lpSum(
    option_stats[k]["Expected_Surplus"] * y[k] for k in K
)

vulnerable_enrollees_expr = pulp.lpSum(
    option_stats[k]["Expected_Enrollees"] * y[k]
    for k in K
    if option_stats[k]["Vulnerable_Group"] == 1
)

high_risk_enrollees_expr = pulp.lpSum(
    option_stats[k]["Expected_Enrollees"] * y[k]
    for k in K
    if option_stats[k]["High_Risk_Group"] == 1
)

# Population-weighted premium-to-income burden among vulnerable groups.
# Eligible lives are fixed weights, which keeps the expression linear.
avg_vulnerable_premium_burden_expr = (
    pulp.lpSum(
        option_stats[k]["Premium_Income_Ratio"]
        * option_stats[k]["Eligible_Lives"]
        * y[k]
        for k in K
        if option_stats[k]["Vulnerable_Group"] == 1
    )
    / vulnerable_eligible_lives
)


# -------------------------------------------------
# 8. Hard constraints
# -------------------------------------------------

# A. Select exactly one premium/subsidy package for each segment.
for s in S:
    model.add_constraint(
        Constraint(
            name=f"One_Package_{s}",
            expression=pulp.lpSum(y[k] for k in options_by_segment[s]),
            sense=ConstraintSense.EQ,
            rhs=1.0,
        )
    )

# B. Annual subsidy / cross-subsidy budget.
model.add_constraint(
    Constraint(
        name="Subsidy_Budget",
        expression=total_subsidy_expr,
        sense=ConstraintSense.LE,
        rhs=global_params["Subsidy_Budget"],
    )
)

# C. The expected portfolio cannot run at a loss.
model.add_constraint(
    Constraint(
        name="Nonnegative_Portfolio_Surplus",
        expression=total_surplus_expr,
        sense=ConstraintSense.GE,
        rhs=global_params["Min_Portfolio_Surplus"],
    )
)

# D. Vulnerable groups cannot be offered a package whose enrollee premium
# exceeds the maximum policy-defined share of income.
for s in vulnerable_segments:
    selected_premium_burden_expr = pulp.lpSum(
        option_stats[k]["Premium_Income_Ratio"] * y[k]
        for k in options_by_segment[s]
    )

    model.add_constraint(
        Constraint(
            name=f"Affordability_Guardrail_{s}",
            expression=selected_premium_burden_expr,
            sense=ConstraintSense.LE,
            rhs=global_params["Max_Vulnerable_Premium_Income_Ratio"],
        )
    )

# E. Minimum vulnerable-group coverage floor.
model.add_constraint(
    Constraint(
        name="Minimum_Vulnerable_Coverage",
        expression=vulnerable_enrollees_expr,
        sense=ConstraintSense.GE,
        rhs=(
            global_params["Min_Vulnerable_Coverage_Floor"]
            * vulnerable_eligible_lives
        ),
    )
)

# F. Minimum high-risk coverage floor.
model.add_constraint(
    Constraint(
        name="Minimum_HighRisk_Coverage",
        expression=high_risk_enrollees_expr,
        sense=ConstraintSense.GE,
        rhs=(
            global_params["Min_HighRisk_Coverage_Floor"]
            * high_risk_eligible_lives
        ),
    )
)


# -------------------------------------------------
# 9. Aspirational goals
# -------------------------------------------------
#
# Goal expressions are normalized around 1.0 so monetary deviations do not
# dominate percentage deviations simply because of scale.
#
# Default illustrative policy weights:
#   vulnerable coverage = 4
#   high-risk coverage  = 4
#   affordability       = 3
#   overall coverage    = 2
#   portfolio surplus   = 2

goal_weights = {}

# Goal 1. Overall coverage >= 82%.
overall_coverage_target_count = (
    global_params["Target_Overall_Coverage"] * total_eligible_lives
)

model.add_goal(
    Goal(
        name="Overall_Coverage",
        expression=total_enrollees_expr / overall_coverage_target_count,
        target=1.0,
        sense=GoalSense.MINIMIZE_OVER,
        weight=2.0,
    )
)
goal_weights["Overall_Coverage"] = (2.0, 0.0)

# Goal 2. Vulnerable-group coverage >= 88%.
vulnerable_coverage_target_count = (
    global_params["Target_Vulnerable_Coverage"]
    * vulnerable_eligible_lives
)

model.add_goal(
    Goal(
        name="Vulnerable_Coverage",
        expression=(
            vulnerable_enrollees_expr / vulnerable_coverage_target_count
        ),
        target=1.0,
        sense=GoalSense.MINIMIZE_OVER,
        weight=4.0,
    )
)
goal_weights["Vulnerable_Coverage"] = (4.0, 0.0)

# Goal 3. High-risk coverage >= 86%.
high_risk_coverage_target_count = (
    global_params["Target_HighRisk_Coverage"]
    * high_risk_eligible_lives
)

model.add_goal(
    Goal(
        name="HighRisk_Coverage",
        expression=high_risk_enrollees_expr / high_risk_coverage_target_count,
        target=1.0,
        sense=GoalSense.MINIMIZE_OVER,
        weight=4.0,
    )
)
goal_weights["HighRisk_Coverage"] = (4.0, 0.0)

# Goal 4. Expected portfolio surplus >= INR 5 million.
surplus_target = float(global_params["Target_Portfolio_Surplus"])

model.add_goal(
    Goal(
        name="Portfolio_Surplus",
        expression=total_surplus_expr / surplus_target,
        target=1.0,
        sense=GoalSense.MINIMIZE_OVER,
        weight=2.0,
    )
)
goal_weights["Portfolio_Surplus"] = (2.0, 0.0)

# Goal 5. Keep vulnerable-group premium burden at or below 1.7% of income.
affordability_target = float(
    global_params["Target_Avg_Vulnerable_Premium_Income_Ratio"]
)

model.add_goal(
    Goal(
        name="Vulnerable_Affordability",
        expression=avg_vulnerable_premium_burden_expr / affordability_target,
        target=1.0,
        sense=GoalSense.MINIMIZE_UNDER,
        weight=3.0,
    )
)
goal_weights["Vulnerable_Affordability"] = (0.0, 3.0)


# -------------------------------------------------
# 10. Solve weighted goal-programming model
# -------------------------------------------------

result = model.solve_weighted(goal_weights=goal_weights)


# -------------------------------------------------
# 11. Report selected policy packages
# -------------------------------------------------

print(f"Status: {result['status']}")
print(f"Objective value: {result['objective']:.6f}")

selected_rows = []

for s in S:
    for k in options_by_segment[s]:
        selected = result["variables"][f"select_{k}"]

        if selected is not None and selected > 0.5:
            row = option_stats[k]
            selected_rows.append(
                {
                    "Segment": s,
                    "Option_ID": k,
                    "Enrollee_Premium": row["Enrollee_Premium"],
                    "Subsidy_per_Enrollee": row["Subsidy_per_Enrollee"],
                    "Expected_TakeUp": row["Expected_TakeUp"],
                    "Expected_Enrollees": row["Expected_Enrollees"],
                    "Claim_Cost_per_Enrollee": row[
                        "Expected_Claim_Cost_per_Enrollee"
                    ],
                    "Expected_Surplus": row["Expected_Surplus"],
                }
            )

selected_df = pd.DataFrame(selected_rows)

print("\nSelected premium/subsidy packages:")
print(
    selected_df.to_string(
        index=False,
        formatters={
            "Enrollee_Premium": lambda x: f"{x:,.0f}",
            "Subsidy_per_Enrollee": lambda x: f"{x:,.0f}",
            "Expected_TakeUp": lambda x: f"{x:.1%}",
            "Expected_Enrollees": lambda x: f"{x:,.0f}",
            "Claim_Cost_per_Enrollee": lambda x: f"{x:,.0f}",
            "Expected_Surplus": lambda x: f"{x:,.0f}",
        },
    )
)


# -------------------------------------------------
# 12. Portfolio outcomes
# -------------------------------------------------

selected_options = {
    k
    for k in K
    if (
        result["variables"][f"select_{k}"] is not None
        and result["variables"][f"select_{k}"] > 0.5
    )
}

total_enrollees = sum(
    option_stats[k]["Expected_Enrollees"] for k in selected_options
)
total_subsidy = sum(
    option_stats[k]["Expected_Subsidy_Spend"] for k in selected_options
)
total_revenue = sum(
    option_stats[k]["Expected_Revenue"] for k in selected_options
)
total_claims = sum(
    option_stats[k]["Expected_Claims"] for k in selected_options
)
total_admin_cost = sum(
    option_stats[k]["Expected_Admin_Cost"] for k in selected_options
)
total_surplus = sum(
    option_stats[k]["Expected_Surplus"] for k in selected_options
)

vulnerable_enrollees = sum(
    option_stats[k]["Expected_Enrollees"]
    for k in selected_options
    if option_stats[k]["Vulnerable_Group"] == 1
)

high_risk_enrollees = sum(
    option_stats[k]["Expected_Enrollees"]
    for k in selected_options
    if option_stats[k]["High_Risk_Group"] == 1
)

overall_coverage = total_enrollees / total_eligible_lives
vulnerable_coverage = vulnerable_enrollees / vulnerable_eligible_lives
high_risk_coverage = high_risk_enrollees / high_risk_eligible_lives

avg_vulnerable_premium_burden = (
    sum(
        option_stats[k]["Premium_Income_Ratio"]
        * option_stats[k]["Eligible_Lives"]
        for k in selected_options
        if option_stats[k]["Vulnerable_Group"] == 1
    )
    / vulnerable_eligible_lives
)

print("\nPortfolio outcomes:")
print(
    f"  Expected enrollees:         "
    f"{total_enrollees:,.0f} / {total_eligible_lives:,.0f}"
)
print(
    f"  Overall coverage:           "
    f"{overall_coverage:.2%} "
    f"(target {global_params['Target_Overall_Coverage']:.0%})"
)
print(
    f"  Vulnerable coverage:        "
    f"{vulnerable_coverage:.2%} "
    f"(target {global_params['Target_Vulnerable_Coverage']:.0%})"
)
print(
    f"  High-risk coverage:         "
    f"{high_risk_coverage:.2%} "
    f"(target {global_params['Target_HighRisk_Coverage']:.0%})"
)
print(
    f"  Subsidy spend:              "
    f"{total_subsidy:,.2f} "
    f"(budget {global_params['Subsidy_Budget']:,.2f})"
)
print(f"  Expected revenue:           {total_revenue:,.2f}")
print(f"  Expected claims:            {total_claims:,.2f}")
print(f"  Expected admin cost:        {total_admin_cost:,.2f}")
print(
    f"  Expected portfolio surplus: {total_surplus:,.2f} "
    f"(target {global_params['Target_Portfolio_Surplus']:,.2f})"
)
print(
    f"  Vulnerable premium burden:  "
    f"{avg_vulnerable_premium_burden:.2%} "
    f"(target <= "
    f"{global_params['Target_Avg_Vulnerable_Premium_Income_Ratio']:.1%})"
)


# -------------------------------------------------
# 13. Goal deviations
# -------------------------------------------------

print("\nNormalized goal deviations:")

for goal_name, (d_minus, d_plus) in result["deviations"].items():
    print(
        f"  {goal_name:<28} "
        f"d_minus={d_minus:.6f}, "
        f"d_plus={d_plus:.6f}"
    )