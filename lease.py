#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from io import BytesIO, StringIO

from bs4 import BeautifulSoup

import csv
import zipfile

from math import ceil

from datetime import datetime, timedelta

class WebLeaseException(Exception):
    pass


class BSEE_DATA(object):
    def __init__(self, url: str, file: str) -> None:
        self.url = url
        self.file = file.split(u'/')
        self.location = None

    def cache(self) -> str:
        try:
            with open(file = u'storage/{}.time'.format(self.file[1]), mode = 'r') as time_file:
                local = datetime.strptime(time_file.read(), u'%m/%d/%Y %I:%M:%S %p')

            if datetime.now() - local < timedelta(days = 1):
                self.location = u'local'
                self.update = local.strftime(u'%m/%d/%Y %I:%M:%S %p')


            else:
                self.location = u'remote'
                self.update = self.last_update()

        except FileNotFoundError:
            self.location = u'remote'
            self.update = self.last_update()

    def last_update(self) -> str:
        with urlopen(u'https://www.data.bsee.gov/Main/RawData.aspx') as web_page:
            data = BeautifulSoup(web_page.read(), features = u'html.parser')

        if self.file[1] == u'mv_lease_owners_main.txt':
            date = data.find(id=u'ContentPlaceHolderBody_ASPxGridView1_DXDataRow19').find_all(u'td')

        elif self.file[1] == u'mv_lease_area_block.txt':
            date = data.find(id=u'ContentPlaceHolderBody_ASPxGridView1_DXDataRow17').find_all(u'td')

        return date[2].text

    def get_data(self):
        if self.location == None:
            self.cache()

        if self.location == u'local':
            self.get_local_data()

        else:
            self.get_remote_data()

    def get_remote_data(self) -> None:
        with urlopen(url = self.url) as web_file:
            if web_file.status == 200:
                zip_archive = BytesIO(web_file.read())

            else:
                raise WebLeaseException(u'Error downloading file. Please check the URL or try again later.')

        try:
            self.csv = zipfile.ZipFile(file = zip_archive).open(name = u'/'.join(self.file)).read()

        except FileNotFoundError:
            raise WebLeaseException(u'The URL does not lead to a file')

        except zipfile.BadZipfile:
            raise WebLeaseException(u'The URL does not lead to a valid zip file')

        except KeyError:
            raise WebLeaseException(u'The URL does not lead to a valid zip file')

        self.save_data_locally()

    def get_local_data(self) -> None:
        with open(file = u'storage/{}'.format(self.file[1]), mode = u'rb') as csv_file:
            self.csv = csv_file.read()

    def load_data(self) -> list:
        self.data = list(csv.DictReader(f = self.csv.decode().split(u'\n')))

    def save_data_locally(self) -> None:
        with open(file = u'storage/{}'.format(self.file[1]), mode = u'wb') as save_file:
            save_file.write(self.csv)

        with open(file = u'storage/{}.time'.format(self.file[1]), mode = u'w') as save_file:
            save_file.write(self.update)

    def parse_data(self) -> None:
        self.parsed_data = dict()

        for row in self.data:
            if self.aliquot == None:
                row_data = [
                    row[u'AREA_CODE'],
                    row[u'BLOCK_NUM'],
                    row[u'LEASE_STATUS_CD'],
                    row[u'LEASE_EFF_DATE'],
                    row[u'LEASE_EXPIR_DATE'],
                    int(row[u'BLK_MAX_WTR_DPTH'])
                ]

            else:
                row_data = {
                    u'owner': row[u'BUS_ASC_NAME'],
                    u'percentage': float(row[u'ASSIGNMENT_PCT'])
                }

            try:
                self.parsed_data[f"{row[u'LEASE_NUMBER']}{row[u'ASGN_STATUS_CODE'] if self.aliquot else u''}"].append(row_data)

            except KeyError:
                self.parsed_data[f"{row[u'LEASE_NUMBER']}{row[u'ASGN_STATUS_CODE'] if self.aliquot else u''}"] = [row_data]

    def format_owner(self, lease: list) -> list:
        """
        Returns a tuple (kind of like a list...) with the largest owner as [OPERATOR] and the
        remainder of the owners as [OTHERS] in the format:

        ([OPERATOR], [LIST_OF_OTHERS])

        However, the actual values returned are also made to look pretty, in the format shown
        in the function "format_string" below.
        """
        lease.sort(key = lambda company: company['percentage'], reverse = True)

        operator = self.format_string(lease.pop(0))

        others = u', '.join([self.format_string(company) for company in lease])

        return [operator, others]

    def format_string(self, owner_data: dict) -> str:
        """
        Creates a "pretty" string in the format:

        Company Name (Percentage Ownership%)

        For example:
            "Edward Cazier Co. (98%)"
        """
        return u'{company_name} ({percentage}%)'.format(
            company_name = owner_data[u'owner'],
            percentage = ceil(owner_data[u'percentage']))


    def prepare(self, aliquot: bool = None):
        self.aliquot = aliquot

        self.get_data()
        self.load_data()
        self.parse_data()

class WebLeaseWrapper(object):
    def __init__(self, owner, area_block):
        self.owner = owner
        self.area_block = area_block
        self.header_row = [
            u'Lease Number',
            u'Primary Owner',
            u'Other Owners',
            u'Area Code',
            u'Block Number',
            u'Lease Status Code',
            u'Lease Effective Date',
            u'Lease Expiration Date',
            u'Block Max Water Depth (m)']

    def prepare_data(self, aliquot):
        self.owner.prepare(aliquot)
        self.area_block.prepare()

    def prepare_csv_list(self):
        self.body_rows = list()

        for lease in self.owner.parsed_data:
            owner = self.owner.format_owner(self.owner.parsed_data[lease])

            while len(self.area_block.parsed_data[lease]) > 0:
                self.body_rows.append(
                    [lease.strip()] + owner + self.area_block.parsed_data[lease].pop(0))


    def send_csv(self):
        memory_file = StringIO()
        memory_csv = csv.writer(memory_file, dialect = u'excel')
        memory_csv.writerow(self.header_row)

        for row in self.body_rows:
            memory_csv.writerow(row)

        send = BytesIO()
        send.write(memory_file.getvalue().encode(u'UTF-8'))
        send.seek(0)

        memory_file.close()

        return send