from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
import openpyxl
import requests


service = Service("C:\\Windows\\System32\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service)


driver.get("https://www.tagesanzeiger.ch/")


try:
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Akzeptieren')]"))
    )
    accept_button.click()
    print("Datenschutz akzeptiert")
except:
    print("Kein Akzeptieren-Button gefunden")


last_height = driver.execute_script("return document.body.scrollHeight")

for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


html = driver.page_source
soup = BeautifulSoup(html, "lxml")


articles_data = []

for block in soup.find_all("article"):
    headline = block.find("h3")
    teaser = block.find("p") or block.find("h4")
    link = block.find("a", href=True)

    if headline and link:
        headline_text = headline.text.strip()
        teaser_text = teaser.text.strip() if teaser else ""
        article_url = "https://www.tagesanzeiger.ch" + link["href"]

        print(headline_text)
        print(teaser_text)
        print(article_url)

        try:
            response = requests.get(article_url)
            article_soup = BeautifulSoup(response.text, "lxml")
            time_tag = article_soup.find("time")
            article_timestamp = time_tag.text.strip() if time_tag else "Unbekannt"
            print("🕒", article_timestamp)
        except:
            article_timestamp = "Fehler beim Abrufen der Zeit"


        if "heute" in article_timestamp.lower():
            articles_data.append({
                "Header": headline_text,
                "Teaser": teaser_text,
                "Link": article_url,
                "Zeit": article_timestamp
            })



df = pd.DataFrame(articles_data)
output_path = r"C:\Users\Kavita\OneDrive\CIP\Webscraping\Tagesanzeiger\FridayPM.xlsx"
df.to_excel(output_path, index=False)


driver.quit()
