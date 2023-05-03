import math
import logging

import requests
from typing import Union, Any

from requests.adapters import HTTPAdapter, Retry

# *********************************************************************
# LOGGING - set of log messages
# *********************************************************************

log = logging.getLogger(__name__)

# *********************************************************************
# SETUP - of API KEY,header 
# *********************************************************************

PAGE_SIZE = 1000
RETRIES = 3

session = requests.Session()
session.headers['Accept'] = "application/json"

MAX_RETRY = 5
MAX_RETRY_FOR_SESSION = 5
BACK_OFF_FACTOR = 1
TIME_BETWEEN_RETRIES = 1000
ERROR_CODES = (400,401,405,500, 502, 503)

### Retry mechanism for server error ### https://stackoverflow.com/questions/23267409/how-to-implement-retry-mechanism-into-python-requests-library###
# {backoff factor} * (2 ** ({number of total retries} - 1))
retry_strategy = Retry(total=25, backoff_factor=1, status_forcelist=ERROR_CODES)
session.mount('https://', HTTPAdapter(max_retries=retry_strategy))

# *********************************************************************
# FUNCTIONS - 
# get login_jwt - get auth key & assign the requests to reponse using post method
# get_people :
# assign the requests to reponse using get method
# calculate total no.of pages required by total_records/page size such 150,860/1000 = 150.860 pages % round up to 151 using math.ceil
# load pages starting from 1 with each containing 1000 records
# increment page number by 1 , for every iteration
# continue with the loop until it reaches the last page
#In case, if error occurs retry
# *********************************************************************

# Generate jwt
def get_jwt(url: str,key:str,scopes:str,session: requests.Session=session)-> str:
    """Returns a jwt for authentication to the iPaaS APIs

    Args:
        url (str): LOGIN_URL= https://api.dartmouth.edu/api/jwt
        key (str): API_KEY

    Returns:
        _type_: str
    """

    headers = {
     'Authorization':key                  
    }

    if scopes:
        url = url + '?scope=' + scopes
    else:
        url = url

    response = session.post(url=url, headers=headers)

    if response.ok:
        response_json = response.json()
        jwt = response_json['jwt']
    else:
        response_json = response.json()
        error = response_json['Failed to obtain a jwt']
        raise Exception(error)
        

    return jwt

# Get_people - access people records
def get_people(jwt: str, url: str ,session: requests.Session=session )-> "Union[list[None],list[dict]]":
    """ returns all the people from People_API
    Args:
        jwt (str): in .env file 
        =PEOPLE_URL (str): https://api.dartmouth.edu/api/people
    Returns:
        _type_: str
    """

    headers: dict = {'Authorization': 'Bearer ' + jwt, 'Content-Type':'application/json'}
    page_number: int = 1

    # params: dict[Any,Any] = { 'page_size': PAGE_SIZE,'page': page_number }
    params = { 'page_size': PAGE_SIZE,'page': page_number }
    people: list[dict] = []
    
    #re-use session
    response = session.get(url=url, headers=headers, params=params) 
    total_count: int = int(response.headers["x-total-count"])
    
    log.info("Total number of records :" + str(total_count))
    log.debug("People count per page = " + str(PAGE_SIZE))

    pages_required : float = int(total_count)/ PAGE_SIZE
    log.info(f"Total pages required:{pages_required}")
    #Last page is a whole number - 150.855 is rounded up to 151
    last_page_number : int = math.ceil(pages_required) 
    log.info(f"last page number:{last_page_number}")    

    last_page_records : int = int(total_count) % PAGE_SIZE
    log.info("last page records:"+ str(last_page_records))
   
    total_rec : str = str(total_count)
    log.info("Total number of records in the system: " + str(total_rec))
    
    last_page_number=last_page_number+1
    
    #use for loop until last page:
    for page in range(page_number,last_page_number):
        log.debug(f"Starting with page number {page}")      
                  
        continuation_key = response.headers.get("x-request-id")
        
        if page_number == 1:
            people_url = f"{url}?page_size={PAGE_SIZE}&page={page_number}"
        else:
            people_url = f"{url}?continuation_key={continuation_key}&pagesize={PAGE_SIZE}&page={page_number}"     
           
        response = session.get(url=people_url, headers=headers)       

        response_json = response.json()

        people+=response_json
        current_page_number: int = page
        
        log.debug(f"Ending on loop {current_page_number}")
        log.debug(f"Records returned, so far: {len(people)}")
        page_number+=1       
    
    return people 

