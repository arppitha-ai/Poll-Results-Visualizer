"""All charts. Each draw_* function paints on a given Axes so the same code
feeds both the individual PNGs and the combined dashboard image."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from . import analysis as A
from . import config as C

sns.set_theme(style="whitegrid", context="notebook")
PALETTE = "Set2"


def draw_vote_bar(df, ax):
    vs = A.vote_share(df).reset_index()
    sns.barplot(data=vs, x=C.TOOL, y="Votes", hue=C.TOOL, palette=PALETTE, legend=False, ax=ax)
    for i, row in vs.iterrows():
        ax.text(i, row["Votes"], f"{row['Share %']}%", ha="center", va="bottom", fontsize=9)
    ax.set(title="Votes per Option (with % share)", xlabel="", ylabel="Votes")
    ax.tick_params(axis="x", rotation=25)


def draw_pie(df, ax):
    vs = A.vote_share(df)
    ax.pie(vs["Votes"], labels=None, startangle=90, pctdistance=0.78,
           autopct=lambda p: f"{p:.1f}%" if p >= 4 else "",
           colors=sns.color_palette(PALETTE, len(vs)), wedgeprops={"edgecolor": "white"})
    ax.legend(vs.index, loc="center left", bbox_to_anchor=(0.95, 0.5), fontsize=9, frameon=False)
    ax.set_title("Vote Share")


def draw_recommend_donut(df, ax):
    rs = A.recommend_share(df)
    ax.pie(rs["Votes"], labels=rs.index, autopct="%1.1f%%", startangle=90,
           colors=["#66c2a5", "#fc8d62"], wedgeprops={"width": 0.4, "edgecolor": "white"})
    ax.set_title("Would You Recommend? (Yes/No)")


def draw_rating_hist(df, ax):
    sns.countplot(data=df, x=C.RATING, order=[1, 2, 3, 4, 5], hue=C.RATING, palette="Blues",
                  legend=False, ax=ax)
    ax.set(title="Satisfaction Rating Distribution (1-5)", xlabel="Rating", ylabel="Responses")


def draw_rating_box(df, ax):
    order = A.rating_by(df, C.TOOL).index
    sns.boxplot(data=df, x=C.TOOL, y=C.RATING, order=order, hue=C.TOOL, palette=PALETTE,
                legend=False, ax=ax)
    ax.set(title="Satisfaction by Option", xlabel="", ylabel="Rating")
    ax.tick_params(axis="x", rotation=25)


def draw_region_stacked(df, ax):
    A.crosstab_pct(df, C.REGION).plot(kind="bar", stacked=True, ax=ax, colormap=PALETTE, width=0.8)
    ax.set(title="Preference by Region (% within region)", xlabel="", ylabel="% of respondents")
    ax.legend(title="", fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4, frameon=False)
    ax.tick_params(axis="x", rotation=0)


def draw_age_heatmap(df, ax):
    sns.heatmap(A.crosstab_pct(df, C.AGE), annot=True, fmt=".0f", cmap="YlGnBu", ax=ax,
                cbar_kws={"label": "% within age group"})
    ax.set(title="Preference by Age Group (%)", xlabel="", ylabel="")


def draw_trend(df, ax):
    d = A.daily_trend(df)
    ax.plot(d.index, d["Responses"], marker="o", ms=3, alpha=0.5, label="Daily")
    ax.plot(d.index, d["7-day avg"], lw=2.5, label="7-day average")
    ax.set(title="Responses Over Time", xlabel="", ylabel="Responses")
    ax.legend()
    ax.tick_params(axis="x", rotation=30)


def draw_sentiment(df, ax):
    s = A.sentiment_share(df).reset_index()
    colors = {"Positive": "#66c2a5", "Neutral": "#ffd92f", "Negative": "#fc8d62", "No comment": "#b3b3b3"}
    sns.barplot(data=s, x="Sentiment", y="Votes", hue="Sentiment", palette=colors, legend=False, ax=ax)
    ax.set(title="Feedback Sentiment", xlabel="", ylabel="Comments")


def draw_wordcloud(df, ax):
    """Word cloud if `wordcloud` is installed, else a top-words bar chart."""
    text = " ".join(df[C.FEEDBACK].astype(str))
    try:
        from wordcloud import WordCloud
        wc = WordCloud(width=800, height=400, background_color="white", colormap="tab10").generate(text)
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
    except ImportError:
        words = A.keywords(df, 10)[::-1]
        ax.barh([w for w, _ in words], [c for _, c in words], color="#66c2a5")
    ax.set_title("Common Words in Feedback")


CHARTS = {
    "01_vote_bar": (draw_vote_bar, (8, 5)),
    "02_vote_pie": (draw_pie, (6, 6)),
    "03_recommend_donut": (draw_recommend_donut, (6, 6)),
    "04_rating_distribution": (draw_rating_hist, (7, 5)),
    "05_rating_by_option": (draw_rating_box, (8, 5)),
    "06_region_stacked": (draw_region_stacked, (9, 5.5)),
    "07_age_heatmap": (draw_age_heatmap, (9, 4.5)),
    "08_response_trend": (draw_trend, (9, 4.5)),
    "09_sentiment": (draw_sentiment, (6, 4.5)),
    "10_wordcloud": (draw_wordcloud, (9, 5)),
}


def save_all(df, out_dir=C.IMAGE_DIR):
    """Save every chart as its own PNG + one combined dashboard image."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, (fn, size) in CHARTS.items():
        fig, ax = plt.subplots(figsize=size)
        fn(df, ax)
        fig.tight_layout()
        p = out_dir / f"{name}.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        paths.append(p)

    fig, axes = plt.subplots(3, 3, figsize=(21, 16))
    for ax, name in zip(axes.ravel(), list(CHARTS)[:9]):
        CHARTS[name][0](df, ax)
    fig.suptitle("Poll Results Visualizer - Dashboard", fontsize=22, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    p = out_dir / "00_dashboard.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    return [p] + paths
