document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const message = document.getElementById('register-message');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            // Check if passwords match
            if (formData.get('password') !== formData.get('confirm-password')) {
                message.textContent = 'Passwords do not match';
                message.className = 'alert error';
                message.style.display = 'block';
                return;
            }
            
            // Send registration request
            fetch('/register', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    message.textContent = data.error;
                    message.className = 'alert error';
                } else {
                    message.textContent = 'Registration successful! Redirecting to login...';
                    message.className = 'alert success';
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                }
                message.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                message.textContent = 'An error occurred. Please try again.';
                message.className = 'alert error';
                message.style.display = 'block';
            });
        });
    }
});
