function initNavbar() {

    // Create the navbar drop down menu:
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');
    const authLinks = document.getElementById('auth-links');

    // Remove any existing click listeners:
    hamburger.replaceWith(hamburger.cloneNode(true));

    // Get the new hamburger element after replacement:
    const newHamburger = document.getElementById('hamburger');

    newHamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        authLinks.classList.toggle('active');
    });

    // Change the nav-item color based on the current URL:
    const links = document.querySelectorAll('.nav-link');
    const currentLocation = location.href;

    links.forEach(link => {
        // Skip links with href="#"
        if (link.getAttribute('href') === '#') {
            return;
        }

        // Get the base URL without query parameters for both current location and link:
        const currentBasePath = currentLocation.split('?')[0];
        const linkBasePath = link.href.split('?')[0];

        // Check if the base paths match:
        if (currentBasePath === linkBasePath ||
            (link.href.includes('/account/') && currentLocation.includes('/account/'))) {
            link.classList.add('active');
        }
        else {
            link.classList.remove('active');
        }
    });
}

// Call initNavbar when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
});

// Also call initNavbar when the URL changes without a page reload:
window.addEventListener('popstate', () => {
    initNavbar();
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initNavbar };
}