from flask import Flask, render_template, send_file
app = Flask(__name__)

import lease

@app.route(u'/')
def home():
    return render_template(u'index.html')

@app.route(u'/format')
def static_page():
    return render_template(u'format.html', input_url = lease.FILE_URL, last_accessed_date = lease.last_update())

@app.route(u'/download')
def download():
    data = lease.get_leases(owners_url = lease.FILE_URL, owners_file_name = lease.FILE_NAME, aliquot = True)
    file = lease.send_file(data)

    return send_file(file,
        as_attachment=True,
        attachment_filename=u'output.csv',
        mimetype=u'text/csv')