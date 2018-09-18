from flask import Flask, render_template
app = Flask(__name__)

import lease

@app.route(u'/')
def home():
    return render_template(u'index.html')

@app.route(u'/format')
def static_page():
    return render_template(u'format.html', input_url = lease.FILE_URL)