$(document).ready(function() {
    window.loginRecaptchaOnDone = function() {
        _loginViewModel.loginRecaptchaOnDone(arguments);
    }

    function LoginViewModel () {
        var self = this;
        self.error = ko.observable();
        self.loginUsername = ko.observable().extend({required: true, usernameChars: true, username: true});
        self.loginPassword = ko.observable().extend({required: true, password: true});
        self.captchaText = ko.observable('');

        self.loginRecaptchaOnDone = function() {
            self.captchaText('');
        };

        self.login = function() {
            var captchaCode = grecaptcha.getResponse();
            if (captchaCode === '') {
                self.captchaText('Solve the CAPTCHA by clicking on "I\'m not a robot".');
                return;
            }

            var errors = ko.validation.group([self.loginUsername, self.loginPassword]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }

            var data = {
                username: self.loginUsername(),
                password: self.loginPassword(),
                captcha_code: captchaCode,
            };

            self.error('');
            $.ajax({
                method: 'POST',
                contentType: 'application/json',
                url: '/login',
                data: JSON.stringify(data),
                success: function (response) {
                    if (response.success) {
                        window.location = '/';
                    }
                    else {
                        self.error('Error: ' + response.message);
                        grecaptcha.reset();
                    }
                },
                error: function(a, b, c) {
                    console.log(a, b, c);
                    ec.utils.bootboxError('An unexpected error occurred while logging in. Please try again later.');
                }
            });
        };
    }

    _loginViewModel = new LoginViewModel();
    ko.applyBindings(_loginViewModel);
});
