from datetime import datetime, timedelta
from dateutil.parser import *
import traceback

import settings


class AutoRXLogFile:
    filename = None
    parsed_date = None
    date_delta = None
    vehicle_id = None
    vehicle_type = None

    def __str__(self):
        return 'AutoRXLogFile: %s - %s' % (self.parsed_date, self.vehicle_id)


class AutoRXLogFileLine:
    date = None
    frame = None
    latitude = None
    longitude = None
    altitude = None
    temperature = None


class AutoRXLogFileStats:
    date_first_heard = None
    date_last_heard = None
    first_latitude = None
    first_longitude = None
    last_latitude = None
    last_longitude = None
    min_altitude = None
    max_altitude = None
    min_temp = None
    max_temp = None
    first_frame = None
    last_frame = None


def parse_filename(filename):
    # Returns an instance of AutoRXLogFile object

    # We expect:
    # <timestamp>_<serial number>_<vehicle type>_<frequency>_sonde.log
    # 20210201-233710_IMET54-55068418_IMET5_402000_sonde.log
    # 20210423-112535_S2540110_RS41-SG_401500_sonde.log

    if not filename.endswith('_sonde.log'):
        # Doesn't look like a log file, return False
        return False

    parts = filename.split('_')

    timestamp = parts[0]
    vehicle_id = parts[1]

    if vehicle_id.startswith(('IMET5', 'IMET4',)):
        vehicle_id_parts = vehicle_id.split('-')
        vehicle_id = vehicle_id_parts[1]

    vehicle_type = parts[2]
    freq = parts[3]

    try:
        y = int(timestamp[0:4])
        m = int(timestamp[4:6])
        d = int(timestamp[6:8])
        h = int(timestamp[9:11])
        minute = int(timestamp[11:13])
        second = int(timestamp[13:15])
        parsed_date = datetime(year=y, month=m, day=d, hour=h, minute=minute, second=second)

        # https://tracker.sondehub.org/?sondehub=1#!mt=osm&mz=11&qm=All&f=RS_IMET54-55068437&q=RS_IMET54-55068437
        # url = 'https://tracker.sondehub.org/?sondehub=1#!mt=osm&mz=11&qm=All&q=RS_%s' % id

    except ValueError:
        return False

    obj = AutoRXLogFile()
    obj.filename = filename
    obj.parsed_date = parsed_date
    obj.date_delta = datetime.utcnow() - parsed_date
    obj.vehicle_id = vehicle_id
    obj.vehicle_type = vehicle_type

    print('-----------------------\n        LOGFILEOBJECT')
    print(obj)
    return obj



def read_telemetry_csv(filename_obj,
                       datetime_field=0,
                       frame_field=2,
                       latitude_field=3,
                       longitude_field=4,
                       altitude_field=5,
                       temperature_field=9,
                       delimiter=','):
    '''
    Shamelessly stolen from https://github.com/projecthorus/radiosonde_auto_rx/blob/master/auto_rx/utils/log_to_kml.py
    Read in a radiosonde_auto_rx generated telemetry CSV file.
    Fields to use can be set as arguments to this function.
    These have output like the following:
    2017-12-27T23:21:59.560,M2913374,982,-34.95143,138.52471,719.9,-273.0,RS92,401.520
    <datetime>,<serial>,<frame_no>,<lat>,<lon>,<alt>,<temp>,<sonde_type>,<freq>
    Note that the datetime field must be parsable by dateutil.parsers.parse.
    If any fields are missing, or invalid, this function will return None.
    The output data structure is in the form:
    [
        [datetime (as a datetime object), latitude, longitude, altitude, raw_line],
        [datetime (as a datetime object), latitude, longitude, altitude, raw_line],
        ...
    ]
    '''
    output = []

    f = open('%s/%s' % (settings.log_path, filename_obj.filename), 'r', encoding='UTF-8')

    add_date = None  # Does this log file not include the actual date. (Early versions of IMET54)
    first_hour = None  # Used to determine whether the hours have rolled over to the next day.

    for line in f:
        try:
            # Split line by comma delimiters.
            _fields = line.split(delimiter)

            # Trim any weird whitespace
            _fields[datetime_field] = _fields[datetime_field].strip('\x00')

            if _fields[0] == 'timestamp':
                # First line in file - header line.
                continue

            else:
                # Hacky check to see if the log file has a full date or just the time.
                if add_date is None:
                    if line[2:3] == ':':
                        add_date = True
                        first_hour = int(line[0:2])
                    else:
                        add_date = False

            # Attempt to parse fields.
            line_obj = AutoRXLogFileLine()

            # Do we need to add the date to the log file.
            if add_date:

                base_date = filename_obj.parsed_date
                # print('TESTING HERE:', filename_obj.filename)
                # print('Fields:', _fields)
                # print('Field:', _fields[datetime_field])
                # print('Len:', len(_fields[datetime_field]))
                # print('Type:', type(_fields[datetime_field]))
                # print('First two:', _fields[datetime_field][0:2])
                # print('Int:', int(str(_fields[datetime_field])[0:2]))
                # print('-----')

                hour = int(_fields[datetime_field][0:2])
                minute = int(_fields[datetime_field][3:5])
                second = int(_fields[datetime_field][6:8])
                # print('done...')

                if hour < first_hour:
                    # We've rolled over to the next day.
                    base_date = base_date + timedelta(hours=24)

                date_corrected = base_date.replace(hour=hour, minute=minute, second=second)

            else:
                # We can use the date as it is logged in the file.
                date_corrected = parse(_fields[datetime_field])

            # We remove timezone info because we're SQLite can't do timezones properly yet.
            line_obj.date = date_corrected.replace(tzinfo=None)
            line_obj.frame_number = int(_fields[frame_field])
            line_obj.latitude = float(_fields[latitude_field])
            line_obj.longitude = float(_fields[longitude_field])
            line_obj.altitude = float(_fields[altitude_field])
            line_obj.temperature = float(_fields[temperature_field])

            output.append(line_obj)

        except Exception as e:
            print('EXCEPTION!!!!')
            print(str(e))
            traceback.print_exc()
            return None

    f.close()

    return output


# def parse_file(filename):
#     # print('Parsing', filename)
#     output =
#     return output


def get_stats(data):
    min_alt = None
    max_alt = None

    min_temp = None
    max_temp = None

    if data is not None:
        print('We have data...')
        for d in data:
            alt = d.altitude
            if max_alt is None or alt > max_alt:
                max_alt = alt
            if min_alt is None or alt < min_alt:
                min_alt = alt

            temp = d.temperature
            if max_temp is None or temp > max_temp:
                max_temp = temp
            if min_temp is None or temp < min_temp:
                min_temp = temp

        s = AutoRXLogFileStats()
        s.date_first_heard = data[0].date
        s.date_last_heard = data[-1].date
        s.first_latitude = data[0].latitude
        s.first_longitude = data[0].longitude
        s.last_latitude = data[-1].latitude
        s.last_longitude = data[-1].longitude
        s.min_altitude = min_alt
        s.max_altitude = max_alt
        s.min_temp = min_temp
        s.max_temp = max_temp

    else:
        print('We have no data...')
        # No data, lets return an empty object.
        s = AutoRXLogFileStats()

    return s
