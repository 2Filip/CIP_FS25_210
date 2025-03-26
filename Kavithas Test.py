from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setup WebDriver
service = Service(r"C:\Windows\System32\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://www.20min.ch/")
time.sleep(5)

# Accept cookie banner
try:
    accept_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Akzeptieren')]")
    driver.execute_script("arguments[0].click();", accept_btn)
    print("✅ Klick auf 'Akzeptieren'")
except:
    print("⚠️ Kein Akzeptieren-Button gefunden.")

# Scroll down to load more articles
for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# Parse main page
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
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # 💬 Extract comments
            try:
                comment_elements = driver.find_elements(By.CSS_SELECTOR, ".sticky-share div")
                numbers = [el.text.strip() for el in comment_elements if el.text.strip().isdigit()]
                if len(numbers) >= 2:
                    comment_number = numbers[1]
                elif numbers:
                    comment_number = numbers[0]
            except Exception as e:
                print("❗ Kommentarfehler:", e)

            # 🕒 Extract publication time from multiple sources
            try:
                article_soup = BeautifulSoup(driver.page_source, "lxml")

                # 1. <time> tag
                time_tag = article_soup.find("time")
                if time_tag and time_tag.text.strip():
                    publication_time = time_tag.text.strip()

                # 2. <meta property="article:published_time">
                if publication_time == "Unbekannt":
                    meta_time = article_soup.find("meta", attrs={"property": "article:published_time"})
                    if meta_time and meta_time.get("content"):
                        publication_time = meta_time["content"].strip()

                # 3. CSS fallback via Selenium
                if publication_time == "Unbekannt":
                    try:
                        time_element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((
                                By.CSS_SELECTOR,
                                "time, .publish-date, .article-info time"
                            ))
                        )
                        if time_element.text.strip():
                            publication_time = time_element.text.strip()
                    except:
                        pass

            except Exception as e:
                print("❗ Fehler beim Zeit-Auslesen:", e)

        except Exception as e:
            print("❗ Fehler beim Laden der Seite:", e)

        print(f"📰 {headline}")
        print(f"💬 Kommentare: {comment_number}")
        print(f"🕒 Zeit: {publication_time}")
        print(f"🔗 Link: {href}\n")

        articles_data.append({
            "Headline": headline,
            "Kommentare": comment_number,
            "Zeit": publication_time,
            "Link": href
        })

# Save to Excel
if not articles_data:
    print("❌ Keine Artikel gespeichert.")
else:
    df = pd.DataFrame(articles_data)
    df["Zeit"] = df["Zeit"].astype(str)  # Ensure string type

    # Optional: parse readable dates
    def parse_time(value):
        if "Unbekannt" in value:
            return None
        try:
            return pd.to_datetime(value, dayfirst=True, errors='coerce')
        except:
            return None

    df["Zeit_Parsed"] = df["Zeit"].apply(parse_time)

    save_path = r"C:\Users\Kavita\OneDrive\CIP\Webscraping\20min\Test.xlsx"
    df.to_excel_
