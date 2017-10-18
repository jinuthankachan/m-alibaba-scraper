# -*- coding: utf-8 -*-

import requests
import csv
from bs4 import BeautifulSoup

record = {}
# List of items
#===============================================
record['title'] = ""
record['image list'] = []

record['moq'] = ""
record['currency'] = ""
record['low price'] = ""
record['high price'] = ""
record['unit'] = ""

record['supplier name'] = ""
record['supplier company'] = ""
record['supplier url'] = ""

record['Packaging Details'] = ""
record['Payment Terms'] = ""
record['Delivery Details'] = ""
record['Supply Ability'] = ""
record['Port'] = ""

keys = record.keys()

#################################################################
def scrape_pdp(url, w, keys):
    try:
        res = requests.get(url)
    except:
        print "failed loading page: ", url
        return None
    print "scraping page: ", url
    soup = BeautifulSoup(res.text, 'html.parser')

    # PDP page details #
    #==================#

    # image list #
    image_list = []
    img_bundle_list = soup.find('ul', class_='image-wrap sized').find_all('li')
    image_list.append(img_bundle_list[0].find('img', class_ ='normal').get('src')[2:].encode('utf-8'))
    for img_bundle in img_bundle_list[1:]:
        img = img_bundle.find('img', class_ ='normal').get('data-src')
        image_list.append(img[2:].encode('utf-8'))
    record['image list'] = image_list

    # Title #
    title_ = soup.find('h1', class_='title')
    record['title'] = " ".join(title_.text.split())

    # MOQ #
    moq_ = soup.find('div', class_='min-order')
    record['moq'] = " ".join(" ".join(item.split()) for item in moq_.find_all(text=True) if item.parent.name != "span")

    # Detail-Product #
    currency = soup.find('span', {"itemprop" : "priceCurrency"})
    record['currency'] = currency.text if currency is not None else ""
    low_price = soup.find('span', {"itemprop" : "lowPrice"})
    record['low price'] = low_price.text if low_price is not None else ""
    high_price = soup.find('span', {"itemprop" : "highPrice"})
    record['high price'] = high_price.text if high_price is not None else ""
    unit = soup.find('span', {"itemprop" : "unit"})
    record['unit'] = unit.text if unit is not None else ""

    # Supplier details #
    record['supplier name'] = soup.find('ai-knock-dialog').get('supplier-name')
    record['supplier company'] = soup.find('ai-knock-dialog').get('supplier-company')
    record['supplier url'] = soup.find('a', {'data-domdot':'id:26234'}).get('href')

    # Item details #
    item_details = {}
    section = soup.find('section', id='item-details')
    table_body = section.find('tbody')
    try:
        rows = table_body.find_all('tr')
        for row in rows:
            th = row.find('th').text[:-1]
            if th not in record.keys():
                continue
            td = row.find('td').text
            record[th] = td
    except:
        print "no body"

    # write to csv #
    w.writerow(record)
###################################################################

#  main() #
searchTerm = "hemp_seed"
pageNo = "1"
file_name = searchTerm + "_" + pageNo + ".csv"

f = open(file_name, 'wb')
w = csv.DictWriter(f, keys)
w.writeheader()

url = "https://m.alibaba.com/products/" + searchTerm + "/" + pageNo + ".html"
print "Searching: ", url
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

urls = soup.find_all('a', class_='product-detail', href=True)
for i, url in enumerate(urls):
    if (url.has_attr('data-role')) and (url['data-role'] == 'appUrl'):
        continue
    scrape_pdp(url['href'], w, keys)

f.close()
