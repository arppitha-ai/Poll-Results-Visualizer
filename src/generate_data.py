"""Create a realistic, deliberately MESSY synthetic poll dataset."""
import numpy as np
import pandas as pd

from . import config as C

POS = ["Great tool, very useful", "Super helpful and easy to use",
       "Love the clear visuals, amazing for reports",
       "Fast and powerful, excellent for analysis", "Intuitive and smooth experience"]
NEU = ["It is okay for basic tasks", "Works fine but nothing special",
       "Average experience overall", "Decent, I use it sometimes"]
NEG = ["Needs improvement, quite confusing", "Too slow and difficult to learn",
       "Complicated setup, frustrating at times", "Poor documentation, hard to use",
       "Buggy and expensive"]
SUFFIX = ["", "", " for reporting", " for data cleaning", " for dashboards", " for team projects"]
MEAN_RATING = {"Python": 4.1, "Power BI": 3.9, "Tableau": 3.7, "SQL": 3.6, "Excel": 3.3, "R": 3.2}


def generate_poll_data(n: int = 600, seed: int = 42, messy: bool = True) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    region = rng.choice(C.REGIONS, n, p=[0.20, 0.25, 0.20, 0.20, 0.15])
    age = rng.choice(C.AGE_GROUPS, n, p=[0.35, 0.35, 0.20, 0.10])
    gender = rng.choice(["Male", "Female", "Other"], n, p=[0.48, 0.48, 0.04])

    # Multiple-choice answers with regional / age patterns
    base = dict(zip(C.TOOLS, [0.30, 0.22, 0.16, 0.12, 0.12, 0.08]))
    tools = []
    for r, a in zip(region, age):
        w = base.copy()
        if r == "South": w["Python"] += 0.15
        if r == "West": w["Power BI"] += 0.12; w["Tableau"] += 0.08
        if r == "North": w["Excel"] += 0.12
        if a == "18-24": w["Python"] += 0.10
        if a == "45+": w["Excel"] += 0.15; w["Python"] -= 0.12
        p = np.clip(np.array([w[t] for t in C.TOOLS]), 0.01, None)
        tools.append(rng.choice(C.TOOLS, p=p / p.sum()))

    # Likert rating + yes/no + feedback driven by the tool
    rating = np.array([int(np.clip(round(rng.normal(MEAN_RATING[t], 0.9)), 1, 5)) for t in tools])
    recommend = np.where(rng.random(n) < 0.15 + 0.16 * rating, "Yes", "No")
    feedback = []
    for r in rating:
        pool = POS if r >= 4 else NEU if r == 3 else NEG
        feedback.append(str(rng.choice(pool)) + str(rng.choice(SUFFIX)))

    # Timestamps: 30 days, responses ramp up as the poll is shared
    day_w = np.linspace(1, 2.2, 30); day_w /= day_w.sum()
    days = rng.choice(30, n, p=day_w)
    secs = rng.integers(8 * 3600, 22 * 3600, n)
    ts = pd.Timestamp("2024-04-01") + pd.to_timedelta(days, "D") + pd.to_timedelta(secs, "s")

    df = pd.DataFrame({
        C.TIMESTAMP: ts, C.AGE: age, C.GENDER: gender, C.REGION: region,
        C.TOOL: tools, C.RECOMMEND: recommend, C.RATING: rating, C.FEEDBACK: feedback,
    }).sort_values(C.TIMESTAMP).reset_index(drop=True)

    if messy:
        for col in (C.RATING, C.TOOL, C.GENDER, C.REGION, C.FEEDBACK, C.RECOMMEND):
            df[col] = df[col].astype(object)
        pick = lambda frac: rng.choice(n, int(n * frac), replace=False)
        for i in pick(0.06):
            df.loc[i, C.TOOL] = str(rng.choice([" python ", "PYTHON", "powerbi", "POWER BI",
                                                "Power-BI", "excel ", "sql", "Tablaeu?", "Julia"]))
        for i in pick(0.02): df.loc[i, C.RATING] = np.nan
        for i in pick(0.01): df.loc[i, C.RATING] = str(rng.choice(["7", "0", "four", "10"]))
        for i in pick(0.02): df.loc[i, C.GENDER] = np.nan
        for i in pick(0.02): df.loc[i, C.REGION] = np.nan
        for i in pick(0.03): df.loc[i, C.FEEDBACK] = np.nan
        for i in pick(0.03): df.loc[i, C.RECOMMEND] = str(rng.choice(["yes", "Y", "no", "N"]))
        dupes = df.sample(int(n * 0.04), random_state=seed)
        df = pd.concat([df, dupes]).sort_values(C.TIMESTAMP).reset_index(drop=True)
    return df


if __name__ == "__main__":
    C.DATA_DIR.mkdir(exist_ok=True)
    generate_poll_data().to_csv(C.RAW_CSV, index=False)
    print(f"Saved {C.RAW_CSV}")
