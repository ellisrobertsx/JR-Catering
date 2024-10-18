document.addEventListener('DOMContentLoaded', function() {
    const burgerBtn = document.getElementById('burger-btn');
    const navLinks = document.getElementById('nav-links');
    const dropdownBtns = document.querySelectorAll('.dropbtn');

    if (burgerBtn && navLinks) {
        burgerBtn.addEventListener('click', function(event) {
            event.stopPropagation();
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
    }

    // Handle dropdowns on mobile
    dropdownBtns.forEach(function(btn) {
        btn.addEventListener('click', function(event) {
            if (window.innerWidth < 768) {  // Adjust this value based on your mobile breakpoint
                event.preventDefault();
                const dropdownContent = this.nextElementSibling;
                dropdownContent.style.display = 
                    dropdownContent.style.display === 'block' ? 'none' : 'block';
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.matches('.dropbtn')) {
            const dropdowns = document.getElementsByClassName('dropdown-content');
            for (let i = 0; i < dropdowns.length; i++) {
                const openDropdown = dropdowns[i];
                if (openDropdown.style.display === 'block') {
                    openDropdown.style.display = 'none';
                }
            }
        }
    });

    // Image gallery rotation (only for pages with gallery)
    const images = document.querySelectorAll('.gallery-image');
    if (images.length > 0) {
        let currentIndex = 0;

        function rotateImage() {
            images[currentIndex].classList.remove('active');
            currentIndex = (currentIndex + 1) % images.length;
            images[currentIndex].classList.add('active');
        }

        setInterval(rotateImage, 5000); // Change image every 5 seconds
    }
});