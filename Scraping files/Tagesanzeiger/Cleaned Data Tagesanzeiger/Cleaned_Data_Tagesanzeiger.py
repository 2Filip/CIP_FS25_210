import pandas as pd
from datetime import datetime, timedelta
import os

# Dates from Monday to Friday
dates = ["2025-03-24", "2025-03-25", "2025-03-26", "2025-03-27", "2025-03-28"]

# To store everything
all_articles = []

# Turns "publiziert heute or gestern" into the real date
def get_pub_date(zeit_text, scrape_time):
    if not isinstance(zeit_text, str):
        return None
    zeit_text = zeit_text.lower()
    if "heute" in zeit_text:
        return scrape_time.date()
    elif "gestern" in zeit_text:
        return (scrape_time - timedelta(days=1)).date()
    else:
        try:
            return pd.to_datetime(zeit_text, dayfirst=True, errors='coerce').date()
        except:
            return None

# Go through each day and time (AM and PM)
for date_str in dates:
    for part, hour in [("AM", 13), ("PM", 19)]:
        # This is the path to the file
        filename = f"Scraping files/Tagesanzeiger/Done/Tagesanzeiger_{date_str}_{part}.xlsx"

        if not os.path.exists(filename):
            print("File not found:", filename)
            continue

        print("Reading file:", filename)

        # Load the data
        df = pd.read_excel(filename)

        # Fill missing teaser values
        df["Teaser"] = df["Teaser"].fillna("")

        # Add scraping time (approx)
        scrape_time = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=hour, minute=30)
        df["ScrapeTime"] = scrape_time

        # Create a column for the actual publish date
        df["PubDate"] = df["Zeit"].apply(lambda z: get_pub_date(z, scrape_time))

        # Add this file's articles to the list
        all_articles.append(df)

# Combine everything into one file
full_df = pd.concat(all_articles, ignore_index=True)

# Drop repeated articles with same URL
full_df = full_df.drop_duplicates(subset="Link")

# Save to new Excel
output_file = "Tagesanzeiger_Cleaned_Week.xlsx"
full_df.to_excel(output_file, index=False)

print(f"Finished! Saved as '{output_file}'")
