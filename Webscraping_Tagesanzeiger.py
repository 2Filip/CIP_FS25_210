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

service = Service("C:\Windows\System32\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)  # , options=chrome_options)

driver.get("https://www.tagesanzeiger.ch/")

try:
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Akzeptieren')]"))
    )
    accept_button.click()
    print("Datenschutz akzeptiert.")
except:
    print("Kein Akzeptieren-Button gefunden oder Timeout.")

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

headlines = []

for h3 in soup.find_all("h3"):
    text = h3.text.strip()
    if text:
        print(text)
        headlines.append(text)

df = pd.DataFrame(headlines, columns=["Überschrift"])

# In Excel speichern
df.to_excel(r"C:\Users\Kavita\OneDrive\CIP\Webscraping\Tagesanzeiger\Sunday.xlsx", index=False)
print("📄 Schlagzeilen wurden in 'schlagzeilen.xlsx' gespeichert.")

driver.quit()
