from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time


service = Service(r"C:\Windows\System32\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://www.srf.ch/news")
time.sleep(5)


try:
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[src*='consentmanager']"))
    )
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Alle akzeptieren')]"))
    )
    accept_button.click()
    driver.switch_to.default_content()
    print("✅ Cookies akzeptiert.")
except:
    print("ℹ️ Kein Cookie-Banner gefunden (Iframe oder Button nicht vorhanden).")

# Scroll to load more content
for _ in range(4):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)


teasers = driver.find_elements(By.CSS_SELECTOR, "a.teaser-ng--article")
print(f"📌 Gefundene Artikel: {len(teasers)}")

articles_data = []

for teaser in teasers:
    try:
        headline_elem = teaser.find_element(By.CSS_SELECTOR, "span.teaser-ng__title")
        headline = headline_elem.text.strip()

        href = teaser.get_attribute("href")
        if not href.startswith("http"):
            href = "https://www.srf.ch" + href

        publish_time = teaser.get_attribute("data-date-published") or "Unbekannt"

        print(f"📰 {headline}")
        print(f"🕒 {publish_time}")
        print(f"🔗 {href}\n")

        articles_data.append({
            "Headline": headline,
            "Zeit": publish_time,
            "Link": href
        })

    except Exception as e:
        print(f"❌ Fehler beim Artikel-Block: {e}")


if articles_data:
    df = pd.DataFrame(articles_data)
    output_path = r"C:\Users\Kavita\OneDrive\CIP\Webscraping\SRF\SRFThursdayPM.xlsx"
    df.to_excel(output_path, index=False)
    print(f"✅ Excel-Datei gespeichert: {output_path}")
else:
    print("❌ Keine Artikel gefunden. Keine Excel-Datei erstellt.")

driver.quit()
