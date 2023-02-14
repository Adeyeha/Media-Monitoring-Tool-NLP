# import pandas as pd
# import pyodbc
# import os
# from .tfidf import rank_documents
# import nltk
# nltk.download('stopwords')
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# import re
# from statistics import mean

import pyodbc
import pandas as pd
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
import re
from statistics import mean
nltk.download('averaged_perceptron_tagger')
from .tfidf import rank_documents
import re
from nltk.util import ngrams
from statistics import mean

import numpy as np
import pickle
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold, learning_curve
from sklearn.model_selection import train_test_split
# from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
import os


from ommt.settings import BASE_DIR


ai_model_path = os.path.join(BASE_DIR, "ommt/models")

def run_relevance_algo():


    def get_ngram(s,toks):
        s = s.lower()
        s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
        tokens = [token for token in s.split(" ") if token != ""]
        output = list(ngrams(tokens, toks))
        return [' '.join(y) for y in output]

    def ngram_counter(x):
        print('*' * 20)
        search = x['search_subject']
        searched = x['summary']
        count_searched = len([word for word in word_tokenize(re.sub(r'[^\w]', ' ', searched)) if word not in stopwords.words() and len(word) > 1])
        count_search = len(word_tokenize(search))
        if count_search == 1:
            print('straight up 1')
            return 1
        
        print(f"I found {count_search} in search")
        print(f"I found {count_searched} in searched")
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


    def wordbyword_cosine(x):
        rnk = [rank_documents(word,[x['summary']])[0] for word in word_tokenize(re.sub(r'[^\w]', ' ', x['search_subject'])) if not word in stopwords.words() and len(word) > 1]
        return mean(rnk) * (sum(map(lambda i: i > 0, rnk))/len(rnk))

    def convert_to_str(lists):
                return [str(el) if not isinstance(el,list) else convert_to_str(el) for el in lists]
        
    with pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};''Server=online-media.database.windows.net;''Database=onlinemediatool;''UID=analytics;''PWD=Password1$') as connection:
        c = connection.cursor()
        irr=c.execute("select count(*) from core_news where annotation = 'Irrelevant' and summary is not null").fetchone()[0] + c.execute("select count(*) from core_filtered_news where annotation = 'Irrelevant'  and summary is not null").fetchone()[0]
        rre=c.execute("select count(*) from core_news where annotation <> 'Irrelevant'  and summary is not null").fetchone()[0] + c.execute("select count(*) from core_filtered_news where annotation <> 'Irrelevant'  and summary is not null").fetchone()[0]
    #     rre += dt[dt['annotation'] == 'Relevant'].annotation.count()
    #     irr += dt[dt['annotation'] != 'Relevant'].annotation.count()
    #     count = min(irr,rre)
    #     countlesscsv = min(irr,rre)
        c.execute("truncate table train")
        c.execute(f"insert into train select top({min(irr,rre)}) search_subject,summary,raw_text,annotation from core_news where annotation = 'Irrelevant'  and summary is not null union select top({min(irr,rre)}) search_subject,summary,raw_text,annotation from core_filtered_news where annotation = 'Irrelevant'  and summary is not null")
        c.execute(f"insert into train select top({min(irr,rre)}) search_subject,summary,raw_text,annotation from core_news where annotation <> 'Irrelevant'  and summary is not null union select top({min(irr,rre)}) search_subject,summary,raw_text,annotation from core_filtered_news where annotation <> 'Irrelevant'  and summary is not null")
        c.commit()
    #     sql = """Insert into [dbo].[train] (search_subject,title,annotation) values (?,?,?)"""
    #     c.fast_executemany=True
    # #     try:
    #     print('running insert')
    #     c.executemany(sql,convert_to_str(dt.to_numpy().tolist()))
    # #     except Exception as e:
    # #         print(e)
    #     c.commit()
        c.execute("update train set annotation = 'Relevant' where annotation <> 'Irrelevant'")
        c.commit()
        dt=pd.read_sql('select * from train',connection)

    dt.replace([None],'',inplace =True)

    dt['cosine_similarity']=dt[['search_subject','summary']].apply(lambda x: wordbyword_cosine(x) * ngram_counter(x) , axis=1)
    dt['target'] =  dt.annotation.map({'Irrelevant':1,'Relevant':0})

    ## Classification Modelling
    x = dt[['cosine_similarity']]
    y = dt['target']
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size  = 0.25)
    kfold = StratifiedKFold(n_splits=10)
    classifier=LogisticRegression(random_state = 2)
    print(cross_val_score(classifier, train_x, y = train_y, scoring = "accuracy", cv = kfold, n_jobs=5).mean())
    classifier=LogisticRegression(random_state = 2)
    classifier.fit(x,y)
    fname = os.path.join(ai_model_path, "RelevanceClassifier.pkl")
    with open(fname,mode = "wb") as a :
        pickle.dump(classifier,a)


    metrics = dt[dt.cosine_similarity > 0].groupby('annotation').cosine_similarity.median().to_dict()
    with pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};''Server=online-media.database.windows.net;''Database=onlinemediatool;''UID=analytics;''PWD=Password1$') as connection:
        c= connection.cursor()
        for x in metrics.keys():
            sql = """update core_relevance_metrics set metrics = """ + str(metrics[x]) + """, run_date = getdate() where state = '""" + x + """'"""
            print(sql)
            c.execute(sql)
            c.commit()

