from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("test", views.test, name = "test"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name = "create_listing"),
    path("watch_list", views.watch_list, name = "watch_list"),
    path("category_page", views.category_page, name = "category_page"),
    path("<str:item_id>", views.listing_page, name = "listing_page")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)