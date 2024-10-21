document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }
        
        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "User registered successfully") {
                alert('Registration successful!');
                window.location.href = '/';  // Redirect to home page
            } else {
                alert('Registration failed: ' + data.error);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred during registration');
        });
    });
});
