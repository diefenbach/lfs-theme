// Checkout steps: show the shipping address, refresh shipping and payment, and add or remove vouchers.

/** Replace the checkout sections the server returned (cart, shipping, payment). */
const showCheckoutSections = (data) => {
    const sections = {'#cart-inline': data.cart, '#shipping-inline': data.shipping, '#payment-inline': data.payment};
    Object.entries(sections).forEach(([selector, html]) => {
        const element = document.querySelector(selector);
        if (element && html) element.innerHTML = html;
    });
};

/** Post the checkout form to its data-url and show the updated sections. */
const refreshCheckout = async () => {
    const form = document.querySelector('.checkout-form');
    if (!form?.dataset.url) return;
    try {
        showCheckoutSections(await postJson(form.dataset.url, new FormData(form)));
    } catch (error) {
        console.error('Updating the checkout failed:', error);
    }
};

/** Add the voucher of the voucher field, or remove the voucher of ``link``; show cart and message. */
const changeVoucher = async (url, body) => {
    try {
        const data = await postJson(url, body);
        document.querySelector('.cart-inline').innerHTML = data.cart;
        document.querySelector('.voucher-inline').innerHTML = data.voucher_inline;
        const message = document.querySelector('.voucher-message');
        if (message && data.message !== undefined) {
            message.textContent = data.message;
            message.classList.toggle('valid', Boolean(data.is_valid_voucher));
            message.classList.toggle('invalid', !data.is_valid_voucher);
        }
    } catch (error) {
        console.error('Changing the voucher failed:', error);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('change', (event) => {
        if (event.target.matches('#id_no_shipping')) {
            const shippingAddress = document.querySelector('.shipping-address');
            if (shippingAddress) shippingAddress.hidden = !event.target.checked;
            refreshCheckout();
        } else if (event.target.matches('.update-checkout')) {
            refreshCheckout();
        }
    });

    const checkAndPay = document.querySelector('.checkout-check-and-pay');
    if (!checkAndPay) return;

    checkAndPay.addEventListener('click', (event) => {
        const deleteLink = event.target.closest('.delete-voucher');
        const addButton = event.target.closest('.add-voucher');
        if (deleteLink) {
            event.preventDefault();
            changeVoucher(deleteLink.href);
        } else if (addButton) {
            event.preventDefault();
            const voucher = document.querySelector('input[name="voucher"]').value;
            changeVoucher(addButton.dataset.url, new URLSearchParams({voucher}));
        }
    });
    checkAndPay.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && event.target.matches('input[name="voucher"]')) {
            event.preventDefault();
            document.querySelector('.add-voucher')?.click();
        }
    });
});
