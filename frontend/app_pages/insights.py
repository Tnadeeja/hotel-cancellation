"""Interactive views of recorded reports only; no prediction/model access."""
from pathlib import Path
import altair as alt
import pandas as pd
import streamlit as st
from frontend.visuals import page_heading

REPORTS = Path(__file__).resolve().parents[2] / "reports" / "eval2"
ALGORITHMS = ["Logistic Regression", "Decision Tree", "Random Forest", "Gradient Boosting"]
METRICS = {"Accuracy": "accuracy", "Precision": "precision", "Recall": "recall", "F1": "f1", "ROC-AUC": "roc_auc"}
BLUE, GOLD, NAVY = "#164B7A", "#C9A227", "#0B1F33"

@st.cache_data(ttl=60, max_entries=6, show_spinner=False)
def read_report(filename, modified):
    return pd.read_csv(REPORTS / filename)

def report(filename, required):
    try:
        path = REPORTS / filename
        frame = read_report(filename, path.stat().st_mtime_ns)
        if not set(required).issubset(frame.columns) or frame.empty:
            raise ValueError("Missing report columns")
        return frame
    except (OSError, ValueError, pd.errors.ParserError):
        st.warning(f"The saved report {filename} is unavailable or incomplete. Its charts cannot be shown; other sections remain available.")
        return None

def show(chart, title):
    st.altair_chart(chart.properties(height=320).configure_view(stroke=None)
        .configure_axis(labelColor=NAVY, titleColor=NAVY, gridColor="#E5E9ED", labelFontSize=12)
        .configure_legend(labelColor=NAVY, title=None, orient="bottom"),
        width="stretch", alt=title)

def grouped(frame, x, series, order, series_order):
    selection = alt.selection_point(fields=[series], bind="legend")
    return alt.Chart(frame).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X(f"{x}:N", sort=order, title=None, axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset(f"{series}:N", sort=series_order),
        y=alt.Y("Value:Q", title="Recorded score", scale=alt.Scale(domain=[0,1]), axis=alt.Axis(format=".0%")),
        color=alt.Color(f"{series}:N", scale=alt.Scale(domain=series_order, range=[BLUE,GOLD])),
        opacity=alt.condition(selection, alt.value(1), alt.value(.18)),
        tooltip=[alt.Tooltip(f"{x}:N"), alt.Tooltip(f"{series}:N"), alt.Tooltip("Value:Q", format=".3%")],
    ).add_params(selection)

page_heading("RECORDED EVALUATION ? INTERACTIVE EXPLORER", "Model insights", "Explore the project's saved development and final holdout evidence. These charts are not live production performance.")
st.caption("Hover for exact values. Click grouped-chart legends to emphasize a series; click again to reset. All score axes start at zero.")
final = report("final_outer_test_results.csv", ["evaluation_population", "rows", *METRICS.values(), "tn", "fp", "fn", "tp"])
cv = report("cross_model_selected_cv_results.csv", ["algorithm", "scope", "selected_stage", "baseline_f1", "selected_mean_cv_f1", "selected_mean_cv_recall", "selected_mean_cv_roc_auc"])
oof = report("specialist_oof_comparison.csv", ["algorithm", "hotel_population", "general_f1", "specialist_f1", "f1_difference"])
overall = None
general = None
if final is not None:
    found = final.loc[final.evaluation_population.eq("Overall")]
    if len(found) == 1:
        overall = found.iloc[0]
        with st.container(horizontal=True):
            for label, field in METRICS.items():
                with st.container(border=True, width=210):
                    st.metric("F1 score" if label == "F1" else label, f"{float(overall[field]):.2%}")
        st.caption(f"Final outer test ? {int(overall['rows']):,} bookings ? Random Forest ? General-only ? Notebook 12")
    else:
        st.warning("The report must contain exactly one Overall final-test row.")
if cv is not None:
    general = cv.loc[cv.scope.eq("General")].copy()
    if len(general) != 4 or set(general.algorithm) != set(ALGORITHMS):
        st.warning("The selected General-scope report is incomplete.")
        general = None

with st.container(border=True, key="insight_card_1"):
    st.subheader("Selected Model Performance")
    st.caption("Training-only grouped CV ? General scope ? F1 was the primary selection metric. Other algorithms are not shown as final-test models.")
    if general is not None:
        chart = alt.Chart(general).mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("algorithm:N", sort=ALGORITHMS, title=None),
            x=alt.X("selected_mean_cv_f1:Q", title="Selected grouped-CV F1", scale=alt.Scale(domain=[0,1]), axis=alt.Axis(format=".0%")),
            color=alt.condition(alt.datum.algorithm == "Random Forest", alt.value(GOLD), alt.value(BLUE)),
            tooltip=[alt.Tooltip("algorithm:N", title="Algorithm"), alt.Tooltip("selected_stage:N", title="Selected stage"),
                     alt.Tooltip("selected_mean_cv_f1:Q", title="F1", format=".3%"),
                     alt.Tooltip("selected_mean_cv_recall:Q", title="Recall", format=".3%"),
                     alt.Tooltip("selected_mean_cv_roc_auc:Q", title="ROC-AUC", format=".3%")])
        show(chart, "Selected General-scope grouped-CV F1 for four algorithms")
        st.markdown("**Gold highlights Random Forest, the selected algorithm.** Selection was frozen before opening the final outer test.")

with st.container(border=True, key="insight_card_2"):
    st.subheader("Baseline vs Selected Configuration")
    st.caption("Baseline compared with the selected configuration, which may be baseline or tuned. General-scope grouped CV only.")
    if general is not None:
        data = pd.DataFrame([{"Algorithm": row.algorithm, "Configuration": name, "Value": row[field]}
            for _, row in general.iterrows() for name, field in [("Baseline", "baseline_f1"), ("Selected configuration", "selected_mean_cv_f1")]])
        show(grouped(data, "Algorithm", "Configuration", ALGORITHMS, ["Baseline", "Selected configuration"]), "Baseline versus selected General-scope F1")
        st.caption("Gradient Boosting retained its baseline configuration because tuning reduced F1; its two bars therefore have the same value.")

with st.container(border=True, key="insight_card_3"):
    st.subheader("City vs Resort Final Performance")
    st.caption("Final outer test ? The SAME General Random Forest produced both subgroup results. These are not separate City and Resort models.")
    if final is not None:
        subgroup = final.loc[final.evaluation_population.isin(["City", "Resort"])]
        if len(subgroup) == 2 and set(subgroup.evaluation_population) == {"City", "Resort"}:
            data = pd.DataFrame([{"Metric": label, "Population": row.evaluation_population, "Value": row[field]}
                for _, row in subgroup.iterrows() for label, field in METRICS.items()])
            show(grouped(data, "Metric", "Population", list(METRICS), ["City", "Resort"]), "City and Resort final-test metrics from the same General model")
        else:
            st.warning("City and Resort final-test rows are unavailable or duplicated.")

with st.container(border=True, key="insight_card_4"):
    st.subheader("Development vs Final Holdout")
    if overall is not None and general is not None:
        rf = general.loc[general.algorithm.eq("Random Forest")].iloc[0]
        data = pd.DataFrame([{"Metric": label, "Evidence": name, "Value": value}
            for label, field in [("F1", "f1"), ("Recall", "recall"), ("ROC-AUC", "roc_auc")]
            for name, value in [("Development grouped-CV", rf[f"selected_mean_cv_{field}"]), ("Final outer test", overall[field])]])
        show(grouped(data, "Metric", "Evidence", ["F1", "Recall", "ROC-AUC"], ["Development grouped-CV", "Final outer test"]), "Random Forest development versus final holdout metrics")
    st.caption("Held-out performance was close to the development estimate. Small differences are not proof that overfitting is absent. The populations and estimation procedures differ.")

with st.container(border=True, key="insight_card_5"):
    st.subheader("Overall Final-Test Confusion Matrix")
    st.caption("Recorded counts from the Overall final-test row. Rows are Actual; columns are Predicted. No predictions have been recomputed.")
    if overall is not None:
        labels = ["Not Cancelled", "Cancelled"]
        data = pd.DataFrame([{"Actual": actual, "Predicted": predicted, "Count": int(overall[field]), "Outcome": outcome}
            for actual, predicted, field, outcome in [
                (labels[0], labels[0], "tn", "True negative"), (labels[0], labels[1], "fp", "False positive"),
                (labels[1], labels[0], "fn", "False negative"), (labels[1], labels[1], "tp", "True positive")]])
        base = alt.Chart(data).encode(x=alt.X("Predicted:N", sort=labels, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Actual:N", sort=labels), tooltip=["Actual:N", "Predicted:N", "Outcome:N", alt.Tooltip("Count:Q", format=",")])
        heat = base.mark_rect(cornerRadius=5).encode(color=alt.Color("Count:Q", scale=alt.Scale(range=["#EEF1F4",BLUE,NAVY]), legend=None))
        text = base.mark_text(fontSize=22, fontWeight=600).encode(text=alt.Text("Count:Q", format=","),
            color=alt.condition(alt.datum.Count > float(data.Count.max()) / 2, alt.value("white"), alt.value(NAVY)))
        show(heat + text, "Overall recorded confusion matrix, actual versus predicted cancellation")

with st.container(border=True, key="insight_card_6"):
    st.subheader("General vs Hotel-Specific Models")
    st.caption("Training-only grouped OOF ? Random Forest only ? Same-hotel comparisons used to freeze routing before the final outer test.")
    if oof is not None:
        specialists = oof.loc[oof.algorithm.eq("Random Forest")]
        if len(specialists) == 2 and set(specialists.hotel_population) == {"City", "Resort"}:
            data = pd.DataFrame([{"Hotel": row.hotel_population, "Model scope": name, "Value": row[field]}
                for _, row in specialists.iterrows() for name, field in [("General on same hotel", "general_f1"), ("Hotel specialist", "specialist_f1")]])
            show(grouped(data, "Hotel", "Model scope", ["City", "Resort"], ["General on same hotel", "Hotel specialist"]), "Random Forest General versus specialist same-hotel OOF F1")
            with st.container(horizontal=True):
                for _, row in specialists.iterrows():
                    with st.container(border=True, width=270):
                        st.metric(f"{row.hotel_population}: specialist ? General", f"{float(row.f1_difference)*100:+.3f} pp")
            st.caption("pp = percentage points. Differences use the recorded specialist-minus-General F1 values.")
            st.write("Random Forest specialist F1 was slightly lower on both same-hotel comparisons. General-only routing was therefore frozen before the final outer test. This evidence is algorithm-dependent; it does not mean specialist models are generally worse.")
        else:
            st.warning("The Random Forest specialist comparison is incomplete.")
st.caption("Sources: cross_model_selected_cv_results.csv ? specialist_oof_comparison.csv ? final_outer_test_results.csv. This page reads reports only. The deployment refit does not replace the recorded final-test results.")
