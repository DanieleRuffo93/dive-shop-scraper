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

    # Convertire la parte iniziale in un valore intero
    def r(n, c):
        return int(n[c:c+2], 16)

    # Decodifica
    def n(n, c):
        o = ""
        a = r(n, c)
        for i in range(c + 2, len(n), 2):
            l = r(n, i) ^ a
            o += chr(l)
        return urllib.parse.unquote(o)

    return n(encoded_email, 0)


def extract_email(detail_url):
    response = requests.get(detail_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        email_link = soup.find('a', href=lambda href: href and '/cdn-cgi/l/email-protection#' in href)
        if email_link:
            return decode_email(email_link['href'])
    return None

def extract_details(detail_url):
    response = requests.get(detail_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        email_link = soup.find('a', href=lambda href: href and '/cdn-cgi/l/email-protection#' in href)
        email = decode_email(email_link['href']) if email_link else None

        phone_link = soup.find('a', href=lambda href: href and href.startswith('tel:'))
        phone = phone_link.text.strip() if phone_link else None

        item_wrappers = soup.find_all('div', class_='item-wrapper')
        address = None
        
        for wrapper in item_wrappers:
            icon = wrapper.find('i', class_='dsl-icons--map-marker')
            if icon:
                address_p = wrapper.find('p')
                if address_p:
                    address = address_p.text.strip()
                    break 

        return {
            'email': email,
            'phone': phone,
            'address': address
        }
    return None


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

    all_data = []

    for page in range(1, total_pages + 1):
        print(f"Fetching page {page}/{total_pages}...")
        
        params['page'] = page
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            for entry in data.get('results', []):
                detail_url = entry.get('url')
                if detail_url:
                    if not detail_url.startswith("https://"):
                        detail_url = detail_url_prefix + detail_url
                    details = extract_details(detail_url)
                    entry['email'] = details['email']
                    entry['phone'] = details['phone']
                    entry['address'] = details['address']
            
            all_data.extend(data.get('results', []))
        else:
            print(f"Error fetching page {page}: {response.status_code}")
        
        time.sleep(1)

    json_filename = 'dive_shops_data.json'
    with open(json_filename, 'w') as json_file:
        json.dump(all_data, json_file, indent=4)

    print(f"Data saved to {json_filename}. Total items: {len(all_data)}")


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
