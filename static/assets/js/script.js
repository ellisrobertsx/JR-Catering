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

    // Handle logout link click
    const logoutLink = document.querySelector('a[href="/logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/';
                    
                    window.location.reload(true);
                }
            })
            .catch(error => console.error('Logout error:', error));
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
    if (heroImages.length > 0) {
        let currentImageIndex = 0;
        heroImages[0].style.display = 'block';

        setInterval(() => {
            heroImages[currentImageIndex].style.display = 'none';
            currentImageIndex = (currentImageIndex + 1) % heroImages.length;
            heroImages[currentImageIndex].style.display = 'block';
        }, 3000);
    }

    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    if (lazyImages.length > 0) {
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
    }
});
  
