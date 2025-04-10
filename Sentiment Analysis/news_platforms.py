import pandas as pd
import matplotlib.pyplot as plt
import os

# Storage location for plots
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# Excel files
nzz_path = "../../Scraping files/NZZ/Cleaned_data/NZZ_Cleaned_Week.xlsx"
taz_path = "../../Scraping files/Tagesanzeiger/Cleaned Data Tagesanzeiger/Tagesanzeiger_Cleaned_Week.xlsx"
twentymin_path = "../../Scraping files/20_Minuten/Cleaned Data 20min/20min_Cleaned_Week.xlsx"
srf_path = "../../Scraping files/SRF/Cleaned_Data/SRF_Cleaned_Week.xlsx"

# Load Excel files
df_nzz = pd.read_excel(nzz_path)
df_taz = pd.read_excel(taz_path)
df_twentymin = pd.read_excel(twentymin_path)
df_srf = pd.read_excel(srf_path)

# Calculate number of articles
nzz_count = len(df_nzz)
taz_count = len(df_taz)
twentymin_count = len(df_twentymin)
srf_count = len(df_srf)

# Output
print("Number of articles per platform:")
print(f"  NZZ:             {nzz_count} articles")
print(f"  TAZ:   {taz_count} articles")
print(f"  20 Minuten:   {twentymin_count} articles")
print(f"  SRF:   {srf_count} articles")

# Convert ScrapeTime to datetime
df_nzz['ScrapeTime'] = pd.to_datetime(df_nzz['ScrapeTime'])
df_taz['ScrapeTime'] = pd.to_datetime(df_taz['ScrapeTime'])
df_twentymin['ScrapeTime'] = pd.to_datetime(df_twentymin['ScrapeTime'])
df_srf['ScrapeTime'] = pd.to_datetime(df_srf['ScrapeTime'])

# Group by date
daily_nzz = df_nzz.groupby(df_nzz['ScrapeTime'].dt.date).size()
daily_taz = df_taz.groupby(df_taz['ScrapeTime'].dt.date).size()
daily_twentymin = df_twentymin.groupby(df_twentymin['ScrapeTime'].dt.date).size()
daily_srf = df_srf.groupby(df_srf['ScrapeTime'].dt.date).size()

# Merging
daily_counts = pd.DataFrame({
    'NZZ': daily_nzz,
    'TAZ': daily_taz,
    '20 Minuten': daily_twentymin,
    'SRF': daily_srf
})

# Format date as DD.MM.YYYY
daily_counts.index = pd.to_datetime(daily_counts.index)
daily_counts.index = daily_counts.index.strftime('%d.%m.%Y')

# Plot
daily_counts.plot(kind='line', marker='o', figsize=(10, 6))
plt.title("Daily number of articles per platform")
plt.xlabel("Date")
plt.ylabel("Number of articles")
plt.grid(True)
plt.legend(title="News Platform")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "newsplatforms.png"))
plt.show()
