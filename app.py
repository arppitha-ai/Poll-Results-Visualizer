"""Streamlit dashboard.  Run:  streamlit run app.py"""
import pandas as pd
import plotly.express as px
import streamlit as st

from src import analysis as A
from src import config as C
from src.cleaning import clean_poll_data
from src.generate_data import generate_poll_data
from src.insights import generate_insights

st.set_page_config(page_title="Poll Results Visualizer", page_icon="📊", layout="wide")
st.title("📊 Poll Results Visualizer")
st.caption("Upload a poll CSV (e.g. Google Forms export) or explore the built-in synthetic poll.")


@st.cache_data
def load(file_bytes=None, n=600, seed=42):
    raw = pd.read_csv(file_bytes) if file_bytes is not None else generate_poll_data(n, seed)
    return clean_poll_data(raw)


st.sidebar.header("Data")
up = st.sidebar.file_uploader("Upload poll CSV", type="csv")
try:
    df_all, log = load(up)
except Exception as e:
    st.error(f"Could not process this file: {e}. Expected columns: "
             f"{C.TIMESTAMP}, {C.AGE}, {C.GENDER}, {C.REGION}, {C.TOOL}, {C.RECOMMEND}, {C.RATING}, {C.FEEDBACK}")
    st.stop()

st.sidebar.header("Filters")
def pick(label, col):
    opts = sorted(df_all[col].unique())
    return st.sidebar.multiselect(label, opts, default=opts)

regions, ages, genders = pick("Region", C.REGION), pick("Age group", C.AGE), pick("Gender", C.GENDER)
dmin, dmax = df_all["Date"].min().date(), df_all["Date"].max().date()
dates = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
start, end = (dates if len(dates) == 2 else (dmin, dmax))

df = df_all[df_all[C.REGION].isin(regions) & df_all[C.AGE].isin(ages) & df_all[C.GENDER].isin(genders)
            & df_all["Date"].between(pd.Timestamp(start), pd.Timestamp(end))]
if df.empty:
    st.warning("No responses match these filters.")
    st.stop()

vs = A.vote_share(df)
rs = A.rating_summary(df)
rec = A.recommend_share(df)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Responses", len(df))
k2.metric("Leading option", vs.index[0], f"{vs.iloc[0]['Share %']}%")
k3.metric("Avg satisfaction", f"{rs['mean']}/5", f"{rs['pct_satisfied']}% rated 4-5")
k4.metric("Would recommend", f"{rec.loc['Yes', 'Share %'] if 'Yes' in rec.index else 0}%")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Demographics", "Trend", "Feedback", "Insights & Data"])

with tab1:
    c1, c2 = st.columns(2)
    v = vs.reset_index()
    c1.plotly_chart(px.bar(v, x=C.TOOL, y="Votes", color=C.TOOL, text="Share %", title="Votes per option"),
                    use_container_width=True)
    c2.plotly_chart(px.pie(v, names=C.TOOL, values="Votes", hole=0.4, title="Vote share"),
                    use_container_width=True)
    c3, c4 = st.columns(2)
    c3.plotly_chart(px.histogram(df, x=C.RATING, nbins=5, title="Satisfaction distribution (1-5)"),
                    use_container_width=True)
    c4.plotly_chart(px.pie(rec.reset_index(), names=C.RECOMMEND, values="Votes", hole=0.5,
                           title="Would you recommend?"), use_container_width=True)

with tab2:
    group = st.radio("Compare by", [C.REGION, C.AGE, C.GENDER], horizontal=True)
    ct = A.crosstab_pct(df, group)
    st.plotly_chart(px.bar(ct, barmode="stack", title=f"Preference by {group} (% within group)",
                           labels={"value": "% of respondents"}), use_container_width=True)
    st.dataframe(A.rating_by(df, group), use_container_width=True)

with tab3:
    d = A.daily_trend(df).reset_index()
    st.plotly_chart(px.line(d, x="Date", y=["Responses", "7-day avg"], markers=True,
                            title="Responses over time"), use_container_width=True)

with tab4:
    s = A.sentiment_share(df).reset_index()
    st.plotly_chart(px.bar(s, x="Sentiment", y="Votes", color="Sentiment", title="Feedback sentiment"),
                    use_container_width=True)
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        text = " ".join(df[C.FEEDBACK].astype(str))
        if text.strip():
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.imshow(WordCloud(width=800, height=400, background_color="white").generate(text))
            ax.axis("off")
            st.pyplot(fig)
    except ImportError:
        st.info("Install `wordcloud` to see the word cloud (pip install wordcloud).")
    st.write("Top keywords:", ", ".join(f"{w} ({c})" for w, c in A.keywords(df, 10)))

with tab5:
    st.subheader("Auto-generated insights")
    for line in generate_insights(df):
        st.markdown(f"- {line}")
    st.subheader("Cleaning log")
    st.json(log)
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇ Download cleaned data", df.to_csv(index=False), "poll_data_cleaned.csv", "text/csv")
