
"""
Author: the.desert.eagle
Project: GDJobScraper Python Script
Purpose: Scrape glassdoor to collect key data about job-postings (job description, job title, etc.)
Motivation: Construct a dataset of job-postings from available data online
Future Works: Extract the technical job required skills in the field of computer science and data science from the collected job data and store them in a concise manner    

Author's Notes: 
• Any comments with "###" indicates the current area of work in the project
• The 'jobURL' HTML Page links in the output field consists of the Job Description Text 
• Future releases may have to rely on HTML parsers instead of Regex due to markup language's complexity
• Lookarounds: Lookahead and Lookbehind seem to be powerful regex functionalities that will replace any existing poor logic
• it appears to be that all job-page requests are actually, of the form, 
  "https://www.glassdoor.co.in/job-listing/details.htm?pos=101&ao=295207&s=58&guid=000001648dea1a72a9d96e8bec675158&src=GD_JOB_AD&t=SR&extid=1
  &exst=OL&ist=&ast=OL&vt=w&slr=true&rtp=0&cs=1_83c72ca4&cb=1531389287652&jobListingId=2827281589"
• Any used abbreviations are listed in the bottom-most docstring below the code 
• The intent of this program is for educational purposes only

"""

# MODULE DEPENDENCIES
import requests
import webbrowser
import re
from sys import exit
from sys import exc_info
from sys import argv
from datetime import datetime

# DEBUG UTILITY FUNCTION {Deprecated}
def htmlFileTester(docName, docContent):
    """Saves the HTML Content of job page
       Deprecated Reason: CORS disabled by Job Website Servers

       Params:
       • title - Profession/Job title to be searched, given the user
       • loc - Abstract Location Information based on which the jobs will be searched, given the user
       • doc - Date on client's side 

       Returns: [None]   
    """

    fileName = '{}.html'.format(docName)
    fileHandler = open(fileName, 'w', encoding='utf-8')
    fileHandler.write(docContent)
    fileHandler.close()
    webbrowser.open_new_tab(fileName)

# CENTRAL AND TUNABLE LOGIC-BASE FOR SCRAPING
class ScraperLogic:
    """Contains the main-logic and search patterns for GD scraping"""
    def __init__(self):
        """Sets the foundational scraper-logic object(s) for information extraction from web pages
           Params: [None]
    
           Returns: [None]   
        """
        self.patternBase = {
            # Applied separately using jobLinkExtractor()
            'jobLink' : re.compile(r'v><a href=(?:\'|")/partner/jobListing([.?=&_0-9a-zA-Z]+)(?:\'|")'), 
            # Applied separately using logoLinkExtractor()
            'logoLink' : re.compile(r'(?:https?://media\.glassdoor\.[a-zA-Z.-]+/sqls/[0-9]+/[a-zA-Z0-9-]+\.png|defLogo)'),
            # Applied collectively on job-pages accessible via extracted job-links [Header Information]
            'jobTitle' : re.compile(r'(?:\'|")jobTitle(?:\'|"):(?:\'|")([\d\w\sÀ-ÿ.,&\)\(\]\[\{\};:\\/#!—–-]+)(?:\'|")'), 
            'companyRating' : re.compile(r'(?:\'|")ratingNum(?:\'|")>([\d.]+)<'), 
            'jobLocation' : re.compile(r'(?:\'|")loc(?:\'|"):(?:\'|")([\d\w\sÀ-ÿ.,&\)\(\]\[\{\};:\\/#!—–-]+)(?:\'|")'),   
            'jobPostingDate' : re.compile(r'(?:\'|")datePosted(?:\'|")\svalue=(?:\'|")([0-9-]+)\s'),
            'companyName' : re.compile(r'(?:\'|")employerName(?:\'|"):(?:\'|")([\d\w\sÀ-ÿ.,&\)\(\]\[\{\};:\\/#!—–-]+)(?:\'|")'), 
            'companyNameAlt' : re.compile(r'(?:\'|")companyName(?:\'|")>([\d\w\sÀ-ÿ.,&\)\(\]\[\{\};:\\/#!—–-]+)<')          
        }                

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
        if doc == 'SERVER_TIMING': self._doc = datetime.strptime(datetime.today().strftime(JobURLUtil.getJobPostingDateFormat()), JobURLUtil.getJobPostingDateFormat()) 
        else: self._doc = datetime.strptime(doc, JobURLUtil.getJobPostingDateFormat())
        
        # URLs and Header Initialization
        self._standardHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # mimicking browser request
        self._locReqURL = 'https://www.glassdoor.co.in/util/ajax/findLocationsByFullText.htm'
        self._listPgBaseReqURL = 'https://www.glassdoor.co.in/Job/jobs.htm'
        
        # Company and Job-related Resource and Regex-Pattern Initialization/Compilation
        self._scraper = ScraperLogic()

        # GD-Formatted Location Information Extraction Initialization  
        self._locationInfoExtractor()

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
        htmlFileTester('test', listPgBaseResObj.text) # Creates an HTML file from the response and displays it for debugging purposes

    def jobLinkExtractor(self, htmlContent, debugPrint = False):
        """Fetches 30 job links (as of 9 July, 2018) present on GD's job-listing page 
            Params: [htmlContent ]
            • htmlContent - HTML text content obtained from the job-listing base page

            Returns:
            • jobLinks - All parse-able job links from the HTML text content 
        """

        jobLinks = ['https://www.glassdoor.co.in/job-listing/details'+extractedPattern for extractedPattern in self._scraper.patternBase['jobLink'].findall(htmlContent)]
        print('|NUMBER OF JOB LINKS EXTRACTED| {}'.format(len(jobLinks)), flush = True) if debugPrint else None
        return jobLinks

    def logoLinkExtractor(self, htmlContent): 
        """Fetches 30 company logo links (as of 9 July, 2018) present on GD's job-listing page 

            Params: 
            • htmlContent - HTML text content obtained from the job-listing base page

            Returns:
            • logoLinks - All parse-able logo links from the HTML text content 
        """
        logoLinks = self._scraper.patternBase['logoLink'].findall(htmlContent)
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
            resObj = self._GETRequester(jobLink, {}, self._standardHeaders, 'job-page header-extraction')
            htmlContent = resObj.text

            # Future Work: Need to preprocess names and titles by removing unicodes like &amp;
            try:
                # Company-Name Extraction
                companyNameRes = self._scraper.patternBase['companyName'].findall(htmlContent)
                if not companyNameRes: companyName = self._scraper.patternBase['companyNameAlt'].findall(htmlContent)[0] # Use Backup Pattern
                else: companyName = companyNameRes[0]
                # print('{} : {}'.format(companyName, jobLink)) # Debug Print Line
                
                # Company-Rating Extraction
                companyRatingRes = self._scraper.patternBase['companyRating'].findall(htmlContent)
                if not companyRatingRes: companyRating = -1
                else: companyRating = companyRatingRes[0] 

                # Job-Title Extraction
                jobTitle = self._scraper.patternBase['jobTitle'].findall(htmlContent)[0]

                # Job-Location Extraction 
                jobLocation = self._scraper.patternBase['jobLocation'].findall(htmlContent)[0]

                # Job Posting Time Difference Extraction
                jobPostingTimeDiff = (self._doc - datetime.strptime(self._scraper.patternBase['jobPostingDate'].findall(htmlContent)[0], JobURLUtil.getJobPostingDateFormat())).days 

            except Exception as error:
                # htmlFileTester('test', htmlContent) # Debugging Line
                print('<ERROR> Could not scrape job header info. \n......> <Further Info> {}\n......> <Line Number> {}\n......> <URL> {}'.format(error, exc_info()[-1].tb_lineno, jobLink), flush = True) # Shows with line number error wth sys.exc_info()
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
                print('<ERROR> Could not store scraped job-header info. \n......> <Further Info> {}\n......> <Line Number> {}\n......> <URL> {}'.format(error, exc_info()[-1].tb_lineno, jobLink), flush = True)

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

    def batchExtract(self, resObj, batchCount = 2, debugPrint = False):        
        """Retrieves job-listing page info by initiating a GET Request 
            Params: 
            • resObj - Response object containing the GD-format job-listing base page information
            • batchCount - Number indicating how many batches of 30 job-listings are to be extracted (1 page = 30 job-listings)   

            Returns:
            • jobHeadersCollection - List of job headers scraped (a dictionary containing header values) of all of the the job postings    
        """
        jobHeadersCollection = []
        htmlContent, jobListingPgURL = resObj.text, resObj.url

        for pageNumber in range(2, batchCount + 2):
            print('\n' + '-'*50 + '\n', flush = True) if pageNumber != 2 else None # Page Divider - implicitly informs the number of batches processed 
            print('|JOB-LISTING PAGE IN CONSIDERATION| {} '.format(jobListingPgURL), flush = True) if debugPrint else None
            jobHeadersList = self.jobLinkHeaderInfoExtractor(self.jobLinkExtractor(htmlContent, debugPrint), htmlContent) # Returns 30 job header info from each job link 
            jobHeadersCollection += jobHeadersList 
            
            # Displays all of the job headers extracted 
            if debugPrint:
                print('|JOB-HEADER EXTRACTION COMPLETE|', flush = True) # Debug Print Lines
                print('|JOB-HEADER INFORMATION ON JOB-LISTING PAGE - {}|\n'.format(pageNumber-1), flush = True) 
                for jobNumber, jobHeader in enumerate(jobHeadersList):                     
                    print('{}:)\n'.format(jobNumber+1)) 
                    for jobHeaderName, jobHeaderValue in jobHeader.items(): print('{} : {}'.format(jobHeaderName, jobHeaderValue), flush = True)
                    print('\n' + '*'*50 + '\n') if jobNumber != 29 else None           
            #htmlFileTester('test', htmlContent) # Debugging Line
            resObj = self.jobListingPageRetriever(pageNumber)
            htmlContent, jobListingPgURL = resObj.text, resObj.url
        print('\n' + '='*50 + '\n') if debugPrint else None   
        print('{} Job-Posting Header Data Extracted Successfully'.format(batchCount*30), flush = True) # Debug Print Line                       
        print('\n' + '='*50 + '\n') # Implicitly indicating that the scrapping is complete

        return jobHeadersCollection 

# COMMAND-LINE ARGUMENT CHECKER
def cmdArgChecker(cmdParams):
    """Validates commandline arguments for the program. (Created for future flexibility abd extensibility for CMD Arguments) 
        Params: 
        • cmdParams - List of Commandline Arguments 

        Returns:
        • JOB_POSITION, JOB_LOCATION, BATCH_SIZE - Job Position, location and Batch Size entered by the user    
    """
    numArgs = len(cmdParams)
    if numArgs < 4 or numArgs > 4: 
        print('<ERROR> 3 Arguments expected - {JOB_POSITION, JOB_LOCATION, BATCH_SIZE}')
        exit(0)
    else: 
        JOB_POSITION, JOB_LOCATION, BATCH_SIZE = cmdParams[1], cmdParams[2], cmdParams[3]

        # Error Handling
        if not re.match(r'^\d+$', BATCH_SIZE): # handles any string or  negative batch size input
            print('<ERROR> Batch Size must be a positive whole number')
            exit(0)
        else: 
            BATCH_SIZE = int(BATCH_SIZE)   

        print('\n' + '='*50 + '\n') # Acts like a screen output divider
        print('Scraping Initiated For Job Listings Pertaining To: \n\t.....\t JOB POSITION: {} \n\t.....\t JOB LOCATION: {}\n\t.....\t BATCH SIZE (1 batch = 30 job-postings): {}\n'.format(cmdParams[1], cmdParams[2], cmdParams[3]))
        print('\n' + '='*50 + '\n', flush = True) # Acts like a screen output divider
        return JOB_POSITION, JOB_LOCATION, BATCH_SIZE

### PROGRAM COMMENCEMENT 
def main():
    # Extracting and Validating command-line arguments, and then setting the base page
    JOB_POSITION, JOB_LOCATION, BATCH_SIZE = cmdArgChecker(argv)
    urlUtil = JobURLUtil(JOB_POSITION, JOB_LOCATION, 'SERVER_TIMING') # Creates the job scraper object
    resObj = urlUtil.jobListingPageBaseRequester() # Sets the job-listing page base URL

    # Displaying batches of 30 individual job-pages
    jobHeaders = urlUtil.batchExtract(resObj, BATCH_SIZE, True) # Recommended Max Batch Size for Testing <= 3 (to prevent likelihood of Glassdoor API blockage in response to DOS attacks)

if __name__ == '__main__': main()


"""
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
• Cmd, CMD - Command / Commandline
• Arg - Arguments

"""