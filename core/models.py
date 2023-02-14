from django.db import models
from django.utils import timezone

templatepurpose = [
    ('addsubject', 'Add Subject'),
    ('customsubjectsearch', 'Custom Subject Search'),
]

# Create your models here.
class news(models.Model):
    id = models.AutoField(primary_key = True)
    timestamp = models.DateTimeField(blank=True, null=False,default=timezone.now) 
    search_subject = models.CharField(max_length=400,blank=True, null=False)
    newsdate = models.CharField(blank=True, null=True,max_length=400) 
    source = models.CharField(max_length=4000,blank=True, null=True)
    url = models.CharField(max_length=4000,blank=True, null=False,unique=True)
    title = models.CharField(max_length=4000,blank=True, null=True)
    summary = models.CharField(max_length=4000,blank=True, null=True)
    sentiment = models.CharField(max_length=10,blank=True, null=True)
    annotation = models.CharField(max_length=10,blank=True, null=True)
    raw_text = models.TextField(blank=True, null=True)
    cosine_similarity = models.FloatField(blank=True,null=True)

    class Meta:
        ordering: ['timestamp']
        unique_together = ('search_subject', 'newsdate','source','url','title')
        
    def __str__(self):
        return self.search_subject

class filtered_news(models.Model):
    id = models.AutoField(primary_key = True)
    timestamp = models.DateTimeField(blank=True, null=False,default=timezone.now) 
    search_subject = models.CharField(max_length=400,blank=True, null=False)
    newsdate = models.CharField(blank=True, null=True,max_length=400) 
    source = models.CharField(max_length=4000,blank=True, null=True)
    url = models.CharField(max_length=4000,blank=True, null=False,unique=True)
    title = models.CharField(max_length=4000,blank=True, null=True)
    summary = models.CharField(max_length=4000,blank=True, null=True)
    sentiment = models.CharField(max_length=10,blank=True, null=True)
    annotation = models.CharField(max_length=10,blank=True, null=True)
    raw_text = models.TextField(blank=True, null=True)
    cosine_similarity = models.FloatField(blank=True,null=True)

    class Meta:
        ordering: ['timestamp']
        unique_together = ('search_subject', 'newsdate','source','url','title')
        
    def __str__(self):
        return self.search_subject

class searchsubject(models.Model):
    id = models.AutoField(primary_key = True)
    timestamp = models.DateTimeField(blank=True, null=False,default=timezone.now) 
    search_subject = models.CharField(max_length=400,blank=True, null=False,unique=True)
    sector = models.CharField(max_length=400,blank=True, null=False,unique=False)
    stakeholder = models.EmailField(blank=True, null=True)
    

    class Meta:
        ordering: ['search_subject']
        unique_together = ('search_subject', 'stakeholder')
        
    def __str__(self):
        return self.search_subject

class templateupload(models.Model):
    id = models.AutoField(primary_key = True)
    filepath = models.FileField(upload_to='uploads/') 
    purpose = models.CharField(max_length=400,blank=True, null=False,choices=templatepurpose)
    timestamp = models.DateTimeField(blank=True, null=False,default=timezone.now) 

    class Meta:
        ordering: ['timestamp']

    def __str__(self):
        return self.purpose


class relevance_metrics(models.Model):
    state = models.CharField(max_length=400,blank=False, null=False)
    metrics = models.FloatField(blank=False, null=False)
    run_date = models.DateField(blank=False, null=False,default=timezone.now)

    def __str__(self):
        return self.state
