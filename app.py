from flask import Flask
import os
from datetime import datetime
from flask import render_template
import settings
import pytz
import utils
from jinja2 import Environment, FileSystemLoader
import os

app = Flask(__name__)

class AutoRXLogFile:
    date = None
    date_delta = None
    habhub_url = None
    balloon_id = None
    stats = {}

    def __str__(self):
        return 'AutoRXLogFile - %s' % self.date


def parse_filename(filename):
    # Returns an instance of AutoRXLogFile object
    # 20210201-233710_IMET54-55068418_IMET5_402000_sonde.log
    try:
        y = int(filename[0:4])
        m = int(filename[4:6])
        d = int(filename[6:8])
        h = int(filename[9:11])
        minute = int(filename[11:13])
        s = int(filename[13:15])
        id = filename[16:31]
        # https://tracker.sondehub.org/?sondehub=1#!mt=osm&mz=11&qm=All&f=RS_IMET54-55068437&q=RS_IMET54-55068437
        # url = 'https://tracker.sondehub.org/?sondehub=1#!mt=osm&mz=11&qm=All&q=RS_%s' % id
        url = 'https://sondehub.org/card/%s' % id
        parsed_date = datetime(year=y, month=m, day=d, hour=h, minute=minute, second=s, tzinfo=pytz.UTC)

    except ValueError:
        return False

    obj = AutoRXLogFile()
    obj.date = parsed_date
    obj.date_delta = datetime.now(tz=pytz.UTC) - parsed_date
    obj.balloon_id = id
    obj.habhub_url = url
    return obj


def parse_file(filename):
    print(filename)
    output = utils.read_telemetry_csv('%s/%s' % (settings.log_path, filename))
    if output:
        stats = utils.get_stats(output)
        return stats
    else:
        return None

@app.route('/')
def log_list():
    logs = os.listdir(settings.log_path)
    list = []

    for log in logs:
        f = parse_filename(log)

        if f:
            f.stats = parse_file(log)
            list.append(f)

    list.sort(key=lambda x: x.date, reverse=True)

    return render_template('list.html', list=list)


if __name__ == '__main__':
    app.run()