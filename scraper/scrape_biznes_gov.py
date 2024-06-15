import requests
from bs4 import BeautifulSoup


start_url = 'https://www.biznes.gov.pl/pl/portal/0516'
page_html = requests.get(start_url).text
page_soup = BeautifulSoup(page_html, 'html.parser')

topic_list = page_soup.find('ul', class_='row tiles list-unstyled')
topics = topic_list.find_all('li')

DOCS = []

for topic in topics:
    topic_url = topic.find('a')['href']
    topic_title = topic.find('a').get_text(strip=True)
    DOCS.append({'title': topic_title, 'url': f'https://biznes.gov.pl/pl/portal/{topic_url}'})

for idx, doc in enumerate(DOCS):
    doc_html = requests.get(doc['url']).text
    with open(f'scraper/test.html', 'w', encoding='utf-8') as file:
        file.write(str(doc_html))

    break

