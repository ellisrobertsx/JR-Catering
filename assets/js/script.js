document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    const burgerBtn = document.getElementById('burger-btn');
    const navLinks = document.getElementById('nav-links');
    const dropdownBtns = document.querySelectorAll('.dropbtn');

    console.log('Burger button:', burgerBtn);
    console.log('Nav links:', navLinks);

    if (burgerBtn && navLinks) {
        console.log('Both burger button and nav links found');
        burgerBtn.addEventListener('click', function(event) {
            console.log('Burger button clicked');
            event.stopPropagation();
            navLinks.classList.toggle('nav-active');
            burgerBtn.classList.toggle('open');
            console.log('Nav active:', navLinks.classList.contains('nav-active'));
        });

        // Close the menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navLinks.contains(event.target) && !burgerBtn.contains(event.target)) {
                navLinks.classList.remove('nav-active');
                burgerBtn.classList.remove('open');
                console.log('Clicked outside, closing menu');
            }
        });
    } else {
        console.log('Burger button or nav links not found');
    }


    // Handle dropdowns on mobile
    dropdownBtns.forEach(function(btn) {
        btn.addEventListener('click', function(event) {
            if (window.innerWidth < 1024) {
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


    
    const images = document.querySelectorAll('.gallery-image');
    let currentIndex = 0;

    function rotateImage() {
        images[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % images.length;
        images[currentIndex].classList.add('active');
    }

    setInterval(rotateImage, 5000); // Change image every 5 seconds
    
});