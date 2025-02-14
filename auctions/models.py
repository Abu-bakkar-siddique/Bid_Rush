from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category (models.Model):
    name = models.CharField(max_length=24)   
    def __str__(self):
        return self.name 

class AuctionListing (models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'user_auctions')
    name = models.CharField(max_length=100)
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add= True)
    category = models.ForeignKey(Category, on_delete= models.CASCADE, related_name = "category_listing")
    description = models.TextField(max_length = 1000)
    is_active = is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name 

class Pictures (models.Model):
    picture = models.ImageField(upload_to= r"images", default="images/placeholder.jpeg", blank = True)
    item = models.ForeignKey(AuctionListing, on_delete= models.CASCADE, related_name= "listing_pictures")
    def __str__(self):
        return self.item.name
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name= "user_comments")
    text = models.TextField(max_length = 500)
    item = models.ForeignKey(AuctionListing, on_delete= models.CASCADE, related_name = "listing_comments")

    def __str__ (self):
        return self.text

class Bid (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "user_bids")
    item = models.ForeignKey(AuctionListing, on_delete= models.CASCADE, related_name= "listing_bids")
    bid_price = models.FloatField()
    date = models.DateTimeField(auto_now_add= True)
 
    def __str__ (self):
        return str(self.bid_price)
    