from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.pipeline import Pipeline
import string
from nltk.corpus import stopwords
import joblib
import nltk, os
from urllib.request import urlopen

storage = 'https://storageaccountonlinb019.blob.core.windows.net/text-classifier-artifacts/inference/'

def words(language):
    if language == 'english':
        with open('predict/'+language) as file:
            return [word.strip() for word in file.readlines()]
stopwords.words = words

def text_process(mess):
    """""
    1. remove punc
    2. remove stop words
    3. return list of clean text words
    """
    nopunc = [char for char in mess if char not in string.punctuation]
    
    nopunc =  ''.join(nopunc)
    return[word for word in nopunc.split() if word.lower() not in stopwords.words('english')+['bank']]


# try:
    # with open(os.path.abspath('predict/RandomForestClassifier_rec_68.pkl'),'rb') as file:
        # model=joblib.load(file)
        # print("Successfully loaded classifier!!!")
# except:
model = joblib.load(urlopen(storage+'RandomForestClassifier_rec_68.pkl'))
    
bow_file = urlopen(storage+'vocabulary.pkl')
bow = CountVectorizer(analyzer=text_process, vocabulary=joblib.load(bow_file))
    
tfidf_file = urlopen(storage+'tfidf.pkl')
tfidf = joblib.load(tfidf_file)
    
pipeline = Pipeline([
    ('bow', bow),
    ('tfidf', tfidf),
    ('classifier', model)
    ])