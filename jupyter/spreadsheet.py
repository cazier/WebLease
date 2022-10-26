#!/usr/bin/env python
# coding: utf-8

import csv
import sys
from io import BytesIO, StringIO
from pprint import pprint
from urllib.request import urlopen
from zipfile import ZipFile

REQUESTED_DATA = [
    "DailyOilList",
    "DailyGasList",
    "DailyWaterList",
    "ProductionDaysList",
]


def url_to_list(url: str, file: str) -> list:
    with urlopen(url) as data:
        archive = ZipFile(BytesIO(data.read()))

    text = archive.open(file).read().decode()
    text = text.replace('"', "")

    return [line.split(",") for line in text.split("\n")]


def create_field_name_dictionary(fields: list) -> dict:
    dictionary = dict()

    for row in fields:
        blocknum = row[2] + row[3]
        blocknum = blocknum.replace(" ", "")

        dictionary[blocknum] = row[0]

    return dictionary


def list_maker(data: dict):
    values = list()
    for month in date_generator(FIRST_MONTH, LAST_MONTH):
        if month in data.keys():
            values.append(data[month])

        else:
            values.append("0")

    return values


def month_range(data: dict) -> tuple:
    first_month = sys.maxsize
    last_month = 0

    for wz in data:
        min_month = int(min(data[wz]["ProductionDays"].keys()))
        max_month = int(max(data[wz]["ProductionDays"].keys()))

        if min_month < first_month:
            first_month = min_month

        if max_month > last_month:
            last_month = max_month

    months = (
        ((last_month // 100) - (first_month // 100)) * 12
        + (last_month % 100 - first_month % 100)
        + 1
    )
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
    (
        "https://www.data.bsee.gov/Production/Files/ogora1996delimit.zip",
        "ogora1996delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora1997delimit.zip",
        "ogora1997delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora1998delimit.zip",
        "ogora1998delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora1999delimit.zip",
        "ogora1999delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2000delimit.zip",
        "ogora2000delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2001delimit.zip",
        "ogora2001delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2002delimit.zip",
        "ogora2002delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2003delimit.zip",
        "ogora2003delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2004delimit.zip",
        "ogora2004delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2005delimit.zip",
        "ogora2005delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2006delimit.zip",
        "ogora2006delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2007delimit.zip",
        "ogora2007delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2008delimit.zip",
        "ogora2008delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2009delimit.zip",
        "ogora2009delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2010delimit.zip",
        "ogora2010delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2011delimit.zip",
        "ogora2011delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2012delimit.zip",
        "ogora2012delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2013delimit.zip",
        "ogora2013delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2014delimit.zip",
        "ogora2014delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2015delimit.zip",
        "ogora2015delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2016delimit.zip",
        "ogora2016delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2017delimit.zip",
        "ogora2017delimit.txt",
    ),
    (
        "https://www.data.bsee.gov/Production/Files/ogora2018delimit.zip",
        "ogora2018delimit.txt",
    ),
    ("https://www.data.bsee.gov/Production/Files/ogoradelimit.zip", "ogoradelimit.txt"),
]

ogora_data = url_to_list(url=ogora_links[19][0], file=ogora_links[19][1])[:-1]
ogora_data = (
    ogora_data + url_to_list(url=ogora_links[20][0], file=ogora_links[20][1])[:-1]
)
ogora_data = (
    ogora_data + url_to_list(url=ogora_links[21][0], file=ogora_links[21][1])[:-1]
)

fields_link = "https://www.data.bsee.gov/Other/Files/DeepQualRawData.zip"

fields_data = url_to_list(
    url=fields_link, file="DeepQualRawData/mv_deep_water_field_leases.txt"
)[1:-1]

fields_dict = create_field_name_dictionary(fields=fields_data)


ogora_dict = {}

for row in ogora_data:
    API = row[8]
    Int = row[15]
    BlockNum = row[10]

    WellZone = API + Int

    ogora_dict[WellZone] = {
        "BlockNum": BlockNum,
        "API": API,
        "Int": Int,
        "DailyOil": dict(),
        "DailyGas": dict(),
        "DailyWater": dict(),
        "ProductionDays": dict(),
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
    a = ogora_dict[well]["BlockNum"].replace(" ", "")

    try:
        ogora_dict[well]["FieldName"] = fields_dict[a]

    except KeyError:
        ogora_dict[well]["FieldName"] = "NAME_NOT_FOUND"

for row in ogora_data:
    ogora_dict[row[8] + row[15]]["DailyOil"][row[2]] = row[5]
    ogora_dict[row[8] + row[15]]["DailyGas"][row[2]] = row[6]
    ogora_dict[row[8] + row[15]]["DailyWater"][row[2]] = row[7]
    ogora_dict[row[8] + row[15]]["ProductionDays"][row[2]] = row[3]


FIRST_MONTH, LAST_MONTH, TOTAL_MONTHS = month_range(ogora_dict)

for wz in ogora_dict.keys():
    for info in REQUESTED_DATA:
        ogora_dict[wz][info] = list_maker(ogora_dict[wz][info[:-4]])

for request in REQUESTED_DATA:
    data_collector = list()

    data_collector.append(
        ["Field", "BlockNum", "API", "Int", "WellZone"]
        + list(date_generator(FIRST_MONTH, LAST_MONTH))
    )

    for wz in ogora_dict.keys():
        Field = ogora_dict[wz]["FieldName"]
        BlockNum = ogora_dict[wz]["BlockNum"]
        API = ogora_dict[wz]["API"]
        Int = ogora_dict[wz]["Int"]

        WellZone = wz

        numbers = ogora_dict[wz][request]

        data = [Field, BlockNum, API, Int, WellZone] + numbers[:]

        data_collector.append(data)

    with open(f"{request}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data_collector)
