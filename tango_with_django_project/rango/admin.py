from django.contrib import admin
from rango.models import Category, Page


# Add in this class to customize the admin interface
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

# Update the registration to include this customized interface
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page)

# Register your models here.
