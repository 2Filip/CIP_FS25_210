import pandas as pd
import spacy
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import os

# Output directory for plots
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# Load data
nzz_path = "../../Scraping files/NZZ/Cleaned_data/NZZ_Cleaned_Week.xlsx"
taz_path = "../../Scraping files/Tagesanzeiger/Cleaned Data Tagesanzeiger/Tagesanzeiger_Cleaned_Week.xlsx"

df_nzz = pd.read_excel(nzz_path)
df_taz = pd.read_excel(taz_path)

# Rename and unify columns
df_nzz = df_nzz.rename(columns={"title": "Title", "teaser": "Teaser"})
df_taz = df_taz.rename(columns={"Header": "Title", "Teaser": "Teaser"})

# Drop rows missing essential content
df_nzz = df_nzz.dropna(subset=["Title", "Teaser"])
df_taz = df_taz.dropna(subset=["Title", "Teaser"])

# Use PubDate for filtering
df_nzz["Date"] = pd.to_datetime(df_nzz["PubDate"])
df_taz["Date"] = pd.to_datetime(df_taz["PubDate"])

# Filter by timeframe
start_date = "2025-03-24"
end_date = "2025-03-28"
df_nzz = df_nzz[(df_nzz["Date"] >= start_date) & (df_nzz["Date"] <= end_date)]
df_taz = df_taz[(df_taz["Date"] >= start_date) & (df_taz["Date"] <= end_date)]

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Keyword extraction
def extract_keywords(texts, pos_tags=["NOUN", "PROPN"]):
    all_keywords = []
    for doc in nlp.pipe(texts, disable=["ner", "parser"]):
        for token in doc:
            if token.pos_ in pos_tags and not token.is_stop and token.is_alpha:
                all_keywords.append(token.lemma_.lower())
    return all_keywords

# Create text column
df_nzz["Text"] = df_nzz["Title"].astype(str) + ". " + df_nzz["Teaser"].astype(str)
df_taz["Text"] = df_taz["Title"].astype(str) + ". " + df_taz["Teaser"].astype(str)

# Extract and count
keywords_nzz = extract_keywords(df_nzz["Text"])
keywords_taz = extract_keywords(df_taz["Text"])

counter_nzz = Counter(keywords_nzz)
counter_taz = Counter(keywords_taz)

# Top 10 keywords per outlet (no overlap filtering)
top_nzz = counter_nzz.most_common(10)
top_taz = counter_taz.most_common(10)

print("\nTop 10 Keywords – NZZ:")
print(top_nzz)
print("\nTop 10 Keywords – Tagesanzeiger:")
print(top_taz)

# Separate keyword lists and counts
nzz_keywords, nzz_counts = zip(*top_nzz)
taz_keywords, taz_counts = zip(*top_taz)

# Plotting
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

# NZZ plot
axes[0].bar(nzz_keywords, nzz_counts, color='steelblue')
axes[0].set_title("Top 10 Keywords – NZZ")
axes[0].set_xlabel("Keyword")
axes[0].set_ylabel("Occurrences")
axes[0].tick_params(axis='x', rotation=45)

# Annotate bars
for i, v in enumerate(nzz_counts):
    axes[0].text(i, v + 0.5, str(v), ha='center', fontsize=9)

# Tagesanzeiger plot
axes[1].bar(taz_keywords, taz_counts, color='darkorange')
axes[1].set_title("Top 10 Keywords – Tagesanzeiger")
axes[1].set_xlabel("Keyword")
axes[1].tick_params(axis='x', rotation=45)

# Annotate bars
for i, v in enumerate(taz_counts):
    axes[1].text(i, v + 0.5, str(v), ha='center', fontsize=9)

plt.suptitle("Top 10 Keywords (24.03 – 28.03.2025)")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "top10_keywords_nzz_taz.png"))
plt.show()
