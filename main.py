from bs4 import BeautifulSoup
import requests
import csv

url = 'https://www.labirint.ru/genres/1852/'

headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
}

# request = requests.get(url, headers=headers)
# response = request.text
#
# with open('index.html', 'w', encoding='utf-8') as file:
#     file.write(response)

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

with open('index.html', 'r', encoding='utf-8') as file:
    index = file.read()

soup = BeautifulSoup(index, 'lxml')
all_category = soup.find('div', class_='js-content-block-tab').find_all('div', class_='genres-carousel__item')

all_books = []
numeration = 1
for item in all_category:
    item_titles = item.find('div', class_='product').get('data-name')
    item_price = int(item.find('div', class_='product').get('data-price'))
    item_discount_price = int(item.find('div', class_='product').get('data-discount-price'))
    item_sale = str(round(item_discount_price / item_price * 100)) + '%'
    item_author = item.find('div', class_='product').find('div', class_='product-author').find('a').get('title')
    item_pubhouse = (item.find('div', class_='product').find('div', class_='product-pubhouse').
                     find('a',class_='product-pubhouse__pubhouse').get('title'))
    try:
        item_series = ': ' + (item.find('div', class_='product').find('div', class_='product-pubhouse').find('a',class_='product-pubhouse__series').get('title'))
    except:
        item_series = ''

    item_pubhouse_series = item_pubhouse + item_series

    with open('labirint_books.csv', 'a', newline='', encoding='utf-8') as csvfile:
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

# print(all_books)






