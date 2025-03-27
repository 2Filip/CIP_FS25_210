from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Set up WebDriver
service = Service(r"C:\Windows\System32\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://www.20min.ch/")
time.sleep(5)

# Accept cookies if prompted
try:
    accept_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Akzeptieren')]")
    driver.execute_script("arguments[0].click();", accept_btn)
    print("✅ Klick auf 'Akzeptieren' per JS.")
except:
    print("⚠️ Kein Akzeptieren-Button gefunden.")

# Scroll down to load more articles
for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# Parse homepage
soup = BeautifulSoup(driver.page_source, "lxml")
articles = soup.find_all("article")
print(f"📌 Gefundene <article>-Blöcke: {len(articles)}")

articles_data = []
seen_links = set()

for article in articles:
    link_tag = article.find("a", href=True)
    if link_tag and link_tag.text.strip():
        headline = link_tag.text.strip()
        href = link_tag["href"]
        if not href.startswith("http"):
            href = "https://www.20min.ch" + href

        if href in seen_links:
            continue
        seen_links.add(href)

        comment_number = "0"
        publication_time = "Unbekannt"

        try:
            driver.get(href)
            time.sleep(2)

            # 💬 Extract comment numbers
            try:
                comment_elements = driver.find_elements(By.CSS_SELECTOR, ".sticky-share div")
                numbers = [el.text.strip() for el in comment_elements if el.text.strip().isdigit()]
                if len(numbers) >= 2:
                    comment_number = numbers[1]
                elif numbers:
                    comment_number = numbers[0]
            except Exception as e:
                print("Fehler beim Auslesen der Kommentare:", e)

            # 🕒 Extract publication time
            try:
                article_soup = BeautifulSoup(driver.page_source, "lxml")
                time_tag = article_soup.find("time")
                if time_tag:
                    publication_time = time_tag.text.strip()
            except Exception as e:
                print("Fehler beim Auslesen der Zeit:", e)

        except Exception as e:
            print("Fehler beim Laden des Artikels:", e)

        print(f"📰 {headline}")
        print(f"💬 Kommentare: {comment_number}")
        print(f"🕒 Publiziert: {publication_time}")
        print(f"🔗 {href}\n")

        articles_data.append({
            "Headline": headline,
            "Kommentare": comment_number,
            "Zeit": publication_time,
            "Link": href
        })

# Save to Excel
if not articles_data:
    print("❌ Keine Artikel gefunden. Excel-Datei wurde nicht erstellt.")
else:
    df = pd.DataFrame(articles_data)

    # ✅ Ensure 'Zeit' is string
    df["Zeit"] = df["Zeit"].astype(str)

    # 🕒 Optionally parse to datetime (if needed)
    def parse_time(value):
        if "Unbekannt" in value:
            return None
        try:
            return pd.to_datetime(value, dayfirst=True)
        except:
            return None

    df["Zeit_Parsed"] = df["Zeit"].apply(parse_time)

    # Save to Excel
    path = r"C:\Users\Kavita\OneDrive\CIP\Webscraping\20min\20minThursdayLunch.xlsx"
    df.to_excel(path, index=False)
    print(f"✅ Excel-Datei gespeichert unter: {path}")

driver.quit()
