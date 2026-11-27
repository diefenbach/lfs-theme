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

};

// Mobile category menu: a drawer from the left that shows one level at a time. It opens at the level of the
// current category, closes on the backdrop, the close buttons, and Escape, keeps the focus inside the level shown,
// and returns it to the menu button when closed.
const initMobileMenu = () => {
    const toggle = document.querySelector('.mobile-nav-toggle-btn');
    const drawer = document.getElementById('mobile-nav');
    const backdrop = document.querySelector('.mobile-nav-backdrop');
    if (!toggle || !drawer) return;

    // The levels come from data-src on first use (see top_nav in lfs_theme_tags.py), or are already in the page.
    let loading = null;
    const load = () => {
        if (!drawer.dataset.src) return Promise.resolve();
        loading ??= fetch(drawer.dataset.src)
            .then((response) => {
                if (!response.ok) throw new Error(`Mobile menu: ${response.status} ${response.url}`);
                return response.text();
            })
            .then((html) => {
                drawer.innerHTML = html;
                markCurrent();
            })
            .catch((error) => {
                loading = null; // try again on the next tap
                throw error;
            });
        return loading;
    };
    // Mark the current category and its parents, so the menu opens at the visitor's level.
    const markCurrent = () => {
        const link = drawer.querySelector(`a[href="${CSS.escape(drawer.dataset.current || '')}"]`);
        if (!link) return;
        link.setAttribute('aria-current', 'page');
        for (let item = link.closest('li'); item; item = item.parentElement.closest('li')) {
            item.classList.add('is-current');
        }
    };
    if (!drawer.dataset.src) markCurrent();

    const isOpen = () => document.body.classList.contains('mobile-nav-is-toggled');
    // The level shown: the deepest open sub menu, or the top level.
    const level = () => [...drawer.querySelectorAll('.mobile-nav-expand.open > .mobile-nav-sub-menu')].pop()
        || drawer.querySelector(':scope > .mobile-nav-items');
    const focusables = () => [...level().querySelectorAll(':scope > li > a, :scope > li > button')];
    const focusLevel = () => focusables()[0]?.focus({preventScroll: true});

    const open = async () => {
        await load();
        // Jump straight to the current category's level; only the drawer itself slides in.
        drawer.classList.add('no-transition');
        drawer.querySelectorAll('.mobile-nav-expand').forEach((item) => {
            item.classList.toggle('open', item.classList.contains('is-current'));
        });
        drawer.offsetWidth; // apply the levels' positions before transitions come back
        drawer.classList.remove('no-transition');
        document.body.classList.add('mobile-nav-is-toggled');
        toggle.setAttribute('aria-expanded', 'true');
        focusLevel();
    };
    const close = () => {
        document.body.classList.remove('mobile-nav-is-toggled');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus({preventScroll: true});
    };

    // Start loading as soon as the visitor reaches for the button, so the menu is there when the tap ends.
    toggle.addEventListener('pointerdown', () => load().catch(() => {}), {once: true});
    toggle.addEventListener('click', () => {
        if (isOpen()) close();
        else open().catch((error) => console.error(error));
    });
    backdrop?.addEventListener('click', close);
    drawer.addEventListener('click', (event) => {
        const button = event.target.closest('button');
        if (!button) return;
        const item = button.closest('.mobile-nav-expand');
        if (button.classList.contains('mobile-nav-close')) {
            close();
        } else if (button.classList.contains('mobile-nav-sub-menu-link')) {
            item.classList.add('open');
            focusLevel();
        } else if (button.classList.contains('mobile-nav-back-link')) {
            item.classList.remove('open');
            item.querySelector(':scope > .mobile-nav-sub-menu-link').focus({preventScroll: true});
        }
    });

    document.addEventListener('keydown', (event) => {
        if (!isOpen()) return;
        if (event.key === 'Escape') {
            close();
        } else if (event.key === 'Tab') {
            const items = focusables();
            const first = items[0];
            const last = items[items.length - 1];
            if (!level().contains(document.activeElement)) {
                event.preventDefault();
                first?.focus({preventScroll: true});
            } else if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus({preventScroll: true});
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus({preventScroll: true});
            }
        }
    });
};

document.addEventListener('DOMContentLoaded', () => {
    initLiveSearch();
    initNavigation();
    initMobileMenu();

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
