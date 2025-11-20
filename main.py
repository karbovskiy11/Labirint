from bs4 import BeautifulSoup
import requests
import csv
import os.path
import time
import random

NUM = 1

def get_headers():
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }
    return headers

def get_page(page):
    print('получаю страницу')
    # with open('index.html', 'r', encoding='utf-8') as file:
    #     response = file.read()
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }

    url = f'https://www.labirint.ru/genres/1852/?page={page}'
    request = requests.get(url, headers=headers)

    if request.status_code == 200:
        print('YES')
    else:
        print('NO')


    # url = f'https://www.labirint.ru/genres/1852/?page={page}'
    # request = requests.get(url, headers)
    response = request.text
    print(f'Page completed')
    time.sleep(random.randrange(2, 4))
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
    with open('data/labirint_books.csv', 'w', newline='', encoding='utf-8') as csvfile:
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

def labirint_books(all_category):
    # собираем данные о книге

    data = []
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
        try:
            item_author = product.find('div', class_='product-author').find('a').get('title')
        except:
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
            [
                NUM,
                item_titles,
                item_author,
                item_pubhouse_series,
                item_price,
                item_discount_price,
                item_sale
            ]
        )

    write_data_books(data)
    print(data)



def write_data_books(data):          #
    print('Записываю данные!')

    with open(f'data/labirint_books.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerows(data)



def main():
    # headers = get_headers()
    create_directories()
    create_labirint_books()

    first_page_content = get_page(1)
    if not first_page_content:
        print('Неудалось загрузить первую страницу')
        return

    soup = BeautifulSoup(first_page_content, 'lxml')
    count_page = get_count_paginations(soup)

    # for page in range(2, count_page + 1):
    for page in range(1, 3):
        soup = BeautifulSoup(get_page(page), 'lxml')
        all_category = soup.find('div', class_='js-content-block-tab').find_all('div', class_='genres-carousel__item')
        labirint_books(all_category)


if __name__ == "__main__":
    main()
