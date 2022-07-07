from tokenize import blank_re
from unicodedata import name
from django.db import models
from numpy import blackman


class Bike(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Part(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=100, blank=True)
    in_excelsis = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=0)
    threshold = models.IntegerField(default=0)
    part_no = models.IntegerField(null=True, blank=True)
    part_group = models.CharField(max_length=50, blank=True)
    item_no = models.IntegerField(null=True, blank=True)
    group_no = models.IntegerField(null=True, blank=True)
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    bike_models = models.JSONField(default=list)
    starting_points = models.JSONField(default=dict,blank=True, null=True)
    trackable = models.BooleanField(default=False)
    tracking = models.BooleanField(default=False) 

class ExcelSheet(models.Model):
    upload_date = models.DateTimeField(auto_now=True)
    data = models.JSONField(default=list)


class LastUpdate(models.Model):
    date = models.DateTimeField(auto_now=True)
    
