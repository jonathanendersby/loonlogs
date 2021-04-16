from flask import Flask
import os
from datetime import datetime
from flask import render_template
import settings
import pytz
import utils
from jinja2 import Environment, FileSystemLoader
import os
import models


app = Flask(__name__)
app.debug = True


@app.route('/')
def log_list():
    vehicles = models.Vehicle.select().order_by(models.Vehicle.date_first_heard.desc())
    system = models.SystemStatistic.select().first()
    return render_template('list.html',
                           vehicles=vehicles,
                           sondehub_url_prefix=settings.sondehub_url_prefix,
                           system=system)


if __name__ == '__main__':
    app.run()