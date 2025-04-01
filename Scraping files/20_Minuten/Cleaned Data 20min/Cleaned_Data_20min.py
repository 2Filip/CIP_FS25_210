import pandas as pd
from datetime import datetime
import os
import re

# Set the folder path where the translated files are saved
folder_path = "../Translated_20min"  # change this if needed
all_articles = []
skipped_files = []

# Go through all Excel files in the folder
for filename in os.listdir(folder_path):
    if filename.startswith("20min_") and filename.endswith("_translated.xlsx"):
        full_path = os.path.join(folder_path, filename)
        print("Reading:", filename)

        # Extract the date and AM/PM part from the filename
        match = re.search(r"20min_(\d{4}-\d{2}-\d{2})_(AM|PM)_translated\.xlsx", filename)
        if not match:
            print("Skipping file with wrong name:", filename)
            skipped_files.append(filename)
            continue

        date_str, part = match.groups()
        scrape_hour = 13 if part == "AM" else 19
        scrape_time = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=scrape_hour, minute=30)

        # Try reading the file
        try:
            df = pd.read_excel(full_path)
        except Exception as e:
            print("Could not read", filename)
            skipped_files.append(filename)
            continue

        columns = {
            "Headline_EN": "Header",
            "Zeit_EN": "Zeit",
            "Link_EN": "Link"
        }

        if not all(col in df.columns for col in columns):
            print("Missing translated columns in:", filename)
            skipped_files.append(filename)
            continue

        df = df[list(columns)].rename(columns=columns)
        df["ScrapeTime"] = scrape_time

        # Convert the Zeit column to datetime
        def parse_pub_datetime(text):
            try:
                return pd.to_datetime(text, dayfirst=True, errors="coerce")
            except:
                return None

        df["PubDateTime"] = df["Zeit"].apply(parse_pub_datetime)
        df["PubDate"] = df["PubDateTime"].apply(lambda x: x.date() if pd.notnull(x) else pd.NaT)

        all_articles.append(df)

# Combine all cleaned data
final_df = pd.concat(all_articles, ignore_index=True)

# Remove duplicate articles by link
final_df = final_df.drop_duplicates(subset="Link")

# Format datetime columns as readable strings
final_df["ScrapeTime"] = final_df["ScrapeTime"].dt.strftime("%Y-%m-%d %H:%M")
final_df["PubDateTime"] = final_df["PubDateTime"].dt.strftime("%Y-%m-%d %H:%M")
final_df["PubDate"] = final_df["PubDate"].astype(str).replace("NaT", "NA")

# Save the cleaned data to Excel
output_file = "20min_Cleaned_Week.xlsx"
final_df.to_excel(output_file, index=False)

print("Saved cleaned file as:", output_file)

# Print skipped files, if any
if skipped_files:
    print("Skipped files:")
    for f in skipped_files:
        print("-", f)
