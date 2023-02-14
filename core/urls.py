from django.conf.urls import include, url
from .views import (home,dashboard,customsearchupload,textsearch,aifeedback,newsdetails,
add_searchsubject,searchsubject_index,searchstring_delete,searchsubject_details,
dashboard_today,bulkaddsubject,upload_fileupload_template,download_fileupload_template,
fetchtodaysnews,update_feedback,fetch_and_predict,searchnews,searchsubjects,retrainmodels)
from django.views.decorators.csrf import csrf_exempt


from django.urls import path 

urlpatterns = [

path('', home, name = 'home'),
path('dashboard', dashboard, name = 'dashboard'),
path('dashboard-today', dashboard_today, name = 'dashboard_today'),
path('customsearch-upload', customsearchupload, name = 'customsearchupload'),
path('addsubject-upload', bulkaddsubject, name = 'bulkaddsubject'),
path('textanalyze', textsearch, name = 'textsearch'),
path('feedback', aifeedback, name = 'aifeedback'),
path('details/<int:pk>', newsdetails, name = 'newsdetails'),
path('add-subject', add_searchsubject, name = 'add_searchsubject'),
path('subject', searchsubject_index, name = 'searchsubject_index'),
path('searchstring-delete/<int:pk>', searchstring_delete, name = 'searchstring_delete'),
path('searchstring-details/<str:string>', searchsubject_details, name = 'searchsubject_details'),
path('fetch_and_predict', fetch_and_predict, name = 'fetch_and_predict'),
path('upload-fileupload-template', upload_fileupload_template, name = 'upload_fileupload_template'),
path('download-fileupload-template/<str:purpose>', download_fileupload_template, name = 'download_fileupload_template'),
# path('fetchtodaysnews', csrf_exempt(fetchtodaysnews), name = 'fetchtodaysnews'),
# path('fetchallnews', csrf_exempt(fetchallnews), name = 'fetchallnews'),
# path('fetchtodaysnews', fetchtodaysnews, name = 'fetchtodaysnews'),
path('update-feedback', update_feedback, name = 'update_feedback'),
path('searchnews', searchnews, name = 'searchnews'),
path('searchsubjects', searchsubjects, name = 'searchsubjects'),
path('retrainaimodels', retrainmodels, name = 'retrainmodels'),
]