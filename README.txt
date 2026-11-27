What is it?
===========

The default theme for LFS (django-lfs), an online shop based on Django: a responsive Bootstrap 5 storefront with
category navigation, live search, cart, and a three-step checkout.

Installation
============

Add ``lfs_theme`` to ``INSTALLED_APPS`` before the LFS apps, so its templates win, and include its URLs::

    path("theme/", include("lfs_theme.urls")),

The mobile menu is then loaded when it is first opened, instead of being part of every page; without the URLs it is
part of every page.

Optional add-ons
================

The theme works without any optional add-on. When one is installed, the theme shows its parts automatically:

* lfs_carousel: image slider on the home page (Swiper is loaded only there)
* lfs_bulk_prices, lfs_samples: bulk discounts and free samples on the product page
* lfs_cookie_consent: cookie banner and a "Cookie settings" link in the footer
* lfs_gtm: Google Tag Manager and e-commerce events
* lfs_stripe: card payment fields in the checkout

Shop content
============

* Logo: the shop's image (Manage > Shop); without one the shop name is shown.
* Footer columns: the first three static blocks.
* Footer links (imprint, terms, privacy, ...): the actions of the group "Footer".
* Colours: ``static/lfs_theme/scss/_colors.scss``; other Bootstrap settings (fonts, radii, spacing): ``static/lfs_theme/scss/bootstrap-custom.scss``. Then ``npm run build:css``.

Development
===========

CSS and the vendored libraries (Bootstrap, Bootstrap Icons, Swiper, htmx) are built with npm::

    cd lfs_theme
    npm install
    npm run build        # vendor files and CSS
    npm run build:css    # theme CSS and Bootstrap, after changing the SCSS

Tests::

    pytest lfs_theme/tests

License
=======

BSD (see LICENSE.txt). The vendored libraries in ``static/lfs_theme/vendor`` are MIT (Bootstrap, Bootstrap Icons,
Swiper) and 0BSD (htmx).
