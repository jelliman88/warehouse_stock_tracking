from django.forms import ModelForm
from .models import Part


class PartForm(ModelForm):
   
    class Meta:
        model = Part
        exclude = ('part_no','group_no','starting_points')

class QuantityForm(ModelForm):
   
    class Meta:
        model = Part
        fields = ['quantity',]
        
    
