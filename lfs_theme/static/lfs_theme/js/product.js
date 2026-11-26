// Product page: image gallery, variant selection, and validation of configurable number properties.
// All handlers are delegated from #product-inline, because variant changes replace its content.

/** Validation message templates come from data attributes of #product-inline, translated by Django. */
const message = (name, values) => {
    const template = document.getElementById('product-inline')?.dataset[name] ?? '';
    return template.replace(/%\((\w+)\)s/g, (_, key) => values[key] ?? '');
};

const parseNumber = (value) => {
    const normalized = String(value).trim().replace(/\s/g, '').replace(',', '.');
    if (normalized === '') return null;
    const number = Number(normalized);
    return Number.isFinite(number) ? number : NaN;
};

const formatNumber = (value) => String(value).replace('.', ',');

/** True when ``value`` is one of the steps min, min + step, ..., max (as the server checks it in add_to_cart). */
const isValidStep = (value, min, max, step) => {
    if (!step) return true;
    const steps = [];
    for (let x = min, guard = 0; x < max && guard < 100000; x += step, guard += 1) {
        steps.push(x.toFixed(2));
    }
    steps.push(Number(max).toFixed(2));
    return steps.includes(Number(value).toFixed(2));
};

/** Return the error message for a configurable number field, or null when the value is valid or empty. */
const validationMessage = (input) => {
    const raw = input.value.trim();
    if (raw === '') return null;
    const value = parseNumber(raw);
    const min = input.dataset.min ? parseNumber(input.dataset.min) : null;
    const max = input.dataset.max ? parseNumber(input.dataset.max) : null;
    const step = input.dataset.step ? parseNumber(input.dataset.step) : null;
    const title = input.dataset.title || '';
    const unit = input.dataset.unit ? ` ${input.dataset.unit}` : '';

    if (value === null || Number.isNaN(value)) return message('msgNumber', {title});
    const hasRange = min !== null && !Number.isNaN(min) && max !== null && !Number.isNaN(max);
    if (hasRange && (value < min || value > max)) {
        return message('msgRange', {title, min: formatNumber(min), max: formatNumber(max), unit});
    }
    if (hasRange && step && !Number.isNaN(step) && !isValidStep(value, min, max, step)) {
        return message('msgStep', {title, value: formatNumber(value), step: formatNumber(step)});
    }
    return null;
};

const showError = (input, text) => {
    const error = input.closest('.property-row')?.querySelector('.property-error');
    input.classList.toggle('is-invalid', text !== null);
    if (error) {
        error.textContent = text ?? '';
        error.hidden = text === null;
    }
};

/** Validate a field; show new errors only when ``showNew`` (on blur), otherwise only update visible ones. */
const validate = (input, showNew) => {
    const text = validationMessage(input);
    if (text === null || showNew || input.classList.contains('is-invalid')) showError(input, text);
    return text === null;
};

/** Post the product form to ``url`` and replace the product with the variant the server returns. */
const loadVariant = async (url, formData) => {
    try {
        const response = await fetch(url, {method: 'POST', body: formData});
        const data = await response.json();
        document.getElementById('product-inline').innerHTML = data.product;
        document.body.dispatchEvent(new CustomEvent('product-updated'));
    } catch (error) {
        console.error('Loading the variant failed:', error);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('product-inline');
    if (!container) return;

    // Gallery: a click on a thumbnail shows it as the main image.
    container.addEventListener('click', (event) => {
        const link = event.target.closest('.sub-images a');
        if (!link) return;
        event.preventDefault();
        const thumbnail = link.querySelector('img');
        const main = container.querySelector('.main-image img');
        if (!main || !thumbnail) return;
        main.src = link.href;
        main.alt = thumbnail.alt;
        main.title = thumbnail.title;
    });

    // Variants: radio list or select fields.
    container.addEventListener('change', (event) => {
        const form = document.getElementById('product-form');
        if (!form) return;
        if (event.target.matches('input.variant')) {
            const formData = new FormData(form);
            formData.set('variant_id', event.target.value);
            loadVariant(container.querySelector('.variants').dataset.url, formData);
        } else if (event.target.matches('select.property')) {
            loadVariant(form.dataset.url, new FormData(form));
        } else if (event.target.matches('.number-field')) {
            validate(event.target, false);
        }
    });

    container.addEventListener('input', (event) => {
        if (event.target.matches('.number-field')) validate(event.target, false);
    });
    container.addEventListener('focusout', (event) => {
        if (event.target.matches('.number-field')) validate(event.target, true);
    });
    container.addEventListener('submit', (event) => {
        let valid = true;
        container.querySelectorAll('.number-field[data-min], .number-field[data-max]').forEach((input) => {
            if (!validate(input, true)) valid = false;
        });
        if (!valid) event.preventDefault();
    });
});
