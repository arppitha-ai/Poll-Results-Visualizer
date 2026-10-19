"""Central configuration: paths, column names and allowed values."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
IMAGE_DIR = ROOT / "images"

RAW_CSV = DATA_DIR / "poll_data_raw.csv"
CLEAN_CSV = DATA_DIR / "poll_data_cleaned.csv"

TIMESTAMP = "Timestamp"
AGE = "Age Group"
GENDER = "Gender"
REGION = "Region"
TOOL = "Preferred Tool"
RECOMMEND = "Would Recommend"
RATING = "Satisfaction"
FEEDBACK = "Feedback"

# Google Forms / Excel exports often use different headers. Map them here.
COLUMN_ALIASES = {
    "Satisfaction (1-5)": RATING,
    "Satisfaction (1–5)": RATING,
    "Rating": RATING,
    "Age": AGE,
    "Favorite Tool": TOOL,
    "Favourite Tool": TOOL,
    "Recommend": RECOMMEND,
    "Comments": FEEDBACK,
}

TOOLS = ["Python", "Excel", "Power BI", "Tableau", "SQL", "R"]
REGIONS = ["North", "South", "East", "West", "Central"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45+"]
