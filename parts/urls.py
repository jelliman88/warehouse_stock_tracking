from django.urls import path
from . import views


app_name = 'parts'
urlpatterns = [
    path('', views.index, name='index'), 
    path('list-parts', views.listParts, name='list-parts'),
    path('edit-part/<int:id>', views.editPart, name='edit-part'),
    path('quantity/<int:id>', views.quantity, name='quantity'),
    path('add-parts', views.addParts, name='add-parts'),
    path('upload', views.upload, name='upload'),
    path('excels', views.excels, name='excels'),
    path('excel-detail/<int:id>', views.excelDetail, name='excel-detail'),
    path('ajax/', views.ajax_view, name="ajax"),
]