from django.contrib import admin
from .models import Part, Bike, ExcelSheet, LastUpdate

class PartAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', )
    ordering = ('title',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()




admin.site.register(Part, PartAdmin)

class BikeAdmin(admin.ModelAdmin):
    list_display = ('name','pk')
    search_fields = ('name',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()




admin.site.register(Bike, BikeAdmin)

class ExcelAdmin(admin.ModelAdmin):
    list_display = ('upload_date','pk')
    search_fields = ('upload_date',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()




admin.site.register(ExcelSheet, ExcelAdmin)

class LastUpdateAdmin(admin.ModelAdmin):
    list_display = ('pk',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()




admin.site.register(LastUpdate, LastUpdateAdmin)