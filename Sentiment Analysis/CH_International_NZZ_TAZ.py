import pandas as pd
import matplotlib.pyplot as plt
import os

# Storage location for plots
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# Load files
nzz_path = "../../Scraping files/NZZ/Cleaned_data/NZZ_Cleaned_Week.xlsx"
taz_path = "../../Scraping files/Tagesanzeiger/Cleaned Data Tagesanzeiger/Tagesanzeiger_Cleaned_Week.xlsx"4

df_nzz = pd.read_excel(nzz_path)
df_taz = pd.read_excel(taz_path)

# Standardise columns
df_nzz = df_nzz.rename(columns={"title": "Title", "teaser": "Teaser"})
df_taz = df_taz.rename(columns={"Header": "Title", "Teaser": "Teaser"})

# Combine texts
df_nzz["Text"] = df_nzz["Title"].astype(str) + ". " + df_nzz["Teaser"].astype(str)
df_taz["Text"] = df_taz["Title"].astype(str) + ". " + df_taz["Teaser"].astype(str)

# Remove empty cells
df_nzz = df_nzz.dropna(subset=["Title", "Teaser"])
df_taz = df_taz.dropna(subset=["Title", "Teaser"])

# Keywords
swiss_keywords = ["switzerland", "swiss", "zurich", "bern", "geneva", "lucerne", "basel", "bundesrat", "national council", "federal council", "sp", "svp", "migros", "coop", "swiss parliament", "swiss army"]
international_keywords = ["trump", "biden", "usa", "united states", "russia", "ukraine", "china", "germany", "france", "israel", "palestine", "europe", "nato", "world", "election", "africa", "EU", "putin"]

# 3. Klassifikations-Funktion
def classify_article(text):
    text = text.lower()
    if any(word in text for word in swiss_keywords):
        return "Swiss"
    elif any(word in text for word in international_keywords):
        return "International"
    else:
        return "Unclear"

# Classification
df_nzz["Category"] = df_nzz["Text"].apply(classify_article)
df_taz["Category"] = df_taz["Text"].apply(classify_article)

# Count frequencies
print("\nTagesanzeiger Distribution:")
for category, count in df_taz["Category"].value_counts().items():
    print(f"  {category}: {count}")

print("\nNZZ Distribution:")
for category, count in df_nzz["Category"].value_counts().items():
    print(f"  {category}: {count}")

# Plot
labels = ["Swiss", "International", "Unclear"]
nzz_vals = [df_nzz["Category"].value_counts().get(label, 0) for label in labels]
taz_vals = [df_taz["Category"].value_counts().get(label, 0) for label in labels]

x = range(len(labels))
width = 0.35

plt.figure(figsize=(8,6))
plt.bar([i - width/2 for i in x], nzz_vals, width, label="NZZ")
plt.bar([i + width/2 for i in x], taz_vals, width, label="Tagesanzeiger")
plt.xticks(x, labels)
plt.ylabel("Number of Articles")
plt.title("Visibility of Swiss vs. International Topics on Main Pages")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "CH_International_NZZ_TAZ_barplot.png"))
plt.show()
