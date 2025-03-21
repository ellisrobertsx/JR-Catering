document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const message = document.getElementById('register-message');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            if (formData.get('password') !== formData.get('confirm-password')) {
                message.textContent = 'Passwords do not match';
                message.className = 'alert error';
                message.style.display = 'block';
                return;
            }
            
            fetch('/register', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    return response.json().then(errorData => {
                        console.log('Error data:', errorData);
                        throw new Error(errorData.error || 'Registration failed');
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                message.style.display = 'block';
                if (data.error) {
                    message.textContent = data.error;
                    message.className = 'alert error';
                } else if (data.success) {
                    message.textContent = 'Registration successful!';  
                    message.className = 'alert success';
                    setTimeout(() => {
                        window.location.href = data.redirect || '/';
                    }, 1000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                message.textContent = error.message;
                message.className = 'alert error';
                message.style.display = 'block';
            });
        });
    }
});