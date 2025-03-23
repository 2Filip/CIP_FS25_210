from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# 🔧 Setup ChromeDriver
service = Service(r"C:\Windows\System32\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

# 🌐 Open 20min.ch
driver.get("https://www.20min.ch/")
time.sleep(5)

# 🍪 Accept cookie popup
try:
    accept_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Akzeptieren')]")
    driver.execute_script("arguments[0].click();", accept_btn)
    print("✅ Klick auf 'Akzeptieren' per JS.")
except:
    print("⚠️ Kein Akzeptieren-Button gefunden.")

# ⏬ Scroll down to load more articles
for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# 🧠 Parse page source
soup = BeautifulSoup(driver.page_source, "lxml")

articles_data = []
seen_links = set()

articles = soup.find_all("article")
print(f"📦 Gefundene <article>-Blöcke: {len(articles)}")

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

        # 🔁 Visit article page with Selenium
        comment_number = "0"
        try:
            driver.get(href)
            time.sleep(2)

            # Extract comment count from floating share bar
            numbers = []
            try:
                comment_elements = driver.find_elements(By.CSS_SELECTOR, ".sticky-share div")
                numbers = [el.text.strip() for el in comment_elements if el.text.strip().isdigit()]
                if len(numbers) >= 2:
                    comment_number = numbers[1]  # 💬 is usually the 2nd number
                elif numbers:
                    comment_number = numbers[0]
            except Exception as e:
                print("⚠️ Fehler beim Auslesen der Kommentare:", e)

            print(f"📊 Extrahierte Zahlen im Artikel: {numbers}")
        except Exception as e:
            print("❌ Fehler beim Laden des Artikels:", e)

        print("📰", headline)
        print("💬", comment_number)
        print("🔗", href)
        print("—")

        articles_data.append({
            "Headline": headline,
            "Kommentare": comment_number,
            "Link": href
        })

# 💾 Save to Excel
if not articles_data:
    print("⚠️ Keine Artikel gefunden. Excel-Datei wurde nicht erstellt.")
else:
    df = pd.DataFrame(articles_data)
    df.to_excel(r"C:\Users\Kavita\OneDrive\CIP\Webscraping\20min\Sunday.xlsx", index=False)
    print("✅ Excel-Datei 'Sunday.xlsx' wurde erfolgreich gespeichert.")

# ✅ Cleanup
driver.quit()
