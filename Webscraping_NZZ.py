{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "9e168a82",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "🔗 Found 98 article links\n",
      "🔒 Skipping paywalled article: https://bellevue.nzz.ch/sponsored-content/ld.1872886\n",
      "🔒 Skipping paywalled article: https://www.nzz.ch/wissenschaft/newsletter-wohl-sein-ld.1829104\n",
      "🔒 Skipping paywalled article: https://www.nzz.ch/podcast/warum-schlaf-lebenswichtig-ist-ld.1844352\n",
      "🔒 Skipping paywalled article: https://bellevue.nzz.ch/reisen-entdecken/destinationen/nostalgische-trips-retro-reiseziele-wie-palm-springs-capri-oder-bad-gastein-sind-immer-noch-ein-besuch-wert-ld.1876303\n",
      "🔒 Skipping paywalled article: https://bellevue.nzz.ch/kochen-geniessen/gastronomie/guenstiger-essen-in-sternerestaurants-dank-kennenlernmenus-ld.1876600\n",
      "🔒 Skipping paywalled article: https://bellevue.nzz.ch/kochen-geniessen/gastronomie/noma-das-gourmet-restaurant-aus-kopenhagen-verkauft-kaffee-ld.1876538\n",
      "✅ Done. Scraped 92 articles. Saved to nzz_teasers_2025-03-23_21-32.xlsx\n"
     ]
    }
   ],
   "source": [
    "import requests\n",
    "from bs4 import BeautifulSoup\n",
    "import pandas as pd\n",
    "from urllib.parse import urljoin\n",
    "from datetime import datetime\n",
    "\n",
    "# Step 1: Setup session with realistic browser headers\n",
    "session = requests.Session()\n",
    "session.headers.update({\n",
    "    \"User-Agent\": \"Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) \"\n",
    "                  \"AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1\",\n",
    "    \"Accept-Language\": \"en-US,en;q=0.9\",\n",
    "    \"Accept\": \"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\",\n",
    "    \"Referer\": \"https://www.google.com/\",\n",
    "    \"DNT\": \"1\"\n",
    "})\n",
    "\n",
    "base_url = 'https://www.nzz.ch'\n",
    "\n",
    "# Step 2: Load main page\n",
    "response = session.get(base_url)\n",
    "soup = BeautifulSoup(response.content, 'html.parser')\n",
    "\n",
    "# Step 3: Collect article URLs\n",
    "weblinks = soup.find_all('article')\n",
    "pagelinks = []\n",
    "\n",
    "for article in weblinks:\n",
    "    a_tag = article.find('a', href=True)\n",
    "    if a_tag:\n",
    "        full_url = urljoin(base_url, a_tag['href'])\n",
    "        if full_url not in pagelinks:\n",
    "            pagelinks.append(full_url)\n",
    "\n",
    "print(f\"🔗 Found {len(pagelinks)} article links\")\n",
    "\n",
    "# Step 4: Visit each article and extract metadata\n",
    "titles = []\n",
    "teasers = []\n",
    "urls = []\n",
    "publication_dates = []\n",
    "\n",
    "for link in pagelinks:\n",
    "    try:\n",
    "        article_page = session.get(link)\n",
    "        article_soup = BeautifulSoup(article_page.content, 'html.parser')\n",
    "\n",
    "        # Skip blocked or paywalled articles\n",
    "        if 'paywall' in article_soup.text.lower() or 'abonnieren' in article_soup.text.lower():\n",
    "            print(f\"🔒 Skipping paywalled article: {link}\")\n",
    "            continue\n",
    "\n",
    "        # Title\n",
    "        try:\n",
    "            title = article_soup.find('h1').get_text(strip=True)\n",
    "        except:\n",
    "            title = 'No title found'\n",
    "\n",
    "        # Teaser\n",
    "        try:\n",
    "            teaser = article_soup.find('p').get_text(strip=True)\n",
    "        except:\n",
    "            teaser = 'No teaser found'\n",
    "\n",
    "        # Publication date\n",
    "        try:\n",
    "            pub_time_tag = article_soup.find('time')\n",
    "            pub_date = pub_time_tag['datetime'] if pub_time_tag else 'Unknown'\n",
    "        except:\n",
    "            pub_date = 'Unknown'\n",
    "\n",
    "        # Append data\n",
    "        titles.append(title)\n",
    "        teasers.append(teaser)\n",
    "        urls.append(link)\n",
    "        publication_dates.append(pub_date)\n",
    "\n",
    "    except Exception as e:\n",
    "        print(f\"❌ Error processing {link}: {e}\")\n",
    "        continue\n",
    "\n",
    "# Step 5: Save to Excel with correct column order\n",
    "df = pd.DataFrame({\n",
    "    'title': titles,\n",
    "    'teaser': teasers,\n",
    "    'url': urls,\n",
    "    'publication_date': publication_dates\n",
    "})\n",
    "\n",
    "timestamp = datetime.now().strftime(\"%Y-%m-%d_%H-%M\")\n",
    "filename = f\"nzz_teasers_{timestamp}.xlsx\"\n",
    "df.to_excel(filename, index=False)\n",
    "print(f\"✅ Done. Scraped {len(df)} articles. Saved to {filename}\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e331cc43",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.13"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
