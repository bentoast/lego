#!/usr/bin/env python3

import ssl
import smtplib
from email.mime.text import MIMEText

testmessage = MIMEText("This is a test message.")
testmessage['subject'] = "Subjects ahoy"
testmessage['from'] = 'ben@benjaminautin.com'
testmessage['to'] = 'ben@benjaminautin.com'
session = smtplib.SMTP('smtp.1and1.com', 587)
context = ssl.create_default_context()
session.starttls()
session.login('ben@benjaminautin.com', 'v0ltr0n')
session.sendmail('ben@benjaminautin.com', 'ben@benjaminautin.com', testmessage.as_string())
session.quit()