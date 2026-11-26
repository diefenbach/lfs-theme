// Shared by all pages: CSRF token, cart badge, live search, navigation, footer links.

/** Return Django's CSRF token from its cookie, for POST requests sent with fetch. */
const getCsrfToken = () => {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : null;
};

/** POST ``body`` (FormData or URLSearchParams) to ``url`` with the CSRF token and return the parsed JSON. */
const postJson = async (url, body) => {
    const response = await fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': getCsrfToken(), 'X-Requested-With': 'XMLHttpRequest'},
        body,
    });
    return response.json();
};

/** Show ``count`` in the cart badges of the header, or hide them when the cart is empty. */
const updateCartBadge = (count) => {
    document.querySelectorAll('.cart-items-count').forEach((badge) => {
        badge.textContent = count;
        badge.hidden = !(Number(count) > 0);
    });
};

/** Live search: show matching products below the search field while typing. */
const initLiveSearch = () => {
    const input = document.getElementById('search-input');
    const result = document.getElementById('livesearch-result');
    if (!input || !result) return;

    const hide = () => { result.hidden = true; };
    let timeout = null;

    input.addEventListener('blur', () => window.setTimeout(hide, 200));
    input.addEventListener('keyup', (event) => {
        clearTimeout(timeout);
        if (event.key === 'Escape') {
            hide();
            return;
        }
        timeout = setTimeout(async () => {
            try {
                const response = await fetch(`${input.dataset.url}?q=${encodeURIComponent(input.value)}`);
                const data = await response.json();
                if (data.state === 'success') {
                    result.innerHTML = data.products;
                    result.hidden = false;
                } else {
                    result.innerHTML = '';
                    hide();
                }
            } catch (error) {
                console.error('Live search failed:', error);
            }
        }, 400);
    });
};

/** Desktop dropdowns (hover, or first tap on touch devices) and the sliding mobile menu. */
const initNavigation = () => {
    const dropdowns = document.querySelectorAll('.desktop-dropdown');
    const container = document.querySelector('.desktop-dropdown-container');
    const hideAll = () => dropdowns.forEach((menu) => menu.classList.remove('desktop-dropdown-active'));
    const show = (id) => {
        hideAll();
        document.getElementById(id)?.classList.add('desktop-dropdown-active');
    };
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    let hideTimeout = null;

    document.querySelectorAll('.desktop-nav-item[data-dropdown]').forEach((item) => {
        if (isTouch) {
            // First tap opens the dropdown, a second tap follows the link.
            item.addEventListener('click', (event) => {
                if (!item.classList.contains('is-open')) {
                    event.preventDefault();
                    document.querySelectorAll('.desktop-nav-item.is-open').forEach((open) => open.classList.remove('is-open'));
                    item.classList.add('is-open');
                    show(item.dataset.dropdown);
                }
            });
        } else {
            item.addEventListener('mouseenter', () => {
                clearTimeout(hideTimeout);
                show(item.dataset.dropdown);
            });
            item.addEventListener('mouseleave', () => {
                hideTimeout = setTimeout(() => {
                    if (!container?.matches(':hover')) hideAll();
                }, 100);
            });
        }
    });
    container?.addEventListener('mouseenter', () => clearTimeout(hideTimeout));
    container?.addEventListener('mouseleave', hideAll);
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.desktop-nav, .desktop-dropdown-container')) hideAll();
    });

    // Mobile menu
    document.querySelectorAll('.mobile-nav-toggle-btn, .mobile-nav-close-link').forEach((button) => {
        button.addEventListener('click', () => document.body.classList.toggle('mobile-nav-is-toggled'));
    });
    document.querySelectorAll('.mobile-nav-expand').forEach((item) => {
        item.querySelector(':scope > .mobile-nav-sub-menu-link')?.addEventListener('click', () => item.classList.add('active'));
        item.querySelector(':scope > .mobile-nav-sub-menu .mobile-nav-back-link')?.addEventListener('click', () => item.classList.remove('active'));
    });
};

document.addEventListener('DOMContentLoaded', () => {
    initLiveSearch();
    initNavigation();

    // External links in the footer open in a new tab.
    document.querySelectorAll('#footer a[href^="https://"]').forEach((link) => {
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
    });

    // "Cookie settings" link of the optional lfs_cookie_consent add-on.
    document.querySelector('.cookie-settings-link')?.addEventListener('click', (event) => {
        event.preventDefault();
        window.showCookieSettings?.();
    });
});
