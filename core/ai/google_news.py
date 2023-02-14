import datetime
# from .GoogleNewsEngine import GoogleNews
from math import ceil
from dateutil.relativedelta import relativedelta
import requests
from urllib.parse import quote_plus
import datetime
from bs4 import BeautifulSoup as Soup
import os
from time import time
from newspaper import Article
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta,date
import nltk
from newspaper import Article
from newspaper import nlp
import os
import logging


class GoogleNews:

    def __init__(self, lang="en", period="", start="", end="", news_type=True):
        self.__texts = []
        self.__links = []
        self.__results = []
        # self.user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36"
        # self.user_agent =  ''
        self.headers = {'User-Agent': self.user_agent}
        self.__lang = lang
        self.__period = period
        self.__start = start
        self.__end = end
        
        self.news_type = news_type

    def setlang(self, lang):
        self.__lang = lang

    def setperiod(self, period):
        self.__period = period

    def setTimeRange(self, start, end):
        self.__start = start
        self.__end = end
        
    def search(self, key):
        """
        Searches for a term in google news and retrieves the first page into __results.
        
        Parameters:
        key = the search term
        """
        self.__key = "+".join(key.split(" "))
        self.getpage()


    def getpage(self, page=1):
        """
        Retrieves a specific page from google news into __results.

        Parameter:
        page = number of the page to be retrieved 
        """
        
            
        try:
            if self.__start != "" and self.__end != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{}&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__start,self.__end,(10 * (page - 1)))
            elif self.__period != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&tbs=lr:lang_1{},qdr:{},&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__period,(10 * (page - 1))) 
            else:
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&tbs=lr:lang_1{}&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,(10 * (page - 1))) 
        except AttributeError:
            raise AttributeError("You need to run a search() before using getpage().")
            
        
        # self.url = 'https://api.proxycrawl.com/?token=EjGEp7fk2XqLjTpZOWWvMw&url=' + quote_plus(self.url)
        # print(self.url)
        try:
            print(self.url)
            self.response = requests.get(self.url, headers = self.headers)
        except Exception as e:
            log = f"Method: 'requests.get' \tError: Exception - {e}\tSearch subject: {self.__key}\tSearch URL: {self.url}"
            # print(log)
        else:
            self.page = self.response.content
            #with open(self.__key.replace('"','').replace("+",' ')+"_first.html", 'wb') as f:
            #    f.write(self.page)
            # If page has "No results found for...", avoid extracting alternate results
            if self.page.find(str(self.__key).encode()) - self.page.find(b"No results found for ") < len("No results found for ")+ 5:
                print("No results found. File has been written to {}".format(self.__key))
                with open(self.__key.replace('"','').replace("+",' ')+".html", 'wb') as f:
                    f.write(self.page)
                return 
            self.content = Soup(self.page, "html.parser")            
            
            result = []
            try:
                result = self.content.find_all("div", id="search")[0]
                # print(result)
                result = result.find_all("g-card")
                # print(result)
                
            except Exception as e:
                log = f"Method: '*self.content.find_all*' \tError: Exception - {e}\tSearch subject: {self.__key}\tPage URL: {self.response.url}"
                # print(log)
                return
            for item in result:
                try:
                    tmp_text = item.find("div", {"role" : "heading"}).text.replace("\n","")
                except Exception:
                    tmp_text = ''
                try:
                    tmp_link = item.find("a").get("href")
                except Exception:
                    tmp_link = ''
                try:
                    tmp_date = item.find("div", {"role" : "heading"}).next_sibling.findNext('div').findNext('div').text
                    tmp_date = compute_date(tmp_date).strftime('%d/%m/%Y')
                except Exception:
                    tmp_date = ''
                self.__texts.append(tmp_text)
                self.__links.append(tmp_link)
                self.__results.append({'title': tmp_text,
                                       'date': tmp_date,
                                       'link': tmp_link})
            
        
            

    
    def result(self):
        """Returns the __results."""
        return self.__results

    def gettext(self):
        """Returns only the __texts of the __results."""
        return self.__texts

    def get__links(self):
        """Returns only the __links of the __results."""
        return self.__links

    def clear(self):
        self.__texts = []
        self.__links = []
        self.__results = []


def compute_date(i):
    '''
    Align the date column of the output of the next function to be same format
    :params date(str): the date column from the output of the next function
    '''
    try:
        if 'min' in i:
            i = int(i.split()[0])
            return datetime.datetime.now() + relativedelta(minutes=-i)
        elif 'hour' in i:
            i = int(i.split()[0])
            return datetime.datetime.now() + relativedelta(hours=-i)
        elif 'day' in i:
            i = int(i.split()[0])
            return datetime.datetime.now().date() + relativedelta(days=-i)
        elif 'week' in i:
            i = int(i.split()[0])
            return datetime.datetime.now().date() + relativedelta(weeks=-i)
        elif 'month' in i:
            i = int(i.split()[0])
            return datetime.datetime.now().date() + relativedelta(months= -i)
        elif 'year' in i:
            i = int(i.split()[0])
            return datetime.datetime.now().date() + relativedelta(years= -i)
        else:
            return datetime.datetime.strptime(i, '%b %d, %Y').strftime('%Y-%m-%d')
    except Exception:
        return ''

def query_input(query: str, start_date: str = None, end_date: str = None, period: str = None, top: int=None):
    '''
    Set the query to search for, run through 10 Google pages, and remove the duplicates
    :param query (str): the search phrase
    :params start_date (str): the start date to search for in the format 'MM/DD/YYYY'
    :params end_date (str): the end date of the query search in the format 'MM/DD/YYYY'
    :param period (str): {'h': 'past 1 hour', 'd':'past 24 hours',
        'w':'past 1 week', 'm':'past 1 month', 'y':'past 1 year'}. When this
        argument is argument is passed, start_date and end_date will be ignored.
    :param top (int): number of top results to return

    :return list:
    '''

    top = top or 10 # Default the number of results to 10

    if end_date is None:
        end_date = date.today().strftime("%m/%d/%Y")
    if start_date is None:
        start_date = (date.today() - timedelta(1)).strftime("%m/%d/%Y")

    # If period parameter is provided, use period to instantiate the GoogleNews class
    if period:
        googlenews = GoogleNews(period = period)
    else:
        googlenews = GoogleNews(start = start_date, end = end_date)

    # Get the first page
    st = time()
    googlenews.search(query)
    print('Search took:', time() - st)
    
    output = googlenews.get__links()

    
    # Get other pages 
    for i in range(2, ceil(top/10)+1):
        print(i, "****")
        googlenews.getpage(i)
        output += googlenews.get__links()
        # Concat each search page result with the others
    return [[query,url] for url in output[:top] ]
#     return output[:top]




def fetch_news_attributes(link):
    # print(link)
    article = Article(link[1])
    article.download()
    try:
        article.parse()
    except Exception as e:
        print(e)
        None
    try:
        article.nlp()
    except Exception as e:
        print(e)
        None
    try:
        source_url = article.source_url
    except Exception as e:
        print(e)
        source_url = None

    try:
        summary = article.summary
    except Exception as e:
        print(e)
        summary = None

    try:
        title = article.title
    except Exception as e:
        print(e)
        title = None

    try:
        publish_date = article.publish_date.strftime('%Y-%m-%d:%H:%M:%S')
    except Exception as e:
        print(e)
        publish_date = None

    try:
        text = article.text
    except Exception as e:
        print(e)
        text = None
    # print([link[0],link[1],source_url,summary,title,publish_date,text])
    return [link[0],link[1],source_url,summary,title,publish_date,text]