"""URLs of a shop that does not include the theme's URLs, for the mobile menu's fallback."""

from django.urls import include, re_path

urlpatterns = [re_path(r"", include("lfs.core.urls"))]
