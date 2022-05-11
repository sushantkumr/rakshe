$(document).ready(function() {
    $('.js--click-active').click(function(e) {
        // Ignore clicks on the navbar if the selected section is already active
        if ($(e.currentTarget).hasClass('active')) {
            return false;
        }

        // Remove focus from the element where the click was received
        $(':focus').blur();

        // Find the id of the div where we should scroll to
        var location = e.currentTarget.firstChild.hash;
        var dest = $(location).offset().top;
        $('html,body').animate({scrollTop: dest}, 1000);
        // history.replaceState({}, '', location);
        return false;
    });

    // Set the correct nav element as active
    (function() {
        var hash = window.location.hash;
        hash = hash.substring(1);
        $('.js--click-active.active').removeClass('active');
        $('.js--go-to-' + hash).addClass('active');
    })();

    function isValidEmailAddress(emailAddress) {
        var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i;
        return pattern.test(emailAddress);
    }

    $('.js--join-us').submit(function(e) {
        e.preventDefault();
        var data = {};
        var checked = $('[name=insurance_interest]:checked');
        data.interest = checked.toArray().map(function(ele) {
            return ele.value;
        });
        if (data.interest.length < 1) {
            $('.js--join-us-error-container').show();
            $('.js--join-us-error-message').html('Please select at least one option.');
            return;
        }
        var email = $('[name=insurance-email]').val();
        if (!isValidEmailAddress(email)) {
            $('.js--join-us-error-container').show();
            $('.js--join-us-error-message').html('Please enter a valid email id.');
            return;
        }
        $('.js--join-us-error-container').hide();
        data.email = email;
        $.ajax({
            method: 'POST',
            url: '/join_us',
            data: data,
            success: function(response) {
                console.log(response);
                if(response.success) {
                    $('.js--join-us-error-container').show();
                    $('.js--join-us-error-message').html('Submitted successfully.');
                }
            },
            error: function(a, b, c) {
                $('.js--join-us-error-container').show();
                $('.js--join-us-error-message').html('Error occurred while saving. Try again after sometime.');
            }
        });
        return false;
    });
});
