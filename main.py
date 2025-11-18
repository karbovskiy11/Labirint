from bs4 import BeautifulSoup
import requests
import csv
import os.path

def get_headers():
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }
    return headers

def get_url(page, headers):
    with open('index.html', 'r', encoding='utf-8') as file:
        response = file.read()
    # url = f'https://www.labirint.ru/genres/1852/?page={page}'
    # request = requests.get(url, headers)
    # response = request.text
    return response

def get_count_paginations(soup):
    count_page = int(soup.find('div', class_='pagination-number__right').find('div', class_='pagination-number').find_next('a').text)
    if count_page:
        return count_page
    else:
        count_page = 1
        return count_page

def create_directories():
    os.makedirs('pages', exist_ok=True)
    os.makedirs('data', exist_ok=True)

def create_labirint_books():
    with open('labirint_books.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            (
                '№',
                'Название',
                'Автор',
                'Издательство',
                'Цена',
                'Цена с учётом скидки',
                'Скидка'
            )
        )

def main():
    # create_labirint_books()
    headers = get_headers()
    create_directories()
    numeration = 1

    first_page_content = get_url(1, headers)
    if not first_page_content:
        print('Неудалось загрузить первую страницу')
        return

    soup = BeautifulSoup(first_page_content, 'lxml')
    count_page = get_count_paginations(soup)
    all_category = soup.find('div', class_='js-content-block-tab').find_all('div', class_='genres-carousel__item')
    data_books(all_category)

def data_books(all_category):
    # собираем данные о книге
    data = []
    numeration = 1
    for item in all_category:
        product = item.find('div', class_='product')
        if not product:
            continue    # пропустить элемент, если нет основного блока

        # название книги
        item_titles = product.get('data-name')
        if not item_titles:
            item_titles = 'Название не указано'

        # цена книги (начальная, со скидкой, размер скидки)
        try:
            item_price = int(product.get('data-price', 0))
            item_discount_price = int(product.get('data-discount-price', 0))
            if item_price > 0:
                item_sale = f'{round(item_discount_price / item_price * 100)}%'
            else:
                item_sale = '0%'
        except(ValueError, TypeError):
            item_price = 0
            item_discount_price = 0
            item_sale = '0%'

        # автор книги
        item_author = product.find('div', class_='product-author').find('a').get('title')
        if not item_author:
            item_author = 'Автор не указан'

        # издательство и издательская серя книги
        product_pubhouse = product.find('div', class_='product-pubhouse')
        item_pubhouse = product_pubhouse.find('a', class_='product-pubhouse__pubhouse').get('title')
        if not item_pubhouse:
            item_pubhouse = 'Идательство не указано'
        try:
            item_series = ': ' + product_pubhouse.find('a',class_='product-pubhouse__series').get('title')
        except(AttributeError):
            item_series = ''
        item_pubhouse_series = item_pubhouse + item_series
        data.append(
            (
                numeration,
                item_titles,
                item_author,
                item_pubhouse_series,
                item_price,
                item_discount_price,
                item_sale
            )
        )
        numeration += 1
    write_data_books(data)

def write_data_books(data):          #
    with open(f'data/labirint_books.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerows(data)

print(f'Page completed')

if __name__ == "__main__":
    main()
