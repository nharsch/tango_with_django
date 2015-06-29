from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

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

    try:
        # Can we find a category name slaug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name
        context_dict['pages'] = pages

        # Adds our results list to  the template context under name pages. 
        context_dict['category'] = category
        context_dict['category_name_slug'] = category.slug

    except Category.DoesNotExist:
        # We get here if we didn't find the specified category
        # Don't do anything = the template displays the "no category" message for us.
        pass

    return render(request, 'rango/category.html', context_dict)

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
def add_page(request, category_name_slug):
    # set the category
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page.category = cat
            page.views = 0
            page.save()
            # probably better to use a redirect here
            return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category':cat}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    # A boolean value for telling the template whether the registration was successful 
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's an HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hased, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False/
            # This delays saving the model until we're ready to avoid integridty problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user probide a profil picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form of forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, se we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
                  'rango/register.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'registred': registered})

def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provide by the under.
        # This information is obtained from the login form.
        username = request.POST.get('username')
        password = request.POST.get('password')

    # Use Django's machinery to attempt to see if the username/password 
    # combo is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)


        # If we have a User object, the details are correct.
        # If None, no user was found
        if user:
            # Is the current user active?
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was userd - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login request is not a HTTP POST, so display the login form.
            # This scenario would most likely be a HTTP GET.
            print "Invalid login details: {0}, {1}".format(username, password)
            return render(request, 'rango/login.html', {'error_msg':'Invalid login details supplied'})
    else:
        # No context vars to pass to the template
        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')
