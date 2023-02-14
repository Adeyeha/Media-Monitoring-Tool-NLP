from django.shortcuts import render,redirect
from .models import news,searchsubject,templateupload,filtered_news
from .forms import fileuploadform,details,templateuploadform
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status as statuses
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import datetime
from ommt.settings import PAGINATOR_COUNT,BASE_DIR,MAX_UPLOAD_SIZE,ALLOWED_EXTENSIONS
from django.forms.models import model_to_dict
import pandas as pd
from django.http import HttpResponse,Http404,JsonResponse
import os
import io
from .serializers import newsserializer
from .ai.predict_logic import execute_all_subjects
import re
from background_task import background
import numpy as np
import pyodbc
from django.utils import timezone
from django.db.models import Q
from itertools import chain
from django.forms.models import model_to_dict



# newslist = [['Access Bank',
#   'https://www.gtreview.com/news/africa/access-bank-eyes-trade-finance-expansion-as-grobank-acquisition-moves-a-step-closer/'],
#  ['Access Bank',
#   'https://www.premiumtimesng.com/business/business-news/452647-access-bank-takes-top-spot-as-nigerias-biggest-bank-by-asset.html'],
#  ['Access Bank',
#   'https://thenationonlineng.net/access-bank-lagos-city-marathon-kenya-ethiopia-elite-runners-arrive/'],
#  ['Access Bank',
#   'https://www.thisdaylive.com/index.php/2021/04/02/access-bank-grows-profit-to-n126bn-recommends-55k-final-dividend/'],
#  ['Access Bank',
#   'https://www.thisdaylive.com/index.php/2021/04/06/access-bank-lagos-city-marathon-2/'],
#  ['Access Bank',
#   'https://thenationonlineng.net/access-banks-assets-hit-n8-7tr-as-consumer-deposits-leap-by-31/'],
#  ['Access Bank',
#   'https://guardian.ng/business-services/access-bank-posts-n764-7-billion-gross-earnings-in-2020/'],
#  ['Access Bank',
#   'https://www.thisdaylive.com/index.php/2021/04/07/muazu-kefas-vows-to-end-dominance-of-east-africans/'],
#  ['Access Bank',
#   'https://www.ecofinagency.com/finance/0104-42495-nigeria-s-access-bank-to-finalize-purchase-of-grobank-in-q2-2021'],
#  ['Access Bank',
#   'https://www.thisdaylive.com/index.php/2021/04/04/as-access-drives-revenue-growth-through-retail-banking/']]

from .relevance_model import run_relevance_algo
from .SentimentTrain.SentimentTrain import run_train
from ommt.settings import BASE_DIR
import os
ai_model_path = os.path.join(BASE_DIR, "ommt/models")



# Create your views here.
def home(request):
    return render(request,'core/homepage.html')


def retrainmodels(request):
    run_train(ai_model_path)
    run_relevance_algo()
    return render(request,'core/homepage.html')

def dashboard(request):
    newslist = news.objects.all().order_by('-timestamp')
    paginator = Paginator(newslist, PAGINATOR_COUNT)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'newslist': newslist,
        'page_obj': page_obj,
    }
    return render(request,'core/dashboard.html',context)

def dashboard_today(request):
    try:
        newslist = news.objects.filter(timestamp__date=datetime.today()).order_by('-timestamp')
        paginator = Paginator(newslist, PAGINATOR_COUNT)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator, page_number)
        context = {
            'newslist': newslist,
            'page_obj': page_obj,
        }
        
        if not newslist.count():
            messages.warning(request, 'No News have been captured today')
        return render(request,'core/dashboard_today.html',context)
    except Exception as e:
        print(e)
        messages.warning(request, 'Something Went Wrong')
        return render(request,'core/dashboard_today.html')

def customsearchupload(request):
    form=fileuploadform()
    return render(request,'core/customsearchupload.html',{'form':form})


from django.db import transaction
@transaction.atomic
@background(schedule=1)
def bulkaddsubjecthelper(df_dict,verbose_name='Background Subject Update'):
    def convert_to_str(lists):
        return [str(el) if not isinstance(el,list) else convert_to_str(el) for el in lists]
    df=pd.DataFrame.from_records(df_dict)
    df['timestamp'] = timezone.now().replace(tzinfo=None)
    df['search_subject']=df['search_subject'].str.strip()
    df['sector']=df['sector'].str.strip()
    df.drop_duplicates(subset=['search_subject'],keep='first',inplace=True)
    print(df)
    with pyodbc.connect('Driver={SQL Server Native Client 11.0};''server=online-media.database.windows.net;''Database=onlinemediatool;''UID=analytics;''PWD=Password1$',autocommit=True) as conn:
        print('connected to db')
        c = conn.cursor()
        sql = """Insert into [dbo].[core_searchsubject](search_subject,sector,stakeholder,timestamp) values (?,?,?,?)"""
        sql2= """delete from [dbo].[core_searchsubject] where search_subject = (?)"""
        #c.fast_executemany=True
        print('running delete')
        c.executemany(sql2,[[x,] for x in convert_to_str(df['search_subject'].to_numpy().tolist())])
        c.commit()
        print('running insert')
        print(convert_to_str(df.to_numpy().tolist()))
        c.executemany(sql,convert_to_str(df.to_numpy().tolist()))
        c.commit()

    # for index,row in df.iterrows():
    #     try:
    #         with transaction.atomic():
    #             searchsubject.objects.update_or_create(search_subject=row['search_subject'],stakeholder=row['stakeholder'])
    #         print(row['search_subject'])
    #     except Exception as e:
    #         print(e)
    #         # # if is_connection_broken_error(Exception):
    #         # reconnect()
    #         continue
    # # searchsubject.objects.bulk_create([searchsubject(**vals) for vals in df.to_dict('records')])
    del df
    print('Bulk Upload Complete')



def bulkaddsubject(request):
    if request.method == 'POST':
        uploadfile=request.FILES.get('file')
        if uploadfile.name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:

            if uploadfile.size <  int(MAX_UPLOAD_SIZE):
                dataframe = pd.read_csv(io.StringIO(uploadfile.read().decode('utf-8')), delimiter=',',error_bad_lines=False,dtype=str)
                x = templateupload.objects.filter(purpose='addsubject').order_by('-timestamp').first()
                file_path = os.path.join(BASE_DIR, str(x.filepath))
                print(dataframe.columns)
                print(pd.read_csv(file_path).columns)
                print(file_path)
                if [x for x in dataframe.columns] != [x for x in pd.read_csv(file_path).columns]:
                # df = pd.read_csv(file_path)
                # if all([set(dataframe.columns) == set(df.columns) for df in dataframe]):
                    messages.warning(request, 'Invalid Template - Please Get Template')
                    return redirect('bulkaddsubject')
                dataframe['search_subject'] = dataframe['search_subject'].map(lambda x: re.sub(r'\W+', ' ', x))
                dataframe.fillna('',inplace=True)
                print(dataframe.to_dict('records'))
                bulkaddsubjecthelper(dataframe.to_dict('records'))

                messages.success(request, 'File Uploaded Successfully - Background Job has been Activated')
                return redirect('searchsubject_index')
            else:
                messages.warning(request, 'File Size Cannot Exceed 5MB')
                return redirect('bulkaddsubject')
        else:
            messages.warning(request, 'Only CSV Files Allowed')
            return redirect('bulkaddsubject')
    form=fileuploadform()
    return render(request,'core/bulkaddsubject.html',{'form':form})


def download_fileupload_template(request,purpose):
    x = templateupload.objects.filter(purpose=purpose).order_by('-timestamp').first()
    try:
        file_path = os.path.join(BASE_DIR, str(x.filepath))
        # print(file_path)
    except Exception as e:
        print(e)
        raise Http404
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404



def upload_fileupload_template(request):
    if request.method == 'POST':
        f=templateuploadform(request.POST, request.FILES)
        if f.is_valid():
            f.save()
            messages.success(request, 'File Uploaded Successfully')
        else:
            print(f.errors)
    form = templateuploadform()
    return render(request,'core/uploadfileuploadtemplate.html',{'form':form})

def textsearch(request):
    return render(request,'core/textsearch.html')

def newsdetails(request,pk):
    newslist = news.objects.get(id=pk)
    form=details(initial=model_to_dict(newslist))
    return render(request,'core/details.html',{"form":form})

def aifeedback(request):
    #newslist =  news.objects.filter(~Q(summary = ''),annotation__isnull=True,search_subject__isnull = False).all().order_by('?')[:30]
    try:
        relnewslist = news.objects.filter(summary__isnull=False,annotation__isnull=True,search_subject__isnull = False, raw_text__isnull = False).order_by('-timestamp')[:10]
        irrelnewslist = filtered_news.objects.filter(summary__isnull=False,annotation__isnull=True,search_subject__isnull = False,raw_text__isnull = False).order_by('-timestamp')[:10]
        # # newslist = news.objects.filter(summary__isnull=False,annotation='',search_subject__isnull = False).order_by('-timestamp')[:30]
        # newslist = news.objects.all().order_by('-timestamp')[:PAGINATOR_COUNT]
        for x in irrelnewslist:
            x.model_source = 'irr'
        
        for x in relnewslist:
            x.model_source = 'rel'

        newslist = list(chain(relnewslist, irrelnewslist))
        # relnewslist = news.objects.filter(summary__isnull=False,annotation__isnull=True,search_subject__isnull = False, raw_text__isnull = False)
        # irrelnewslist = filtered_news.objects.filter(summary__isnull=False,annotation__isnull=True,search_subject__isnull = False,raw_text__isnull = False)
 
        # newslist=relnewslist.union(irrelnewslist)
        # newslist=newslist.order_by('-timestamp')[:10]
        print(newslist)

        # if not newslist.count():
        if len(newslist) == 0:
            messages.warning(request, 'No Unlabeled News Yet')

    except Exception as e:
        print(e)
        messages.error(request, 'Something Went Wrong')
        return redirect('dashboard')
    # print(newslist)
    paginator = Paginator(newslist, PAGINATOR_COUNT)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'newslist': newslist,
        'page_obj': page_obj,
    }
    print(context)
    return render(request,'core/feedback.html',context)
    

def add_searchsubject(request):

    context = {
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'core/add_searchstring.html',context)

    if request.method == 'POST':
        searchstring = request.POST['searchstring']
        stakeholder = request.POST['stakeholder']
        sector = request.POST['sector']

        if not searchstring:
            messages.error(request, 'Search String is required')
            return render(request, 'core/add_searchstring.html',context)

        if searchsubject.objects.filter(search_subject=searchstring).exists():
            messages.error(request, 'Duplicate Record Exists')
            return render(request, 'core/add_searchstring.html',context)

        searchsubject.objects.create(search_subject=searchstring, sector=stakeholder, stakeholder=sector)

        messages.success(request, 'Record saved successfully')
        return redirect('searchsubject_index')



def searchsubject_details(request,string):
    try:
        newslist = news.objects.filter(search_subject=string).order_by('-timestamp')
        paginator = Paginator(newslist, PAGINATOR_COUNT)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator, page_number)
        context = {
            'newslist': newslist,
            'page_obj': page_obj,
        }

        if not newslist.count():
            messages.warning(request, 'No News Found')
        return render(request,'core/searchsubject_details.html',context)
        #TO DO: Link details page to searchsubject result
        
    except Exception as e:
        print(e)
        messages.warning(request, 'No News Found')
        return redirect('searchsubject_index')

def searchstring_delete(request,pk):
    searchstring = searchsubject.objects.get(id=pk)
    searchstring.delete()
    messages.success(request, 'record removed')
    return redirect('searchsubject_index')


@api_view(['POST'])
def update_feedback(request):
    data = request.data
    print(data)
    if data['model_source'] == 'irr':
        t = filtered_news.objects.get(id=data['id'])
        t.annotation = data['value']
        t.save()
        response = {'message':str(data['id']) + ' updated'} 
        return Response(response,status=statuses.HTTP_200_OK)
    elif data['model_source'] == 'rel':
        t = news.objects.get(id=data['id'])
        t.annotation = data['value']
        t.save()
        response = {'message':str(data['id']) + ' updated'} 
        return Response(response,status=statuses.HTTP_200_OK)


def fetchtodaysnews(request):
    if request.method == 'POST':
        # search_str = json.loads(request.body).get('searchText')
        newslist=news.objects.filter(timestamp__date=datetime.today()).order_by('-timestamp')
        data = newslist.values()
        return JsonResponse(list(data), safe=False)


# def fetchallnews(request):
#     if request.method == 'POST':
#         # search_str = json.loads(request.body).get('searchText')
#         newslist=news.objects.all()
#         data = newslist.values()
#         return JsonResponse(list(data), safe=False)

def fetch_and_predict(request):
    # # newslist = query_input(query="Access Bank",period="w")

    # newsattributes = list(map(fetch_news_attributes,newslist))

    # summary_predictions = pipeline.predict([x[3] for x in newsattributes])
    # summary_predictions = np.where(summary_predictions=='P','Positive',summary_predictions)
    # summary_predictions = np.where(summary_predictions=='-','Neutral',summary_predictions)
    # summary_predictions = np.where(summary_predictions=='N','Negative',summary_predictions)

    # newsattributes_complete = [y+[x] for x,y in zip(summary_predictions,newsattributes)]

    # values = list(map(array2model,newsattributes_complete))
    values = execute_all_subjects()

    context={
        'predictions':values
    }

    return render(request,'core/fetchpredict.html',context)

# def search_allnews(request):
#     if request.method == 'POST':
#         search_str = json.loads(request.body).get('searchText')
#         newslist = news.objects.filter(
#             search_subject__icontains=search_str) | news.objects.filter(
#             title__icontains=search_str)
#         data = newslist.values()
#         return JsonResponse(list(data), safe=False)

# def search_todaysnews(request):
#     if request.method == 'POST':
#         search_str = json.loads(request.body).get('searchText')
#         newslist = news.objects.filter(
#             search_subject__icontains=search_str) | news.objects.filter(
#             title__icontains=search_str)
#         data = newslist.values()
#         return JsonResponse(list(data), safe=False)

# def search_subject(request):
#     if request.method == 'POST':
#         search_str = json.loads(request.body).get('searchText')
#         newslist = news.objects.filter(
#             search_subject__icontains=search_str) | news.objects.filter(
#             stakeholder__icontains=search_str)
#         data = newslist.values()
#         return JsonResponse(list(data), safe=False)

def searchsubject_index(request):
    searchstring = searchsubject.objects.all().order_by('search_subject')
    paginator = Paginator(searchstring, PAGINATOR_COUNT)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'searchstring': searchstring,
        'page_obj': page_obj,
    }
    return render(request,'core/searchsubject_index.html',context)

def searchnews(request):
    if request.method == 'POST':
        print(request.META.get('HTTP_REFERER'))
        # print(request.POST)
        if request.POST['datesearchField'] == "" and len(request.POST['keywordsearchField']) > 0:
            keywordField = request.POST['keywordsearchField']
            newslist = news.objects.filter(Q(search_subject__icontains=keywordField) | Q(title__icontains=keywordField) |Q(summary__icontains=keywordField)).order_by('-timestamp')
            msg=keywordField
            paginator = Paginator(newslist, PAGINATOR_COUNT)
            page_number = request.GET.get('page')
            page_obj = Paginator.get_page(paginator, page_number)
            context = {
                'newslist': newslist,
                'page_obj': page_obj,
            }

            messages.success(request,"Showing result for "+msg)
            return render(request,'core/dashboard.html',context)

        elif request.POST['datesearchField'] != "" and len(request.POST['keywordsearchField']) == 0:
            dateField = request.POST['datesearchField']
            print(dateField)
            newslist = news.objects.filter(timestamp__date=dateField).order_by('-timestamp')
            msg=dateField
            paginator = Paginator(newslist, PAGINATOR_COUNT)
            page_number = request.GET.get('page')
            page_obj = Paginator.get_page(paginator, page_number)
            context = {
                'newslist': newslist,
                'page_obj': page_obj,
            }

            messages.success(request,"Showing result for "+msg)
            return render(request,'core/dashboard.html',context)

    messages.warning(request,"No search result")
    return redirect('dashboard')




def searchsubjects(request):
    if request.method == 'POST':
        print(request.META.get('HTTP_REFERER'))
        # print(request.POST)
        if request.POST['datesearchField'] == "" and len(request.POST['keywordsearchField']) > 0:
            keywordField = request.POST['keywordsearchField']
            searchstring = searchsubject.objects.filter(Q(stakeholder__icontains=keywordField) | Q(search_subject__icontains=keywordField)).order_by('-timestamp')
            msg=keywordField
            paginator = Paginator(searchstring, PAGINATOR_COUNT)
            page_number = request.GET.get('page')
            page_obj = Paginator.get_page(paginator, page_number)
            context = {
                'searchstring': searchstring,
                'page_obj': page_obj,
            }
            messages.success(request,"Showing result for "+msg)
            return render(request,'core/searchsubject_index.html',context)

        elif request.POST['datesearchField'] != "" and len(request.POST['keywordsearchField']) == 0:
            dateField = request.POST['datesearchField']
            print(dateField)
            searchstring = searchsubject.objects.filter(timestamp__date=dateField).order_by('-timestamp')
            msg=dateField
            paginator = Paginator(searchstring, PAGINATOR_COUNT)
            page_number = request.GET.get('page')
            page_obj = Paginator.get_page(paginator, page_number)
            context = {
                'searchstring': searchstring,
                'page_obj': page_obj,
            }

            messages.success(request,"Showing result for "+msg)
            return render(request,'core/searchsubject_index.html',context)

    messages.warning(request,"No search result")
    return redirect('searchsubject_index')