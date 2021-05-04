from flask import Flask
from datetime import datetime
from flask import render_template

import timeago
import haversine

app = Flask(__name__)

try:
    import settings
    no_settings_file = False
    app.debug = settings.debug
except ImportError:
    no_settings_file = True
    app.debug = True

import utils
import models


@app.template_filter('timeago')
def handler(date):
    return timeago.format(date, datetime.now())


@app.route('/')
def log_list():

    if no_settings_file:
        return render_template('errors.html', errors=['No settings file (settings.py) importable.'])

    # Check if the database has the required tables and create if not.
    tables = models.db.get_tables()
    if len(tables) == 0:
        models.create_tables()

    vehicles = models.Vehicle.select().order_by(models.Vehicle.date_first_heard.desc())
    system = models.SystemStatistic.select().first()

    for vehicle in vehicles:
        vehicle.show_tracker_link = False

        # If we have coords, get the haversine distance.
        if vehicle.first_latitude and vehicle.first_longitude and vehicle.last_latitude and vehicle.last_longitude:
            l1 = (vehicle.first_latitude, vehicle.first_longitude)
            l2 = (vehicle.last_latitude, vehicle.last_longitude)
            vehicle.flight_distance_km = haversine.haversine(l1, l2)

        # If we have last_heard, calculate the time since we last heard.
        if vehicle.date_last_heard and vehicle.date_last_heard:
            vehicle.flight_time_minutes = (vehicle.date_last_heard - vehicle.date_first_heard).total_seconds() / 60

            # Show the tracker link if we've heard this vehicle in the last hour.
            if (datetime.utcnow() - vehicle.date_last_heard).total_seconds() < 60*60:  # 1 Hour.
                vehicle.show_tracker_link = True
                vehicle.tracker_url = utils.get_tracker_url(vehicle.last_latitude,
                                                            vehicle.last_longitude,
                                                            vehicle.vehicle_id)

    return render_template('list.html',
                           vehicles=vehicles,
                           sondehub_url_prefix=settings.sondehub_url_prefix,
                           system=system,
                           auto_rx_url=settings.auto_rx_url)


if __name__ == '__main__':
    app.run()