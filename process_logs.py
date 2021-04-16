import os
import datetime
import pytz
from dateutil.parser import parse

import utils
import settings
import models

# Get the list of lof files in the logs folder
logs = os.listdir(settings.log_path)

# Fetch the current list of vehicles from the database
vehicles = models.Vehicle.select(models.Vehicle.vehicle_id)  # .order_by(models.Vehicle.date_first_heard)

vehicle_ids = []

# Create a list of the vehicle_ids
for vehicle in vehicles:
    vehicle_ids.append(vehicle.vehicle_id)

# Loop through the files
for log in logs:

    # Attempt to parse the filename
    filename_obj = utils.parse_filename(log)

    # Check if we were able to parse the filename
    if filename_obj:
        print('\nProcessing: ', filename_obj.filename)
        # Fetch the data from the log file.
        # data = utils.read_telemetry_csv('%s/%s' % (settings.log_path, filename_obj))
        data = utils.read_telemetry_csv(filename_obj)

        # Parse the statistics from the data
        stats = utils.get_stats(data)

        # Check if we have this vehicle in the database already
        if filename_obj.vehicle_id not in vehicle_ids:
            # Not in the database, lets add it.
            v = models.Vehicle(
                vehicle_id=filename_obj.vehicle_id,
                serial_number=filename_obj.serial_number,
                filename=filename_obj.filename,
                date_created=datetime.datetime.now(tz=pytz.UTC)
            ).save()
            print('Created:', v)

        v = models.Vehicle.get(models.Vehicle.vehicle_id == filename_obj.vehicle_id)
        print('Vehicle Exists in DB:', v)

        # Have we got new data for this record?

        print(stats.date_last_heard)
        if v.date_last_heard is None or stats.date_last_heard > v.date_last_heard:
            # we have fresh data, lets update the record.
            print('Fresh data, Updating database.')

            v.first_latitude = stats.first_latitude
            v.first_longitude = stats.first_longitude

            v.last_latitude = stats.last_latitude
            v.last_longitude = stats.last_longitude

            v.date_first_heard = stats.date_first_heard
            v.date_last_heard = stats.date_last_heard

            v.min_altitude = stats.min_altitude
            v.max_altitude = stats.max_altitude

            v.min_temperature = stats.min_temp
            v.max_temperature = stats.max_temp
            v.save()
            print('Vehicle updated')


        else:
            # Nothing to do
            print('Old data, doing nothing.')
            pass

# Update the system statistics table
system = models.SystemStatistic.select().first()

if system is None:
    models.SystemStatistic.create(date_last_complete_processing=datetime.datetime.utcnow()).save()
    system = models.SystemStatistic.select().first()

else:
    system.date_last_complete_processing = datetime.datetime.utcnow()
    system.save()

print('\n\nProcessing complete at', system.date_last_complete_processing, 'UTC')
