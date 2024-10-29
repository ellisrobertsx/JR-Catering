$(document).ready(function() {
    $('#login-form').on('submit', function(e) {
        e.preventDefault();
        $.ajax({
            url: '/login',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                $('#login-message').text(response.message);
                if (response.success) {
                    window.location.href = '/';
                }
            },
            error: function(xhr) {
                $('#login-message').text(xhr.responseJSON.message);
            }
        });
    });
});
