import pandas as pd
from datetime import datetime
import os
import re

# Folder containing the SRF Excel files
folder_path = "Scraping files/SRF/Translation"
all_srf_articles = []

for filename in os.listdir(folder_path):
    if filename.startswith("SRF_") and filename.endswith("_translated.xlsx"):
        full_path = os.path.join(folder_path, filename)
        print(f"📄 Processing: {filename}")

        # Extract scrape time from filename
        match = re.search(r"SRF_(\d{4}-\d{2}-\d{2})_(AM|PM)", filename)
        if not match:
            print(f"⚠️ Skipping invalid filename: {filename}")
            continue

        date_str, part_of_day = match.groups()
        hour = 13 if part_of_day == "AM" else 19
        scrape_time = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=hour, minute=30)

        # Load the Excel file safely
        try:
            df = pd.read_excel(full_path)
        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")
            continue

        print("🔍 Columns found:", df.columns.tolist())

        # Only keep English translation columns
        required_cols = {
            "Headline_EN": "title",
            "Zeit_EN": "zeit",
            "Link_EN": "url"
        }

        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"⚠️ Missing columns in {filename}: {missing}")
            continue

        df_clean = df[required_cols.keys()].rename(columns=required_cols)
        df_clean = df_clean.dropna(subset=["title", "url"])

        # Add scrape time
        df_clean["ScrapeTime"] = scrape_time

        # Force strings before parsing (handles timezone offsets properly)
        zeit_strings = df_clean["zeit"].astype(str)

        # Parse with timezone-aware format
        zeit_converted = pd.to_datetime(zeit_strings, errors="coerce", utc=True)

        if pd.api.types.is_datetime64_any_dtype(zeit_converted):
            df_clean["PubDate"] = zeit_converted.dt.date
        else:
            print(f"⚠️ Skipping PubDate assignment in {filename} – still invalid after fix.")
            df_clean["PubDate"] = None

        all_srf_articles.append(df_clean)

# Combine all cleaned SRF files
if all_srf_articles:
    srf_df = pd.concat(all_srf_articles, ignore_index=True)
    srf_df = srf_df.drop_duplicates(subset="url")
    srf_df.to_excel("SRF_Cleaned_Week.xlsx", index=False)
    print("✅ All SRF data saved to: SRF_Cleaned_Week.xlsx")
else:
    print("⚠️ No valid SRF files processed.")
