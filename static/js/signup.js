$(document).ready(function() {
    window.signupRecaptchaOnDone = function() {
        _signupViewModel.signupRecaptchaOnDone(arguments);
    }

    function SignUpViewModel () {
        var self = this;
        self.display = ko.observable('showChangePassword');
        self.error = ko.observable();
        self.username = ko.observable().extend({required: true, username: true, usernameChars: true});
        self.password = ko.observable().extend({required: true, password: true});
        self.emailId = ko.observable().extend({emailId:true});
        self.confirmPassword = ko.observable().extend({required: true, password: true, passwordMatch: self.password});

        self.captchaText = ko.observable('');

        self.signupRecaptchaOnDone = function() {
            self.captchaText('');
        };

        self.signup = function() {
            var captchaCode = grecaptcha.getResponse();
            if (captchaCode === '') {
                self.captchaText('Solve the CAPTCHA by clicking on "I\'m not a robot".');
                return;
            }

            var errors = ko.validation.group([self.username, self.password, self.confirmPassword]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }

            var data = {
                username: self.username(),
                password: self.password(),
                confirm_password: self.confirmPassword(),
                emailId: self.emailId(),
                captcha_code: captchaCode,
            };

            self.error('');
            $.ajax({
                method: 'POST',
                contentType: 'application/json',
                url: '/signup',
                data: JSON.stringify(data),
                success: function (response) {
                    if (response.success) {
                        if (self.emailId()) {
                            // Try to send a verification email but wait for success or errors
                            ec.utils.ajax('profile', 'views', 'submit_for_verify_email', {email_id: self.emailId()});
                        }

                        window.location = '/';
                    }
                    else {
                        self.error('Error: ' + response.message);
                        grecaptcha.reset();
                    }
                },
                error: function(a, b, c) {
                    console.log(a, b, c);
                    ec.utils.bootboxError('An unexpected error occurred while creating an account. Please try again later.');
                }
            });
        }
    }

    var _signupViewModel = new SignUpViewModel();
    ko.applyBindings(_signupViewModel);
});
