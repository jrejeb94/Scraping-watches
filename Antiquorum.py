# from __future__ import unicode_literals
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlretrieve
import urllib
path = 'D:/Extra_Projects/watches/Antiquorum/Antiquorum 1989/'  # Antiquorum 2002-2003/


def replace_all(string, to_replace, replace_with):
    for caract in to_replace:
        while string.__contains__(caract):
            string = string.replace(caract, replace_with)
    return string


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


def img_download(img_file):
    df = pd.read_csv(img_file, sep=';')
    df = df.fillna(0)
    for name, group in df.groupby(['Sale_Title']):
        auction_folder = '{0}{1}'.format(path, name)
        if not os.path.exists(auction_folder):
            os.makedirs(auction_folder)
        for row in group.itertuples():
            img_name = "{0}/{1}.jpg".format(auction_folder, str(int(row.Lot)))
            if not os.path.exists(img_name) and row.img_src != 0:
                try:
                    urlretrieve(row.img_src, img_name)
                except urllib.error.HTTPError:
                    print(row.img_src)
                    continue


def scappe_article(link, homepage):

    r = requests.get(homepage+link)
    soup = BeautifulSoup(r.content, "html5lib")

    date_place = None
    price = None
    ccy = None
    estimated_ccy = None
    estimated_min = None
    estimated_max = None
    estimated_other_ccy = None
    footnote = None

    # ## #         # # # # # # # # # # # #     Getting the footnote block          # # # # # # # # # # # #        # ## #
    c = soup.find_all('div', {'class': 'container'})
    i = 0
    exists = False
    while i < len(c) and not exists:
        if c[i].find('h4') is not None:
            content = c[i].contents
            j = 0
            while j < len(content) and not exists:
                if str(type(content[j])) == "<class 'bs4.element.Tag'>":
                    footnote = content[j].text
                    exists = footnote.startswith('Notes')
                    if not exists:
                        j = j + 1
                    else:
                        footnote = replace_all(str(content[j].next_sibling), ['\n', '\t', '\r'], '')
                else:
                     j += 1
            i = i + 1 if not exists else i
        else:
            i += 1
    if not exists:
        # print('No footnote for this article')
        pass

    # ## #         # # # # # # # # # # # #     Getting the details/price block       # # # # # # # # # # #        # ## #
    try:
        central_block = soup.find('div', {'class': 'row', 'style': ' padding-top: 80px;'})
        test = central_block.find_all('div', {'class': "col-xs-12 col-md-6"})
        img_block, info_block = test[0], test[1]
    except (AttributeError, IndexError):
        print("Error while scapping the central block")
        return [('House', 'Antiquorum'), ('Footnote', footnote)]

    try:
        img_src = replace_all(img_block.find('div', {'style': 'clear: left;'}).find('a').get('href'), ['\n', '\r'], '')
    except AttributeError:
        img_src = None

    try:
        lot = info_block.find('h3').text
        lot = replace_all(lot, ['\n', '\t', '\r'], '')
        split = lot.split('\xa0\xa0')
        lot = split[0].replace('LOT', '')
    except (AttributeError, IndexError):
        lot = None

    try:
        date_place = info_block.find('small').text
        split = date_place.split(',')
        place = split[0]
        year = split[2]
        day_month = replace_all(split[1], ['  '], ' ').split(' ')
        month = month_string_to_number(day_month[1])
        if '-' in day_month[2]:
            day = day_month[2]
        else:
           day = day_month[2][:2] if day_month[2][:2].isdigit() else day_month[2][:1]
    except (AttributeError, IndexError, KeyError):
        place = None
        year = ''
        month = ''
        day = ''

    try:
        description = replace_all(info_block.find('strong').text, ['\n', '\r'], '')
    except AttributeError:
        description = None

    try:
        estimated = info_block.find('h4')
        estimated_other_ccy = replace_all(str(estimated.next_sibling), ['\t', '  ', '\n', '\r'], '')

        est_split = estimated.text.split(' ')
        estimated_min = est_split[1]
        estimated_ccy = est_split[0]
        estimated_max = est_split[3]
    except (AttributeError, IndexError):
        estimated = None
    try:
        sold = info_block.find('h4', {'style': "TEXT-ALIGN: center;background-color: #eeeeee;color: #c71c1c;padding-top:"
                                               " 5px;padding-bottom: 5px;"}).text.replace(' Sold: ', '')
        sold_split = sold.split(' ')

        if sold_split[1].isdigit():
            price = sold_split[1]
            ccy = sold_split[0]
        else:
            price = sold_split[0]
            ccy = sold_split[1]
    except (AttributeError,IndexError):
        sold = None

    tab = [('House', 'Antiquorum'), ('Sale_Title', date_place), ('Location', place),
                 ('Date', day+'/'+str(month)+'/'+year), ('Lot', lot),
                 ('Sold', sold), ('Price', price), ('Currency', ccy),
                 ('Title', description), ('Estimated', replace_all(estimated.text, ['\n', '\r'], '')),
                 ('Low_Est', estimated_min), ('High_Est', estimated_max), ('Ccy_Est', estimated_ccy),
                 ('img_src', img_src), ('Footnote', footnote),
                 ('Est_other_ccy', estimated_other_ccy), ('link_watch', homepage+link)]

    try:
        container = list(info_block.children)
        for item in container:
            if str(type(item)) != "<class 'bs4.element.Tag'>":
                continue
            if item.name not in ['p', 'span']:
                continue
            try:
                line = item.text
                if line == description:
                    continue
                else:
                    try:
                        cell = item.find('strong').text
                        value = line.replace(cell, '')
                        if value == '':
                            value = str(item.nextSibling)
                            cell = {'C. ': 'Case', 'D. ': 'Dial', 'M. ': 'Mouvement'}[cell]
                        tab.append((cell, value))
                    except (AttributeError, KeyError):
                        # print("check for a new key in the description (Mouvement/Dial/Case)")
                        full_description = item.text
                        tab.append(('Description', full_description))
            except AttributeError:
                continue
    except AttributeError:
        print('An error occurred while retrieving the tabs info from link : ', link)

    return dict(tab)


if __name__ == '__main__':

    file = os.path.join(path, 'Auction Data Sale URLs.xlsx')
    df_auctions = pd.read_excel(file, sheetname='Antiquorum')
    antiquorum_data = pd.DataFrame(columns=('House', 'Sale_Title', 'link_watch', 'Lot', 'Location', 'Date', 'Estimated',
                                            'Low_Est', 'High_Est', 'Ccy_Est', 'Est_other_ccy',
                                            'Sold', 'Price',
                                            'Currency', 'Title', 'Brand', 'Model', 'Year', 'Numbers', 'Caliber',
                                            'Bracelet', 'Case', 'Dial', 'Mouvement',
                                            'Accessories', 'Dimensions', 'Signed', 'Footnote', 'Description'))
    start_year = 1991
    df_auctions = df_auctions.loc[df_auctions.Year <= start_year]
    for row in df_auctions.itertuples():
        try:
            if start_year - int(row.Year) == 2:
                out_file = '{2}scrapping Antiquorum {0}-{1}.csv'.format(row.Year+1, start_year, path)
                antiquorum_data.to_csv(out_file, sep=';', index=False, encoding='utf-8')
                # img_download(antiquorum_data)
                start_year = row.Year
                antiquorum_data = pd.DataFrame(columns=('House', 'Sale_Title', 'link_watch', 'Lot', 'Location', 'Date',
                                                        'Estimated', 'Low_Est', 'High_Est', 'Ccy_Est', 'Est_other_ccy',
                                                        'Sold', 'Price', 'Currency', 'Title', 'Brand', 'Model', 'Year',
                                                        'Numbers', 'Caliber', 'Bracelet', 'Case', 'Dial', 'Mouvement',
                                                        'Accessories', 'Dimensions', 'Signed', 'Footnote', 'Description'
                                                        ))
            r = requests.get(row.URL)
            soup = BeautifulSoup(r.content, "html5lib")
            try:
                pagination = soup.find('span', {'class': 'last'}).find('a').get('href')
                index = pagination.index('page=')
                nb_pages = int(pagination[index + 5:])
            except AttributeError:
                nb_pages = 1

            for page in range(1, nb_pages + 1):
                url_page = row.URL + '?page=' + str(page)
                soup = BeautifulSoup(requests.get(url_page).content, "html5lib")
                all_links = soup.find_all('a')
                for link in all_links:

                    ch = list(link.children)
                    if not list(link.children):
                        print('start scrapping for article : {}'.format(link.get('href')))
                        line = scappe_article(link.get('href'), 'https://catalog.antiquorum.swiss')
                        antiquorum_data = antiquorum_data.append(line, ignore_index=True)
                    else:
                        if len(list(link.children)[0]) > 100:
                            print('start scrapping for article : {}'.format(link.get('href')))
                            line = scappe_article(link.get('href'), 'https://catalog.antiquorum.swiss')
                            antiquorum_data = antiquorum_data.append(line, ignore_index=True)

        except (AttributeError, requests.exceptions.RequestException, requests.exceptions.SSLError) as e:
            out_file = 'D:/Extra_Projects/watches/Missing scrapping Antiquorum {0}-{1}.csv'.format(start_year,
                                                                                                   row.Year-1)
            antiquorum_data.to_csv(out_file, sep=';', index=False, encoding='utf-8')
            print('stopped at : ', row.URL)

    out_file = '{1}last scrapping Antiquorum {0}.csv'.format(start_year, path)
    antiquorum_data.to_csv(out_file, sep=';', index=False, encoding='utf-8')
    # img_download(antiquorum_data)
