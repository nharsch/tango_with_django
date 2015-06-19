from django.http import HttpResponse
from django.shortcuts import render
from rango.models import Category

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
