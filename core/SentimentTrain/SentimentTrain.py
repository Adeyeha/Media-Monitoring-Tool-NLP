import pandas as pd
import numpy as np
np.random.seed(2021)
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from joblib import dump, load

from pathlib import Path
from datetime import datetime
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('punkt')

import pyodbc
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.pipeline import Pipeline
from ommt.settings import BASE_DIR
import os
data_path = os.path.join(BASE_DIR, "core/SentimentTrain/sentiment_data.csv")

np.random.seed(2021)

PATH = Path('sentiment-artifacts')

def train_test_score(X_train, X_test, y_train, y_test, model=None):
    np.random.seed(2021)
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, )
    if model is None:
        model = LogisticRegression(class_weight={'-':10, '+':4})
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print(classification_report(y_test, pred))
    # print(confusion_matrix(y_test, pred))
    return model, None

def make_pipeline(model=None, processor=None):
    if not model:
        model = LogisticRegression(class_weight={'N':10, 'P':4},multi_class='multinomial')
    
    if not processor:
        processor = TfidfVectorizer()

    tfidf = TfidfVectorizer()
    pipe = Pipeline([
                    ('tfidf', tfidf),
                    ('lr', model),
    ])

    return pipe

def save_model(pipe,model_name=None,modelpath=None):
    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    if not model_name:
        PATH.mkdir(exist_ok=True)
        model_name = PATH / f'sentiment-model-{now}.joblib'
    
    else:
        PATH.mkdir(exist_ok=True)
        model_name = modelpath / Path(model_name+ '.joblib')
        #model_name.parent.mkdir(exist_ok=True)
    
    #pipe = make_pipeline(model=None, processor=None)
    
    dump(pipe, model_name)

def run_train(modelpath):
    print(os.getcwd())
    data_cleaned = pd.read_csv(data_path)


    import pyodbc
    with pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};''Server=online-media.database.windows.net;''Database=onlinemediatool;''UID=analytics;''PWD=Password1$') as connection:
        c = connection.cursor()
        pos=c.execute("select count(*) from core_news where annotation = 'Positive' and raw_text is not null").fetchone()[0] + c.execute("select count(*) from core_filtered_news where annotation = 'Positive'  and raw_text is not null").fetchone()[0]
        neg=c.execute("select count(*) from core_news where annotation = 'Negative'  and raw_text is not null").fetchone()[0] + c.execute("select count(*) from core_filtered_news where annotation = 'Negative'  and raw_text is not null").fetchone()[0]
        neu=c.execute("select count(*) from core_news where annotation = 'Neutral'  and raw_text is not null").fetchone()[0] + c.execute("select count(*) from core_filtered_news where annotation = 'Neutral'  and raw_text is not null").fetchone()[0]

        dt=pd.read_sql(f"""select top({min(pos,neg,neu)}) search_subject,title,summary,raw_text,annotation from core_news where annotation <> 'Irrelevant'  and raw_text is not null union select top({min(pos,neg,neu)}) search_subject,title,summary,raw_text,annotation from core_filtered_news where annotation <> 'Irrelevant'  and raw_text is not null""",connection)
    data_cleaned = pd.concat([data_cleaned,dt[['title','annotation']].rename(columns={'title':'COMMENT','annotation':'Sentiment'})],axis=0)
    del dt
    data_cleaned.dropna(inplace=True,axis = 1)


    train_data = train_test_split(data_cleaned.COMMENT, data_cleaned.Sentiment, test_size=0.3)
    pipe=make_pipeline()
    train_test_score(*train_data, pipe)
    save_model(pipe,model_name = 'SentimentClassifier',modelpath = modelpath)
    return None

    with pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};''Server=online-media.database.windows.net;''Database=onlinemediatool;''UID=analytics;''PWD=Password1$') as connection:
        c= connection.cursor()
        sql = """insert into SentimentTrain values(cast(getdate() as date))"""
        print(sql)
        c.execute(sql)
        c.commit()
    
if __name__=='__main__':
    run_train()

