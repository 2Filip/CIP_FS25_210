import pandas as pd
import spacy
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Output directory
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# Load data
srf_path = "Scraping files/SRF/Cleaned_Data/SRF_Cleaned_Week.xlsx"
min20_path = "Scraping files/20_Minuten/Cleaned Data 20min/20min_Cleaned_Week.xlsx"

df_srf = pd.read_excel(srf_path)
df_20min = pd.read_excel(min20_path)

# Standardize columns
df_srf = df_srf.rename(columns={"title": "Title", "PubDate": "PubDate"})
df_20min = df_20min.rename(columns={"Header": "Title", "PubDate": "PubDate"})

# Drop rows with missing values
df_srf = df_srf.dropna(subset=["Title", "PubDate"])
df_20min = df_20min.dropna(subset=["Title", "PubDate"])

# Convert pubdate to datetime
df_srf["PubDate"] = pd.to_datetime(df_srf["PubDate"])
df_20min["PubDate"] = pd.to_datetime(df_20min["PubDate"])

# Add source column
df_srf["Source"] = "SRF"
df_20min["Source"] = "20 Minuten"

# Filter time window
start_date = "2025-03-24"
end_date = "2025-03-28"

df_srf_filtered = df_srf[(df_srf["PubDate"] >= start_date) & (df_srf["PubDate"] <= end_date)]
df_20min_filtered = df_20min[(df_20min["PubDate"] >= start_date) & (df_20min["PubDate"] <= end_date)]

# Round dates to daily
df_combined["Date"] = df_combined["PubDate"].dt.date

# Group and count articles per day per source
daily_counts = df_combined.groupby(["Date", "Source"]).size().unstack(fill_value=0)

# Plot grouped bar chart
daily_counts.plot(kind="bar", stacked=True, figsize=(12, 6))
plt.title("Number of Articles Over Time (24.03 – 28.03.2025)")
plt.xlabel("Publication Date")
plt.ylabel("Number of Articles")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "article_frequency_over_time_filtered.png"))
plt.show()

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

def extract_keywords(texts, pos_tags=["NOUN", "PROPN"]):
    keywords = []
    for doc in nlp.pipe(texts, disable=["ner", "parser"]):
        for token in doc:
            if token.pos_ in pos_tags and not token.is_stop and token.is_alpha:
                keywords.append(token.lemma_.lower())
    return keywords

# Extract keywords
keywords_srf = extract_keywords(df_srf_filtered["Title"])
keywords_20min = extract_keywords(df_20min_filtered["Title"])

# Count top keywords
counter_srf = Counter(keywords_srf)
counter_20min = Counter(keywords_20min)

top_srf = counter_srf.most_common(10)
top_20min = counter_20min.most_common(10)

print("Top 10 Keywords – SRF:")
print(top_srf)
print("\nTop 10 Keywords – 20 Minuten:")
print(top_20min)

# Compare top shared keywords
common_keywords = set([kw for kw, _ in counter_srf.most_common(30)]) & set([kw for kw, _ in counter_20min.most_common(30)])
common_keywords = list(common_keywords)

srf_counts = [counter_srf.get(kw, 0) for kw in common_keywords]
min20_counts = [counter_20min.get(kw, 0) for kw in common_keywords]

x = np.arange(len(common_keywords))
width = 0.35

plt.figure(figsize=(12, 6))
plt.bar(x - width/2, srf_counts, width, label='SRF')
plt.bar(x + width/2, min20_counts, width, label='20 Minuten')
plt.xticks(x, common_keywords, rotation=45, ha="right")
plt.title("Top Common Keywords Comparison (24.03 – 28.03.2025)")
plt.xlabel("Keyword")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "keyword_srf_20min_barplot_filtered.png"))
plt.show()
