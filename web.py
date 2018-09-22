#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, send_file
app = Flask(__name__)

import lease

owner = lease.BSEE_DATA(url=u'https://www.data.bsee.gov/Leasing/Files/LeaseOwnerRawData.zip', file=u'LeaseOwnerRawData/mv_lease_owners_main.txt')

area_block = lease.BSEE_DATA(url=u'https://www.data.bsee.gov/Leasing/Files/LABRawData.zip', file = u'LABRawData/mv_lease_area_block.txt')

w = lease.WebLeaseWrapper(owner, area_block)

@app.route(u'/')
def home():
    return render_template(u'index.html')

@app.route(u'/format')
def static_page():
    w.owner.cache()
    w.area_block.cache()

    return render_template(u'format.html',
        owner_url = w.owner.url,
        owner_date = w.owner.update,
        area_block_url = w.area_block.url,
        area_block_date = w.area_block.update)

@app.route(u'/download')
def download():
    w.prepare_data(aliquot = False)
    w.prepare_csv_list()

    file = w.send_csv()

    return send_file(file,
        as_attachment=True,
        attachment_filename=u'output.csv',
        mimetype=u'text/csv')


if __name__ == '__main__':
    app.run(host=u'0.0.0.0')