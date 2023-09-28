from models import LegoTrack

class LegoTrackService:
  def __init__(self, databaseService) -> None:
    self.databaseService = databaseService

  def updateUserTrack(self, legoTrack):
    statement = 'UPDATE LegoTrack SET Track = %s, Have = %s WHERE SetId = %s AND UserId = %s;'
    self.databaseService.executeNonQuery(
      statement,
      (
        legoTrack.track,
        legoTrack.have,
        legoTrack.setid,
        legoTrack.userid
      ))

  def createUserTrack(self, legoTrack):
    statement = 'INSERT INTO LegoTrack (Track, Have, SetId, UserId) VALUES (%s, %s, %s, %s);'
    self.databaseService.executeNonQuery(
      statement,
      (
        legoTrack.track,
        legoTrack.have,
        legoTrack.setid,
        legoTrack.userid
      ))

  def userTracksSet(self, userid, setid) -> bool:
    countResult = self.databaseService.executeQuery('SELECT COUNT(*) FROM LegoTrack WHERE SetId = %s AND UserId = %s', (setid, userid))[0]
    return countResult > 0