import pandas as pd
from datetime import datetime, timedelta
import os

# List of dates to check
dates = ["2025-03-24", "2025-03-25", "2025-03-26", "2025-03-27", "2025-03-28"]

# List to collect all article data
all_articles = []

# Convert Zeit text to actual date
def get_pub_date(text, scrape_time):
    if not isinstance(text, str):
        return None
    text = text.lower()
    if "heute" in text:
        return scrape_time.date()
    elif "gestern" in text:
        return (scrape_time - timedelta(days=1)).date()
    try:
        return pd.to_datetime(text, dayfirst=True, errors='coerce').date()
    except:
        return None

# Loop through each date and file (AM and PM)
for date_str in dates:
    for part, hour in [("AM", 13), ("PM", 19)]:
        filename = f"../Translated_Tagesanzeiger/Tagesanzeiger_{date_str}_{part}_translated.xlsx"

        if not os.path.exists(filename):
            print("File not found:", filename)
            continue

        print("Reading file:", filename)

        df = pd.read_excel(filename)
        df.index = pd.RangeIndex(len(df))  # Fix index if broken

        # Rename columns
        df = df.rename(columns={
            "Header_EN": "Header",
            "Teaser_EN": "Teaser",
            "Zeit_EN": "Zeit",
            "Link_EN": "Link"
        })

        df["Teaser"] = df["Teaser"].fillna("NA")

        scrape_time = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=hour, minute=30)
        df["ScrapeTime"] = scrape_time
        df["PubDate"] = df["Zeit"].apply(lambda z: get_pub_date(z, scrape_time))

        all_articles.append(df)

# Combine all data
final_df = pd.concat(all_articles, ignore_index=True)
final_df = final_df.drop_duplicates(subset="Link")

# Save final file
final_df.to_excel("Tagesanzeiger_Translated_Cleaned.xlsx", index=False)
print("✅ Done! File saved: Tagesanzeiger_Translated_Cleaned.xlsx")

