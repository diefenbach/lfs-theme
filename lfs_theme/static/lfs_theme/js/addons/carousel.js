// Image slider of the optional lfs_carousel add-on.
new Swiper('.carousel', {
    loop: true,
    pagination: {el: '.swiper-pagination', clickable: true},
    navigation: {nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev'},
    autoplay: {delay: 4000},
    keyboard: true,
});
