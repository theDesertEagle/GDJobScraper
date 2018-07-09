
"""
Author: the.desert.eagle
Project: GDJobScraper Python Script
Purpose: Extract the technical job-required skills in the field of computer science and data science and store them in the concise manner    
Abbreviations :
• GD - GlassDoor
• Req - Request
• Res - Response
• Obj - Object
• Loc - Location
• Info - Information
• LocID - Location Identification
• LocT - Location Type
• Pg - Page
• Params - Parameters
Notes: 
• Any comments with "###" indicates the current area of work in the project
• Future releases may have to rely on HTML parsers instead of Regex due to markup language's complexity
"""

# MODULE DEPENDENCIES
import requests
import webbrowser
import re
from sys import exit

# DEBUG UTILITIES
def htmlFileTester(docName, docContent):
    fileName = '{}.html'.format(docName)
    fileHandler = open(fileName, 'w', encoding='utf-8')
    fileHandler.write(docContent)
    fileHandler.close()
    webbrowser.open_new_tab(fileName)

# JOB-PAGES URL HANDLER CLASS
class JobURLUtil:
    """Handles all URLS and requests related to job-list page fetching
    
    • Private variables and methods are semantically indicated with names beginning with "_"
    """
     
    def __init__(self, title, loc):
        """Initially sets basic instance info such as the user's location and job/profession title
        
           Params:
           • title - Profession/Job title to be searched, given the user
           • loc - Abstract Location Information based on which the jobs will be searched, given the user 
    
           Returns: [None]   
        """
        
        self._title = title
        self._loc = loc
        # URLs and Header Initialization
        self._standardHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # mimicking browser request
        self._locReqURL = 'https://www.glassdoor.co.in/util/ajax/findLocationsByFullText.htm'
        self._listPgBaseReqURL = 'https://www.glassdoor.co.in/Job/jobs.htm'
        # Company and Job-related Resource Initialization
        self._jobLinkPattern = re.compile(r'https?://www\.glassdoor\.[a-zA-Z.-]+/job-listing/[a-zA-Z0-9_.,?=-]+') # raw string
        self._logoLinkPattern = re.compile(r'(?:https?://media\.glassdoor\.[a-zA-Z.-]+/sqls/[0-9]+/[a-zA-Z0-9-]+\.png|defLogo)')
        self._jobTitlePattern = re.compile(r'g(?:"|\')>([a-zA-Z\s.,\)\(\]\[\{\};:\\/-]+)</h2>') # Complex Pattern Logic: Job title is enclosed between <h2> tags where opening tag's last letter-value is 'g' {present in job-page link}
        self._companyRatingPattern = re.compile(r'n>\s([0-9]+\.[0-9])+<i') # Rating lies between <span> and <i> tag
        self._jobLocationPattern = re.compile(r'ib(?:\'|")>[a-z;&-]+([a-zA-Z,\s]+)') # Removes non-breaking spaces and dash appended to the beginning of location within a <span> tag
        # Failed Regex Logical Expressions 
        # self._jobLocationPattern = re.compile(r'ib(?:"|\')>([a-zA-Z]+)+</s') # 
        # self._companyRatingPattern = re.compile(r'</span>"\s?([0-9.]+)"<i') 

    def _setLocInfo(self, locId, locT):
        """Set the user's location and job/profession title, as found by the location GET request
        
           Params:
           • locId - Specific Location ID set by GD for a certain geographical location name
           • locT - Assumed Specific type of location (such as city (C), state (S), etc.) set by GD   
    
           Returns: [None]   
        """
        
        self._locId = locId
        self._locT = locT

    def _setJobListBaseInfo(self, baseJobURL):
        """Set the user's location and job/profession title, as found by the location GET request
        
           Params:
           • locId - Specific Location ID set by GD for a certain geographical location name
           • locT - Assumed Specific type of location (such as city (C), state (S), etc.) set by GD   
    
           Returns: [None]   
        """
        self._baseJobURL = baseJobURL

    def _GETRequester(self, url, parameters, headers, requestType):
        """Perform a specfic contextual type of GET Request with typical error handling
        
           Params:
           • url - Address for the GET request
           • parameters - Assumed GD's-format query-string arguments
           • headers - Headers, usually specifying info such as mimicking a browser request to avoid [403] errors
           • requestType - Context type of the GET request 

           Returns:
           • responseObj - Response object created from the GET request    
        """        
        try:
            responseObj = requests.get(url, params=parameters, headers=headers)
        except:
            print('<ERROR> Unable to make {} GET request'.format(requestType))
            exit(0)
        if responseObj.status_code != 200: return False
        return responseObj
    
    def locationInfoExtractor(self): 
        """Extracts GD's required location parameters for assistance in building up the job-listing page GET request  
           (GD requires location type (locT) and location id (locId) for successful request build-up for job-list page)

           Params: [None]
    
           Returns:
           • Response object containing the GD-format location information
        """

        locReqParams = {
            'locationSearchString' : self._loc.replace(' ', '+'),
            'allowPostalCodes' : 'true'
        }            


        resObj =  self._GETRequester(self._locReqURL, locReqParams, self._standardHeaders, 'location')
        if not resObj: return False
        

        locResJsonObj = resObj.json() # json data extraction from response object as dictionary
        if isinstance(locResJsonObj['locations'], list):
            self._setLocInfo(locResJsonObj['locations'][0]['id'], locResJsonObj['locations'][0]['type']) # returning first match for location
        else:
            self._setLocInfo(locResJsonObj['locations']['id'], locResJsonObj['locations']['type'])
        return resObj

    def jobListingPageBaseRequester(self):
        """Requests for the main job-listing base page and URL 

            Params: [None]

            Returns:
            • Response object containing the GD-format job-listing base page information
        """

        listPgBaseReqParams = {
            'suggestCount' : '0',
            'suggestChosen' : 'false',
            'clickSource' : 'searchBtn',
            'typedKeyword' : self._title.replace(' ', '+'),
            'sc.keyword' : self._title.replace(' ', '+'),
            'locT' : self._locT,
            'locId' : str(self._locId)
        }

        resObj =  self._GETRequester(self._listPgBaseReqURL, listPgBaseReqParams, self._standardHeaders, 'job-listing base page') # requests handle redirections automatically [301]
        if not resObj: return False
    
        self._setJobListBaseInfo(resObj.url)        
        return resObj
        # htmlFileTester('test', listPgBaseResObj.text) # Creates an HTML file from the response and displays it for debugging purposes

    def jobLinkExtractor(self, htmlContent):
        """Fetches 30 job links (as of 9 July, 2018) present on GD's job-listing page 

            Params: [htmlContent ]
            • htmlContent - HTML text content obtained from the job-listing base page

            Returns:
            • jobLinks - All parse-able job links from the HTML text content 
        """
        jobLinks = self._jobLinkPattern.findall(htmlContent)
        # for jobLink in enumerate(jobLinks): print(jobLink) # Printing debug line
        return jobLinks

    def logoLinkExtractor(self, htmlContent): 
    # [UPDATE]
    # [Initial plan: Deprecating module, as logo extraction was supposed to be carried in 'extractResourcesFromJobPage' module]    
    # [Module unchanged due to the complexity imposed Logo-less companies]
        """Fetches 30 company logo links (as of 9 July, 2018) present on GD's job-listing page 

            Params: [htmlContent ]
            • htmlContent - HTML text content obtained from the job-listing base page

            Returns:
            • logoLinks - All parse-able logo links from the HTML text content 
        """
        logoLinks = self._logoLinkPattern.findall(htmlContent)
        #for logoLink in logoLinks: print(logoLink) # Printing debug line
        return logoLinks

    ### AREA OF INTEREST
    def extractResourcesFromJobPage(self, url):
        resObj = self._GETRequester(url, {}, self._standardHeaders, 'job page')
        htmlContent = resObj.text
        
        # Job-Title Extraction
        jobTitle = self._jobTitlePattern.findall(htmlContent)  

        # Company-Rating Extraction
        companyRating = self._companyRatingPattern.findall(htmlContent)

        # Job-Location Extraction 
        jobLocation = self._jobLocationPattern.findall(htmlContent)

        for item in jobLocation: print(item) # Debugging line
        htmlFileTester('test', resObj.text) # Debugging Utility Line


# PROGRAM COMMENCEMENT 
def main():
    urlUtil = JobURLUtil('software', 'minnesota')
    urlUtil.locationInfoExtractor()
    htmlContent = urlUtil.jobListingPageBaseRequester().text
    urlUtil.extractResourcesFromJobPage(urlUtil.jobLinkExtractor(htmlContent)[15])
    # urlUtil.logoLinkExtractor(htmlContent)
    # urlUtil.jobTitleExtractor(htmlContent)

if __name__ == '__main__': main()
