from urllib.request import urlopen
from io import BytesIO

import zipfile

import csv

from math import ceil

FILE_URL = u'https://www.data.bsee.gov/Leasing/Files/LeaseOwnerRawData.zip'
FILE_NAME = u'LeaseOwnerRawData/mv_lease_owners_main.txt'

def get_csv(url: str, file: str) -> list:
    with urlopen(url = url) as web_file:
        byte_response = BytesIO(web_file.read())

    delim_file = zipfile.ZipFile(file = byte_response).open(name = file).read()

    return csv.DictReader(f = delim_file.decode().split(u'\n'))


def load_lease_owner_data_no_aliquot(source_data: list) -> dict:
    """
    Goes through every row of the lease data, and creates a dictionary of the format:

        {
            LEASE_1_NUMBER: {
                COMPANY_1_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_2_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_3_NAME: PERCENTAGE_OWNERSHIP,
                ...
            },
            LEASE_2_NUMBER: {
                COMPANY_1_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_2_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_3_NAME: PERCENTAGE_OWNERSHIP,
                ...
            },
            LEASE_3_NUMBER: {
                COMPANY_1_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_2_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_3_NAME: PERCENTAGE_OWNERSHIP,
                ...
            },
            ...
        }
    """

    data = dict()

    for row in source_data:
        try:
            data[row[u'LEASE_NUMBER']].append({
                u'owner': row[u'BUS_ASC_NAME'],
                u'percentage': float(row[u'ASSIGNMENT_PCT'])})

        except KeyError:
            data[row[u'LEASE_NUMBER']] = [{
                u'owner': row[u'BUS_ASC_NAME'],
                u'percentage': float(row[u'ASSIGNMENT_PCT'])}]

    return data


def load_lease_owner_data_with_aliquot(source_data: list) -> dict:
    """
    Goes through every row of the lease data, and creates a dictionary of the format:

       {
            LEASE_1_NUMBER + ALIQUOT_CODE: {
                COMPANY_1_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_2_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_3_NAME: PERCENTAGE_OWNERSHIP,
                ...
            },
            LEASE_2_NUMBER + ALIQUOT_CODE: {
                COMPANY_1_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_2_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_3_NAME: PERCENTAGE_OWNERSHIP,
                ...
            },
            LEASE_3_NUMBER + ALIQUOT_CODE: {
                COMPANY_1_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_2_NAME: PERCENTAGE_OWNERSHIP,
                COMPANY_3_NAME: PERCENTAGE_OWNERSHIP,
                ...
            },
            ...
        }
    """

    data = dict()

    for row in source_data:
        try:
            data[u'{lease}{aliquot}'
            .format(
                lease = row[u'LEASE_NUMBER'],
                aliquot = row[u'ASGN_STATUS_CODE']
                )].append({
                    u'owner': row[u'BUS_ASC_NAME'],
                    u'percentage': float(row[u'ASSIGNMENT_PCT'])})

        except KeyError:
            data[u'{lease}{aliquot}'.format(
                lease = row[u'LEASE_NUMBER'],
                aliquot = row[u'ASGN_STATUS_CODE'])] = [{
                    u'owner': row[u'BUS_ASC_NAME'],
                    u'percentage': float(row[u'ASSIGNMENT_PCT'])}]

    return data


def format_data(lease_data: list) -> tuple:
    """
    Returns a tuple (kind of like a list...) with the largest owner as [OPERATOR] and the
    remainder of the owners as [OTHERS] in the format:

    ([OPERATOR], [LIST_OF_OTHERS])

    However, the actual values returned are also made to look pretty, in the format shown
    in the function "format_string" below.
    """
    lease_data.sort(key = lambda company: company['percentage'], reverse = True)

    operator = format_string(lease_data.pop(0))

    others = u', '.join([format_string(company) for company in lease_data])

    return [operator, others]


def format_string(owner_data: dict) -> str:
    """
    Creates a "pretty" string in the format:

    Company Name (Percentage Ownership%)

    For example:
        "Edward Cazier Co. (98%)"
    """
    return u'{company_name} ({percentage}%)'.format(
        company_name = owner_data[u'owner'],
        percentage = ceil(owner_data[u'percentage']))


def get_leases(owners_url: str, owners_file_name: str, save_as: str, aliquot: bool) -> None:
    """
    This is the main function doing everything. It opens both files with data, and iterates
    through each row to figure out who the various owners/operators are, and what percentage
    of the operation they own.
    """

    lease_owners = list(get_csv(owners_url, owners_file_name))

    output_csv = csv.writer(open(save_as, 'w'), dialect=u'excel')
    output_csv.writerow([u'Lease Number', u'Primary Owner', u'Other Owners'])

    # Check to see whether the user wanted to look at the files by including the ALIQUOT code
    if not aliquot:
        owners_data = load_lease_owner_data_no_aliquot(lease_owners)

    else:
        owners_data = load_lease_owner_data_with_aliquot(lease_owners)

    for entry in owners_data.keys():
        output_csv.writerow([entry] + format_data(owners_data[entry]))

    # return output_csv



    # # Generate a list of the rows to evaluate. Ignore the title row (Row 1)
    # lease_rows = range(2, leases_file.max_row)

    # # Iterate thorugh each of the rows listed above.
    # for lease_row in lease_rows:

    #     # Get the lease number (Format is "G#####")
    #     lease_number = leases_file.cell(row = lease_row, column = 1).value

    #     # This is just a... check for weirdness if the owners percentages are more than 100%
    #     if sum([company[u'percentage'] for company in owners_data[lease_number]]) > 101:
    #         print(f'{lease_number} has some weirdness... Check it out!')
    #         continue

    #     else:
    #         # Otherwise, get pretty formatted data for each owner
    #         operator, others = format_data(owners_data[lease_number])

    #         # Save that pretty data into the correct cells in the document
    #         leases_file.cell(row = lease_row, column = 8).value = operator
    #         leases_file.cell(row = lease_row, column = 9).value = others

    # # Save the lease file with all the new information!
    # leases_file_wb.save(save_as)
    # all_leases = [entry for entry in open_csv(u'mv_lease_owners_main.csv')][:100]

    # parsed_leases = load_lease_owner_data_with_aliquot(all_leases)

    # pprint(parsed_leases)

    # a = get_leases(u'other.csv', save_as = u'output.csv', aliquot = True)

a = get_leases(owners_url = FILE_URL, owners_file_name = FILE_NAME, save_as = u'output.csv', aliquot = True)


