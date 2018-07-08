import  requests

class JobURLUtil:
    def __init__(self, title, loc):
        self._title = title
        self._loc = loc
        self._locReqURL = 'https://www.glassdoor.co.in/util/ajax/findLocationsByFullText.htm'
        self._baseURL = 'https://www.glassdoor.co.in/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=software&sc.keyword=software&locT=C&locId=1142551&jobType='

    def setLocInfo(self, locId, locT):
        self._locId = locId
        self._locT = locT
        
    def locationInfoExtractor(self): # glassdoor requires location type (locT) and location id (locId) for successful request
        locReqParams = {
            'locationSearchString' : self._loc.replace(' ', '+'),
            'allowPostalCodes' : 'true'
        }
        locReqHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # mimicking browser request        
        self._locResObj = requests.get(self._locReqURL, params = locReqParams, headers = locReqHeaders) # json data extraction from response object
        if self._locResObj.status_code != 200: return False
        if isinstance(self._locResObj['locations'], list):
            setLocInfo(self, self._locResObj['locations'][0]['id'], self._locResObj['locations'][0]['type']) # returning first match for location
        else:
            setLocInfo(self, self._locResObj['locations']['id'], self._locResObj['locations']['type'])
        # return self._locResObj.json() # returns json response data as a dictionary

    
    #def URLRequestBuilder(countryName, pageNumber):

#def PageRequester(self, jobName, jobPageNumber):

#locationInfoExtractor('new delhi')    

urlUtil = JobURLUtil('software', 'new delhi')
print(urlUtil.locationInfoExtractor())
