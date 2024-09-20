import requests
import json
import time
import pandas as pd
import argparse
import urllib.parse
from bs4 import BeautifulSoup

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

def decode_email(encoded_email):
    encoded_email = encoded_email.replace('/cdn-cgi/l/email-protection#', '')

    def r(n, c):
        return int(n[c:c+2], 16)

    def n(n, c):
        o = ""
        a = r(n, c)
        for i in range(c + 2, len(n), 2):
            l = r(n, i) ^ a
            o += chr(l)
        return urllib.parse.unquote(o)

    return n(encoded_email, 0)

def extract_details(detail_url):
    response = requests.get(detail_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Estrazione dell'email
        email_link = soup.find('a', href=lambda href: href and '/cdn-cgi/l/email-protection#' in href)
        email = decode_email(email_link['href']) if email_link else None

        # Estrazione del numero di telefono
        phone_link = soup.find('a', href=lambda href: href and href.startswith('tel:'))
        phone = phone_link.text.strip() if phone_link else None

        # Estrazione dell'indirizzo
        address = None
        address_wrapper = soup.find('div', class_='item-wrapper', string=lambda text: text and 'Address' in text)
        if not address_wrapper:
            address_wrapper = soup.find('h5', string='Address')
            if address_wrapper:
                address_wrapper = address_wrapper.find_parent('div', class_='item-wrapper')

        if address_wrapper:
            address_p = address_wrapper.find('p')
            if address_p:
                address = address_p.text.strip()

        return {
            'email': email,
            'phone': phone,
            'address': address
        }

    return {
        'email': None,
        'phone': None,
        'address': None
    }

def save_data_incrementally(data, filename):
    with open(filename, 'a') as json_file:
        for entry in data:
            json.dump(entry, json_file)
            json_file.write('\n')  # Scriviamo una riga per ogni entry

def save_checkpoint(page, checkpoint_file='checkpoint.txt'):
    with open(checkpoint_file, 'w') as file:
        file.write(str(page))

def load_checkpoint(checkpoint_file='checkpoint.txt'):
    try:
        with open(checkpoint_file, 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 1

def fetch_and_save_data(convert_to_excel=False):
    base_url = "https://travel.padi.com/api/v2/travel/dsl/dive-shops/world/all/"
    params = {
        "bottom_left": "-88.73184165403327,-231.32812500000003",
        "lang": "en",
        "page_size": 20,
        "top_right": "88.79258445879006,467.57812500000006"
    }

    detail_url_prefix = "https://www.padi.com"
    total_pages = 298

    json_filename = 'dive_shops_data.json'
    checkpoint_file = 'checkpoint.txt'

    all_data = []
    current_page = load_checkpoint(checkpoint_file)

    for page in range(current_page, total_pages + 1):
        print(f"Fetching page {page}/{total_pages}...")
        
        params['page'] = page
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            page_data = []
            for entry in data.get('results', []):
                detail_url = entry.get('url')
                if detail_url:
                    if detail_url.startswith('https'):
                        full_detail_url = detail_url
                    else:
                        full_detail_url = detail_url_prefix + detail_url

                    details = extract_details(full_detail_url)

                    if details:
                        entry['email'] = details.get('email')
                        entry['phone'] = details.get('phone')
                        entry['address'] = details.get('address')
                    else:
                        print(f"Details not found for URL: {full_detail_url}")

                page_data.append(entry)
            
            all_data.extend(page_data)
            save_data_incrementally(page_data, json_filename)
            save_checkpoint(page, checkpoint_file)
        else:
            print(f"Error fetching page {page}: {response.status_code}")
        
        time.sleep(1)

    print(f"Data saved incrementally to {json_filename}. Total items: {len(all_data)}")

    if convert_to_excel:
        excel_filename = 'dive_shops_data.xlsx'
        save_to_excel(all_data, excel_filename)
        print(f"Data also saved to {excel_filename}")

def main():
    parser = argparse.ArgumentParser(description='Fetch dive shop data and save to JSON and optionally Excel.')
    parser.add_argument('--excel', action='store_true', help='Save the data to an Excel file as well')
    args = parser.parse_args()
    fetch_and_save_data(convert_to_excel=args.excel)

if __name__ == "__main__":
    main()
