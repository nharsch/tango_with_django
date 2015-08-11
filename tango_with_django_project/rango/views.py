from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.shortcuts import render, redirect

from rango.models import Category, Page, UserProfile, User
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.forms import PageBulkForm, PageFormSet, ManifestInitForm, FullPageForm
from rango.bing_search import run_query

def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only = or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list,
                    'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...increment value of the cookie by 1
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True

    else:
        # Cookie last_visit doesn't exist, so create it to the current dat/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request, 'rango/index.html', context_dict)

    return response

def about(request):
    return render(request, 'rango/about.html')

def category(request, category_name_slug):
    # Create a context dict
    context_dict = {}

    if request.method == 'POST':
        result_list = []
        query = request.POST.get('query').strip()
        if query:
            result_list = run_query(query)
        print result_list
        context_dict.update({'result_list':result_list})
        context_dict.update({'query': query})

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        pass
    
    if not context_dict.get('query'):
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)

@login_required
def like_category(request):
    if request.method == "GET":
        cat_id = request.GET.get('category_id')
    
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    # return just number of likes
    return HttpResponse(likes)

def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return HttpResquest(request, {'result_list': result_list})

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        page_id = request.GET.get('page_id')
        if page_id:
            try:
                page = Page.objects.get(id=page_id)
                url = page.url
                page.views += 1
                page.save()
            except:
                pass
    return redirect(url)


def get_category_list(max_results=0, starts_with=''):
    '''helper function that returns matches as a list'''
    cat_list = []
    if starts_with:
        # find the categories that start with string
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        # just get the the first n results
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list



def suggest_category(request):

    if request.method == 'GET':
        starts_with = request.GET.get('suggestion')
    
    # use helper function to get top 8 results
    cat_list = get_category_list(8, starts_with=starts_with)

    # populate them to reused cats html
    return render(request, 'rango/cats.html', {'cats': cat_list })


def register_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        profile = form.save(commit=False)
        profile.user = request.user
        profile.save()
        return HttpResponseRedirect("/rango/users/") 
    form = UserProfileForm
    return render(request, 'rango/profile_registration.html', {"form":form})

def list_users(request):
    # get all the users
    user_list = UserProfile.objects.all()

    return render(request, 'rango/users.html', {'users':user_list})

@login_required
def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category with a
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplie form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to endet details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form':form})

@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)

            pages = Page.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages

    return render(request, 'rango/page_list.html', context_dict)

@login_required
def add_page(request, category_name_slug):
    # set the category
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.category = cat
            page.views = 0
            page.save()
            # probably better to use a redirect here
            return HttpResponseRedirect( '/rango/category/{}'.format(category_name_slug))
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category':cat}
    return render(request, 'rango/add_page.html', context_dict)

def add_pages(request):
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
            print "form is bound: ", form.is_bound
            print form.errors if form.errors else "where are the errors??"
            return render(request, 'rango/add_pages.html', {'form':form})
    else:
        form = PageBulkForm
        context_dict = {'form':form}
        return render(request, 'rango/add_pages.html', context_dict)

def manifest_add(request):
    '''
    take one input, create form with cats populated
    '''
    if request.method == 'GET':
        return render(request, 'rango/manifest_add.html', {'manifest_init_form':ManifestInitForm})
    else:

        incoming_title = request.POST.get('title')
        cats = Category.objects.all()
        # create the formset dynamically
        PageFormSet = modelformset_factory(Page,
                                           fields=('category', 'title', 'url'), 
                                           extra=len(cats),
                                           )

        formset = PageFormSet(initial=[
                             {'title':'test_input'}],
                             queryset=Page.objects.none(),
                             )

        for form in formset.forms:
            form.initial['title'] = incoming_title

        return render(request, 'rango/manifest_add.html', {'formset':formset})


def bulk_page_form_add(request):
    '''
    take list of assets, create render page with formset for each asset 
    '''
    job_list = [
        {'category':'', 'title':'test_1','url': 'www.url1.com'},
        {'title':'test_2','url': 'www.url2.com'}
    ]

    if request.method == 'GET':
    #     # TODO: make this CSV import
    #     return render(request, 'rango/manifest_add.html', {'manifest_init_form':ManifestInitForm})
    #
    # else:
    # create the formset dynamically
        formset = PageFormSet(
                             initial=job_list
                             )
        return render(request, 'rango/bulk_page_add.html', {'formset':formset})

    if request.method == 'POST':
        formset = PageFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                print form
                form.save()
            return HTTPRedirect('/admin/rango/categories')

        else:
            return render(request, 'rango/bulk_page_add.html', {'formset':formset})



@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


