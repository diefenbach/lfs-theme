What is it?
===========

This is the default theme for `LFS`_, an online shop based on Django.

Changes
=======

0.5.0 beta 6 (2011-04-13)
-------------------------

* Improved error message for checkout form (Andres Vargas / zodman); issue #87
* Fixed invalid HTML; issue #81
* Bugfix: correct display of cart within shop view after cart has been updated; issue #82
* Added transifex config file
* Added translations for mexican spanish (Andres Vargas)
* Updated romanian translations
* Updated german translations

0.5.0 beta 5 (2010-10-16)
-------------------------

* Bugfix added_to_cart: Display correct taxes within added_to_cart view. Issue #65.
* Bugfix variants: display variant's properties on cart, added_to_cart, checkout, received_mail, sent_mail. Issue #40.

0.5.0 beta 4 (2010-07-30)
-------------------------

* Bugfixed right-slot-wrapper
* Bugfix order_received_mail.html: display property price only if display_price is true
* Added french translations (Jacques Seite)

0.5.0 beta 3 (2010-06-30)
-------------------------

* Bugfix filter portlet: display option name
* Added new_user_mail_subject template
* Display default value for configurable properties
* Bugfix: correct display of property title
* Bugfix: correct display of product unit
* CSS fix: remove display:block from label

0.5.0 beta 2 (2010-06-27)
-------------------------

* Cleaned up contact form

0.5.0 beta 1 (2010-06-27)
-------------------------

* First beta release

.. _`LFS`: http://pypi.python.org/pypi/django-lfs