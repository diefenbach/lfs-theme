"""Settings for the theme's tests: the core, its required add-ons, and this theme; no optional add-ons."""
from django.utils.translation import gettext_lazy as _

SECRET_KEY = "test-only"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
SITE_ID = 1
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
INSTALLED_APPS = [
    "lfs_theme", "crispy_forms", "crispy_bootstrap5", "compressor",
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions",
    "django.contrib.messages", "django.contrib.staticfiles", "django.contrib.sites", "django.contrib.flatpages",
    "django.contrib.redirects", "django.contrib.sitemaps", "django_countries",
    "reviews", "portlets",
    "lfs.addresses", "lfs.caching", "lfs.cart", "lfs.catalog", "lfs.checkout", "lfs.core", "lfs.criteria",
    "lfs.customer", "lfs.customer_tax", "lfs.discounts", "lfs.export", "lfs.gross_price", "lfs.mail", "lfs.manage",
    "lfs.marketing", "lfs.manufacturer", "lfs.net_price", "lfs.order", "lfs.page", "lfs.payment", "lfs.portlet",
    "lfs.search", "lfs.shipping", "lfs.supplier", "lfs.tax", "lfs.tests", "lfs.utils", "lfs.voucher",
    "lfs_contact", "lfs_order_numbers", "localflavor", "postal", "lfs_paypal", "captcha",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "lfs_theme.tests.urls"
STATIC_URL = "static/"
STATICFILES_FINDERS = ("django.contrib.staticfiles.finders.AppDirectoriesFinder", "compressor.finders.CompressorFinder")
COMPRESS_ENABLED = False
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug", "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages",
        "lfs.core.context_processors.main"]},
}]
AUTHENTICATION_BACKENDS = ["lfs.customer.auth.EmailBackend", "django.contrib.auth.backends.ModelBackend"]
USE_TZ = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en"
SESSION_SERIALIZER = "lfs.core.pickle_serializer.PickleSerializer"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
LFS_CURRENCY = "EUR"
LFS_AFTER_ADD_TO_CART = "lfs_added_to_cart"
LFS_RECENT_PRODUCTS_LIMIT = 5
LFS_ORDER_NUMBER_GENERATOR = "lfs_order_numbers.models.OrderNumberGenerator"
LFS_DOCS = ""
LFS_INVOICE_COMPANY_NAME_REQUIRED = False
LFS_INVOICE_EMAIL_REQUIRED = True
LFS_INVOICE_PHONE_REQUIRED = True
LFS_SHIPPING_COMPANY_NAME_REQUIRED = False
LFS_SHIPPING_EMAIL_REQUIRED = False
LFS_SHIPPING_PHONE_REQUIRED = False
LFS_PAYMENT_METHOD_PROCESSORS = [["lfs_paypal.processor.PayPalProcessor", _("PayPal")]]
LFS_PRICE_CALCULATORS = [
    ["lfs.gross_price.calculator.GrossPriceCalculator", _("Price includes tax")],
    ["lfs.net_price.calculator.NetPriceCalculator", _("Price excludes tax")],
]
LFS_SHIPPING_METHOD_PRICE_CALCULATORS = [
    ["lfs.shipping.calculator.GrossShippingMethodPriceCalculator", _("Price includes tax")],
    ["lfs.shipping.calculator.NetShippingMethodPriceCalculator", _("Price excludes tax")],
]
LFS_UNITS = ["kg", "l", "m", "Stück"]
LFS_PRICE_UNITS = LFS_BASE_PRICE_UNITS = LFS_PACKING_UNITS = LFS_UNITS
LFS_CRITERIA = [
    ["lfs.criteria.models.CartPriceCriterion", _("Cart Price")],
    ["lfs.criteria.models.CountryCriterion", _("Country")],
    ["lfs.criteria.models.WeightCriterion", _("Weight")],
    ["lfs.criteria.models.ShippingMethodCriterion", _("Shipping Method")],
    ["lfs.criteria.models.PaymentMethodCriterion", _("Payment Method")],
]
PAYPAL_TEST = True
STATIC_ROOT = "/tmp/lfs-theme-tests/static"
MEDIA_ROOT = "/tmp/lfs-theme-tests/media"
MEDIA_URL = "media/"
PAYPAL_MODE = "sandbox"
PAYPAL_CLIENT_ID = "test"
PAYPAL_CLIENT_SECRET = "test"  # not a real secret
LOGIN_URL = "/login/"
REVIEWS_SHOW_PREVIEW = False
REVIEWS_IS_NAME_REQUIRED = False
REVIEWS_IS_EMAIL_REQUIRED = False
REVIEWS_IS_MODERATED = False
