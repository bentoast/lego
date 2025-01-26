import ssl
import smtplib
from email.mime.text import MIMEText


class MessageService:
    def __init__(self, configuration):
        self.configuration = configuration

    def SendMessage(self, messageType, subject, messageBody):
        message = MIMEText(messageBody, messageType)
        message['subject'] = subject
        message['from'] = self.configuration.email
        message['to'] = self.configuration.email
        session = smtplib.SMTP(
            self.configuration.emailhost, self.configuration.emailport)
        context = ssl.create_default_context()
        session.starttls(context=context)
        session.login(
            self.configuration.email, self.configuration.emailpassword)
        session.sendmail(
            self.configuration.email,
            self.configuration.email,
            message.as_string())
        session.quit()
