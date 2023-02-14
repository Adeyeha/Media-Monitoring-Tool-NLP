from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
# from forecastUpdater import forecastApi
from .ai.predict_logic import execute_all_subjects
from ommt.settings import SCHEDULER_PERIOD
from .relevance_model import run_relevance_algo
from .SentimentTrain.SentimentTrain import run_train
from ommt.settings import BASE_DIR

import os


ai_model_path = os.path.join(BASE_DIR, "ommt/models")

def run_sentiment_train():
    run_train(ai_model_path)
    return None

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(execute_all_subjects, 'interval', hours=SCHEDULER_PERIOD,max_instances=3,replace_existing=True)
    scheduler.add_job(run_relevance_algo, 'cron',month='jan-dec', day_of_week='mon-sun', hour='2',replace_existing=True)
    scheduler.add_job(run_sentiment_train, 'cron',month='jan-dec', day_of_week='mon-sun', hour='2',replace_existing=True)
    scheduler.start()