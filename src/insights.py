"""Turn the numbers into plain-English findings."""
from . import analysis as A
from . import config as C


def generate_insights(df) -> list[str]:
    n = len(df)
    out = []

    vs = A.vote_share(df)
    top, second = vs.index[0], vs.index[1]
    moe = A.margin_of_error(vs.iloc[0]["Share %"], n)
    gap = round(vs.iloc[0]["Share %"] - vs.iloc[1]["Share %"], 1)
    verdict = ("a clear lead" if gap > 2 * moe else
               "a likely but not conclusive lead - collect more responses to confirm" if gap > moe
               else "too close to call")
    out.append(f"**{top}** leads with {vs.iloc[0]['Share %']}% of votes (±{moe} pts, 95% confidence), "
               f"{gap} pts ahead of {second}: {verdict}.")

    s = A.rating_summary(df)
    out.append(f"Average satisfaction is **{s['mean']}/5** (median {s['median']}); "
               f"{s['pct_satisfied']}% rated 4-5 and {s['pct_dissatisfied']}% rated 1-2.")
    rb = A.rating_by(df[df[C.TOOL] != "Other"], C.TOOL)
    out.append(f"Happiest users: **{rb.index[0]}** ({rb.iloc[0]['Avg Rating']}); "
               f"least happy: **{rb.index[-1]}** ({rb.iloc[-1]['Avg Rating']}).")

    reg = A.leader_by_group(df, C.REGION)
    odd = reg[reg["Leading Option"] != top]
    if len(odd):
        for region, row in odd.iterrows():
            out.append(f"Regional exception: **{region}** prefers **{row['Leading Option']}** "
                       f"({row['Share %']}%) instead of {top}.")
    else:
        out.append(f"{top} leads in every region.")
    age = A.leader_by_group(df, C.AGE)
    age = age[age.index != "Unknown"]
    out.append("Leading option by age group: " +
               "; ".join(f"{a} -> {r['Leading Option']} ({r['Share %']}%)" for a, r in age.iterrows()) + ".")

    rec = A.recommend_share(df)
    if "Yes" in rec.index:
        out.append(f"**{rec.loc['Yes', 'Share %']}%** would recommend the tool they chose.")

    d = A.daily_trend(df)
    out.append(f"Peak day was **{d['Responses'].idxmax().date()}** with {int(d['Responses'].max())} responses; "
               f"the poll ran {len(d)} days.")

    sent = A.sentiment_share(df)
    words = ", ".join(w for w, _ in A.keywords(df, 6))
    out.append("Open-text sentiment: " + ", ".join(f"{k} {v}%" for k, v in sent["Share %"].items()) +
               f". Most frequent words: {words}.")

    out.append(f"**Recommendation:** prioritise {top} in training/tooling decisions, but localise by region "
               f"and address the pain points raised in negative comments.")
    return out


def save_report(df, path=C.OUTPUT_DIR / "insights_report.md"):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Poll Insights Report\n\n_Based on {len(df)} valid responses._\n"]
    lines += [f"{i}. {t}" for i, t in enumerate(generate_insights(df), 1)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
