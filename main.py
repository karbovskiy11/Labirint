from bs4 import BeautifulSoup
import requests
import csv
import os.path
import time
import random
import json


def get_page(page):
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }

    url = f'https://www.labirint.ru/genres/1852/?page={page}'

    try:
        response = requests.get(url=url, headers=headers, timeout=10)
        response.raise_for_status()
        save_page(page, response.text)
        soup = BeautifulSoup(response.text, 'lxml')
        time.sleep(random.randrange(2, 4))
        return soup
    except requests.exceptions.HTTPError as error:
        print(f'Не удалось загрузить страницу {page}: ошибка {error} ')
        return None
    except requests.exceptions.ConnectionError:
        print(f'Ошибка соединения на странице {page}')
        return None
    except requests.exceptions.Timeout:
        print(f'Таймаут на странице {page}')
        return None
    except requests.exceptions.RequestException as error:
        print(f'Общая ошибка на странице {page}: ошибка {error}')
        return None


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
                'Автор',
                'Издательство',
                'Цена',
                'Цена со скидкой',
                'Скидка'
            )
        )


def get_data(item, count):
    product = item.find('div', class_='product')
    if product:
        title = product.get('data-name')
        price = int(product.get('data-price'))
        if price > 0:
            price_discount = int(product.get('data-discount-price'))
            discount = round(100 - ((price_discount / price) * 100))
        else:
            price_discount = 0
            discount = 0

        try:
            pubhouse_series = ': ' + product.get('data-series')
        except AttributeError:
            pubhouse_series = ''

        pubhouse = (product.get('data-pubhouse') + pubhouse_series).strip()

        try:
            author = product.find('div', class_='product-author').find('a').get('title')
        except AttributeError:
            author = 'Автор отсутствует'

        return {
            'N': count,
            'title': title,
            'author': author,
            'pubhouse': pubhouse,
            'price': price,
            'price_discount': price_discount,
            'discount': discount
        }


def write_in_file(data):
    with open(f'data/books.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(data.values())


def main():
    create_directories()
    first_page = get_page(1)
    if not first_page:
        print('Первая страница не загружена. Невозможно продолжить парсинг!')
        return

    count_page = int(first_page.find('div', class_='pagination-numbers__right').find_all('a')[-1].text)
    print(f'Найдено {count_page} страниц.')
    count = 1

    data_json = []
    for page in range(1, count_page + 1):
        print(f'Страница {page} загружена.')
        if page > 1:
            soup = get_page(page)
            if soup is None:
                continue
            all_cards = soup.find('div', class_='js-content-block-tab')
        else:
            all_cards = first_page.find('div', class_='js-content-block-tab')

        book_items = all_cards.find_all('div', class_='genres-carousel__item')
        for item in book_items:
            data = get_data(item, count)
            data_json.append(data)
            write_in_file(data)
            count += 1
        print(f'Парсинг страницы {page} завершён!')

    with open(f'data/books.json', 'w', encoding='utf-8') as json_file:
        json.dump(data_json, json_file, indent=4, ensure_ascii=False)

    print(f'Парсинг окончен!')

if __name__ == "__main__":
    main()
