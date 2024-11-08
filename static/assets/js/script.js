if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => console.log('ServiceWorker registered'))
            .catch(err => console.log('ServiceWorker registration failed: ', err));
    });
}

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

    try {
        heroSlider();  // Now safe to call on any page
    } catch (error) {
        console.log('Hero slider initialization error:', error);
    }
});

// Use IntersectionObserver for lazy loading
document.addEventListener('DOMContentLoaded', () => {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                observer.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
    
    // Hero slider
    const heroSlider = () => {
        const heroSlider = document.querySelector('.hero-slider');
        // Check if hero slider exists before proceeding
        if (!heroSlider) return;  // Exit if no slider found

        const slides = heroSlider.querySelectorAll('.slide');
        let currentSlide = 0;
        
        slides[currentSlide].classList.add('active');
        
        setInterval(() => {
            slides[currentSlide].classList.remove('active');
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add('active');
        }, 5000);
    };
    
    heroSlider();
}); 