#!/usr/bin/env python
# coding: utf-8

from urllib.request import urlopen
from io import BytesIO, StringIO
from zipfile import ZipFile

import csv

import sys

from pprint import pprint

REQUESTED_DATA = [u'DailyOilList', u'DailyGasList', u'DailyWaterList', u'ProductionDaysList']

def url_to_list(url: str, file: str) -> list:
    with urlopen(url) as data:
        archive = ZipFile(BytesIO(data.read()))
        
    text = archive.open(file).read().decode()
    text = text.replace(u'"', u'')
    
    return [line.split(u',') for line in text.split(u'\n')]

def create_field_name_dictionary(fields: list) -> dict:    
    dictionary = dict()

    for row in fields:
        blocknum = row[2] + row[3]
        blocknum = blocknum.replace(u' ', u'')

        dictionary[blocknum] = row[0]
    
    return dictionary

def list_maker(data: dict):
    values = list()
    for month in date_generator(FIRST_MONTH, LAST_MONTH):
        if month in data.keys():
            values.append(data[month])
        
        else:
            values.append('0')
    
    return values

def month_range(data: dict) -> tuple:
    first_month = sys.maxsize
    last_month = 0
    
    for wz in data:
        min_month = int(min(data[wz][u'ProductionDays'].keys()))
        max_month = int(max(data[wz][u'ProductionDays'].keys()))

        if min_month < first_month:
            first_month = min_month

        if max_month > last_month:
            last_month = max_month
            
    months = ((last_month // 100) - (first_month // 100)) * 12 + (last_month % 100 - first_month % 100) + 1
    return first_month, last_month, months

def date_generator(start: int, stop: int) -> str:
    value = start
    while value <= stop:
        yield str(value)
        
        if value % 100 == 12:
            value += 100
            value -= 11

        else:
            value += 1

ogora_links = [
    ('https://www.data.bsee.gov/Production/Files/ogora1996delimit.zip', u'ogora1996delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora1997delimit.zip', u'ogora1997delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora1998delimit.zip', u'ogora1998delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora1999delimit.zip', u'ogora1999delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2000delimit.zip', u'ogora2000delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2001delimit.zip', u'ogora2001delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2002delimit.zip', u'ogora2002delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2003delimit.zip', u'ogora2003delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2004delimit.zip', u'ogora2004delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2005delimit.zip', u'ogora2005delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2006delimit.zip', u'ogora2006delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2007delimit.zip', u'ogora2007delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2008delimit.zip', u'ogora2008delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2009delimit.zip', u'ogora2009delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2010delimit.zip', u'ogora2010delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2011delimit.zip', u'ogora2011delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2012delimit.zip', u'ogora2012delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2013delimit.zip', u'ogora2013delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2014delimit.zip', u'ogora2014delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2015delimit.zip', u'ogora2015delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2016delimit.zip', u'ogora2016delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2017delimit.zip', u'ogora2017delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogora2018delimit.zip', u'ogora2018delimit.txt'),
    ('https://www.data.bsee.gov/Production/Files/ogoradelimit.zip', u'ogoradelimit.txt')]

ogora_data = url_to_list(url = ogora_links[19][0], file = ogora_links[19][1])[:-1]
ogora_data = ogora_data + url_to_list(url = ogora_links[20][0], file = ogora_links[20][1])[:-1]
ogora_data = ogora_data + url_to_list(url = ogora_links[21][0], file = ogora_links[21][1])[:-1]

fields_link = u'https://www.data.bsee.gov/Other/Files/DeepQualRawData.zip'

fields_data = url_to_list(url = fields_link, file = u'DeepQualRawData/mv_deep_water_field_leases.txt')[1:-1]

fields_dict = create_field_name_dictionary(fields = fields_data)


ogora_dict = {}

for row in ogora_data:
    API = row[8]
    Int = row[15]
    BlockNum = row[10]
   
  
    WellZone = API + Int
    
    ogora_dict[WellZone] = {
        u'BlockNum': BlockNum,
        u'API': API,
        u'Int': Int,
        u'DailyOil': dict(),
        u'DailyGas': dict(),
        u'DailyWater': dict(),
        u'ProductionDays': dict()
    }
    
#     if WellZone not in ogora_dict.keys():
#         ogora_dict[WellZone] = {
#             u'BlockNum': BlockNum,
#             u'API': API,
#             u'Int': Int,
#             u'FieldName': u'MISSING_DATA',
#             u'DailyOil': dict(),
#             u'DailyGas': dict(),
#             u'DailyWater': dict(),
#             u'ProductionDays': dict()
#         }

for well in list(ogora_dict.keys()):
    a = ogora_dict[well][u'BlockNum'].replace(u' ', u'')
    
    try:
        ogora_dict[well][u'FieldName'] = fields_dict[a]
    
    except KeyError:
        ogora_dict[well][u'FieldName'] = u'NAME_NOT_FOUND'

for row in ogora_data:
    ogora_dict[row[8] + row[15]][u'DailyOil'][row[2]] = row[5]
    ogora_dict[row[8] + row[15]][u'DailyGas'][row[2]] = row[6]
    ogora_dict[row[8] + row[15]][u'DailyWater'][row[2]] = row[7]
    ogora_dict[row[8] + row[15]][u'ProductionDays'][row[2]] = row[3]

       
FIRST_MONTH, LAST_MONTH, TOTAL_MONTHS = month_range(ogora_dict)

for wz in ogora_dict.keys():
    for info in REQUESTED_DATA:
        ogora_dict[wz][info] = list_maker(ogora_dict[wz][info[:-4]])

for request in REQUESTED_DATA:
    data_collector = list()
    
    data_collector.append([u'Field', u'BlockNum', u'API', u'Int', u'WellZone'] + list(date_generator(FIRST_MONTH, LAST_MONTH)))

    for wz in ogora_dict.keys():
        Field = ogora_dict[wz][u'FieldName']
        BlockNum = ogora_dict[wz][u'BlockNum']
        API = ogora_dict[wz][u'API']
        Int = ogora_dict[wz][u'Int']

        WellZone = wz

        numbers = ogora_dict[wz][request]

        data = [Field, BlockNum, API, Int, WellZone] + numbers[:]

        data_collector.append(data)
    
    with open(f'{request}.csv', u'w', newline = u'') as f:
        writer = csv.writer(f)
        writer.writerows(data_collector)
        
