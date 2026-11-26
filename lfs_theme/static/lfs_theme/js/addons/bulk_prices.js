// Popups of the optional lfs_bulk_prices and lfs_samples add-ons on the product page.
// Delegated from the document, because variant changes replace the product's content.

const closeBulkPricePopups = () => {
    document.querySelectorAll('.bulk-prices-popup.active, .product-samples-popup.active').forEach((popup) => popup.classList.remove('active'));
    document.querySelectorAll('.bulk-prices-info[aria-expanded="true"]').forEach((button) => button.setAttribute('aria-expanded', 'false'));
};

document.addEventListener('click', (event) => {
    const toggle = event.target.closest('.bulk-prices-info');
    if (toggle) {
        const popup = document.getElementById(toggle.getAttribute('aria-controls'));
        const open = !popup?.classList.contains('active');
        closeBulkPricePopups();
        if (popup && open) {
            popup.classList.add('active');
            toggle.setAttribute('aria-expanded', 'true');
        }
    } else if (event.target.closest('.bulk-prices-popup-close')) {
        closeBulkPricePopups();
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeBulkPricePopups();
});
