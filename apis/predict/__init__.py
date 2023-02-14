import logging

import azure.functions as func

from .inference_script import pipeline
import numpy as np
import json
import nltk
import time


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    start = time.time()
    texts = req.params.get('texts')
    if not texts:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            texts = req_body.get('texts')

  
    if texts:
        if type(texts) != type([]):
            texts = [texts]
            
        summary_predictions = pipeline.predict(texts)
        summary_predictions = np.where(summary_predictions=='P','Positive',summary_predictions)
        summary_predictions = np.where(summary_predictions=='-','Neutral',summary_predictions)
        summary_predictions = np.where(summary_predictions=='N','Negative',summary_predictions)
        
        return func.HttpResponse(json.dumps({'time_taken':time.time()-start, 'results':list(summary_predictions)}))
    else:
        return func.HttpResponse(
             "Error: Pass 'texts' as a parameter or as json body to the endpoint",
             status_code=400
        )
