document.addEventListener('DOMContentLoaded', function() {
    const burgerBtn = document.getElementById('burger-btn');
    const navLinks = document.getElementById('nav-links');
    
    if (burgerBtn && navLinks) {
        burgerBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            burgerBtn.classList.toggle('open');
            navLinks.classList.toggle('active');
        });
    }

    const dropdownBtn = document.querySelector('.dropbtn');
    const dropdownContent = document.querySelector('.dropdown-content');
    
    if (dropdownBtn) {
        dropdownBtn.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                dropdownContent.classList.toggle('show');
            }
        });
    }

    document.addEventListener('click', function(e) {
        if (!e.target.matches('.dropbtn')) {
            const dropdowns = document.getElementsByClassName('dropdown-content');
            for (let dropdown of dropdowns) {
                if (dropdown.classList.contains('show')) {
                    dropdown.classList.remove('show');
                }
            }
        }
    });

    const heroImages = document.querySelectorAll('.hero-image');
    let currentImageIndex = 0;

    if (heroImages.length > 0) {
        heroImages[0].style.display = 'block';

        setInterval(() => {
            heroImages[currentImageIndex].style.display = 'none';
            currentImageIndex = (currentImageIndex + 1) % heroImages.length;
            heroImages[currentImageIndex].style.display = 'block';
        }, 3000);
    }
}); 