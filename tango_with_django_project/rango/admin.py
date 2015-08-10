from django.conf.urls import patterns
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from rango.models import Category, Page, UserProfile
from rango.forms import PageBulkForm 

# Add in this class to customize the admin interface
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

# class PageInline(admin.TabularInline):
#     model = Page
#     form = PageInlineForm
#

class PageAdmin(admin.ModelAdmin):
    # update urls
    # inlines = [PageInline]

    change_list_template = 'admin/custom_change_list.html'

    def get_urls(self):
        urls = super(PageAdmin, self).get_urls()
        print "ursl are"
        my_urls = patterns('',
                           (r'bulk_add_pages/$', self.admin_site.admin_view(self.bulk_add_pages))
                           )
        print my_urls + urls
        return my_urls + urls
    # add a new view here
    def bulk_add_pages(self, request):
        '''
        create several pages from a submitted list
        '''
        if request.method == 'POST':
            form = PageBulkForm(request.POST)
            # bind the form?
            if form.is_valid():
            # Loop through categories, create bulk insert list
                insert_list = []
                for cat in request.POST.getlist('category_choices'):
                    page = Page(
                        category=Category.objects.get(pk=int(cat)),
                        title=request.POST['title'],
                        url=request.POST['url'],
                        views=request.POST['views'],) 
                    insert_list.append(page)
                # bulk create objects
                Page.objects.bulk_create(insert_list)
                return HttpResponseRedirect('/admin/rango/page/')
            else:
                return render(request, 'admin/add_pages.html', {'form':form})
        else:
            form = PageBulkForm
            context_dict = {'form':form}
            return render(request, 'admin/add_pages.html', context_dict)

# Update the registration to include this customized interface
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
# Register your models here.
