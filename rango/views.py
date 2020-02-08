from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from django.shortcuts import redirect
from django.shortcuts import redirect
from django.urls import reverse

def index(request) :
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine.
    # '-' in likes denotes descending order
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = pages_list

    return render(request, 'rango/index.html', context=context_dict)

def show_category(request, category_name_slug) :
    # Create a context dictionary which we can pass
    # to the template rendering engine.
    context_dict = {}
    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # The .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
        # the database to the context dictionary.
        # We'll use this in the template to verify
        context_dict['category'] = category

    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
    
    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context=context_dict)

def about(request) :
    return render(request, 'rango/about.html')

def add_category(request) :
    form = CategoryForm()
    # A HTTP POST?
    if request.method == 'POST' :
        form = CategoryForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid() :
            # Save the new category to the database.
            # print(form)
            new_cat = form.save(commit=True)  
            print(new_cat, new_cat.slug)
            # redirect the user back to the index view.
            return redirect('/rango/')
        else :
            # errors
            print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug) :
    try:
        category = Category.objects.get(slug=category_name_slug)
        print(category)
    except Category.DoesNotExist:
        category = None
    
    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect('/rango/')
        
    form = PageForm()

    if request == 'POST' :
        form = PageForm(request.POST)
        if form.is_valid() :
            if category :
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                # reverse looks up URL names in urls.py
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
        else :
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

