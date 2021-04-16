from peewee import *
import pathlib

db = SqliteDatabase(str(pathlib.Path(__file__).parent.absolute()) + '/loonlogs.db')


class SystemStatistic(Model):
    date_last_complete_processing = DateTimeField()

    class Meta:
        database = db


class Vehicle(Model):
    vehicle_id = CharField()
    serial_number = CharField()
    filename = CharField()
    date_created = DateTimeField()

    first_latitude = DecimalField(max_digits=9, decimal_places=6, null=True)
    first_longitude = DecimalField(max_digits=9, decimal_places=6, null=True)

    last_latitude = DecimalField(max_digits=9, decimal_places=6, null=True)
    last_longitude = DecimalField(max_digits=9, decimal_places=6, null=True)

    date_first_heard = DateTimeField(null=True)
    date_last_heard = DateTimeField(null=True)

    min_altitude = DecimalField(null=True)
    max_altitude = DecimalField(null=True)

    min_temperature = DecimalField(null=True)
    max_temperature = DecimalField(null=True)

    class Meta:
        database = db


def create_tables():
    with db:
        db.create_tables([Vehicle, SystemStatistic])
