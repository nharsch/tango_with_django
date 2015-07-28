from django.contrib import admin
from rango.models import Category, Page, UserProfile
from rango.forms import PageBulkForm, PageFormSetBase

# Add in this class to customize the admin interface
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

# class PageAdmin(admin.ModelAdmin):
#     form = PageBulkAdminForm
#
#     list_display = ('title', 'category', 'url', 'views')
#
#     # build a list of objects to be created
#     insert_list = []
#     for cat in form.cleaned_data['category_choices']:
#        page = Page(
#        #fingers crossed that this works
#            category=cat,
#            title= form.title,
#            url=form.url,
#            views=form.views)
#     insert_list.append(page)
#
#     Page.objects.bulk_create(insert_list)
#
#     # def save_model(self, request, form, form, change):
#         # this info to be written on each new abject
#         # form.title = form.cleaned_data['title']
#         # form.url = form.cleaned_data['url']
#         # form.views = form.cleaned_data['views']
#
#         # for cat in form.cleaned_data['category_choices']:
#         #     # create new page formect
#         #     page = Page(
#         #         #fingers crossed that this works
#         #         category=cat,
#         #         title=form.title,
#         #         url=form.url,
#         #         views=form.views)
#         #     page.save()
#         #
#

# Update the registration to include this customized interface
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page)
admin.site.register(UserProfile)
# Register your models here.
