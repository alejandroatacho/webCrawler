import os
import requests
from bs4 import BeautifulSoup
import csv
import json
import pandas as pd
import dotenv

dotenv.load_dotenv()
URL_TARGET = os.getenv('URL_TARGET')
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

def fetch_page(url):
    try:
        return session.get(url).text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    
    # Find empty divs
    empty_divs = soup.find_all('div', string=lambda text: not text or not text.strip())
    for div in empty_divs:
        data.append({
            'type': 'empty_div',
            'content': str(div)
        })

    # Find broken HTML tags
    for tag in soup.find_all(True):  # Finds all tags
        try:
            tag.contents
        except Exception as e:
            data.append({
                'type': 'broken_html',
                'content': str(tag),
                'error': str(e)
            })

    return data

def save_to_csv(data, filename='data.csv'):
    df = pd.DataFrame(data)
    save_path = os.path.join(os.path.dirname(__file__), 'data', filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)

def save_to_json(data, filename='data.json'):
    save_path = os.path.join(os.path.dirname(__file__), 'data', filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def save_to_excel(data, filename='data.xlsx'):
    df = pd.DataFrame(data)
    save_path = os.path.join(os.path.dirname(__file__), 'data', filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_excel(save_path, index=False)

def main():
    base_url = URL_TARGET
    html_content = fetch_page(base_url)
    if html_content:
        all_data = parse_data(html_content)
        print(f"Found {len(all_data)} issues on {base_url}:")
        for item in all_data:
            print(item)

        save_to_csv(all_data)
        save_to_json(all_data)
        save_to_excel(all_data)

if __name__ == "__main__":
    main()
