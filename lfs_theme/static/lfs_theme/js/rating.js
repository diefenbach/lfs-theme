// Review form: a click on a star sets the score and fills the stars up to it.
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('id_score');
    const rates = [...document.querySelectorAll('.star-input .rate')];
    if (!input || !rates.length) return;

    const show = (score) => rates.forEach((rate) => {
        const on = parseFloat(rate.dataset.score) <= score;
        const icon = rate.querySelector('i');
        icon.classList.toggle('bi-star-fill', on);
        icon.classList.toggle('bi-star', !on);
        rate.setAttribute('aria-pressed', on && parseFloat(rate.dataset.score) === score ? 'true' : 'false');
    });

    rates.forEach((rate) => {
        rate.addEventListener('click', () => {
            input.value = rate.dataset.score;
            show(parseFloat(input.value));
        });
        rate.addEventListener('mouseenter', () => show(parseFloat(rate.dataset.score)));
        rate.addEventListener('mouseleave', () => show(parseFloat(input.value) || 0));
    });
    show(parseFloat(input.value) || 0);
});
