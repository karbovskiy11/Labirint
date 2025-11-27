import json

from bs4 import BeautifulSoup
import requests
import csv
import os.path
import time
import random


def get_page(page):
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }

    url = f'https://www.labirint.ru/genres/1852/?page={page}'

    request = requests.get(url=url, headers=headers)
    response = request.text
    save_page(page, response)
    soup = BeautifulSoup(response, 'lxml')
    time.sleep(random.randrange(2, 4))
    return soup


def save_page(page, response):
    with open(f'pages/page_{page}.html', 'w', encoding='utf-8') as html_file:
        html_file.write(response)


def create_directories():
    os.makedirs('data', exist_ok=True)
    os.makedirs('pages', exist_ok=True)

    with open(f'data/books.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(
            (
                '№',
                'Наименование',
                'цена',
                'цена со скидкой',
                'Издательство',
                'серия',
                'автор'
            )
        )


def get_data(item, count):
    product = item.find('div', class_='product')
    title = product.get('data-name')
    price = product.get('data-price')
    price_discount = product.get('data-discount-price')

    try:
        pubhouse_series = ': ' + product.get('data-series')
    except AttributeError:
        pubhouse_series = ''

    pubhouse = product.get('data-pubhouse') + pubhouse_series

    try:
        author = product.find('div', class_='product-author').find('a').get('title')
    except AttributeError:
        author = 'Автор отсутствует'

    return  {
        'N': count,
        'title': title,
        'price': price,
        'price_discount': price_discount,
        'pubhouse': pubhouse,
        'pubhouse_series': pubhouse_series,
        'author': author
    }


def write_in_file(data):
    with open(f'data/books.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(data.values())

    with open(f'data/books.json', 'a', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def main():
    create_directories()
    first_page = get_page(1)
    count_page = int(first_page.find('div', class_='pagination-numbers__right').find_all('a')[-1].text)
    count = 1

    data_json = []
    for page in range(1, count_page + 1):
        soup = get_page(page)
        all_cards = soup.find('div', class_='js-content-block-tab').find_all('div', class_='genres-carousel__item')
        for item in all_cards:
            data = get_data(item, count)
            data_json.append(data)
            # data.insert(0, count)
            write_in_file(data)
            count += 1
            # print(data)
        print(f'Парсинг страницы {page} завершён!')

    with open(f'data/books.json', 'w', encoding='utf-8') as json_file:
        json.dump(data_json, json_file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
