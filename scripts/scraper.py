import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

def get_rating(star_str):
    ratings = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    return ratings.get(star_str, 0)

def scrape_books():
    all_books = []

    for page in range(1, 51):  
        print(f"🔍 Coletando página {page}...")
        response = requests.get(BASE_URL.format(page))
        response.encoding = 'utf-8'  
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.find_all('article', class_='product_pod')

        for book in books:
            title = book.h3.a['title']
            price_text = book.find('p', class_='price_color').text
            price_clean = ''.join(c for c in price_text if c.isdigit() or c == '.' or c == ',')
            price = float(price_clean)
            rating = book.p['class'][1]  # Ex: 'Three'
            availability = book.find('p', class_='instock availability').text.strip()
            image = "https://books.toscrape.com/" + book.img['src'].replace('../', '')
            
            book_data = {
                'title': title,
                'price': float(price),
                'rating': get_rating(rating),
                'availability': availability,
                'image_url': image,
                'category': "Desconhecida"  # Temporariamente
            }
            all_books.append(book_data)

        time.sleep(1)  # respeita o servidor

    return all_books

def save_to_csv(data, filename='data/books.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"📁 Dados salvos em {filename}")

if __name__ == '__main__':
    books = scrape_books()
    save_to_csv(books)
