document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const message = document.getElementById('register-message');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
      
        const formData = new FormData(form);
        
        if (formData.get('password') !== formData.get('confirm-password')) {
            message.textContent = 'Passwords do not match';
            message.className = 'error';
            return;
        }
        
        
        fetch('/register', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                message.textContent = data.error;
                message.className = 'error';
            } else {
                message.textContent = 'Registration successful! Redirecting to login...';
                message.className = 'success';
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            }
        })
        .catch(error => {
            message.textContent = 'An error occurred. Please try again.';
            message.className = 'error';
            console.error('Error:', error);
        });
    });
});
