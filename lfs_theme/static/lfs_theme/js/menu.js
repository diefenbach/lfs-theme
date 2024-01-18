// Mobile Menu

// Toggle sidebar
const hamburger = document.querySelectorAll('.hamburger')
hamburger.forEach(hamburger => {
    hamburger.addEventListener('click', event => document.body.classList.toggle('nav-mobile-is-toggled'));
})

// Toggle submenus
const navExpand = [].slice.call(document.querySelectorAll('.nav-mobile-expand'))
navExpand.forEach(item => {
    item.querySelector('.nav-mobile-link').addEventListener('click', () => item.classList.add('active'))
    item.querySelector('.nav-back-link').addEventListener('click', () => item.classList.remove('active'))
})


// Top Menu for mobile devices (make hovering work)
// By default click and touchstart is triggered, when clicking on the menu point on a mobile device.
if (/Mobi|Android/i.test(navigator.userAgent)) {
    const links = document.querySelectorAll('.lfs-theme-nav-top-item-link');

    links.forEach(link => {
        // Don't go to the target
        link.addEventListener('click', event => {
            event.preventDefault();
        });


        link.addEventListener('touchstart', event => {
            // Remove "is-hovered" class from all links which is not the currently touched.
            links.forEach(l => {
                if (l !== link) {
                    l.classList.remove('is-hovered')
                }
            })

            // If the currently touched link has already the "is-hovered" class, go to the target
            if (link.classList.contains('is-hovered')) {
                window.location = link.getAttribute('href');
            }

            // add the "is-hovered" class to the currently touched link, in order to go to the target, if the link
            // is touched again.
            link.classList.add('is-hovered');
        });
    });
    // On mobile we don't want to have the hover intent feature;
    const menuItems = document.querySelectorAll('.lfs-theme-nav-top-item');
    menuItems.forEach(menuItem => {
        menuItem.addEventListener('mouseenter', event => {
            menuItem.classList.add('hover');
        });
        menuItem.addEventListener('mouseout', event => {
            menuItem.classList.remove('hover');
        });
    });
} else {
    const menuItems = document.querySelectorAll('.lfs-theme-nav-top-item');
    const hi = new SV.HoverIntent(menuItems, {
        onEnter: function(targetItem) {
            targetItem.classList.add('hover');
        },
        onExit: function(targetItem) {
            targetItem.classList.remove('hover');
        },
    });
}
