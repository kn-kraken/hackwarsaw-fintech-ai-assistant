from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


start_url = 'https://www.biznes.gov.pl/pl/portal/0516'

driver = webdriver.Chrome()

driver.get(start_url)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.row.tiles.list-unstyled'))
)

page_html = driver.page_source
page_soup = BeautifulSoup(page_html, 'html.parser')

topic_list = page_soup.find('ul', class_='row tiles list-unstyled')
topics = topic_list.find_all('li')

DOCS = []

for topic in topics:
    topic_url = topic.find('a')['href']
    topic_title = topic.find('a').get_text(strip=True)
    DOCS.append({'topic': topic_title, 'topic_url': f'https://biznes.gov.pl/pl/portal/{topic_url}'})

for idx, doc in enumerate(DOCS):
    driver.get(doc['topic_url'])
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#insidecontent'))
    )

    topic_html = driver.page_source
    
    topic_soup = BeautifulSoup(topic_html, 'html.parser')

    doc["articles"] = []

    articles_list = topic_soup.find('ul', class_='content-list mt-0')
    articles = articles_list.find_all('li')
    for article in articles:
        a_tag = article.find('a', class_='title')
        if a_tag is None:
            continue
        title = a_tag.get_text(strip=True)
        url = f"https://www.biznes.gov.pl{a_tag['href']}"

        driver.get(url)

        article_html = driver.page_source
        article_soup = BeautifulSoup(article_html, 'html.parser')

        article_content_outer = article_soup.find('div', class_='col-12 col-md-7 position-static')
        try:
            content_raw = article_content_outer.find('div')
            content_clean = content_raw.get_text(separator=' ', strip=True)
            doc["articles"].append({'article': title, 'article_url': url, 'content_raw': content_raw, 'content_clean': content_clean})
        except AttributeError:
            print(f"Error in article at {url}")
       
driver.quit()
