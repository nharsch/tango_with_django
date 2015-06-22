from django.http import HttpResponse
from django.shortcuts import render
from rango.models import Category, Page

def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only = or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5] # returns just the first five
    context_dict = {'categories': category_list}
    
    # Render the response and sent it back!
    return render(request, 'rango/index.html', context_dict)

# Return a rendered response to send to the client. 
# We make use of the shortcut function to make our lives easier. 
# Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context_dict)

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

        # Adds our results list to  the template context under name pages. 
        conext_dict['category'] = category


    except Category.DoesNotExist:
        # We get here if we didn't find the specified category
        # Don't do anything = the template displays the "no category" message for us.
        pass

    return render(request, 'rango/category.html', context_dict)
