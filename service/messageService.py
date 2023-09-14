#!/usr/bin/env python3

import ssl
import smtplib
from email.mime.text import MIMEText
import service.legoService as ls

def SendMessage(messageType, subject, messageBody):
  message =  MIMEText(messageBody, messageType)
  message['subject'] = subject
  message['from'] = ls.settings['email']
  message['to'] = ls.settings['email']
  session = smtplib.SMTP(ls.settings['emailhost'], ls.settings['emailport'])
  context = ssl.create_default_context()
  session.starttls(context=context)
  session.login(ls.settings['email'], ls.settings['emailpassword'])
  session.sendmail(ls.settings['email'], ls.settings['email'], message.as_string())
  session.quit()