from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Max
from django import forms
from .models import *
from datetime import datetime 

def index(request):

    if request.method == 'GET':
        auctioned = AuctionListing.objects.all()
        auction_data = []

        # preparing context to be forwarded to the frontend
        for obj in auctioned:
            if obj.is_active :
                    
                auc = {}
                auc["id"] = obj.id
                auc['user'] = obj.user.username  
                auc["name"] = obj.name
                auc["price"] = obj.price
                auc["date"] = obj.date
                auc["categery"] = obj.categery.name
                auc["description"] = obj.description

                try :
                    p = Pictures.objects.get(item = obj)
                    auc["image"] = p.picture.url

                except Pictures.DoesNotExist :
                    auc["image"] = "media/images/placeholder.jpeg"
          
                auction_data.append(auc)
            
        return render(request, "auctions/index.html", {"items" : auction_data })    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        
        else:   
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")
    
@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def test(request):
    return render( request,"auctions/test.html")

class CreateListing(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs= {'placeholder' : 'Title'}))
    categery = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select,
        required=True
    )
    image = forms.ImageField(required=False)
    description = forms.CharField(widget = forms.Textarea(attrs= {'width' : '80%','text-aligh' : 'center', 'placeholder': 'Description'} ))
    starting_bid = forms.IntegerField(widget=forms.NumberInput(attrs= { 'placeholder' : 'Starting bid' }))    

@login_required
def create_listing(request):
    if request.method == 'GET':

        form = CreateListing()
        return render(request, 'auctions/create_listing.html', context= { 'form' : form })
    view_form = CreateListing(request.POST, request.FILES)

    if not view_form.is_valid():
        return render(request, 'auctions/create_listing.html', context= { 'form' : view_form })

    listing = AuctionListing(
        user = request.user,
        name = view_form.cleaned_data["title"],
        price = view_form.cleaned_data['starting_bid'],
        categery = view_form.cleaned_data['categery'],
        description = view_form.cleaned_data['description']  
    )
    listing.save()
    init_bid = Bid(user = request.user, item = listing, bid_price = view_form.cleaned_data['starting_bid'])
    init_bid.save ()

    image = view_form.cleaned_data.get('image')
    if image:
        product_picture = Pictures(item = listing, picture = image)
        product_picture.save()
    return render(request, "auctions/create_listing.html", context = {'form' : view_form, 'success_message' : "Item added for auction successfully" })

# this is the view for listing_page.html
def listing_page(request, item_id):
    
    context = {}   
    
    obj = AuctionListing.objects.get(id=item_id)    

    highest_bid = Bid.objects.filter(item = obj).aggregate(Max("bid_price"))["bid_price__max"]
    if not highest_bid :
        highest_bid = obj.price

    try :
        highest_bidder = Bid.objects.get(item = obj, bid_price = highest_bid).user
    
    except Bid.DoesNotExist :
        highest_bidder = obj.user
    if not obj.is_active :
    
        # if : this user is the winner user, display the info for this
        if request.user == highest_bidder : 
            message = f" You have won the auction for {obj.name} for ${highest_bid}"
            context["win_message"] = message
            return render(request, "auctions/listing_page.html", context = context)
        
        inactive_message = f"This listing, {obj.name} is no more active"

        context["listing_inactive"] = inactive_message
        return render(requEst, "auctions/listing_page.html", context = context)

    try:
        obj_image = Pictures.objects.get(item=obj) 
        obj_image_url = obj_image.picture.url
    except Pictures.DoesNotExist:
        obj_image_url = "media/images/placeholder.jpeg"
    
    auc = {
        'creator_id' : obj.user.id,
        'id': obj.id,
        'title': obj.name,
        'creator': obj.user.username,
        'price': obj.price,
        'date': str(obj.date),
        'categery': obj.categery.name,
        'description': obj.description,
        'image': obj_image_url,
        "highest_bid" : highest_bid
    }

    context["listing"] = auc
    w_list = request.session.get("watchlist", [])
    
    check = False
    context["in_watchlist"] = check 

    # Checking if item is in watch list 
    if w_list:
        for w in w_list:
            if w["id"] == int(item_id):
                check = True
                context["in_watchlist"] = check
                break

    # creating comments list to pass in the get request 
    all_comments = Comment.objects.filter(item = obj)
    comment_list = []

    for com in all_comments :
        c = {"user" : com.user.username, "content" : com.text}
        comment_list.append(c)
    context["comments"] = comment_list

    if request.method == "POST": 
        # item is in the watch list
        if not request.user.is_authenticated :
            context["error"] = "You are not Logged In"
            return render(request, "auctions/listing_page.html", context=context)
        
        #comment check
        comment = request.POST.get("comment")
        if comment :
            new_comment = Comment(user = request.user, text = comment, item = obj)
            new_comment.save()
            return redirect("listing_page", item_id = obj.id)
            # return render(request, "auctions/listing_page.html", context=context)
            
        # bid check
        bid = (request.POST.get("bid_amount"))
        if bid :
            bid = float(bid)
            if bid <= highest_bid or bid < float(obj.price):
                context["error"] = "please make sure that your bid is greater than the current highest bid."
                return render(request, "auctions/listing_page.html", context=context)

            auc["highest_bid"] = str(bid)
            context["listing"] = auc
            new_bid = Bid(user = request.user, item = obj, bid_price = bid)
            new_bid.save()
            return render(request, "auctions/listing_page.html", context=context)

        # auction closing check
        close_auction = request.POST.get("close_auction")
        
        # this option is only for the creator of this auction
        if close_auction:
            winner_user = Bid.objects.get(item = obj, bid_price = highest_bid).user.username
            context = {}

            closing_details = { 
                "item_name" : auc["title"],
                "winner_user" : winner_user,
                "initial_price" : auc["price"],
                "sold_price" : highest_bid
            }
            obj.is_active = False
            obj.save()

            context["closing_details"] = closing_details
            return render(request, "auctions/listing_page.html", context = context)
        watch_list_check = request.POST.get("wl")

        # check for action related to the watch list
        if check:
            w_list.remove(auc)
        else: 
            w_list.append(auc)
        
        request.session["watchlist"] = w_list
        return redirect("watch_list")

    return render(request, "auctions/listing_page.html", context=context)

@login_required 
def watch_list(request):
    if not request.user.is_authenticated :
        return render(request, "auctions/forOfor.html")

    if request.method == "POST":
        item_id = int(request.POST.get("to_remove"))
        print("item to remove :", item_id)
        watchlist = request.session.get("watchlist", [])
        
        updated_watchlist = [listing for listing in watchlist if listing["id"] != item_id]
        request.session["watchlist"] = updated_watchlist
        
        return render(request, "auctions/watch_list.html")
    return render(request, "auctions/watch_list.html")

def category_page(request) :

    context = {}
    all_categories = []

    for cat in Category.objects.all():
        all_categories.append(cat.name)

    context["all_categories"] = all_categories

    
    category = request.GET.get("category")
    print("Category : " ,category)
    if not category :

        return render(request, "auctions/category_page.html", context = context)
    this_category = Category.objects.get(name = category)
    category_objects = AuctionListing.objects.filter(categery = this_category)

    category_listings = []
    for obj in category_objects:
        if obj.is_active :
                
            auc = {}
            auc["id"] = obj.id
            auc['user'] = obj.user.username  
            auc["name"] = obj.name
            auc["price"] = obj.price
            auc["date"] = obj.date
            auc["categery"] = obj.categery.name
            auc["description"] = obj.description

            try :
                p = Pictures.objects.get(item = obj)
                auc["image"] = p.picture.url

            except Pictures.DoesNotExist :
                auc["image"] = "media/images/placeholder.jpeg"

            category_listings.append(auc)
    context["category_listings"] = category_listings
    return render(request, "auctions/category_page.html", context = context)
    