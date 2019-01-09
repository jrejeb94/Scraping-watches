# from __future__ import unicode_literals
import pandas as pd
import re
from numpy import nan
from Antiquorum import replace_all
path = 'D:/Extra_Projects/watches/Antiquorum/'


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


def parsing(antiquorum_data):
    for row in antiquorum_data.itertuples():
        Sale_Title = row.Sale_Title.replace(' & ', '-')
        if '&' in Sale_Title:
            antiquorum_data.loc[row.Index, 'Date'] = '27-28/6/2015'
        if row.Date == '//' or row.Location == '':

            try:
                Location, date = Sale_Title.replace('rd', '').split(', ')
            except ValueError:
                Location, town, date = Sale_Title.replace('rd', '').split(', ')
            day, month, year = date.replace('th', '').split(' ')
            month = month_string_to_number(month)
            Date = day.replace('nd', '')+'/'+str(month)+'/'+year
            antiquorum_data.loc[row.Index, 'Date'] = Date
            antiquorum_data.loc[row.Index, 'Location'] = Location
        if row.Price in ['CHF', 'EUR', 'HKD', 'USD', 'ITL', 'JPY']:
            antiquorum_data.loc[row.Index, 'Price'], antiquorum_data.loc[row.Index, 'Currency'] = \
                antiquorum_data.loc[row.Index, 'Currency'], antiquorum_data.loc[row.Index, 'Price']
        if any(',' in str(x) for x in [row.Price, row.High_Est, row.Low_Est]):
            antiquorum_data.loc[row.Index, 'Price'] = str(row.Price).replace(',', ' ')
            antiquorum_data.loc[row.Index, 'High_Est'] = str(row.High_Est).replace(',', ' ')
            antiquorum_data.loc[row.Index, 'Low_Est'] = str(row.Low_Est).replace(',', ' ')

    return antiquorum_data
    # to_parse_file = 'D:/Extra_Projects/watches/Antiquorum/parsed scrapping Antiquorum 2008-2009.csv'
    # antiquorum_data.to_csv(to_parse_file, sep=';', index=False, encoding='utf-8')


def paring_detailed_info(dataframe):
    dataframe = dataframe.assign(Reference=nan)
    for row in dataframe.itertuples():
        if row.Title is nan:
            continue
        mouvement_pattern = re.compile("movement N?o?.?\s?\d+,?.?", re.IGNORECASE)
        if len(re.findall(mouvement_pattern, row.Title)) == 1:
            movement = re.findall(mouvement_pattern, row.Title)[0]
            movement = movement + ' ' + row.Mouvement if row.Mouvement is not nan else movement
            dataframe.loc[row.Index, 'Mouvement'] = movement

        else:
            print('no movement information in line ', row.Index)

        case_pattern = re.compile("case N?o?.?\s?\w+\d+,?.?", re.IGNORECASE)
        if len(re.findall(case_pattern, row.Title)) == 1:
            case = re.findall(case_pattern, row.Title)[0]
            case = case + ' ' + row.Case if row.Case is not nan else case
            dataframe.loc[row.Index, 'Case'] = case
        else:
            print('no case information in line ', row.Index)

        ref_pattern = re.compile("ref.?\s?\w+\s*\d+,?.?", re.IGNORECASE)
        if len(re.findall(ref_pattern, row.Title)) == 1:
            ref = re.findall(ref_pattern, row.Title)[0]
            dataframe.loc[row.Index, 'Reference'] = ref
        else:
            print('no ref information in line ', row.Index)
    return dataframe

def parse_price(antiquorum_data):
    pattern = re.compile('\d+,?\d*,?\d*')
    for row in antiquorum_data.itertuples():
        if row.Sold is nan:
            continue
        p = re.findall(pattern, row.Sold)[0] if \
            len(re.findall(pattern, row.Sold)) == 1 else nan
        antiquorum_data.loc[row.Index, 'Price'] = replace_all(p, [','], ' ')
    return antiquorum_data

path = 'D:/Extra_Projects/watches/Antiquorum/'
file = 'last scrapping Antiquorum 1989.csv'
antiquorum_data = pd.read_csv(path+file, sep=';')

antiquorum_data = parsing(antiquorum_data)
antiquorum_data = parse_price(antiquorum_data)
antiquorum_data = paring_detailed_info(antiquorum_data)
out_file = path + 'parsed ' + file[:-4] + '.csv'
antiquorum_data.to_csv(out_file, sep=';', index=False, encoding='utf-8')
