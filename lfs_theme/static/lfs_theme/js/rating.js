// Review form: a click on a star sets the score.
document.addEventListener('DOMContentLoaded', () => {
    const rates = document.querySelectorAll('.rate');
    rates.forEach((rate) => {
        rate.addEventListener('click', (event) => {
            event.preventDefault();
            rates.forEach((element) => element.classList.remove('current-rating'));
            rate.classList.add('current-rating');
            document.getElementById('id_score').value = rate.getAttribute('data');
        });
    });
});
