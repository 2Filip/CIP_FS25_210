import pandas as pd

# Excel files
nzz_path = "../../Scraping files/NZZ/Cleaned_data/NZZ_Cleaned_Week.xlsx"
taz_path = "../../Scraping files/Tagesanzeiger/Cleaned Data Tagesanzeiger/Tagesanzeiger_Cleaned_Week.xlsx"
twentymin_path =
srf_path = "../../Scraping files/SRF/Cleaned_Data/SRF_Cleaned_Week.xlsx"

# Load Excel files
df_nzz = pd.read_excel(nzz_path)
df_taz = pd.read_excel(taz_path)
df_twentymin = pd.read_excel(twentymin_path)
df_srf = pd.read_excel(srf_path)

# Calculate number of articles
nzz_count = len(df_nzz)
taz_count = len(df_taz)
twentymin_count = len(df_20min)
srf_count = len(df_srf)

# Output
print("Number of articles per platform:")
print(f"  NZZ:             {nzz_count} articles")
print(f"  Tagesanzeiger:   {taz_count} articles")
print(f"  20 Minuten:   {twentymin_count} articles")
print(f"  SRF:   {srf_count} articles")
