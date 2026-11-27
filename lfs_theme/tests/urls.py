"""URLs for the theme's tests."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

urlpatterns = [
    re_path(r"", include("lfs.core.urls")),
    path("theme/", include("lfs_theme.urls")),
    re_path(r"^manage/", include("lfs.manage.urls")),
    path("paypal/", include("lfs_paypal.urls")),
    re_path(r"^reviews/", include("reviews.urls")),
    path("captcha/", include("captcha.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
