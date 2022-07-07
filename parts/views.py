from django.shortcuts import render, get_object_or_404, redirect
from .models import Part, ExcelSheet, LastUpdate
from .forms import PartForm, QuantityForm
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)
import numpy as np
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.http import JsonResponse


def index(request):
    return render(request, 'index.html')

def listParts(request):
    search = request.GET.get('search')
    print(search)
    if search:
        parts = Part.objects.filter(trackable=True, slug__contains=search).order_by(Lower('title'))
    else:
        parts = Part.objects.filter(trackable=True).order_by(Lower('title'))
    paginator = Paginator(parts, 25) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'list-parts.html', {'page_obj': page_obj})
    

def addParts(request):
    form = PartForm()
    if request.method == 'POST':
        part_form = PartForm(request.POST)
        if part_form.is_valid():
            part_form.save()
            msg = 'part added'
            return render(request, 'add-parts.html', {'form':form, 'msg': msg})

    return render(request, 'add-parts.html', {'form':form})

def editPart(request, id):
    part = get_object_or_404(Part, id=id)
    form = PartForm(instance=part)
    if request.POST:
        filled_form = PartForm(request.POST, instance=part)
        filled_form.save()
        
        return redirect('parts:list-parts')
    return render(request, 'edit-part.html', {'form': form})

def quantity(request, id):

    part = get_object_or_404(Part, id=id)
    part = Part.objects.get(id=id)
    form = QuantityForm(instance=part)
    if request.POST:
        additional = request.POST.get('number')
        if additional:
            prev_quant = part.quantity
            if request.POST.get('add'):
                part.quantity = prev_quant + int(additional)
            else:
                part.quantity = prev_quant - int(additional)
            part.save(update_fields=['quantity'])
            return redirect('parts:list-parts')
        
        filled_form = QuantityForm(request.POST, instance=part)
        filled_form.save()
        return redirect('parts:list-parts')
    return render(request, 'quantity.html', {'form': form, 'part': part})

def excels(request):
    excels = ExcelSheet.objects.only('upload_date')
    update = request.POST.get('update-system')
    last_update = LastUpdate.objects.values()
    print(last_update)
    if update:

        last_2 = ExcelSheet.objects.values().order_by('-id')[:2]
        compare_last_2(last_2[1]['data'], last_2[0]['data'])
        # update date
        obj = LastUpdate.objects.get(id=1)
        obj.save()
        last_update = LastUpdate.objects.values()
        msg = "success"
        return render(request, 'excels.html', {'excels':excels, 'msg': msg, 'last_update': last_update})
            
    return render(request, 'excels.html', {'excels':excels, 'last_update': last_update})


def excelDetail(request, id):
    #excel = get_object_or_404(ExcelSheet, id=id)
    db_data = ExcelSheet.objects.filter(id=id).values()
    data = []
    for obj in db_data[0]['data']:
        for k, v in obj.items():
            if k == 'O1+':
                obj['O1'] = v
                obj.pop('O1+')
                data.append(obj)
    return render(request, 'excel-detail.html', {'data': data})


def upload(request):
    arr = []
    if request.method == 'POST':
        # get and clean dataframe
        file = request.FILES['file']
        df = pd.read_excel(file, sheet_name='Sheet 1',engine='openpyxl', usecols="A,B,D,E,F,G")
        df.rename(columns=df.iloc[2], inplace = True)
        df.columns = ['asset', 'position','D7', 'O1+', 'P1', 'P7']
        df = df.drop([0,1, 2])
        # iterate
        arr = []
        for row in df.iterrows():
            for obj in row:
                newObj = {}
                if isinstance(obj, int):
                    pass
                else:
                    for k, v in obj.items():
                        v = check_if_asset(k, v, arr)
                        if type(v) == float:
                            v = 0
                        newObj[k] = v
                    arr.append(newObj)
        # add totals of both to respective bike and sides    
        arr = split_left_right_remove_both(arr)
        new_upload = ExcelSheet(data=arr)
        new_upload.save()
    
    return render(request, 'upload.html', {'arr':arr})


#########HELPER FUNCS###########

def check_if_asset(k,v, arr):
    if k == 'asset':
        if type(v) != str:
            sibling= arr[-1]
            v = sibling.get('asset')
    return v


def split_left_right_remove_both(arr):
    to_be_removed = []
    for i,obj in enumerate(arr):
        position = obj.get('position')
        if position == 'Both/All':
            to_be_removed.append(i)
            asset = obj.get('asset')
            totals = {'D7': obj.get('D7'), 'O1+': obj.get('O1+'), 'P1': obj.get('P1'), 'P7': obj.get('P7')}
            for obj in arr:
                if asset == obj.get('asset'):
                    for k, v in totals.items():
                        prevTotal = obj.get(k)
                        newTotal = prevTotal + v
                        obj[k] = newTotal
    newArr = []
    for i, obj in enumerate(arr):
        if i in to_be_removed:
            pass
        else:
            newArr.append(obj)
    adjust_totals(newArr)
    return newArr

def adjust_totals(arr):
    first_upload_of_month = False
    bikes = ['D7', 'O1+', 'P1', 'P7']
    exceptions = ['Brake lever','Innertube' ]
    for obj in arr:
        for k, used in obj.items():
            if k in bikes:
                if used:
                    pos = obj['position'] 
                    asset = obj['asset']
                    if asset in exceptions:
                        pos = None
                    if pos:
                        qs = Part.objects.filter(in_excelsis=asset, slug__icontains=pos, tracking=True).values()
                    else: 
                        qs = Part.objects.filter(in_excelsis=asset, tracking=True).values()
                        
                    for part in qs:
                        
                        if k in part['bike_models']:
                            if first_upload_of_month:
                                part_obj = Part.objects.get(id=part['id'])
                                part_obj.starting_points[k] = used
                                part_obj.save(update_fields=['starting_points'])

                            else:
                                sp = part['starting_points']
                                part_obj = Part.objects.get(id=part['id'])
                                if not sp:
                                    pass
                                else:
                                    difference = used - sp[k]
                                    #print(f" starting point :{sp[k]} used: {used} prev quant:{quant} new quant: {difference}")
                                    quantity = part_obj.quantity
                                    updated_quantity = quantity - difference
                                    part_obj.quantity = updated_quantity
                                
                                part_obj.starting_points[k] = used
                                part_obj.save(update_fields=['quantity','starting_points'])
                                
                                
                            




            
#########AJAX#########
def ajax_view(request):
      
    search = request.GET.get('search')
    parts = Part.objects.values().filter(trackable=True, slug__contains=search).order_by('slug')
    res = []
    for i in parts:
        res.append(i)
    data = {
        "msg": "It worked!!",
    }
    return JsonResponse(res, safe=False)


def compare_last_2(prev, recent):
    bikes = ['D7', 'O1+', 'P1', 'P7']
    
    i = 0
    for obj in recent:
        for bike in bikes:
            recent_num = obj[bike]
            prev_num = prev[i][bike]
            if recent_num != prev_num:
                
                part = Part.objects.filter(in_excelsis=obj['asset'], slug__contains=obj['position'], tracking=True).values().first()
                if part:
                    if bike in part['bike_models']:
                        
                        total = recent_num - prev_num
                        print(f"{obj['asset']}{obj['position']}{bike} = {recent_num} / {prev_num} = {total}")
                        #Part.objects.filter(pk=part['id']).update(used_since_last_update=total)
                        
                    
                            
                    #print(f"{prev[i]['asset']}: {prev[i][k]}/({recent[i]['asset']}: {recent[i][k]}// difference = {v - prev_num}")
                    
        i += 1
