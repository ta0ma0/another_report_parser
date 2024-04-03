# another_report_parser
For solvo SPO monitoring tool.

This is comprehensive solution for Linux servers monitoring.

###Logic:

1. Get mails with SPO reports from clients servers. Used imaplib, email.
2. Parse report files. Get Disk space info (df -h output from sesrvers)
3. Put data into MySQL data base.
4. Localhost Grafana for build dashbords and alerts.

![Grafana](/images/grafana.png "Example")

###Settings

1. python -m venv venv
2. source venv/bin/activate
3. pip install mysql-connector-python

###Usage

```
python spo_parser.py
```
