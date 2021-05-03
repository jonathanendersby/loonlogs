from flask import Flask
from datetime import datetime
from flask import render_template
import settings
import models
import timeago
import haversine
import utils

app = Flask(__name__)
app.debug = settings.debug

@app.template_filter('timeago')
def handler(date):
    return timeago.format(date, datetime.now())


@app.route('/')
def log_list():

    # Check if the database has the required tables and create if not.
    tables = models.db.get_tables()
    if len(tables) == 0:
        models.create_tables()

    vehicles = models.Vehicle.select().order_by(models.Vehicle.date_first_heard.desc())
    system = models.SystemStatistic.select().first()

    for vehicle in vehicles:
        vehicle.show_tracker_link = False

        if vehicle.first_latitude and vehicle.first_longitude and vehicle.last_latitude and vehicle.last_longitude:
            l1 = (vehicle.first_latitude, vehicle.first_longitude)
            l2 = (vehicle.last_latitude, vehicle.last_longitude)
            vehicle.flight_distance_km = haversine.haversine(l1, l2)

        if vehicle.date_last_heard and vehicle.date_last_heard:
            vehicle.flight_time_minutes = (vehicle.date_last_heard - vehicle.date_first_heard).total_seconds() / 60

            if (datetime.utcnow() - vehicle.date_last_heard).total_seconds() < 24*60*60:
                vehicle.show_tracker_link = True
                vehicle.tracker_url = utils.get_tracker_url(vehicle.last_latitude, vehicle.last_longitude, vehicle.vehicle_id)

    return render_template('list.html',
                           vehicles=vehicles,
                           sondehub_url_prefix=settings.sondehub_url_prefix,
                           system=system)


if __name__ == '__main__':
    app.run()