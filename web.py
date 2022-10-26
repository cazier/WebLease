#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from flask import Flask, Response, send_file, render_template

import lease

app = Flask(__name__)

owner = lease.OwnerData()
area_block = lease.LabData()
lease_data = lease.LeaseData()
companies = lease.CompanyNumberToName()
lease_operators = lease.LeaseNumberToOperator()

w = lease.WebLeaseWrapper(owner, area_block, lease_data, companies, lease_operators)


@app.route("/")
def home() -> str:
    return render_template("index.html")


@app.route("/format")
def static_page() -> str:
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
def download() -> Response:
    w.prepare_data()
    w.prepare_csv_list()

    file = w.send_csv()

    return send_file(
        file,
        as_attachment=True,
        download_name=f"output_{datetime.now().strftime('%Y%m%d%H%m')}.csv",
        mimetype="text/csv",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
