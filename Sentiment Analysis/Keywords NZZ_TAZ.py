import pandas as pd
import spacy
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import os

# Storage location for plots
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# Load files
nzz_path = "../../Scraping files/NZZ/Cleaned_data/NZZ_Cleaned_Week.xlsx"
taz_path = "../../Scraping files/Tagesanzeiger/Cleaned Data Tagesanzeiger/Tagesanzeiger_Cleaned_Week.xlsx"

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

# Prepare SpaCy
nlp = spacy.load("en_core_web_sm")

def extract_keywords(texts, pos_tags=["NOUN", "PROPN"]):
    all_keywords = []
    for doc in nlp.pipe(texts, disable=["ner", "parser"]):
        for token in doc:
            if token.pos_ in pos_tags and not token.is_stop and token.is_alpha:
                all_keywords.append(token.lemma_.lower())
    return all_keywords

# Extract keywords
keywords_nzz = extract_keywords(df_nzz["Text"])
keywords_taz = extract_keywords(df_taz["Text"])

# Count keywords
counter_nzz = Counter(keywords_nzz)
counter_taz = Counter(keywords_taz)

#  Show Top 20 keywords
top_nzz = counter_nzz.most_common(20)
top_taz = counter_taz.most_common(20)

print("\nTop 20 Keywords – NZZ:")
print(top_nzz)
print("\nTop 20 Keywords – Tagesanzeiger:")
print(top_taz)

# Plot
common_keywords = set([kw for kw, _ in counter_nzz.most_common(30)]) & set([kw for kw, _ in counter_taz.most_common(30)])
common_keywords = list(common_keywords)

nzz_counts = [counter_nzz.get(kw, 0) for kw in common_keywords]
taz_counts = [counter_taz.get(kw, 0) for kw in common_keywords]

x = np.arange(len(common_keywords))
width = 0.35

plt.figure(figsize=(12,6))
plt.bar(x - width/2, nzz_counts, width, label='NZZ')
plt.bar(x + width/2, taz_counts, width, label='Tagesanzeiger')
plt.xticks(x, common_keywords, rotation=45, ha="right")
plt.title("Comparison of the Top Keywords")
plt.xlabel("Keyword")
plt.ylabel("Number of occurrences")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "keyword_barplot.png"))
plt.show()
