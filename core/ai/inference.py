from joblib import dump, load
from pathlib import Path
from argparse import ArgumentParser

import numpy as np
from ommt.settings import BASE_DIR

import os


ai_model_path = os.path.join(BASE_DIR, "ommt/models")

PATH = Path(ai_model_path)
MODEL_NAME = 'SentimentClassifier.joblib'

def init():
    global pipeline
    pipeline = load(PATH/MODEL_NAME)

def run(data):
    init()
    data=np.array(data, ndmin=1)
    preds = pipeline.predict(data)
    return preds


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-d", "--data", nargs="+", help='<Required> Data to be predicted', required=True)
    # parser.add_argument("-b", "--bow", help="bow model name")
    parser.add_argument("-m", "--model", help="model name")
    parser.add_argument("-p", "--path", help="path to load model artifacts")
    args = parser.parse_args()

    if args.path:
        PATH = Path(args.path)
        
    # MODEL_NAME = next(PATH.glob('*')).name

    if args.model:
        MODEL_NAME = args.model
    

    data = args.data
    
    # init()
    print(run(data))