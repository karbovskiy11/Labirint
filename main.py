from bs4 import BeautifulSoup
import requests
import csv
import os.path

# url = 'https://www.labirint.ru/genres/1852/'
#
# headers = {
#     'accept': '*/*',
#     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
# }
#
# request = requests.get(url, headers=headers)
# response = request.text
#
# soup = BeautifulSoup(response, 'lxml')
# all_category = soup.find('div', class_='js-content-block-tab').find_all('div', class_='genres-carousel__item')
# count_page = int(
#     soup.find('div', class_='pagination-number__right').find('div', class_='pagination-number').find_next('a').text)
#
# if os.path.exists('pages') is not True:
#     os.mkdir('pages')
#
# if os.path.exists('data') is not True:
#     os.mkdir('data')
#
# with open('labirint_books.csv', 'w', newline='', encoding='utf-8') as csvfile:
#     csvwriter = csv.writer(csvfile, delimiter=',')
#     csvwriter.writerow(
#         (
#             '№',
#             'Название',
#             'Автор',
#             'Издательство',
#             'Цена',
#             'Цена с учётом скидки',
#             'Скидка'
#         )
#     )

numeration = 1
for page in range(1, 2):

    # url = f'https://www.labirint.ru/genres/1852/?page={page}'
    # headers = {
    #     'accept': '*/*',
    #     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    # }
    #
    # request = requests.get(url, headers=headers)
    # response = request.text
    #
    # with open(f'pages/page_{page}.html', 'w', encoding='utf-8') as link:
    #     link.write(response)

    with open('index.html', 'r', encoding='utf-8') as file:
        response = file.read()

    soup = BeautifulSoup(response, 'lxml')
    all_category = soup.find('div', class_='js-content-block-tab').find_all('div', class_='genres-carousel__item')

    # собираем данные о книге
    for item in all_category:
        product = item.find('div', class_='product')
        if not product:
            continue    # пропустить элемент, если нет основного блока

        item_titles = product.get('data-name')
        if not item_titles:
            item_titles = 'Название не указано'    # если название книги отсутствует

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

        item_author = product.find('div', class_='product-author').find('a').get('title')
        if not item_author:
            item_author = 'Автор не указан'   # если автор книги отсутствует

        product_pubhouse = product.find('div', class_='product-pubhouse')
        item_pubhouse = product_pubhouse.find('a', class_='product-pubhouse__pubhouse').get('title')
        if not item_pubhouse:
            item_pubhouse = 'Идательство не указано'

        try:
            item_series = ': ' + product_pubhouse.find('a',class_='product-pubhouse__series').get('title')
        except(AttributeError):
            item_series = ''

        item_pubhouse_series = item_pubhouse + item_series

        with open(f'data/labirint_books_{page}.csv', 'a', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow(
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

    print(f'Page {page} completed')