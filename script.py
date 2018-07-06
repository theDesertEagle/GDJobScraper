import  requests

def baseRequestBuilder(countryName):
    helperReqURL = 'https://www.glassdoor.co.in/util/ajax/findLocationsByFullText.htm'
    helperReqParams = {
        'locationSearchString' : countryName.replace(' ', '+'),
        'allowPostalCodes' : 'true'
    }
    helperReqHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    print(helperReqParams)
    helperResponse = requests.get('https://www.glassdoor.co.in/util/ajax/findLocationsByFullText.htm?locationSearchString=new+delhi&allowPostalCodes=true', headers = helperReqHeaders)
    #helperResponse = requests.get(helperReqURL, params = helperReqParams) # json data extraction from response object
    print(helperResponse.json()) # 
    return helperResponse

#def URLRequestBuilder(countryName, pageNumber):

print(baseRequestBuilder('new delhi'))    
