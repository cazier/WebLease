#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, send_file, render_template

import lease

app = Flask(__name__)

owner = lease.Owner_Data()
area_block = lease.LAB_Data()
lease_data = lease.Lease_Data()
companies = lease.CompanyNumberToName()
lease_operators = lease.LeaseNumberToOperator()

w = lease.WebLeaseWrapper(owner, area_block, lease_data, companies, lease_operators)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/format")
def static_page():
    w.owner.cache()
    w.area_block.cache()
    w.lease_data.cache()
    w.lease_operators.cache()
    w.companies.cache()

    return render_template(
        "format.html",
        owner_url=w.owner.url,
        owner_date=w.owner.update,
        area_block_url=w.area_block.url,
        area_block_date=w.area_block.update,
        lease_data_url=w.lease_data.url,
        lease_data_date=w.lease_data.update,
    )


@app.route("/download")
def download():
    w.prepare_data()
    w.prepare_csv_list()

    file = w.send_csv()

    return send_file(
        file,
        as_attachment=True,
        attachment_filename="output_{timestamp}.csv".format(
            timestamp=lease.datetime.now().strftime("%Y%m%d%H%m")
        ),
        mimetype="text/csv",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
