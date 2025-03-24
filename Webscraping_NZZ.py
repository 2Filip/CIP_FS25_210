import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime

# Step 1: Setup session with realistic browser headers
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "DNT": "1"
})

base_url = 'https://www.nzz.ch'

# Step 2: Load main page
response = session.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Step 3: Collect article URLs
weblinks = soup.find_all('article')
pagelinks = []

for article in weblinks:
    a_tag = article.find('a', href=True)
    if a_tag:
        full_url = urljoin(base_url, a_tag['href'])
        if full_url not in pagelinks:
            pagelinks.append(full_url)

print(f"🔗 Found {len(pagelinks)} article links")

# Step 4: Visit each article and extract metadata
titles = []
teasers = []
urls = []
publication_dates = []

for link in pagelinks:
    try:
        article_page = session.get(link)
        article_soup = BeautifulSoup(article_page.content, 'html.parser')

        # Skip blocked or paywalled articles
        if 'paywall' in article_soup.text.lower() or 'abonnieren' in article_soup.text.lower():
            print(f"🔒 Skipping paywalled article: {link}")
            continue

        # Title
        try:
            title = article_soup.find('h1').get_text(strip=True)
        except:
            title = 'No title found'

        # Teaser
        try:
            teaser = article_soup.find('p').get_text(strip=True)
        except:
            teaser = 'No teaser found'

        # Publication date
        try:
            pub_time_tag = article_soup.find('time')
            pub_date = pub_time_tag['datetime'] if pub_time_tag else 'Unknown'
        except:
            pub_date = 'Unknown'

        # Append data
        titles.append(title)
        teasers.append(teaser)
        urls.append(link)
        publication_dates.append(pub_date)

    except Exception as e:
        print(f" Error processing {link}: {e}")
        continue

# Step 5: Save to Excel with correct column order
df = pd.DataFrame({
    'title': titles,
    'teaser': teasers,
    'url': urls,
    'publication_date': publication_dates
})

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
filename = f"nzz_teasers_{timestamp}.xlsx"
df.to_excel(filename, index=False)
print(f" Done. Scraped {len(df)} articles. Saved to {filename}")
