// Cart page: change amounts, country, shipping and payment method, or delete items, without reloading.

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('cart-inline');
    if (!container) return;

    /** Replace the cart with the server's HTML and update the header badge. */
    const showCart = (html) => {
        container.innerHTML = html;
        const count = container.querySelector('#cart-items-count-value')?.dataset.cartItemsCountValue ?? 0;
        updateCartBadge(count);
        document.body.dispatchEvent(new CustomEvent('cart-updated'));
    };

    const refresh = async () => {
        const form = document.getElementById('cart-form');
        if (!form) return;
        try {
            const data = await postJson(form.action, new FormData(form));
            showCart(data.html);
        } catch (error) {
            console.error('Updating the cart failed:', error);
        }
    };

    container.addEventListener('change', (event) => {
        if (event.target.matches('.cart-amount, .cart-country, .cart-shipping-method, .cart-payment-method')) {
            refresh();
        }
    });

    // Enter in an amount field updates the cart instead of submitting the form.
    container.addEventListener('submit', (event) => {
        event.preventDefault();
        refresh();
    });

    container.addEventListener('click', async (event) => {
        const deleteLink = event.target.closest('.delete-cart-item');
        if (!deleteLink) return;
        event.preventDefault();
        try {
            const response = await fetch(deleteLink.href, {method: 'POST', headers: {'X-CSRFToken': getCsrfToken()}});
            showCart(await response.text());
        } catch (error) {
            console.error('Deleting the cart item failed:', error);
        }
    });
});
