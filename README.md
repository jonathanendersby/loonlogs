# loonlogs

Loonlogs processes and displays your AutoRX Logs with a quick summary of the information.

![alt text](https://github.com/jonathanendersby/loonlogs/blob/3f9cb7ed6af6c8bda49af8f186c0356e6831823b/screenshot.png?raw=true)



To learn more about Radiosonde and AutoRX visit https://github.com/projecthorus/radiosonde_auto_rx

# Theory of Operation and Setup
LoonLogs is a Flask application paired with a standalone Python script (`process_logs.py`) that processes auto_rx log files and populates a SQLite Database.

## Setup
* First ```cp settings.py.example settings.py``` and set your paths correctly. 
* `pip install -r requirements.txt` to install all the dependencies.
* Test Flask by running `python3 app.py`
* Test log processor by running `python3 process_logs.py`

If all is working correctly you should see it parsing some logs and your loonlogs.db file should increase in size.

## How it works
Once running the software should create a SQLite `loonlogs.db` file and two tables:
* `vehicles` (which stores summary data for each vehicle)
* `systemstatistic` (which stores information about the last time process_logs ran.)
* Once Flask is running you should be able to visit http://127.0.0.1:5000/ and see your vehicle logs. 

It is recommended that you install the Flask app using SystemD (see the example service file below)

Once you've got the Flask app running, configure the settings.py file to point to your auto_rx log file path and then run `python3 process_logs.py` which will populate the database.

It is recommended that you set up your log processing in cron.


## systemd 
eg `/etc/systemd/system/loonlogs.service`

```
[Unit]
Description=loonlogs
After=syslog.target

[Service]
ExecStart=/usr/bin/flask run --host 0.0.0.0 --port 5002
Restart=always
RestartSec=120
WorkingDirectory=/home/pi/loonlogs/
User=pi
SyslogIdentifier=loonlogs

[Install]
WantedBy=multi-user.target
```

## Cron
This config is purposely dumping the output to /tmp/cron.log for any debugging that might need to be done.
```
*/5 * * * *     /usr/bin/python3 /home/pi/loonlogs/process_logs.py >>/tmp/cron.log 2>&1
```
