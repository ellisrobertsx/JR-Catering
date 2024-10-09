document.addEventListener('DOMContentLoaded', function() {
    const burgerBtn = document.getElementById('burger-btn');
    const navLinks = document.getElementById('nav-links');

    if (burgerBtn && navLinks) {
        burgerBtn.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent the click from propagating to the document
            navLinks.classList.toggle('nav-active');
            burgerBtn.classList.toggle('open');
        });

        // Close the menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navLinks.contains(event.target) && !burgerBtn.contains(event.target)) {
                navLinks.classList.remove('nav-active');
                burgerBtn.classList.remove('open');
            }
        });
    } else {
        if (!burgerBtn) console.error('Burger button not found!');
        if (!navLinks) console.error('Nav links not found!');
    }

    // Image gallery rotation
    const images = document.querySelectorAll('.gallery-image');
    let currentIndex = 0;

    function rotateImage() {
        images[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % images.length;
        images[currentIndex].classList.add('active');
    }

    setInterval(rotateImage, 5000); // Change image every 5 seconds
});