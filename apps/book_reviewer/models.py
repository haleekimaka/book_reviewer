from __future__ import unicode_literals

from django.db import models
import re
import bcrypt
import time
import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
BDAY_REGEX = re.compile(r'^[0-9]{4}[-][0-9]{2}[-][0-9]{2}$')

def num_check(name):
    #checks if the entered password meets our requirements
    has_num = False

    for char in name:
        if char.isdigit():
            has_num = True

    return has_num


def has_upper_num(password):
    #checks if the entered password meets our requirements
    has_upper = False
    has_num = False
    check = False

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.isdigit():
            has_num = True

    if has_num and has_upper:
        check = True

    return check


# Create your models here.

class UserManager(models.Manager):
    def registration_validation(self, postData):
        errors = {}
        for thing in postData:
            if len(postData[thing]) < 1:
                errors['submit'] = "All fields required"
                return (True, errors)
            if len(postData[thing]) > 255:
                errors[thing] = "Exceeded field length"
                return (True, errors)

        if len(postData['name']) < 2:
            errors['name'] = "Name should be more than 2 characters"

        if len(postData['alias']) < 2:
            errors['alias'] = "Alias should be more than 2 characters"

        if num_check(postData['name']):
           errors['name'] = "Names must only contain letters"

        if not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "Invalid email address"

        if len(postData['pwd']) < 8:
            errors["pwd"] = "Password must be at least 8 characters"

        if not has_upper_num(postData['pwd']):
            errors["pwd"] = "Password must contain at least one uppercase letter and one number"

        if postData['pwd_c'] != postData['pwd']:
            errors["pwd_c"] = "Passwords must match"

        if not BDAY_REGEX.match(postData['bday']):
            errors["bday"] = "Birthdate must be in format yyyy-mm-dd"

        today = datetime.datetime.now()

        try:
            submit = datetime.datetime.strptime(postData['bday'], "%Y-%m-%d")

            if submit > today:
                errors["bday"] = "Birthdate must be before today"
        except:
            errors["bday"] = "Birthdate format incorrect"

        records = User.objects.filter(email=postData['email'])

        if len(records) > 0:
            errors["email"] = "Account already exists for this email"

        records = User.objects.filter(alias=postData['alias'])

        if len(records) > 0:
            errors["email"] = "Account already exists for this alias"

        if len(errors) > 0:
            return (True, errors)

        else:
            name_format = postData['name'].title()
            new_pwd = bcrypt.hashpw(postData['pwd'].encode(), bcrypt.gensalt())
            bday = datetime.datetime.strptime(postData['bday'], '%Y-%m-%d')

            new_user = User.objects.create(
                name=name_format, alias=postData['alias'], email=postData['email'], password=new_pwd, birthdate=bday)
            user_id = new_user.id
            return (False, user_id)

    def login_validation(self, postData):
        errors = {}
        for thing in postData:
            if len(postData[thing]) < 1:
                errors[thing] = "All fields required"
                return errors
            if len(postData[thing]) > 255:
                errors[thing] = "Exceeded field length"
                return errors

        records = User.objects.filter(email=postData['email'])

        if len(records) > 0:
            pwd = records[0].password
            check = bcrypt.checkpw(postData['pwd'].encode(), pwd.encode())
            if check:
                return errors
            else:
                errors["pwd"] = "Incorrect user/password"
                return errors
        else:
            errors["email"] = "Account doesn't exist for this email. Please register."
            return errors


class AuthorManager(models.Manager):
    def create_author(self, author):
        author = author.title()
        all_authors = Author.objects.all()
        if author in all_authors:
            return (False, "Author already in our system")
        else:
            new_author = Author.objects.create(name=author)
            new_author_name = new_author.name
            return (True, new_author_name)

class BookManager(models.Manager):
    def create_book(self, title_book, author):
        try:
            auth = Author.objects.get(name=author)
        except: 
            auth = False

        title_book = title_book.title()
        book_list = Book.objects.filter()
        
        if len(book_list) > 0:
            for item in book_list:
                if item.title == title_book:
                    return (False, "Title already exists in our library")
            
            if auth != False:
                new_book = Book.objects.create(title=title_book, author=auth)
                new_book_id = new_book.id
                return(True, new_book_id)


class ReviewManager(models.Manager):
    def review_check(self, author):
        pass

    def latest_three(self):
        top_three = []
        review_info = Review.objects.all().order_by("created_at")
        count = len(review_info)
        print "Review Info Query (top3): {}".format(review_info)
        if count > 3:
            limit = 3
        else:
            limit = count
        count = 0
        while count < limit:
            for review in review_info:
                top_three.append(review)
                count +=1

        return top_three

    def all_reviews(request):
        try:
            get = Review.objects.all()
        except:
            return (False, "No reviews yet")
        
        return (True, get)           
            
    def create_review(request, review_text, rating, book_id, user_id):
        try:
            booky = Book.objects.get(id=book_id)
        except:
            return(False, "Couldn't find an book match")

        stars = ['1','2','3','4','5']

        if rating not in stars:
            return(False, "Rating values must be between 1-5")
        
        user = User.objects.get(id=user_id)

        try:
            new_review = Review.objects.create(review=review_text, stars=rating, reviewer=user, book=booky)
        except:
            return(False, "Error processing review")

        return(True, book_id)

    def delete_review(request, review_id):
        try:
            get_review = Review.objects.get(id=review_id)
        except:
            return(False, "Couldn't find that review")

        get_review.delete()

        return(True, "Success")

class User(models.Model):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    birthdate = models.DateField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __repr__(self):
        return "<User object: id='{}' name='{}' alias='{}' email='{}' birthdate='{}' created='{}'>".format(self.id, self.name, self.alias, self.email, self.birthdate, self.created_at)


class Author(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AuthorManager()

    def __repr__(self):
        return "<Author object: id='{}' name='{}' created='{}'>".format(self.id, self.name, self.created_at)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, related_name="books")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BookManager()

    def __repr__(self):
        return "<Book object: id='{}' title='{}' author='{}' created='{}'>".format(self.id, self.title, self.author, self.created_at)


class Review(models.Model):
    review = models.CharField(max_length=255)
    stars = models.CharField(max_length=255)
    reviewer = models.ForeignKey(User, related_name="reviewers")
    book = models.ForeignKey(Book, related_name="reviews")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects=ReviewManager()

    def __repr__(self):
        return "<Review object: id='{}' review='{}' stars='{}' reviewer='{}' book='{}' created='{}'>".format(self.id, self.review, self.stars, self.reviewer, self.book, self.created_at)
