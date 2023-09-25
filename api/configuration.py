import json

class Configuration:
  def __init__(self, settingsFile):
    openFile = open(settingsFile)
    settings = json.load(openFile)
    openFile.close()

    self.host = settings['host']
    self.user = settings['user']
    self.password = settings['password']
    self.database = settings['db']
    self.email = settings['email']
    self.emailpassword = settings['emailpassword']
    self.emailhost = settings['emailhost']  
    self.emailport = settings['emailport']