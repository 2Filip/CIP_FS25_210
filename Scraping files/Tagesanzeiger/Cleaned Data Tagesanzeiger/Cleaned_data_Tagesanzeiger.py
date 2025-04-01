import pandas as pd
from datetime import datetime, timedelta
import os
import re

# Folder where your translated Tagesanzeiger files are
folder_path = "../Translated_Tagesanzeiger"
all_articles = []
skipped_files = []

# Go through all Excel files in the folder
for filename in os.listdir(folder_path):
    if filename.startswith("Tagesanzeiger_") and filename.endswith("_translated.xlsx"):
        full_path = os.path.join(folder_path, filename)
        print("Reading:", filename)

        # Try to extract date and part (AM/PM) from filename
        match = re.search(r"Tagesanzeiger_(\d{4}-\d{2}-\d{2})_(AM|PM)_translated\.xlsx", filename)
        if not match:
            print("Skipping file with wrong format:", filename)
            skipped_files.append(filename)
            continue

        date_str, part = match.groups()
        scrape_hour = 13 if part == "AM" else 19
        scrape_time = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=scrape_hour, minute=30)

        try:
            df = pd.read_excel(full_path)
        except Exception as e:
            print(f"Could not read {filename}: {e}")
            skipped_files.append(filename)
            continue

        # Only keep translated columns
        cols = {
            "Header_EN": "Header",
            "Teaser_EN": "Teaser",
            "Zeit_EN": "Zeit",
            "Link_EN": "Link"
        }

        if not all(col in df.columns for col in cols):
            print("Missing columns in:", filename)
            skipped_files.append(filename)
            continue

        df = df[list(cols)].rename(columns=cols)
        df["Teaser"] = df["Teaser"].fillna("NA")
        df["ScrapeTime"] = scrape_time

        # Convert Zeit string to datetime
        def extract_pub_datetime(text):
            if not isinstance(text, str):
                return None
            text = text.lower()

            # Match relative date
            if "heute" in text:
                pub_date = scrape_time.date()
            elif "gestern" in text:
                pub_date = (scrape_time - timedelta(days=1)).date()
            else:
                return None

            # Match time string (like 13:13)
            try:
                match = re.search(r"um (\d{1,2}:\d{2})", text)
                if match:
                    pub_time = datetime.strptime(match.group(1), "%H:%M").time()
                    return datetime.combine(pub_date, pub_time)
            except:
                return None
            return None

        df["PubDateTime"] = df["Zeit"].apply(extract_pub_datetime)
        df["PubDate"] = df["PubDateTime"].apply(lambda x: x.date() if pd.notnull(x) else None)

        all_articles.append(df)

# Combine all data
final_df = pd.concat(all_articles, ignore_index=True)
final_df = final_df.drop_duplicates(subset="Link")

# Save final file
output_file = "Tagesanzeiger_Cleaned_Week.xlsx"
final_df.to_excel(output_file, index=False)

print(f"\n✅ Done! Saved cleaned file as: {output_file}")

# If anything was skipped
if skipped_files:
    print("\nSkipped the following files:")
    for f in skipped_files:
        print(" -", f)

