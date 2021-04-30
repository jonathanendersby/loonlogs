# loonlogs

Loonlogs processes and presents your AutoRX Logs with a quick summary of the information.

# Setup
## systemd (eg /etc/systemd/system/loonlogs.service)
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
```
*/5 * * * *     /usr/bin/python3 /home/pi/loonlogs/process_logs.py >>/tmp/cron.log 2>&1
```