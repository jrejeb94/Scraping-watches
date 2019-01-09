# from __future__ import unicode_literals
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlretrieve

path = 'D:/Extra_Projects/watches/'


def month_string_to_number(string):
    return {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12
        }[string.strip()[:3].lower()]


def parsing_data(df):
    df = df.assign(auction_place='', auction_date='')
    for elt in df.date_place.unique():
        try:
            place, date = elt.split(' Auction ')
            date_tab = date.split(' ')
        except ValueError:
            place, date = elt.split(' Auctions ')
            date_tab = date.split(' ')

        if len(date_tab) < 5:
            date = '{0}/{1}/{2}'.format(date_tab[0], month_string_to_number(date_tab[1]), date_tab[2])
            date = date if len(date_tab) == 3 else date + ' {}'.format(date_tab[3])
        else:
            date = '{0}-{1}/{2}/{3}'.format(date_tab[0], date_tab[2], month_string_to_number(date_tab[3]), date_tab[4])
        df.loc[df['date_place'] == elt, 'auction_place'] = place
        df.loc[df['date_place'] == elt, 'auction_date'] = date

    return df


def img_download(df):
    df = df.fillna(0)
    for name, group in df.groupby(['auction_name']):
        name = name.replace(':', '')
        name = name.replace('...', '')
        auction_folder = '{0}{1}'.format(path, name)
        if not os.path.exists(auction_folder):
            os.makedirs(auction_folder)
        for row in group.itertuples():
            img_name = "{0}/{1}.jpg".format(auction_folder, row.lot_num)
            if not os.path.exists(img_name) and row.img_src != 0:
                img_src = row.img_src.replace('t_Website_LotDetailMainImage/v25', 't_Website_LotDetailZoomImage/v1')
                urlretrieve(img_src, img_name)


def scappe_article(link, auction_url, homepage):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html5lib")
    lot_symb = ''
    auc_name = ''
    lot_num = ''
    date_place = ''
    price = ''
    ccy = ''
    estimated_ccy = ''
    estimated_min = ''
    estimated_max = ''
    estimated_other_ccy = ''
    auction_name = soup.find_all('a', {"href": auction_url[len(homepage):]})
    if len(auction_name) != 1:
        print('ERROR while getting auction name (url:{})'.format(link))
    else:
        auc_name = auction_name[0].find_all('strong')[0].text
        date_place = (auction_name[0].find_all('span')[0]).text
    lot_info = soup.find('div', attrs={'class': 'lot-information'})
    try:
        lot = lot_info.find('h1').text
        lot_num=''
        lot_symb = ''
        for s in lot:
            if s.isdigit():
                lot_num = lot_num + s
            else:
                lot_symb = lot_symb + s
    except AttributeError:
        lot = ''
    container = lot_info.find_all('p', {'class': 'title'})
    description = container[0].find('em').text
    try:
        estimated = lot_info.find('p', {'class': 'estimates'}).text.replace('Estimate', '')
        estimated_first = estimated.replace('•', '')
        estimated_first = estimated_first.replace('\t', ' ')
        estimated_first = estimated_first.replace('\xa0', ' ')
        estimated_first = estimated_first.replace('\n', ' ').split(' ')
        estimate_min = estimated_first[0]

        for s in estimate_min:
            if s.isdigit() or s == ',':
                estimated_min = estimated_min + s
            else:
                estimated_ccy = estimated_ccy + s
        estimated_max = estimated_first[2]
        estimated_other_ccy = estimated_first[3]

    except AttributeError:
        estimated = ''

    try:
        sold = lot_info.find('p', attrs={'class': 'sold'}).text.replace('sold for ', '')
        price = ''
        ccy = ''
        for s in sold:
            if s.isdigit() or s in [',', '.']:
                price = price + s
            else:
                ccy = ccy +s
    except AttributeError:
        sold = ''

    details_container =soup.find('ul', {"class": "info-list"}).find_all('span')
    tab = [('house', 'phillips'), ('auction_url', auction_url), ('article_url', link)]
    for item in details_container:
        try:
            tab.append((item.find('strong', {'class': 'section-header'}).text, item.text.replace(item.find('strong', {'class': 'section-header'}).text, '')))
        except AttributeError:
            pass
    try:
        essay = soup.find('div',{'class':'lot-essay'}).text
    except AttributeError:
        essay = ''
    try:
        img = soup.find('img', {'alt': "no alt text provided"}).get('src')
    except AttributeError:
        img = ''

    tab = tab+[('auction_name', auc_name), ('essay', essay), ('date_place',date_place), ('lot', lot),
               ('lot_num', lot_num),('lot_symb', lot_symb), ('sold for', sold), ('price', price), ('currency', ccy),
               ('description', description), ('estimated', estimated), ('estimated_ccy', estimated_ccy), ('img_src', img),
               ('estimated_min', estimated_min), ('estimated_max', estimated_max), ('estimated_other_ccy', estimated_other_ccy)]

    return dict(tab)


if __name__ == '__main__':

    file = os.path.join(path, 'auction url phillips.csv')
    df_auctions = pd.read_csv(file, delimiter=';')
    phillips_data = pd.DataFrame(columns=('house', 'auction_url', 'auction_name', 'article_url', 'img_src',
                                          'Manufacturer:',
                                          'lot', 'lot_symb', 'lot_num', 'Year:', 'date_place', 'auction_place',
                                          'auction_date',
                                          'Reference No:', 'Movement No:', 'Case No:', 'Material:', 'Calibre:',
                                          'estimated', 'estimated_min', 'estimated_max', 'estimated_ccy',
                                          'estimated_other_ccy', 'sold for', 'price', 'currency', 'essay'))
    for url in df_auctions.URL.unique():
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html5lib")

        for link in soup.find_all('option'):
            if link.get('value').startswith('https'):
                print('start scrapping for article : {}'.format(link.get('value')))
                line = scappe_article(link.get('value'), url, 'https://www.phillips.com')
                phillips_data = phillips_data.append(line, ignore_index=True)

    file = 'D:/Extra_Projects/watches/scrapping phillips.csv'
    phillips_data = pd.read_csv(file, delimiter=';')
    phillips_data = parsing_data(phillips_data)
    phillips_data.to_csv('D:\Extra_Projects\watches\\outout auction data phillips.csv', sep=';', index=False,
                         encoding='utf-8')
    # img_download(phillips_data)

