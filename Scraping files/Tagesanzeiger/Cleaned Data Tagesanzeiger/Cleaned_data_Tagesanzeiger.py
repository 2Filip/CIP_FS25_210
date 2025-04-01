import pandas as pd
from datetime import datetime, timedelta
import os

# List of dates that were scraped
dates = ["2025-03-24", "2025-03-25", "2025-03-26", "2025-03-27", "2025-03-28"]

# List to collect all articles
all_articles = []

# Function to get full publish datetime from text
def get_publish_time(text, scrape_time):
    if not isinstance(text, str):
        return None

    text = text.lower()

    if "heute" in text:
        date = scrape_time.date()
    elif "gestern" in text:
        date = (scrape_time - timedelta(days=1)).date()
    else:
        return None

    parts = text.split("um")
    if len(parts) > 1:
        time_str = parts[1].replace("uhr", "").strip()
        try:
            return datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
        except:
            return None

    return None

# Loop through each date and period (AM or PM)
for date_str in dates:
    for period, hour in [("AM", 13), ("PM", 19)]:
        tagesanzeiger_path = f"Scraping files/Tagesanzeiger/Translated_Tagesanzeiger/Tagesanzeiger_{date_str}_{period}_translated.xlsx"

        if not os.path.exists(tagesanzeiger_path):
            print("Not found:", tagesanzeiger_path)
            continue

        df = pd.read_excel(tagesanzeiger_path)

        # Rename columns
        df = df.rename(columns={
            "Header_EN": "Header",
            "Teaser_EN": "Teaser",
            "Zeit_EN": "Zeit",
            "Link_EN": "Link"
        })

        # Replace missing values
        df = df.fillna("NA")

        # Create scrape time to help interpret "heute" and "gestern"
        scrape_time = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=hour, minute=30)
        df["ScrapeTime"] = scrape_time

        # Extract actual publish datetime
        df["PubDateTime"] = df["Zeit"].apply(lambda x: get_publish_time(x, scrape_time))

        # Label as AM or PM based on publish time
        df["AM_PM"] = df["PubDateTime"].apply(
            lambda x: "AM" if x and x.time() < datetime.strptime("13:30", "%H:%M").time() else "PM"
        )

        all_articles.append(df)

# Combine all data
final_df = pd.concat(all_articles)

# Drop duplicates by article link
final_df = final_df.drop_duplicates(subset="Link")

# Save full dataset
final_df.to_excel("Tagesanzeiger_All_Dates_Cleaned.xlsx", index=False)

# Save AM and PM datasets separately
final_df[final_df["AM_PM"] == "AM"].to_excel("Tagesanzeiger_AM.xlsx", index=False)
final_df[final_df["AM_PM"] == "PM"].to_excel("Tagesanzeiger_PM.xlsx", index=False)

