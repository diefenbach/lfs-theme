"""URLs of the theme; a shop includes them under ``theme/``."""

from django.urls import path

from lfs_theme import views

urlpatterns = [
    path("mobile-menu/", views.mobile_menu, name="lfs_theme_mobile_menu"),
]
