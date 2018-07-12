
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
• Doc - Date On Client-Side
• Info - Information
• LocID - Location Identification
• LocT - Location Type
• Pg - Page
• Params - Parameters
• Diff - Difference
• Alt - Alternate

Author's Notes: 
• Any comments with "###" indicates the current area of work in the project
• Future releases may have to rely on HTML parsers instead of Regex due to markup language's complexity
• Lookarounds: Lookahead and Lookbehind seem to be powerful regex functionalities that will replace existing poor logic
• ***MAJOR UPDATE EXPLANATION*** : 
  Previously, I thought all job-page requests are of the following form, [giving styled job-pages]

  "https://www.glassdoor.co.in/job-listing/software-development-engineer-amazon-JV_IC2921225_KO0,29_KE30,36.htm?jl=2827281589"
  
  with the base "/job-listing/some-profession-some-code.htm?some-args". This logic failed as soon as tried implementing 
  the job-header extraction procedure for multiple job-listing pages, which failed to recognise the headers from the 2nd job-listing
  page. My new logic revolved around the fact that the request was formed by the extensions embedded in the <a> tag "href" attribute, of the form:
  
  "https://www.glassdoor.co.in/partner/jobListing.htm?pos=102&ao=295207&s=58&guid=000001648e020dfb9562679748ae9d52&src=GD_JOB_AD&t=SR&extid=1
  &exst=OL&ist=&ast=OL&vt=w&slr=true&rtp=0&cs=1_24d58d85&cb=1531390857391&jobListingId=2827281589"

  Although this logic showed some success intially for supporting multiple job-listing pages by scraping the styled job-pages, two problems 
  were associated with this approach:
  > MAIN ISSUE: Some partner sites (assumed to be associated with GD to provide info for some jobs in a very ugly format) like indianfresher.com  
                were loaded instead of GD's, making it impossible to scrape due to the provision neccesity of support for scraping for such sites    
  > Redirections were common and slowed the scraping process

  After much research on GD's http requests, it appears to be that all job-page requests are actually, of the form, 

  "https://www.glassdoor.co.in/job-listing/details.htm?pos=101&ao=295207&s=58&guid=000001648dea1a72a9d96e8bec675158&src=GD_JOB_AD&t=SR&extid=1
  &exst=OL&ist=&ast=OL&vt=w&slr=true&rtp=0&cs=1_83c72ca4&cb=1531389287652&jobListingId=2827281589"

  which is very similar to my 2nd logic, since the query strings for both links are nearly identical, but they are slightly different on the 
  basis of their URL parameters. Two disadvantages in this method are that, first, company's photos and page-styling is lost, but all of the relevant
  information pertaining to the job-page is retrieved. Second, header-info regex search-patterns will need slight modifications but thankfully
  these job-pages seem to follow a template. One big advantage is that the regex search will be performed on a relatively smaller document file with lesser text.
  Moreover, these jobLinks have additional useful information, such as company's CEO, competitor, etc.     

"""

# MODULE DEPENDENCIES
import requests
import webbrowser
import re
from sys import exit
from sys import exc_info
from datetime import datetime

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

    # PRIVATE VARIABLES
    _dateFormat = '%Y-%m-%d' 
    
    def __init__(self, title, loc, doc):
        """Initially sets up thebasic instance functionality and info such as the user's location and job/profession title
        
           Params:
           • title - Profession/Job title to be searched, given the user
           • loc - Abstract Location Information based on which the jobs will be searched, given the user
           • doc - Date on client's side 
    
           Returns: [None]   
        """
        
        # User Input Preference Storage
        self._title = title
        self._loc = loc
        self._doc = datetime.strptime(doc, JobURLUtil.getJobPostingDateFormat())
        
        # URLs and Header Initialization
        self._standardHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # mimicking browser request
        self._locReqURL = 'https://www.glassdoor.co.in/util/ajax/findLocationsByFullText.htm'
        self._listPgBaseReqURL = 'https://www.glassdoor.co.in/Job/jobs.htm'
        
        # Company and Job-related Resource and Regex-Pattern Initialization/Compilation
        self._jobLinkPattern = re.compile(r'v><a href=(?:\'|")/partner/jobListing([.?=&_0-9a-zA-Z]+)(?:\'|")') # raw string, extracts links susceptible to redirection => better compatibility + slower scrape-speed + partner-site redirection errors
        self._logoLinkPattern = re.compile(r'(?:https?://media\.glassdoor\.[a-zA-Z.-]+/sqls/[0-9]+/[a-zA-Z0-9-]+\.png|defLogo)')
        self._jobTitlePattern = re.compile(r'(?:\'|")jobTitle(?:\'|"):(?:\'|")([\d\w\sÀ-ÿ.,&\)\(\]\[\{\};:\\/#!—–-]+)(?:\'|")') # Added support for accented characters and brackets
        self._companyRatingPattern = re.compile(r'(?:\'|")ratingNum(?:\'|")>([\d.]+)<') 
        self._jobLocationPattern = re.compile(r'(?:\'|")loc(?:\'|"):(?:\'|")([\d\w\sÀ-ÿ.,&\)\(\]\[\{\};:\\/#!—–-]+)(?:\'|")') # Added support for accented characters and brackets  
        self._jobPostingDatePattern = re.compile(r'(?:\'|")datePosted(?:\'|")\svalue=(?:\'|")([0-9-]+)\s')
        # self._jobPostingTimeDiffPattern = re.compile(r'\s([0-9]+)\sdays? ago')
        self._companyNamePattern = re.compile(r'(?:\'|")employerName(?:\'|"):(?:\'|")([\d\w\sÀ-ÿ.,&\)\(\]\[\{\};:\\/#!—–-]+)(?:\'|")') # Added support for accented characters and brackets 
        self._companyNameAltPattern = re.compile(r'(?:\'|")companyName(?:\'|")>([\d\w\sÀ-ÿ.,&\)\(\]\[\{\};:\\/#!—–-]+)<') # Avoiding usage due to scraping HTML instead of JSON-like data 
        
        # GD-Formatted Location Information Extraction Initialization  
        self._locationInfoExtractor()

        # Deprecated patterns in future releases
        # self._jobLocationPattern = re.compile(r'ib(?:\'|")>[a-z;&-]+([a-zA-Z,\s]+)')
        # self._companyRatingPattern = re.compile(r'n>\s([0-9]+\.[0-9])+<i') s
        # self._jobTitlePattern = re.compile(r'g(?:"|\')>([a-zA-Z0-9\s.,&\)\(\]\[\{\};:\\/#!—–-]+)</h2>') 
        # self._jobLinkPattern = re.compile(r'v><a href=(?:\'|")(/partner/jobListing[.?=&_0-9a-zA-Z]+)(?:\'|")') # raw string, extracts links susceptible to redirection => better compatibility + slower scrape-speed + partner-site redirection errors
        # self._jobLinkPattern = re.compile(r'https?://www\.glassdoor\.[a-zA-Z.-]+/job-listing/[a-zA-Z0-9_.,?=-]+') 
        # self._companyNamePattern = re.compile(r'ib(?:\'|")>\s([a-zA-Z0-9./\\,_\s"\'&!;#—–-]+)') # Deprecated in future releases

    @staticmethod
    def getJobPostingDateFormat():
        """Returns the class varable depicting the date format
           Helper Method for general tasks and calculations involving Job-Posting Date
        
           Params: [None ]
    
           Returns: 
           • _dateFormat - Date Format in accordance to GD's job-posting date  
        """
        return JobURLUtil._dateFormat

    def _setLocInfo(self, locId, locT):
        """Set the user's location and job/profession title, as found by the location GET request
           Helper Method For: _locationInfoExtractor()
        
           Params:
           • locId - Specific Location ID set by GD for a certain geographical location name
           • locT - Assumed Specific type of location (such as city (C), state (S), etc.) set by GD   
    
           Returns: [None]   
        """
        
        self._locId = locId
        self._locT = locT

    def _setJobListBaseInfo(self, baseJobListPgURL):
        """Sets the job-listing pages' base URL
           Helper Method For: jobListingPageBaseRequester()
        
           Params:
           • baseJobListPgURL - Specific Location ID set by GD for a certain geographical location name
    
           Returns: [None]   
        """

        self._baseJobListPgURL = baseJobListPgURL # Main Base URL for finding Job Links

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
    
    def _locationInfoExtractor(self): 
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

        jobLinks = ['https://www.glassdoor.co.in/job-listing/details'+extractedPattern for extractedPattern in self._jobLinkPattern.findall(htmlContent)]
        print('|NUMBER OF JOB LINKS EXTRACTED| {}'.format(len(jobLinks)))
        # for x in jobLinks:
        #     print("\n::::::")
        #     resObj = self._GETRequester(x, {}, self._standardHeaders, 'test')
        #     print(resObj)
        #     print(resObj.url)
        #     resObj = self._GETRequester(resObj.url, {}, self._standardHeaders, 'test')
        #     print(resObj)
        #     print(resObj.url)
        # exit(0)
        # for jobLink in enumerate(jobLinks): print(jobLink) # Printing debug line
        return jobLinks

    def logoLinkExtractor(self, htmlContent): 
        """Fetches 30 company logo links (as of 9 July, 2018) present on GD's job-listing page 

            Params: 
            • htmlContent - HTML text content obtained from the job-listing base page

            Returns:
            • logoLinks - All parse-able logo links from the HTML text content 
        """
        logoLinks = self._logoLinkPattern.findall(htmlContent)
        #for logoLink in logoLinks: print(logoLink) # Printing debug line
        return logoLinks

    def jobLinkHeaderInfoExtractor(self, jobLinks, jobListPgHTMLContent):
        """Processes 30 job links (as of 9 July, 2018) at once to collect relevant jobs' header-information 
            Params: 
            • jobLinks - Collection of links extracted from the job-listing page 
            • jobListPgHTMLContent - HTML Content of Job Listing Page, for whom the job links have been extracted <to prevent GET Request repetition and delay for HTML Content> 

            Returns:
            • headerInfo - Array of dictioinaries containing each job's header information   
        """
        headerInfo = []
        logoLinks = self.logoLinkExtractor(jobListPgHTMLContent)

        for logoLinkIndex, jobLink in enumerate(jobLinks):
        #     headers = {
        #     ':Authority': 'www.glassdoor.co.in',
        #     ':Scheme': 'https',
        #     'Accept': '*/*',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept-Language': 'en-US,en;q=0.9',
        #     'Cache-Control': 'no-cache',
        #     'Cookie': '__cfduid=d422f8ae751cc6bcb75707cef4cb0e5861530882013; gdId=5803da01-19f5-4a28-a878-df6189dfd0ee; trs=direct:direct:direct:2018-07-06+06%3A00%3A13.475:undefined:undefined; ARPNTS_AB=139; ARPNTS=1835378880.64288.0000; _ga=GA1.3.1237923810.1530882019; __qca=P0-274212888-1530884158973; G_ENABLED_IDPS=google; cto_lwid=19c7109b-cb7b-4df8-b25e-19f85b300d1b; uc=8F0D0CFA50133D96DAB3D34ABA1B873324E3F5DA1D1CA8D53F7CDB15E0E972C88D8AF602813C5C4B348C3B29B3D04FF6325FD44230E522ACB46583BD23C57828C2FBC611438D6AC5EADA5958631E5766560ECF96BB9E0E1F35CE441A9AC10EFB971FA3DEAFF5E41E8F1958EF8D718D34502F922D3BC8423EB243E7C1366FA74EB99283B525D7B8E264B898BFDEFBC49B; ARPNTS-JX=1046849728.64288.0000; JSESSIONID_JX_APP=5F6168E4A719730610C7091410C2CD7A; GSESSIONID=5F6168E4A719730610C7091410C2CD7A; JSESSIONID=1544085D25CB362656DC9CE9011F5606; _gid=GA1.3.35418599.1531328297; cass=2; _uetsid=_uet5b4962ff; _gat_UA-2595786-1=1',
        #     'Pragma': 'no-cache',
        #     'Referrer-Policy': 'origin',
        #     'Referer': 'https://www.glassdoor.co.in/',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        #     'X-Requested-With': 'XMLHttpRequest',
        #     }
            resObj = self._GETRequester(jobLink, {}, self._standardHeaders, 'job-page header-extraction')
            htmlContent = resObj.text

            # Future Work: Need to preprocess names and titles by removing unicodes like &amp;
            try:
                # Company-Name Extraction
                companyNameRes = self._companyNamePattern.findall(htmlContent)
                if not companyNameRes: companyName = self._companyNameAltPattern.findall(htmlContent)[0] # Use Backup Pattern
                else: companyName = companyNameRes[0]
                # print('{} : {}'.format(companyName, jobLink)) # Debug Print Line
                
                # Company-Rating Extraction
                companyRatingRes = self._companyRatingPattern.findall(htmlContent)
                if not companyRatingRes: companyRating = -1
                else: companyRating = companyRatingRes[0] 

                # Job-Title Extraction
                jobTitle = self._jobTitlePattern.findall(htmlContent)[0]

                # Job-Location Extraction 
                jobLocation = self._jobLocationPattern.findall(htmlContent)[0]

                # Job Posting Time Difference Extraction
                jobPostingTimeDiff = (self._doc - datetime.strptime(self._jobPostingDatePattern.findall(htmlContent)[0], JobURLUtil.getJobPostingDateFormat())).days 
                # if not jobPostingTimeDiffRes: jobPostingTimeDiff = 0 # Accomodating empty list values from job posted "today"
                # else: jobPostingTimeDiff = self._jobPostingTimeDiffPattern.findall(htmlContent)[0] # Two identical matches made, choose only one 

            except Exception as error:
                # htmlFileTester('test', htmlContent) # Debugging Line
                print('<ERROR> Could not scrape job header info. \n......> <Further Info> {}\n......> <Line Number> {}\n......> <URL> {}'.format(error, exc_info()[-1].tb_lineno, jobLink)) # Shows with line number error wth sys.exc_info()
            # for item in companyName: print(item) # Debugging line
            # htmlFileTester('test', resObj.text) # Debugging Utility Line

            try:
                headerInfo.append( {'companyName': companyName, 
                                   'companyRating': companyRating, 
                                   'jobTitle': jobTitle, 
                                   'jobLocation': jobLocation, 
                                   'jobPostingTimeDiff': jobPostingTimeDiff,
                                   'companyLogoURL': logoLinks[logoLinkIndex],
                                   'jobURL': jobLink})
            except Exception as error:
                print('<ERROR> Could not store scraped job-header info. \n......> <Further Info> {}\n......> <Line Number> {}\n......> <URL> {}'.format(error, exc_info()[-1].tb_lineno, jobLink))

        return headerInfo

    def jobListingPageRetriever(self, pageNumber):
        """Retrieves job-listing page info by initiating a GET Request 
            Params: 
            • pageNumber - Job-listing page number > 1  

            Returns:
            • Job-listing page response-object, for utilizing its properties like html content, url, etc.    
        """
        currentJobListPgURL = '{}{}{}{}'.format(self._baseJobListPgURL[:-4], '_IP', pageNumber, self._baseJobListPgURL[-4:]) # Assumed extension is .htm for now, but might need 'future proofing' 
        # print('|JOB-LISTING PAGE URL CONSTRUCTED AS| {}'.format(currentJobListPgURL)) # Debugging Line
        return self._GETRequester(currentJobListPgURL, {}, self._standardHeaders, 'job-listing page-number ({})'.format(pageNumber))        

### PROGRAM COMMENCEMENT 
def main():
    doc = datetime.today().strftime(JobURLUtil.getJobPostingDateFormat())          
    urlUtil = JobURLUtil('software', 'muscat', doc)
    resObj = urlUtil.jobListingPageBaseRequester() # Sets the job-listing page base URL
    htmlContent, jobListingPgURL = resObj.text, resObj.url

    for pageNumber in range(2, 4): # Display 2 pages, each consisting of 30 individual job-pages
        print('|JOB-LISTING PAGE IN CONSIDERATION| {} '.format(jobListingPgURL))
        jobHeadersList = urlUtil.jobLinkHeaderInfoExtractor(urlUtil.jobLinkExtractor(htmlContent), htmlContent) # Returns 30 job header info from each job link 
        print('|JOB-HEADER EXTRACTION COMPLETE|') # Debug Print Line
        print('|JOB-HEADER INFORMATION ON JOB-LISTING PAGE - {}|\n'.format(pageNumber-1)) # Debug Print Line
        for jobNumber, jobHeader in enumerate(jobHeadersList): 
            print('{}:)\n'.format(jobNumber+1)) # Debug Print Line
            for jobHeaderName, jobHeaderValue in jobHeader.items(): print('{} : {}'.format(jobHeaderName, jobHeaderValue)) # Debug Print Line
        # htmlFileTester('test', htmlContent) # Debugging Print Line
        resObj = urlUtil.jobListingPageRetriever(pageNumber)
        htmlContent, jobListingPgURL = resObj.text, resObj.url

if __name__ == '__main__': main()
