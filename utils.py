from dateutil.parser import *
import traceback


def read_telemetry_csv(filename,
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

    f = open(filename,'r')

    for line in f:
        try:
            # Split line by comma delimiters.
            _fields = line.split(delimiter)

            if _fields[0] == 'timestamp':
                # First line in file - header line.
                continue

            # Attempt to parse fields.
            _datetime = parse(_fields[datetime_field])
            _frame = float(_fields[frame_field])
            _latitude = float(_fields[latitude_field])
            _longitude = float(_fields[longitude_field])
            _altitude = float(_fields[altitude_field])
            _temperature = float(_fields[temperature_field])

            output.append([_datetime, _frame, _longitude, _altitude, _temperature])
        except:
            traceback.print_exc()
            return None

    f.close()

    return output


def get_stats(data):
    # print(data)
    # quit()
    max_alt = 0
    min_alt = 9999999999

    for d in data:
        alt = d[3]
        if alt > max_alt:
            max_alt = alt
        if alt < min_alt:
            min_alt = alt

    return({
        'minimum_altitude': min_alt,
        'maximum_altitude': max_alt,
    })