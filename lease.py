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


class WebLeaseWrapper(object):
    def __init__(self, owner, area_block, lease_data, companies, lease_operators):
        self.owner = owner
        self.area_block = area_block
        self.lease_data = lease_data
        self.companies = companies
        self.lease_operators = lease_operators

        self.header_row = [
            u'Lease Number',
            u'Primary Owner',
            u'Other Owners',
            u'BlockNum',
            u'Lease Status Code',
            u'Lease Effective Date',
            u'Block Max Water Depth (m)',
            u'Sale Number',
            u'Primary Term',
            u'Lease Expiration Date',
            u'Bid Amount',
            u'Operator']

    def prepare_data(self):
        self.owner.prepare()
        self.area_block.prepare()
        self.lease_data.prepare()
        self.companies.prepare()
        self.lease_operators.prepare()

    def prepare_csv_list(self):
        self.body_rows = list()

        for row in self.owner.parsed_data.keys():
            lease, aliquot = row.split(u';')

            owner = self.owner.format_owner(self.owner.parsed_data[row])

            while len(self.area_block.parsed_data[lease]) > 0:
                self.body_rows.append(
                    [lease.strip()] + \
                    owner + \
                    self.area_block.parsed_data[lease].pop(0) + \
                    self.lease_data.parsed_data[lease] + \
                    [self.companies.parsed_data[self.lease_operators.parsed_data[lease]]])


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

class ZIP_DATA(object):
    def __init__(self, url: str, filepath: str) -> None:
        self.url = url
        self.filepath = filepath.split(u'/')
        self.location = None

        self.delta_days = 1 

    def cache(self) -> str:
        try:
            with open(file = u'storage/{}.time'.format(self.filepath[-1]), mode = 'r') as time_file:
                local = datetime.strptime(time_file.read(), u'%m/%d/%Y %I:%M:%S %p')

            if datetime.now() - local < timedelta(days = self.delta_days):
                self.location = u'local'
                self.update = local.strftime(u'%m/%d/%Y %I:%M:%S %p')

            else:
                self.location = u'remote'
                self.update = self.last_update()

        except FileNotFoundError:
            self.location = u'remote'
            self.update = self.last_update()

    def last_update(self) -> str:
        with urlopen(self.update_site) as web_page:
            data = BeautifulSoup(web_page.read(), features = u'html.parser')

        date = data.find(id = self.update_tag).find_all(u'td')

        return date[self.update_column].text

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
            self.data_file = zipfile.ZipFile(file = zip_archive).open(name = u'/'.join(self.filepath)).read()

        except FileNotFoundError:
            raise WebLeaseException(u'The URL does not lead to a file')

        except zipfile.BadZipfile:
            raise WebLeaseException(u'The URL does not lead to a valid zip file')

        except KeyError:
            raise WebLeaseException(u'The URL does not lead to a valid zip file')

        self.save_data_locally()

    def get_local_data(self) -> None:
        with open(file = u'storage/{}'.format(self.filepath[-1]), mode = u'rb') as local_file:
            self.data_file = local_file.read()

    def save_data_locally(self) -> None:
        with open(file = u'storage/{}'.format(self.filepath[-1]), mode = u'wb') as save_file:
            save_file.write(self.data_file)

        with open(file = u'storage/{}.time'.format(self.filepath[-1]), mode = u'w') as save_file:
            save_file.write(self.update)

    def load_data(self) -> list:
        self.data = list(csv.DictReader(f = self.data_file.decode().split(u'\n')))

    def prepare(self):
        self.get_data()
        self.load_data()
        self.parse_data()

class Lease_Data(ZIP_DATA):
    def __init__(self) -> None:
        super().__init__(
            url = u'https://www.data.boem.gov/Leasing/Files/lsetapefixed.zip',
            filepath = u'LSETAPE.DAT')

        self.update_site = u'https://www.data.boem.gov/Main/Leasing.aspx'
        self.update_tag = u'ContentPlaceHolderBody_ASPxGridView1_DXDataRow4'
        self.update_column = 1

        self.location = None

        self.delta_days = 7


    def load_data(self) -> None:
        self.data = [[
            row[:7].strip(),
            row[16:23].strip(),
            row[50:58].strip(),
            row[58:60].strip(),
            row[60:68].strip(),
            row[122:135].strip()
        ] for row in self.data_file.decode().split(u'\n')]


    def parse_data(self) -> None:
        self.parsed_data = dict()

        for row in self.data:
            if len(row[4]) != 0:
                exp_date = datetime.strptime(row[4], u'%Y%m%d')
                exp_date = exp_date.strftime(u'%m/%d/%Y')

            else:
                if len(row[2]) != 0:
                    exp_date = datetime.strptime(row[2], u'%Y%m%d') + timedelta(days = 365 * int(row[3]))
                    exp_date = exp_date.strftime(u'%m/%d/%Y')
                else:
                    exp_date = u'N/A'

            self.parsed_data[row[0]] = [
                # u'sale_num': 
                string_ifelse(row[1]),
                # u'primary_term': 
                int_ifelse(row[3]),
                # u'exp_date': 
                exp_date,
                # u'bid_amount': 
                float_ifelse(row[5])]

class LAB_Data(ZIP_DATA):
    def __init__(self) -> None:
        super().__init__(
            url = u'https://www.data.bsee.gov/Leasing/Files/LABRawData.zip',
            filepath = u'LABRawData/mv_lease_area_block.txt')

        self.update_site = u'https://www.data.bsee.gov/Main/RawData.aspx'
        self.update_tag = u'ContentPlaceHolderBody_ASPxGridView1_DXDataRow17'
        self.update_column = 2

        self.location = None

    def parse_data(self) -> None:
        self.parsed_data = dict()

        for row in self.data:
            row_data = [
                str(row[u'AREA_CODE']) + str(row[u'BLOCK_NUM']),
                row[u'LEASE_STATUS_CD'],
                row[u'LEASE_EFF_DATE'],
                # row[u'LEASE_EXPIR_DATE'],
                int(row[u'BLK_MAX_WTR_DPTH'])
            ]

            try:
                self.parsed_data[u'{lease}'.format(lease = row[u'LEASE_NUMBER'].strip())].append(row_data)

            except KeyError:
                self.parsed_data[u'{lease}'.format(lease = row[u'LEASE_NUMBER'].strip())] = [row_data]

class Owner_Data(ZIP_DATA):
    def __init__(self) -> None:
        super().__init__(
            url = u'https://www.data.bsee.gov/Leasing/Files/LeaseOwnerRawData.zip',
            filepath = u'LeaseOwnerRawData/mv_lease_owners_main.txt')

        self.update_site = u'https://www.data.bsee.gov/Main/RawData.aspx'
        self.update_tag = u'ContentPlaceHolderBody_ASPxGridView1_DXDataRow19'
        self.update_column = 2

        self.location = None

    def parse_data(self) -> None:
        self.parsed_data = dict()

        for row in self.data:
            row_data = {
                u'owner': row[u'BUS_ASC_NAME'],
                u'percentage': float(row[u'ASSIGNMENT_PCT'])
            }

            try:
                self.parsed_data[u'{lease};{aliquot}'.format(
                    lease = row[u'LEASE_NUMBER'].strip(), 
                    aliquot = row[u'OWNER_ALIQUOT_CD'] if row[u'OWNER_ALIQUOT_CD'] != u'1' else u'')
                ].append(row_data)

            except KeyError:
                self.parsed_data[u'{lease};{aliquot}'.format(
                    lease = row[u'LEASE_NUMBER'].strip(), 
                    aliquot = row[u'OWNER_ALIQUOT_CD'] if row[u'OWNER_ALIQUOT_CD'] != u'1' else u'')
                ] = [row_data]

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

class CompanyNumberToName(ZIP_DATA):
    def __init__(self) -> None:
        super().__init__(
            url = u'https://www.data.bsee.gov/Company/Files/compallfixed.zip',
            filepath = u'compallfixed.txt')

        self.update_site = u'https://www.data.bsee.gov/Main/Leasing.aspx'
        self.update_tag = u'ContentPlaceHolderBody_ASPxGridView1_DXDataRow1'
        self.update_column = 1

        self.location = None
        self.delta_days = 7

    def load_data(self) -> None:
        self.data_file = self.data_file.decode(encoding=u'utf-8', errors=u'ignore').replace(u', \nLLC', u',  LLC')
        self.data = [{
            u'num': row[:5].strip(),
            u'name': row[13:113].strip(),
            } for row in self.data_file.split(u'\n') if row[213:221] == u'        ']

    def parse_data(self) -> None:
        self.parsed_data = {
            entry[u'num']: entry[u'name'] for entry in self.data}

class LeaseNumberToOperator(ZIP_DATA):
    def __init__(self) -> None:
        super().__init__(
            url = u'https://www.data.bsee.gov/Leasing/Files/lseowndfixed.zip',
            filepath = u'lseowndfixed.txt')

        self.update_site = u'https://www.data.bsee.gov/Main/Leasing.aspx'
        self.update_tag = u'ContentPlaceHolderBody_ASPxGridView1_DXDataRow3'
        self.update_column = 1

        self.location = None
        self.delta_days = 1

    def load_data(self) -> None:
        self.data_file = self.data_file.decode(encoding=u'utf-8', errors=u'ignore')
        self.data = [{
            u'lease': row[:7].strip(),
            u'operator': row[49:].strip(),
            u'date': max([self.int_ifelse(row[7:15]), self.int_ifelse(row[41:49])])
            } for row in self.data_file.split(u'\n')]

    def parse_data(self) -> None:
        parsed_data = dict()

        for row in self.data:
            if row[u'lease'] not in parsed_data.keys():
                parsed_data[row[u'lease']] = {u'operator': self.clean_operator(row[u'operator']), u'date': row[u'date']}

            else:
                if row[u'date'] > parsed_data[row[u'lease']][u'date']:
                    parsed_data[row[u'lease']] = {u'operator': self.clean_operator(row[u'operator']), u'date': row[u'date']}

        self.parsed_data = {entry: parsed_data[entry][u'operator'] for entry in parsed_data.keys()}

    def int_ifelse(self, value):
        if len(value.strip()) == 0:
            return 0

        else:
            return int(value)

    def clean_operator(self, value):
        if len(value.strip()) == 0:
            return u'NONE'

        else:
            return value

def int_ifelse(file_value) -> str or int:
    if len(file_value) != 0:
        return int(file_value)

    else:
        return u'N/A'

def float_ifelse(file_value) -> str or float:
    if len(file_value) != 0:
        return float(file_value)

    else:
        return u'N/A'

def string_ifelse(file_value) -> str:
    if len(file_value) != 0:
        return file_value

    else:
        return u'N/A'