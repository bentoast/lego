from models import LegoTrack

class LegoController:
  def __init__(self, legoSetService, legoTrackService, scrapingService) -> None:
    self.legoSetService = legoSetService
    self.legoTrackService = legoTrackService
    self.scrapingService = scrapingService

    self.routes = {
      'single': self.SingleRequest,
      'multiple': self.MultipleRequest,
      'update': self.UpdateRequest
    }

  def MultipleRequest(self, request):
    filter = {}
    if 'new' in request:
      filter['new'] = request['new'] == 'true'
    if 'retiring' in request:
      filter['retiring'] = request['retiring'] == 'true'
    if 'have' in request:
      filter['have'] = request['have'] == 'true'
    if 'track' in request:
      filter['track'] = request['track'] == 'true'
    if 'setid' in request:
      filter['setid'] = request['setid']
    if 'name' in request:
      filter['name'] = request['name']
    if 'discount' in request:
      filter['discount'] = request['discount'] == 'true'
      
    page = 1
    if 'page' in request:
      page = int(request['page'])
    count = 10
    if 'count' in request:
      count = int(request['count'])

    (allCount, allSets) = self.legoSetService.getFilteredSets(filter, request['order'], 'asc' in request and request['asc'], count, page)
    print(f'{{ "total": {allCount}, "page": {page}, "results": [{",".join([ls.toJson() for ls in allSets])}]}}')
    
  def SingleRequest(self, request):
    updatedSet = self.scrapingService.ScrapeSite(f'https://lego.com/en-us/product/{request["setid"]}', '//div[@class="ProductOverviewstyles__Container-sc-1a1az6h-2 etzprq"]')

    if len(updatedSet) > 0:
      self.legoSetService.saveSet(updatedSet[0])
      print(f'''[{updatedSet[0].toJson()}]''')
    else:
      print('[{{"status": "failure", "setcount": 0 }}]')
    
  def UpdateRequest(self, jsondata):
    tempTrack = LegoTrack(jsondata)
    tempTrack.userid = 1

    if (self.legoTrackService.userTracksSet(1, tempTrack.setid)):
      self.legoTrackService.updateUserTrack(tempTrack)
    else:
      self.legoTrackService.createUserTrack(tempTrack)
    
    print('{{"status":"success"}}')

  def ProcessRequest(self, requestData):
    #This is common to all requests
    print('Content-type: application/javascript')
    print()
    
    #Here are all of our commands so far.
    #Eventually, this will probably need to be different
    if requestData['action'] in self.routes:
      self.routes[requestData['action']](requestData['parameters'])
    else:
      print('{{"status:"invalid"}}')