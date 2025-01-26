class LegoTrack:
    def __init__(self, dataDict=None) -> None:
        if dataDict is not None:
            self.importData(dataDict)
        else:
            self.setid = None
            self.userid = None
            self.track = False
            self.have = False

    def importData(self, dataDict):
        self.setid = dataDict['setid'] if 'setid' in dataDict else None
        self.userid = dataDict['userid'] if 'userid' in dataDict else None
        self.track = dataDict['track'] if 'track' in dataDict else False
        self.have = dataDict['have'] if 'have' in dataDict else False
