from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.db.models import Count
from .models import *
import bcrypt
import time
import datetime
# Create your views here.

def index(request):    
    today = datetime.date.today().strftime("%Y-%m-%d")
    request.session['today'] = today

    if 'id' in request.session:
        return redirect('/books')
    else:
        context = {
            'today': today
        }
        return render(request, 'book_reviewer/index.html', context)


def register(request):
    if request.method == "POST":
            print request.POST

            errors = User.objects.registration_validation(request.POST)
            print errors
            if errors[0] == True:
                for tag, error in errors[1].iteritems():
                    messages.error(request, error, extra_tags=tag)
                return redirect('/')
            else:
                user_id = errors[1]
                request.session['id'] = str(user_id)
                return redirect('/books')

    else:
        messages.error(request, "Oops, something went wrong")
        return redirect("/")


def login(request):
    if 'id' in request.session:
        return redirect("/")
    if request.method == "POST":
        errors = User.objects.login_validation(request.POST)
        if len(errors) > 0:
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/')

        else:
            logged_user = User.objects.get(email=request.POST['email'])
            request.session['id'] = logged_user.id
            return redirect('/books')
    else:
        messages.error(request,"Oops, something went wrong")
        return redirect("/")


def home(request):
    if 'id' not in request.session:
        return redirect("/")
    
    user_info = User.objects.get(id=request.session['id'])
    allreviews = Review.objects.all_reviews()

    errors = []
    print allreviews
    if allreviews[0]== False:
        messages.error(request, allreviews[1])
        context = {'user': user_info}
        return render(request, 'book_reviewer/home.html', context)

    recent_reviews = Review.objects.latest_three()
    books = allreviews[1].values('book__title', 'book_id').annotate(rvws=Count('review'))
    context = {
        'user': user_info,
        'top3': recent_reviews,
        'reviews': books,
    }
    print context
    return render(request,'book_reviewer/home.html',context)


def add(request):
    if 'id' not in request.session:
        return redirect("/")

    try:
        author_list = Author.objects.all()
    except:
        messages.error(request, "Error retriving authors")
        return redirect("/books/add")

    context = {'authors': author_list}

    return render(request, 'book_reviewer/add.html', context)


def addbook(request):
    if 'id' not in request.session:
        return redirect("/")

    if request.method == "POST":
        if 'author_pick' in request.POST:
            if len(request.POST['author_pick']) > 0:
                new_book = Book.objects.create_book(request.POST['title'],request.POST['author_pick'])

        if 'author_add' in request.POST:
            new_author = Author.objects.create_author(request.POST['author_add'])
            if new_author[0] == False:
                messages.error(request, new_author[1])
                return redirect("/books/add")
            else:
                new_book = Book.objects.create_book(request.POST['title'], new_author[1])

        if new_book[0] == False:
            messages.error(request, new_book[1])
            return redirect("/books/add")

        if len(request.POST['review']) > 5:
            new_review = Review.objects.create_review(request.POST['review'], request.POST['rating'], new_book[1], request.session['id'])
            
            if new_review[0] == False: 
                messages.error(request, new_review[1])
                return redirect("/books/add")
            else:
                book_id = new_review[1]
                return redirect("/books/" + str(book_id))
        else: 
            messages.error(request, 'Reviews must be longer than 5 characters long')
            return redirect("/books/add")

    else:
        messages.error(request, "Oops something went wrong")
        return redirect("/books/add")

def show(request, book_id):
    if 'id' not in request.session:
        return redirect("/")
    try:
        select_book = Book.objects.get(id=book_id)
    except:
        messages.error(request, "Couldn't find that book")
        return redirect("/books")

    try:
        select_reviews = Review.objects.filter(book=book_id)
    except:
        messages.error(request, "No reviews yet for this book, but you can add one!")
        return redirect("/books")
    
    user_info = User.objects.get(id=request.session['id'])
    context = {
        'user': user_info,
        'book': select_book,
        'reviews': select_reviews,
    }
    print context
    return render(request, 'book_reviewer/show.html', context)

def delete(request,book_id,review_id):
    if 'id' not in request.session:
        return redirect("/")

    delete_rvw = Review.objects.delete_review(review_id)

    return redirect("/books/" + str(book_id))

def addreview(request, book_id):
    if 'id' not in request.session:
        return redirect("/")
    
    if request.method == 'POST':
        if len(request.POST['review']) < 5:
            messages.error(request, 'Reviews must be longer than 5 characters long')
            return redirect("/books/" + str(book_id))

        else:
            new_review = Review.objects.create_review(request.POST['review'], request.POST['rating'], book_id, request.session['id'])

            if new_review[0] == False:
                messages.error(request, new_review[1])
                return redirect("/books/" + str(book_id))
            
            book_id = new_review[1]
            return redirect("/books/" + str(book_id))

    messages.error(request, "Oops something went wrong")
    return redirect("/books/" + str(book_id))

def users(request, user_id):
    if 'id' not in request.session:
        return redirect("/")
    user_info = User.objects.get(id=request.session['id'])
    reviews = Review.objects.filter(reviewer=user_info)
    count_r = len(reviews)

    context = {
        'user': user_info,
        'reviews': reviews,
        'count': count_r,
    }
    return render(request, 'book_reviewer/user.html', context)


def logout(request):
    request.session.clear()
    return redirect("/")

