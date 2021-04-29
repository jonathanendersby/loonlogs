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
import timeago
import haversine

app = Flask(__name__)
app.debug = settings.debug

@app.template_filter('timeago')
def fromnow(date):
    return timeago.format(date, datetime.now())


@app.route('/')
def log_list():
    vehicles = models.Vehicle.select().order_by(models.Vehicle.date_first_heard.desc())
    system = models.SystemStatistic.select().first()

    for vehicle in vehicles:
        if vehicle.first_latitude and vehicle.first_longitude and vehicle.last_latitude and vehicle.last_longitude:
            l1 = (vehicle.first_latitude, vehicle.first_longitude)
            l2 = (vehicle.last_latitude, vehicle.last_longitude)
            vehicle.flight_distance_km = haversine.haversine(l1, l2)

        if vehicle.date_last_heard and vehicle.date_last_heard:
            vehicle.flight_time_minutes = (vehicle.date_last_heard - vehicle.date_first_heard).total_seconds() / 60

    return render_template('list.html',
                           vehicles=vehicles,
                           sondehub_url_prefix=settings.sondehub_url_prefix,
                           system=system)

if __name__ == '__main__':
    app.run()