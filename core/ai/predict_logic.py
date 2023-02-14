from .inference import run
from .google_news import fetch_news_attributes,query_input
import numpy as np
from core.models import news,searchsubject,templateupload,filtered_news,relevance_metrics
from ommt.settings import SEARCH_PERIOD,SUBJECT_BATCH,BASE_DIR
import os
import requests
from core.tfidf import rank_documents
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from statistics import mean
import re
from nltk.util import ngrams
import joblib
from datetime import datetime


from ommt.settings import BASE_DIR

ai_model_path = os.path.join(BASE_DIR, "ommt/models")

cosine_threshold = relevance_metrics.objects.filter(state='Relevant').first().metrics

def azfuncappgeturlsearch(search,period):
    url = 'https://online-media-func.azurewebsites.net/api/google_search'
    params={'search':search, 'start_date':datetime.now().strftime('%m-%d-%Y'),'end_date':datetime.now().strftime('%m-%d-%Y'),'top':20}
    resp = requests.get(url=url,json=params)
    if resp.status_code != 200:
        return None
    return [[search,url] for url in resp.json()['urls']]

def azfuncappgeturlnews(search,period):
    url = 'https://online-media-func.azurewebsites.net/api/google_news'
    params={'search':search, 'start_date':datetime.now().strftime('%m-%d-%Y'),'end_date':datetime.now().strftime('%m-%d-%Y'),'top':20}
    resp = requests.get(url=url,json=params,)
    if resp.status_code != 200:
        return None
    return [[search,url] for url in resp.json()['urls']]

def fetch_and_predict_with_period(modeldict):

    classifier = os.path.join(ai_model_path, "RelevanceClassifier.pkl")
    classifier = joblib.load(classifier)

    def wordbyword_cosine(x):
        rnk = [rank_documents(word,[x[3]])[0] for word in word_tokenize(re.sub(r'[^\w]', ' ', x[0])) if not word in stopwords.words() and len(word) > 1]
        return mean(rnk) * (sum(map(lambda i: i > 0, rnk))/len(rnk))


    def get_ngram(s,toks):
        s = s.lower()
        s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
        tokens = [token for token in s.split(" ") if token != ""]
        output = list(ngrams(tokens, toks))
        return [' '.join(y) for y in output]

    def ngram_counter(x):
        print('*' * 20)
        search = x[0]
        searched = x[3]
        #count_searched = len([word for word in word_tokenize(re.sub(r'[^\w]', ' ', searched)) if word not in stopwords.words() and len(word) > 1])
        count_search = len(word_tokenize(search))
        if count_search == 1:
            print('straight up 1')
            return 1
        
        print(f"I found {count_search} in search")
        #print(f"I found {count_searched} in searched")
        lst = []
        for x in range(1,count_search):
            y=x+1
            print(f"I will now  do {y} grams")
            total = []
            for ab in get_ngram(search,y):
                print(ab)
                total.append(get_ngram(searched,y).count(ab))
            print(f"for {y} ngrams i got {len(total)} results and took the mean")
            lst.append(mean(total))
        print(f'I finally got {len(lst)} averges')
        return mean(lst)

    try:
        newslist1 = None 
        try:
            newslist1 = query_input(query=modeldict['search_subject'],period=SEARCH_PERIOD,top=20)
        except Exception as e:
            None
        newslist2 = azfuncappgeturlsearch(search=modeldict['search_subject'],period=SEARCH_PERIOD)
        newslist3 = azfuncappgeturlnews(search=modeldict['search_subject'],period=SEARCH_PERIOD)

        # if newslist1 != None:
        #     newlist = newslist + newslist1 + newslist2
        # else:
        #     newlist = newslist + newslist2
        newss = [newslist1,newslist2,newslist3]
        newlist = []
        for x in newss:
            if x != None:
                newlist.extend(x)
        newslist = [i for n, i in enumerate(newlist) if i not in newlist[:n]]
        print(newslist)
        # print('Log'.join(["".join(x) for x in newslist]))
        # print('writing to log')
        # with open(os.path.join(BASE_DIR,'newlog.txt'),'w') as f:
        #     f.write('Startedlog')
        #     f.write('Log'.join(["".join(x) for x in newslist]))
        #     f.write('/n')
        newsattributes = list(map(fetch_news_attributes,newslist))
        
        newsattributes = [x for x in newsattributes if (len(x[3]) > 0 and len(x[4]) > 0 and len(x[6]) > 0)]
        # print(newsattributes)

        # FILTER OFF IRRELEVANT NEWS
        print('start filtering')
        cosine_similarities = [[wordbyword_cosine(x) * ngram_counter(x)] for x in newsattributes]
        cosine_similarities = [x for x in classifier.predict(cosine_similarities)]
        print('Mid filtering')
        newsattributes = [y + [x] for x,y in zip(cosine_similarities,newsattributes)]
        print('End filtering')
        summary_predictions = run([x[4] for x in newsattributes])
        summary_predictions = np.where(summary_predictions=='P','Positive',summary_predictions)
        summary_predictions = np.where(summary_predictions=='-','Neutral',summary_predictions)
        summary_predictions = np.where(summary_predictions=='N','Negative',summary_predictions)
        print('Done predicting')
        newsattributes_complete = [y+[x] for x,y in zip(summary_predictions,newsattributes)]

        print(len(newsattributes_complete[0]))

        relevant_news = [x for x in newsattributes_complete if x[7] == 0]
        irrelevant_news = [x for x in newsattributes_complete if x[7] == 1]

        values = list(map(array2model,relevant_news))
        values = list(map(array2modelirrelevant,irrelevant_news))

        return values
    except Exception as e:
        print(e)
        return None

# def get_all_subjects():
#     searchsubjectlist=searchsubject.objects.all().values()
#     return searchsubjectlist

def array2model(x):
    try:
        news.objects.create(search_subject=x[0], url=x[1],source=x[2],summary=x[3],title=x[4],newsdate=x[5], raw_text = x[6],cosine_similarity=x[7],sentiment=x[8])
    except Exception as e:
        return False
    return True

def array2modelirrelevant(x):
    try:
        filtered_news.objects.create(search_subject=x[0], url=x[1],source=x[2],summary=x[3],title=x[4],newsdate=x[5], raw_text = x[6],cosine_similarity=x[7] ,sentiment=x[8])
    except Exception as e:
        return False
    return True

def execute_all_subjects():

    values=[]
    batch = SUBJECT_BATCH
    count = searchsubject.objects.all().count()
    # print(count)
    y=0
    z=y+batch
    if count > 0:
        for x in range(round(count/batch) + 1):
            searchsubjectlist=searchsubject.objects.all().order_by('search_subject').values()[y:z]
            # print(f'{y}==>{z}')
            value = list(map(fetch_and_predict_with_period,searchsubjectlist))
            values.append(value)
            y+=(batch+1)
            z=y+batch
        # return values
    return None



