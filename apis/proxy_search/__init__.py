import logging
import azure.functions as func

# Try to import the required libraries, install if not available
import logging
from bs4 import BeautifulSoup
from time import time, sleep
import requests
import json


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36"

def main(req: func.HttpRequest) -> func.HttpResponse:
    from collections import defaultdict
    logging.info('Python HTTP trigger function processed a request.')

    search = req.params.get('search')
    top = req.params.get('top')
    period = req.params.get('period')
    start_date = req.params.get('start_date')
    end_date = req.params.get('end_date')
    type = req.params.get('type')

    if not search:
        try:
            req_body = req.get_json()
        except ValueError:
            logging.log()
            pass
        else:
            search = req_body.get('search')
            top = req_body.get('top')
            period = req_body.get('period')
            start_date = req_body.get('start_date')
            end_date = req_body.get('end_date')
            type = req_body.get('type')

    if search:
        start = time()
        search_result = google_search(search, top=top, period=period, start_date=start_date, end_date=end_date, type=type)
        search_result_dict = defaultdict(list)
        for url, search_url in search_result:
            search_result_dict['search url'] = search_url
            search_result_dict['urls'].append(url)

        output = {'time taken': round(time()-start,2), 'timestamp':time()}
        output.update(search_result_dict)
        return func.HttpResponse(json.dumps(output), status_code=200)
    else:
        return func.HttpResponse(
             "Error 400: \"search\" parameter not found in the url",
             status_code=400
        )
        
def get_page_(url, user_agent = None):
    '''This funciton returns an html document of a google search page
    :param url (str): google search url
    :param user_agent (str):
    '''
    if user_agent is None:
        user_agent = USER_AGENT
    
    html = None
    try:
        headers = {'user-agent':user_agent}
        cookies = {
            'privacy-policy': '1,XXXXXXXXXXXXXXXXXXXXXX'
            }
        response = requests.get(url, headers=headers, cookies=cookies)
        html = response.content
    except Exception as e:
        # print("Exception:", e)
        logging.log('Exception')
        pass
        
    return html
    
def prepare_date(start_date, end_date, period):
    '''Accept date range and return a google url formatted string
    :param str start_date (optional): start date of result in the format "MM-DD-YYYY"
    :param str end_date (optional): end date of result in the format "MM-DD-YYYY"
    '''
    if period:
        return 'qdr:' + period
    start_date = start_date.split('-') if start_date is not None else [None]*3
    end_date = end_date.split('-') if end_date is not None else [None] *3
    #print(start_date, end_date)
    
    return "cdr%3A1%2Ccd_min%3A{}%2F{}%2F{}%2Ccd_max%3A{}%2F{}%2F{}".\
           format(*start_date, *end_date)
        
    
def parse_html(html, type):
    '''Parse the xml of a given html string
    :param str html: html string of a webpage

    :return dict: specific contents of the html page parsed'''

    # Create a soup object
    if html == None:
        #print("Nothing in the HTML")
        return []
    soup = BeautifulSoup(html, 'html5lib')

    # Find links the titles and summaries from soup object
    links = []
    if type == 'news':
        for link in soup.find_all("g-card"):
            links.append(link.find('a').get('href'))
    else:
        for link in soup.findAll('div', class_='g'):
            links.append(link.find('a').get('href'))        
        
    return links
    

def google_search(query, top = None, period: str = None, start_date = None,
           end_date=None, type='search'):
    '''Search google based on a passed in query
    :param str query: the search string
    :param int count: number of search results expected
    :param str period: {'h': 'past 1 hour', 'd':'past 24 hours',
        'w':'past 1 week', 'm':'past 1 month', 'y':'past 1 year'}. When this
        argument is argument is passed, start_date and end_date will be ignored.
    :param str start_date: start date of result in the format "MM-DD-YYYY"
    :param str end_date: end date of result in the format "MM-DD-YYYY"

    :return dict: search result as dictionaries
    '''
    count=top or 10 # Use 10 as the default number of results to return
    query = query.replace(" ", "+")
    
    tbs = prepare_date(start_date, end_date, period)
    #print('TBS', tbs)
    start = 0
    
    # Max result to return per search loop, taking counts at a time
    # if required number of results is more, then batch in 50s
    
    max_ = 50
    while count>0:
        num = min(count, max_)
        proxy = 'https://api.proxycrawl.com/?token=EjGEp7fk2XqLjTpZOWWvMw&url='
        search_url= proxy + f'https://www.google.ng/search?q={query}&start={start}&tbs={tbs}&num={num}&source=lnms'
        if type == 'news':
            search_url += '&tbm=nws'

        html = get_page_(search_url)
        if start > 1:
            sleep(1.5)
        for result in parse_html(html, type):
            yield result, search_url

        count -= num
        start +=1