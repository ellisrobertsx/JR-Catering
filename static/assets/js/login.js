$(document).ready(function() {
    $('#login-form').on('submit', function(e) {
        e.preventDefault();
        $.ajax({
            url: '/login',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    $('#login-message').text('Login successful! Redirecting...')
                                     .removeClass('error')
                                     .addClass('success');
                    setTimeout(function() {
                        window.location.href = '/';
                    }, 1000);
                } else {
                    $('#login-message').text(response.message)
                                     .removeClass('success')
                                     .addClass('error');
                }
            },
            error: function(xhr) {
                $('#login-message').text(xhr.responseJSON.message)
                                 .removeClass('success')
                                 .addClass('error');
            }
        });
    });
});
