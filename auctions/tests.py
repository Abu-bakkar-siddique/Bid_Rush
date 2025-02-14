from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Category, AuctionListing, Pictures, Comment, Bid
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class AuctionModelsTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(name='Electronics')
        
        # Create test auction listing
        self.auction = AuctionListing.objects.create(
            user=self.user,
            name='Test Laptop',
            price=500.00,
            category=self.category,
            description='A brand new test laptop'
        )
        
        # Create test image
        self.picture = Pictures.objects.create(
            item=self.auction,
            picture=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        )
        
        # Create test comment
        self.comment = Comment.objects.create(
            user=self.user,
            text='This is a test comment',
            item=self.auction
        )
        
        # Create test bid
        self.bid = Bid.objects.create(
            user=self.user,
            item=self.auction,
            bid_price=550.00
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(str(self.category), 'Electronics')
    
    def test_auction_listing_creation(self):
        self.assertEqual(self.auction.name, 'Test Laptop')
        self.assertEqual(self.auction.price, 500.00)
        self.assertEqual(self.auction.user, self.user)
        self.assertEqual(self.auction.category, self.category)
        self.assertTrue(self.auction.is_active)
        self.assertIsNotNone(self.auction.date)
        self.assertEqual(str(self.auction), 'Test Laptop')
    
    def test_pictures_creation(self):
        self.assertEqual(self.picture.item, self.auction)
        self.assertIsNotNone(self.picture.picture)
        self.assertEqual(str(self.picture), 'Test Laptop')
    
    def test_comment_creation(self):
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.text, 'This is a test comment')
        self.assertEqual(self.comment.item, self.auction)
        self.assertEqual(str(self.comment), 'This is a test comment')
    
    def test_bid_creation(self):
        self.assertEqual(self.bid.user, self.user)
        self.assertEqual(self.bid.item, self.auction)
        self.assertEqual(self.bid.bid_price, 550.00)
        self.assertIsNotNone(self.bid.date)
        self.assertEqual(str(self.bid), '550.0')
    
    def test_relationships(self):
        # Test that relationships are working
        self.assertEqual(self.user.user_auctions.count(), 1)
        self.assertEqual(self.category.category_listing.count(), 1)
        self.assertEqual(self.auction.listing_pictures.count(), 1)
        self.assertEqual(self.auction.listing_comments.count(), 1)
        self.assertEqual(self.auction.listing_bids.count(), 1)
        self.assertEqual(self.user.user_auctions.count(), 1)
        self.assertEqual(self.user.user_comments.count(), 1)
        self.assertEqual(self.user.user_bids.count(), 1)