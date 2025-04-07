import pandas as pd
from datetime import datetime
import os
import re

folder_path = "Scraping files/NZZ/Translation"
all_articles = []

for filename in os.listdir(folder_path):
    if filename.startswith("nzz_teasers_") and filename.endswith("_translated.xlsx"):
        full_path = os.path.join(folder_path, filename)
        print("Processing:", filename)

        # Extract scrape time from filename
        match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})", filename)
        if not match:
            print("Skipping file with bad filename format:", filename)
            continue
        date_str, hour, minute = match.groups()
        scrape_time = datetime.strptime(f"{date_str} {hour}:{minute}", "%Y-%m-%d %H:%M")

        # Load file
        df = pd.read_excel(full_path)

        # Only keep English columns
        cols_to_keep = {
            'title_EN': 'title',
            'teaser_EN': 'teaser',
            'url_EN': 'url',
            'publication_date_EN': 'zeit'
        }

        missing_cols = [col for col in cols_to_keep if col not in df.columns]
        if missing_cols:
            print(f"Missing expected EN columns in {filename}: {missing_cols}")
            continue

        df_clean = df[cols_to_keep.keys()].rename(columns=cols_to_keep)

        # Drop rows with missing title or URL
        df_clean = df_clean.dropna(subset=['title', 'url'])

        # Add ScrapeTime and PubDate
        df_clean["ScrapeTime"] = scrape_time
        df_clean["PubDate"] = pd.to_datetime(df_clean["zeit"], errors="coerce").dt.date

        all_articles.append(df_clean)

# Combine all cleaned articles
final_df = pd.concat(all_articles, ignore_index=True)
final_df = final_df.drop_duplicates(subset="url")

# Save output
output_file = "NZZ_Cleaned_Week.xlsx"
final_df.to_excel(output_file, index=False)
print(f"All done! Final cleaned file saved as: {output_file}")
