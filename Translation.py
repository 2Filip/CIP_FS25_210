import os
import pandas as pd
import requests
import time

DEEPL_API_KEY = "e266391d-6881-452d-b1a9-20057e6a04d0:fx"
DEEPL_URL = "https://api-free.deepl.com/v2/translate"
folder_path = "C:/Users/Celine/OneDrive - Hochschule Luzern/HSLU/2. Sem/CIP02/CIP_FS25_210/Scraping files"
output_folder = "C:/Users/Celine/OneDrive - Hochschule Luzern/HSLU/2. Sem/CIP02/CIP_FS25_210/Scraping files/Translations"
os.makedirs(output_folder, exist_ok=True)


# Translate text via DeepL
def translate_deepl(text, source_lang="DE", target_lang="EN"):
    if pd.isna(text) or str(text).strip() == "":
        return text

    data = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(DEEPL_URL, data=data)

            if response.status_code == 429:
                wait_time = 10 + attempt * 5
                print(f"Too many requests – waiting {wait_time}s before retrying (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue

            if response.status_code != 200:
                print(f"DeepL API error: {response.status_code} - {response.text}")
                return text

            result = response.json()
            time.sleep(1)
            return result["translations"][0]["text"]

        except Exception as e:
            print(f"Translation error: {e}")
            return text

    print("Translation failed after several attempts.")
    return text


# Walk through all Excel files in subfolders
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        if filename.endswith(".xlsx"):
            file_path = os.path.join(root, filename)

            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

            print(f"\n Processing file: {filename}")

            for col in df.columns:
                new_col = f"{col}_EN"
                print(f"Translating column: {col} → {new_col}")
                df[new_col] = df[col].apply(translate_deepl)

            # Save to the central output folder
            new_filename = f"{os.path.splitext(filename)[0]}_translated.xlsx"
            save_path = os.path.join(output_folder, new_filename)
            df.to_excel(save_path, index=False)

            print(f"File saved: {save_path}")
