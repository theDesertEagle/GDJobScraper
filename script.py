
"""
Author: the.desert.eagle
Project: GDJobScraper Python Script
Purpose: Extract the technical job-required skills in the field of computer science and data science and store them in the concise manner    
Abbreviations (in Documentation):
• GD - GlassDoor
"""

# MODULE DEPENDENCIES
import  requests
from sys import exit

# JOB-PAGES URL HANDLER CLASS
class JobURLUtil:
    """Handles all URLS and requests related to job-list page fetching
    
    • Private variables are semantically indicated with names beginning with "_"
    """
     
    def __init__(self, title, loc):
        """Initially sets the user's location and job/profession title
        
           Params:
           • title - Profession/Job title to be searched, given the user
           • loc - Abstract Location Information based on which the jobs will be searched, given the user 
    
           Returns: [None]   
        """
        
        self._title = title
        self._loc = loc
        self._locReqURL = 'https://www.glassdoor.co.in/util/ajax/findLocationsByFullText.htm'
        self._baseURL = 'https://www.glassdoor.co.in/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=software&sc.keyword=software&locT=C&locId=1142551&jobType='

    def setLocInfo(self, locId, locT):
        """Set the user's location and job/profession title, as found by the location GET request
        
           Params:
           • locId - Specific Location ID set by GD for a certain geographical location name
           • locT - Assumed Specific type of location (such as city (C), state (S), etc.) set by GD   
    
           Returns: [None]   
        """
        
        self._locId = locId
        self._locT = locT
        
    def locationInfoExtractor(self): # glassdoor requires location type (locT) and location id (locId) for successful request build-up for job-list page
        """Utilizes GD's 
        
           Params: [None]
    
           Returns:
           • Response object obtained by the location GET request
        """

        locReqParams = {
            'locationSearchString' : self._loc.replace(' ', '+'),
            'allowPostalCodes' : 'true'
        }
        locReqHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # mimicking browser request        

        try:
            locResObj = requests.get(self._locReqURL, params = locReqParams, headers = locReqHeaders)
        except:
            print('<ERROR> Unable to make location GET request')
            sys.exit(0)
        if locResObj.status_code != 200: return False

        locResJsonObj = locResObj.json() # json data extraction from response object as dictionary
        if isinstance(locResJsonObj['locations'], list):
            self.setLocInfo(locResJsonObj['locations'][0]['id'], locResJsonObj['locations'][0]['type']) # returning first match for location
        else:
            self.setLocInfo(locResJsonObj['locations']['id'], locResJsonObj['locations']['type'])
        return locResObj
    
    #def URLRequestBuilder(countryName, pageNumber):

#def PageRequester(self, jobName, jobPageNumber):

#locationInfoExtractor('new delhi')    

urlUtil = JobURLUtil('software', 'new delhi')
print(urlUtil.locationInfoExtractor().json())
