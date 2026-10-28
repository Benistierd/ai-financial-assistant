"""Home / Overview page. Run with:  streamlit run app.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

from src import analytics as an  # noqa: E402
from src import config, ui  # noqa: E402
from src import database as db  # noqa: E402
from src import visualizations as viz  # noqa: E402
from src.formatting import format_inr, format_pct  # noqa: E402
from src.summary import build_financial_summary  # noqa: E402

ui.setup_page("Home", "💰")
st.title("💰 AI Financial Advisor")
st.caption("Personalised budgeting and educational investment guidance. All amounts are in Indian rupees (₹).")

if db.is_first_run():
    st.subheader("Welcome! Let's get you started")
    st.write("Choose how to begin. The demo data is fully synthetic, so no real financial records are needed.")
    if st.button("Load synthetic demo data", type="primary"):
        n = db.load_demo_data()
        st.success(f"Loaded {n} demo transactions, a demo profile and two demo goals.")
        st.rerun()
    st.markdown("**Or start fresh:** enter your profile below, then add transactions on the Transactions page.")
    if ui.profile_form(None, key="first_run_profile"):
        st.rerun()
    with st.expander("Privacy notice and disclaimer"):
        st.write(config.PRIVACY_NOTICE)
        st.write(config.DISCLAIMER)
    st.stop()

df, profile, goals, budgets = ui.load_all()
if df.empty:
    st.info("Your profile is saved. Add transactions on the **Transactions** page (or import a CSV) to see analytics.")
    st.stop()

month = ui.month_selector(df, key="home_month")
kpis = an.compute_kpis(df, month, profile)
if kpis["income_source"] == "profile":
    st.caption("No income transactions this month, so income comes from your profile.")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Income", format_inr(kpis["income"]))
c2.metric("Expenses", format_inr(kpis["expenses"]))
c3.metric("Remaining balance", format_inr(kpis["balance"]))
c4.metric("Savings rate", format_pct(kpis["savings_rate"]))
c5.metric("Estimated total savings", format_inr(kpis["total_savings"]))
st.caption("Total savings = existing savings from your profile + net savings (income minus expenses) across all tracked months.")

ef = kpis["emergency_fund"]
st.subheader("Emergency savings progress")
if ef["defined"]:
    st.progress(min(ef["progress_pct"] / 100, 1.0),
                text=f"{format_inr(ef['current'])} of {format_inr(ef['target'])} target (6 months of essential spending), "
                     f"covering about {ef['months_covered']:.1f} months")
else:
    st.write("Add expenses so the app can estimate your essential monthly spending.")

left, right = st.columns(2)
with left:
    st.plotly_chart(viz.category_donut(an.category_breakdown(df, month), f"Spending by category, {month}"))
with right:
    st.plotly_chart(viz.income_vs_expenses(an.monthly_summary(df)))

summary = build_financial_summary(df, profile, goals, month, budgets)
st.subheader("Top budget suggestions")
if summary["recommendations"]:
    for r in summary["recommendations"][:3]:
        st.warning(f"**{r['category'].title()}**: spent {format_inr(r['current'])} vs usual {format_inr(r['usual'])}. "
                   f"Suggested limit {format_inr(r['suggested_limit'])} (could save about "
                   f"{format_inr(r['potential_monthly_saving'])} a month). See the Budget Planner for the full reasoning.")
else:
    st.success("No category stands out as unusually high compared with your own history.")
st.caption(config.DISCLAIMER)
