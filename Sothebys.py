from urllib.request import urlretrieve
import os, urllib, re
from bs4 import BeautifulSoup
from selenium import common, webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.action_chains.ActionChains import ActionChains
import pandas as pd
from numpy import nan
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
path = 'D:/Extra_Projects/watches/Sothebys/'
url_file = path + 'Auction Data Sale URLs.xlsx'
driver = webdriver.Chrome('C:\Program Files\ChromeDriver\chromedriver.exe')
auction_house_url = 'http://www.sothebys.com'


def parse_price(data):

    price, ccy = '', ''
    if data != '':
        data = data.replace(',', '')
        try:
            ccy, price = data.split()
            if not price.isdigit():
                ccy, price = price, ccy
            return price, ccy
        except (TypeError, ValueError):
            if data[1].isdigit():
                return price, data


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

def img_cleaner(img_file):
    df = pd.read_csv(img_file, sep=';')
    df = df.fillna(0)
    for name, group in df.groupby(['Sale_number']):
        print(name)
        for row in group.itertuples():
            imgs = str(row.img_src).split('\t')
            for img in imgs:
                if len(img) < 5:
                    continue
                img = auction_house_url + img if not img.startswith(auction_house_url) else img
                if img != 'http://www.sothebys.com/content/dam/sothebys/default/lot.jpg':
                    print(img)
    print('\n')


def img_download(year, img_file):
    df = pd.read_csv(img_file, sep=';')
    df = df.fillna(0)
    for name, group in df.groupby(['Sale_number']):
        auction_folder = '{0}{1}/{2}'.format(path, int(year), str(name))
        if not os.path.exists(auction_folder):
            os.makedirs(auction_folder)
        for row in group.itertuples():
            imgs = str(row.img_src).split('\t')
            i = 0
            for img in imgs:
                if len(imgs) == 0:
                    img_name = "{0}/{1}.jpg".format(auction_folder, str(row.Lot).replace(".0", ''))
                else:
                    img_name = "{0}/{1}-{2}.jpg".format(auction_folder, str(row.Lot).replace(".0", ''), i)
                    i += 1
                    img = auction_house_url + img if not img.startswith(auction_house_url) else img
                    print(img_name)
                    urlretrieve('https://www.sothebys.com/content/dam/stb/lots/GE0/GE0804/GE0804-1-lr-1.jpg', img_name)
                if not os.path.exists(img_name) and img != 0:
                    try:
                        img = auction_house_url+img if not img.startswith(auction_house_url) else img
                        urlretrieve(img, img_name)
                    except urllib.error.HTTPError:
                        print(img)
                        continue


def scrape_article(lot_link):

    driver.set_page_load_timeout(10)

    try:
        driver.get(lot_link)
    except common.exceptions.TimeoutException:
        print("Failed")
        try:
            driver.delete_all_cookies()
            time.sleep(10)
        except common.exceptions.TimeoutException:
            pass

    # try:
    #     sale_title = replace_all(
    #         driver.find_element_by_xpath('//*[@id="bodyWrap"]/div[7]/div[5]/div[1]/div/div[4]/h1/div').text,
    #         ['\n', '\r'], '')
    # except common.exceptions.NoSuchElementException:
    #     sale_title = ''

    try:
        lot = driver.find_element_by_xpath('//*[@id="bodyWrap"]/div[6]/div/div[1]/div[1]').text
    except common.exceptions.NoSuchElementException:
        try:
            lot = driver.find_element_by_xpath('//*[@id="bodyWrap"]/div[4]/div').text
        except common.exceptions.NoSuchElementException:
            lot = ''

    try:
        sold = driver.find_element_by_xpath('//*[@id="bodyWrap"]/div[6]/div/div[1]/div[2]/section/div/div[2]').text.replace('LOT SOLD.', '')
        price, ccy = parse_price(sold.strip())
    except (common.exceptions.NoSuchElementException, TypeError):
        price, ccy, sold = '', '', ''

    try:
        Low_Est = replace_all(
            driver.find_element_by_xpath('//*[@id="bodyWrap"]/div[6]/div/div[1]/div[2]/section/div/div[1]/div[2]/span[1]').text,
            ['\n', '\r', ','], '')
        High_Est = replace_all(
            driver.find_element_by_xpath(
                '//*[@id="bodyWrap"]/div[6]/div/div[1]/div[2]/section/div/div[1]/div[2]/span[2]').text,
            ['\n', '\r', ','], '')

        Ccy_Est = replace_all(
            driver.find_element_by_xpath(
                '//*[@id="bodyWrap"]/div[6]/div/div[1]/div[2]/section/div/div[1]/div[3]/div[1]/a').text,
            ['\n', '\r'], ' ')

    except common.exceptions.NoSuchElementException:
            Low_Est, High_Est, Ccy_Est = '', '', ''

    try:
        lotEssay_Xpath = '//*[@id="bodyWrap"]/div[7]/div[6]/div/div/div/div/em'
        essay = replace_all(driver.find_element_by_xpath(lotEssay_Xpath).text,['\r', '\n'], '' )

    except common.exceptions.NoSuchElementException:
        essay = ''

    img1, img2, img3 = '', '', ''
    try:
        img1 = driver.find_element_by_xpath('//*[@id="lotDetail-carousel"]/ul/li[1]/a/img').get_attribute(
            'data-image-path')
        try:
            img2 = driver.find_element_by_xpath('//*[@id="lotDetail-carousel"]/ul/li[2]/a/img').get_attribute(
                'data-image-path')
        except common.exceptions.NoSuchElementException:
            pass
        try:
            img3 = driver.find_element_by_xpath('//*[@id="lotDetail-carousel"]/ul/li[3]/a/img').get_attribute(
                'data-image-path')
        except common.exceptions.NoSuchElementException:
            pass
        img = img1 + '\t' + img2 + '\t' + img3
    except common.exceptions.NoSuchElementException:
        try:
            img = driver.find_element_by_xpath('//*[@id="main-image-container"]/img[1]').get_attribute('src')
        except common.exceptions.NoSuchElementException:
            img = ''


    try:
        brand = replace_all(driver.find_element_by_xpath('//*[@id="bodyWrap"]/div[7]/div[5]/div[2]/div[1]').text,
                            ['\n', '\r', ','], '')
    except common.exceptions.NoSuchElementException:
        brand = ''

    try:
        description = replace_all(driver.find_element_by_xpath('//*[@id="bodyWrap"]/div[7]/div[5]/div[2]/div[2]').text,
                                  ['\n', '\r', ','], '')
    except common.exceptions.NoSuchElementException:
        description = ''

    try:
        details = replace_all(driver.find_element_by_xpath('//*[@id="bodyWrap"]/div[7]/div[5]/div[2]/div[3]/div').text,
                              ['\n', '\r', ','], '')
    except common.exceptions.NoSuchElementException:
        details = ''

    tab = [
           ('link_watch', lot_link), ('Lot', lot),
           ('Price', price), ('Currency', ccy),
           ('High_Est', High_Est), ('Low_Est', Low_Est), ('Ccy_Est', Ccy_Est),
           ('Brand', brand), ('Description', description), ('lots_Essay', essay), ('Details', details), ('img_src', img)]

    try:
        for tag in description.contents:
            if str(type(tag)) == "<class 'bs4.element.Tag'>":
                if tag.name == 'br' or tag.nextSibling.name == 'br':
                    continue
                else:
                    if str(tag.next).lower().__contains__('with') or str(tag.next).lower().__contains__('accompanied'):
                        tab.append(('Accessories', replace_all(str(tag.nextSibling), ['\n', '\r'], ' ')))

                    elif str(tag.next).lower().__contains__('dial'):
                        tab.append(('Dial', replace_all(str(tag.nextSibling), ['\n', '\r'], ' ')))

                    elif str(tag.next).lower().__contains__('case'):
                        tab.append(('Case', replace_all(str(tag.nextSibling), ['\n', '\r'], ' ')))
                    elif str(tag.next).lower().__contains__('movement'):
                        tab.append(('Movement', replace_all(str(tag.nextSibling), ['\n', '\r'], ' ')))
                    elif str(tag.next).lower().__contains__('strap') or str(tag.next).lower().__contains__('buckle')\
                            or str(tag.next).lower().__contains__('bracelet'):
                        tab.append(('Strat/Buckle/Bracelet', replace_all(str(tag.nextSibling), ['\n', '\r'], ' ')))
                    elif str(tag.next).lower().__contains__('signed'):
                        tab.append(('Signed', replace_all(str(tag.nextSibling), ['\n', '\r'], ' ')))
                    else:
                        pass
            elif str(type(tag)) == "<class 'bs4.element.NavigableString'>":
                if str(tag).lower().__contains__('dial'):
                    tab.append(('Dial', replace_all(str(tag), ['Dial: ', '\n', '\r'], ' ')))
                elif str(tag).lower().__contains__('movement'):
                    tab.append(('Movement', replace_all(str(tag), ['Movement: ', '\n', '\r'], ' ')))
                elif str(tag).lower().__contains__('case'):
                    tab.append(('Case', replace_all(str(tag), ['Case: ', '\n', '\r'], ' ')))
                elif any(['with' in str(tag).lower(), 'accompanied' in str(tag).lower()]):
                    tab.append(('Accessories', replace_all(str(tag), ['With: ', 'Accompanied by: ', '\n', '\r'], ' ')))
                elif str(tag).lower().__contains__('strap') or str(tag).lower().__contains__('buckle') or str(tag).lower().__contains__('bracelet'):
                    tab.append(('Strat/Buckle/Bracelet', replace_all(str(tag), ['\n', '\r'], ' ')))
    except AttributeError:
        pass

    return tab


if __name__ == '__main__':
    # driver.delete_all_cookies()
    # df_auctions = pd.read_excel(url_file, sheetname="Sotheby's")
    # Sothebys_data = pd.DataFrame(columns=(
    #                                        'House', 'Sale_number', 'Date', 'Location',
    #                                        'link_watch', 'Lot',
    #                                        'Price', 'Currency',
    #                                        'Low_Est', 'High_Est', 'Ccy_Est',
    #                                        'Description', 'lots_Essay', 'img_src',
    #                                        'Details'
    #                                       )
    #                               )
    # start_year = 2016
    # df_auctions = df_auctions.loc[df_auctions.Year <= start_year]
    # for row in df_auctions.itertuples():
    #     if row.URL is nan:
    #         continue
    #
    #     if int(row.Year) == 2015:
    #         out_file = '{0}scrapping Sothebys {1}.csv'.format(path, start_year)
    #         Sothebys_data.to_csv(out_file, sep=';', index=False, encoding='utf-8')
    #         start_year = row.Year
    #         Sothebys_data = pd.DataFrame(columns=(
    #                                        'House', 'Sale_number', 'Date', 'Location',
    #                                        'link_watch', 'Lot',
    #                                        'Price', 'Currency',
    #                                        'Low_Est', 'High_Est', 'Ccy_Est',
    #                                        'Description', 'lots_Essay', 'img_src',
    #                                        'Details')
    #                                     )
    #
    #     print("Auction link : ", row.URL)
    #     try:
    #         driver.get(row.URL)
    #     except:
    #         pass
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #
    #     # # #  Load all Lots  # # #
    #     try:
    #         loadqtt_Xpath = '//*[@id="bodyWrap"]/div[3]/div[1]/div[3]/div[1]/div/span[2]'
    #         loadqtt = driver.find_element_by_xpath(loadqtt_Xpath).text
    #         lots_qtt = [int(s) for s in loadqtt.split(' ') if s.isdigit()]
    #
    #     except (common.exceptions.NoSuchElementException, common.exceptions.TimeoutException):
    #         # loadqtt_Xpath = '//*[@id="bodyWrap"]/div[3]/div[1]/div[3]/div[1]/div/span[2]'
    #         # loadqtt = driver.find_element_by_xpath(loadqtt_Xpath).text
    #         if row.URL == 'www.sothebys.com/en/auctions/2016/important-watches-hk0671.html':
    #             lot_qtt = 289
    #         elif row.URL == 'www.sothebys.com/en/auctions/2016/important-watches-ge1604.html':
    #             lots_qtt = 311
    #         elif row.URL == 'www.sothebys.com/en/auctions/2015/important-watches-n09521.html':
    #             lots_qtt = 209
    #         elif row.URL == 'www.sothebys.com/en/auctions/2016/important-watches-ge1601.html':
    #             lots_qtt = 261
    #         elif row.URL == 'www.sothebys.com/en/auctions/2016/important-watches-hk0636.html':
    #             lots_qtt = 337
    #         # elif row.URL == ''
    #
    #     # try:
    #     #     WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'loadAllUpcomingPast')))
    #     # except common.exceptions.TimeoutException or AttributeError:
    #     #     pass
    #     # try:
    #     #     browse_button = driver.find_element_by_xpath(loadAll_Xpath)
    #     #     driver.execute_script("arguments[0].click();", browse_button)
    #     # except common.exceptions.NoSuchElementException:
    #     #     pass
    #
    #     # # # Start parsing source code # # #
    #     lot_tags = []
    #     lot_links = []
    #     while len(lot_links) < lots_qtt[0]:
    #         lot_tags = []
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #         time.sleep(5)
    #         soup = BeautifulSoup(driver.page_source, "html5lib")
    #         lot_tags = soup.find_all('a', class_='capture-scroll')
    #         lot_links = [lot_tags[2*s].get('href') for s in range(0, (len(lot_tags)-1)//2 + 1)]
    #
    #     try:
    #         pattern = re.compile('\w+\d+')
    #         sale_nb = driver.find_element_by_xpath('//*[@id="bodyWrap"]/div[3]/div[1]/div[3]/div[1]/div').text
    #         sale_nb = re.findall(pattern, sale_nb)[0]
    #     except common.exceptions.NoSuchElementException:
    #         sale_nb = ''
    #
    #     try:
    #         location = replace_all(
    #             driver.find_element_by_xpath('//*[@id="undefined-sticky-wrapper"]/div/div/div[1]/div/span').text,
    #             ['\n', '\r'], '')
    #     except common.exceptions.NoSuchElementException:
    #         location = ''
    #     try:
    #         date = driver.find_element_by_xpath('//*[@id="x-event-date"]').text
    #         day, month, year = date.split(' ')
    #         date = day + '/' + str(month_string_to_number(month)) + '/' + year
    #     except common.exceptions.NoSuchElementException:
    #         date = ''
    #
    #     tab = [('House', "Sotheby's"), ('Sale_number', sale_nb), ('Date', date), ('Location', location)]
    #
    #     for link in lot_links:
    #         link = auction_house_url + link
    #         print('start scrapping for article : {}'.format(link))
    #
    #         line = scrape_article(link)
    #         Sothebys_data = Sothebys_data.append(dict(tab + line), ignore_index=True)
    #
    # out_file = '{1}last scrapping Antiquorum {0}.csv'.format(start_year, path)
    # Sothebys_data.to_csv(out_file, sep=';', index=False, encoding='utf-8')
    # driver.quit()
    #
    # for i in range(2008, 2018):
    i = 2008
    file = 'D:/Extra_Projects/watches/Sothebys/scrapping Sothebys {}.csv'.format(str(i))
        # df = pd.read_csv(file, sep=';')
        # df = df.fillna(0)
        # for name, group in df.groupby(['Sale_number']):
        #     auction_folder = '{0}{1}/{2}'.format(path, int(i), str(name))
        #     if not os.path.exists(auction_folder):
        #         os.makedirs(auction_folder)
    print(i)
    img_cleaner(file)
#
# for i in range(2008, 2018):
#     df = pd.read_csv(file, sep=';')
#     df = df.fillna(0)
#     for name, group in df.groupby(['Sale_number']):
#         auction_folder = '{0}{1}/{2}'.format(path, int(i), str(name))
#         if not os.path.exists(auction_folder):
#             os.makedirs(auction_folder)
#     file = 'D:/Extra_Projects/watches/Sothebys/scrapping Sothebys {}.csv'.format(str(i))
#     print(i)
#     img_cleaner(file)
