from urllib.request import urlretrieve
import os, urllib
from bs4 import BeautifulSoup
from selenium import webdriver, common
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from numpy import nan
from selenium.webdriver.support.ui import WebDriverWait
import time
path = 'D:/Extra_Projects/watches/Christies/'
url_file = path + 'Auction Data Sale URLs.xlsx'
# driver = webdriver.Chrome('C:\Program Files\ChromeDriver\chromedriver.exe')


def parse_price(data):

    price, ccy = '', ''
    if data != '':
        data = data.replace(',', '')
        ccy, price = data.split(' ')
        if not price.isdigit():
            ccy, price = price, ccy
    return price, ccy


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


def img_download(year, img_file):
    df = pd.read_csv(img_file, sep=';')
    df = df.fillna(0)
    for name, group in df.groupby(['Sale_number']):
        auction_folder = '{0}{1}/{2}'.format(path, int(year), int(name))
        if not os.path.exists(auction_folder):
            os.makedirs(auction_folder)
        for row in group.itertuples():
            img_name = "{0}/{1}.jpg".format(auction_folder, str(row.Lot).replace(".0", ''))
            if not os.path.exists(img_name) and row.img_src != 0:
                try:
                    urlretrieve(row.img_src, img_name)
                except urllib.error.HTTPError:
                    print(row.img_src)
                    continue


def scrape_article(lot_link):

    driver.get(lot_link)

    lot_soup = BeautifulSoup(driver.page_source, 'html5lib')
    try:
        sale_nb = driver.find_element_by_xpath('//*[@id="main_center_0_lnkSaleNumber"]').text
    except common.exceptions.NoSuchElementException:
        sale_nb = ''
    try:
        sale_title = replace_all(driver.find_element_by_css_selector('#main_center_0_lblSaleTitle').text,
                                 ['\n', '\r'], '')
    except common.exceptions.NoSuchElementException:
        sale_title = ''
    try:
        lot = driver.find_element_by_xpath('//*[@id="main_center_0_lblLotNumber"]').text
    except common.exceptions.NoSuchElementException:
        lot = ''
    try:
    # print(lot_soup.prettify())
        img_src = lot_soup.find('a', class_='panzoom--link').get('data-large-url')
    except AttributeError:
        img_src = ''
    try:
        location = driver.find_element_by_xpath('//*[@id="main_center_0_lblSaleLocation"]').text
    except common.exceptions.NoSuchElementException:
        location = ''
    try:
        date = driver.find_element_by_xpath('//*[@id="main_center_0_lblSaleDate"]').text
        day, month, year = date.split(' ')
        date = day + '/' +str(month_string_to_number(month)) + '/' + year
    except common.exceptions.NoSuchElementException:
        date = ''

    try:
        sold = driver.find_element_by_xpath('//*[@id="main_center_0_lblPriceRealizedPrimary"]').text
        price, ccy = parse_price(sold)
    except common.exceptions.NoSuchElementException:
        price, ccy, sold = '', '', ''

    estimated = ''
    try:
        estimated = driver.find_element_by_xpath('//*[@id="main_center_0_lblPriceEstimatedPrimary"]').text
        estimated = replace_all(estimated, ['\n', '\r'], ' ')
        estimated_list = estimated.split(' - ')
        Low_Est = parse_price(estimated_list[0])[0]
        High_Est, Ccy_Est = parse_price(estimated_list[1])
        if float(Low_Est) > float(High_Est):
            Low_Est, High_Est = High_Est, Low_Est
    except (IndexError, common.exceptions.NoSuchElementException):
        if estimated == '':
            Low_Est, High_Est, Ccy_Est = '', '', ''
        else:
            High_Est, Ccy_Est = '', ''

    try:
        lotEssay_Xpath = '//*[@id="mainform"]/ul[2]/li/div[2]/div/section[1]/header/div'
        lotEssay_button = driver.find_element_by_xpath(lotEssay_Xpath)
        driver.execute_script("arguments[0].click();", lotEssay_button)
        essay = replace_all(driver.find_element_by_xpath('//*[@id="main_center_0_lblLotNotes"]').text,
                            ['\n', '\r'], ' ')
    except common.exceptions.NoSuchElementException:
        essay = ''


    try:
        description = lot_soup.find('span', id='main_center_0_lblLotDescription')

        description_title = str(description.contents[0].next) \
            if str(type(description.contents[0])) == "<class 'bs4.element.Tag'>" else str(description.contents[0])
        description_title = replace_all(description_title, ['\n', '\r'], ' ')
        brand = description_title[:description_title.find('.')]
        description_text = replace_all(description.text, ['\n', '\r'], '')
    except (AttributeError, AttributeError):
        description = ''
        brand = ''
        description_title = ''
        description_text = ''

    tab = [('House', "Christie's"), ('Sale_Title', sale_title), ('Date', date), ('Location', location),
           ('Sale_number', sale_nb), ('link_watch', lot_link), ('Lot', lot), ('Title', description_title),
           ('Sold', sold), ('Price', price), ('Currency', ccy),
           ('Estimated', estimated), ('High_Est', High_Est), ('Low_Est', Low_Est), ('Ccy_Est', Ccy_Est),
           ('Brand', brand), ('Description', description_text), ('lots_Essay', essay), ('img_src', img_src)]

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

    return dict(tab)


if __name__ == '__main__':
    # df_auctions = pd.read_excel(url_file, sheetname="Christie's")
    # christies_data = pd.DataFrame(columns=('House', 'Sale_Title', 'Date', 'Location', 'Sale_number',
    #                                        'link_watch', 'Lot',  'Title',
    #                                        'Sold', 'Price', 'Currency',
    #                                        'Estimated', 'Low_Est', 'High_Est', 'Ccy_Est',
    #                                        'Case', 'Dial', 'Movement', 'Strat/Buckle/Bracelet',
    #                                        'lots_Essay', 'img_src', 'Description',
    #                                        'Brand', 'Reference','Accessories', 'Signed'
    #                                        )
    #                               )
    # start_year = 2005
    # df_auctions = df_auctions.loc[df_auctions.Year <= start_year]
    # for row in df_auctions.itertuples():
    #     if row.URL is nan:
    #         continue
    #
    #     if start_year - int(row.Year) == 1:
    #         out_file = '{0}scrapping Christies {1}.csv'.format(path, start_year)
    #         christies_data.to_csv(out_file, sep=';', index=False, encoding='utf-8')
    #         start_year = row.Year
    #         christies_data = pd.DataFrame(columns=(
    #                                        'House', 'Sale_Title', 'Date', 'Location', 'Sale_number',
    #                                        'link_watch', 'Lot',  'Title',
    #                                        'Sold', 'Price', 'Currency',
    #                                        'Estimated', 'Low_Est', 'High_Est', 'Ccy_Est',
    #                                        'Case', 'Dial', 'Movement', 'Strat/Buckle/Bracelet',
    #                                        'lots_Essay', 'img_src', 'Description',
    #                                        'Brand', 'Reference','Accessories', 'Signed')
    #                                       )
    #
    #     # try:
    #     print("Auction link : ", row.URL)
    #     driver.get(row.URL)
    #
    #     # # #  Load all Lots  # # #
    #     loadAll_Xpath = '//*[@id="loadAllUpcomingPast"]'
    #     try:
    #         WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'loadAllUpcomingPast')))
    #     except common.exceptions.TimeoutException or AttributeError:
    #         pass
    #     try:
    #         browse_button = driver.find_element_by_xpath(loadAll_Xpath)
    #         driver.execute_script("arguments[0].click();", browse_button)
    #     except common.exceptions.NoSuchElementException:
    #         pass
    #     time.sleep(6)
    #
    #     # # # Start parsing source code # # #
    #     soup = BeautifulSoup(driver.page_source, "html5lib")
    #
    #     # links = [link.get_attribute('href') for link in driver.find_elements_by_xpath('//*[@id=""]')]
    #     # a_tags = soup.find_all('a', href=re.compile("https://www.christies.com/lotfinder/.+"))
    #
    #     lot_tags = soup.find_all('a', class_='cta-image')
    #     lot_links = [tag.get('href') for tag in lot_tags if not tag.get('href').endswith('.aspx')]
    #
    #     for link in lot_links:
    #         print('start scrapping for article : {}'.format(link))
    #         line = scrape_article(link)
    #         christies_data = christies_data.append(line, ignore_index=True)
    #
    #     # except (AttributeError, requests.exceptions.RequestException, requests.exceptions.SSLError) as e:
    #     #     out_file = '{2}Missing scrapping Christies {0}-{1}.csv'.format(start_year, row.Year-1, path)
    #     #     christies_data.to_csv(out_file, sep=';', index=False, encoding='utf-8')
    #     #     print('stopped at : ', row.URL)
    #
    # # driver.quit()
    # out_file = '{1}last scrapping Antiquorum {0}.csv'.format(start_year, path)
    # christies_data.to_csv(out_file, sep=';', index=False, encoding='utf-8')

    for i in range(2014, 2017):

        file = 'D:/Extra_Projects/watches/Christies/scrapping Christies {}.csv'.format(str(i))
        print(i)
        img_download(i, file)
