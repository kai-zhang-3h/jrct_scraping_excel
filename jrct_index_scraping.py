from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup

# Selenium Server に接続する
options = webdriver.ChromeOptions()
driver = webdriver.Remote(
    command_executor='http://selenium:4444/wd/hub',
    options=options
)

driver.implicitly_wait(10)

# Selenium 経由でブラウザを操作する
driver.get('https://jrct.niph.go.jp')
search_button = driver.find_element(By.CSS_SELECTOR, "button[name='button_type'][value='confReg']")

# 検索ボタンをクリック
search_button.click()

# 検索結果ページの読み込みを待つ
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".table")))  # 結果ページの特定要素で待機

html = driver.page_source

soup = BeautifulSoup(html, 'html.parser')

table = soup.find('table', class_='table')
rows = table.find_all('tr')

table_data = []

header_row = rows[0]
headers = [header.text.strip() for header in header_row.find_all('th')]
for row in rows[1:]:
    cells = row.find_all('td')
    cell_data = [cell.text.strip() for cell in cells]
    
    # 閲覧リンクのIDを取得
    view_button = row.find('a')
    onclick_attr = view_button['onclick']
    id_value = onclick_attr.split(".post_")[1].split(".submit")[0]
    # IDをデータに追加
    cell_data.append(id_value)
    table_data.append(cell_data)
    
# データフレームに変換
# カラム名を追加
headers.append("ViewID")
data_df = pd.DataFrame(table_data, columns=headers)

page_number = 1

while True:
    print("page_number: ", page_number)
    page_number += 1
    # Selenium 経由でブラウザを操作する
    driver.get('https://jrct.niph.go.jp/search?searched=1&page='+ str(page_number))
    # 検索結果ページの読み込みを待つ
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".table")))  # 結果ページの特定要素で待機

    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='table')
    rows = table.find_all('tr')

    table_data = []

    header_row = rows[0]
    headers = [header.text.strip() for header in header_row.find_all('th')]
    for row in rows[1:]:
        cells = row.find_all('td')
        cell_data = [cell.text.strip() for cell in cells]
        
        # 閲覧リンクのIDを取得
        view_button = row.find('a')
        onclick_attr = view_button['onclick']
        id_value = onclick_attr.split(".post_")[1].split(".submit")[0]
        # IDをデータに追加
        cell_data.append(id_value)
        table_data.append(cell_data)
        
    # データフレームに変換
    # カラム名を追加
    headers.append("ViewID")
    df = pd.DataFrame(table_data, columns=headers)
    data_df = pd.concat([data_df, df], ignore_index=True)
    
    #全ページ数をえる
    # ページネーションの要素を取得
    pagination = soup.find('ul', class_='pagination')
    # ページネーションのリンクをすべて取得
    page_links = pagination.find_all('a', class_='page-link')
    # リンクの中から最大ページ数を取得
    max_page = max([int(link.text) for link in page_links if link.text.isdigit()])
    if page_number >= max_page:
        break
    
driver.quit()

data_df.to_csv('jrct_index_data.csv', index=False)
    