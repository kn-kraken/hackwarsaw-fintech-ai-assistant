from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


start_url = 'https://www.biznes.gov.pl/pl/portal/0516'

driver = webdriver.Chrome()

# Fetch the initial page
driver.get(start_url)

# Allow some time for dynamic content to load, or use an explicit wait
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.row.tiles.list-unstyled'))
)

# Now parse the page with BeautifulSoup
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
    # Fetch the page using Selenium to ensure all dynamic content is loaded
    driver.get(doc['topic_url'])
    
    # Allow time for dynamic content to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#insidecontent'))
    )

    doc_html = driver.page_source
    
    # Process the page with BeautifulSoup
    doc_soup = BeautifulSoup(doc_html, 'html.parser')

    doc["articles"] = []

    content_list = doc_soup.find('ul', class_='content-list mt-0')
    content_items = content_list.find_all('li')
    for item in content_items:
        a_tag = item.find('a', class_='title')
        if a_tag is None:
            continue
        title = a_tag.get_text(strip=True)
        url = f"https://www.biznes.gov.pl{a_tag['href']}"

        doc["articles"].append({'article': title, 'article_url': url})

driver.quit()
