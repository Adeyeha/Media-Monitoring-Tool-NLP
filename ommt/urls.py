"""
Definition of urls for ommt.
"""

from django.conf.urls import include, url

from django.urls import path 

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    path('', include('core.urls')),
]
