$(document).ready(function() {

    url = window.location.href
    var tokenId = ec.utils.getQueryStringValue('token');

    function PasswordResetViewModel () {
        var self = this;
        self.information = ko.observable();
        self.error = ko.observable();
        self.password = ko.observable().extend({required: true, password: true});
        self.passwordCheck = ko.observable().extend({required: true, password: true, passwordMatch: self.password});
        self.information('');
        self.error('');

        self.submit = function() {
            var errors = ko.validation.group([self.emailId]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }

            self.information('');
            self.error('');
            ec.utils.eajax('profile', 'views', 'password_change', {
                password: self.password(),
                token: tokenId
            }, function(response) {
                if (response.data) {
                    var f = document.getElementById("passwordResetForm");
                    f.parentNode.removeChild(f);
                    self.information(response.data.message);
                }
                else {
                    self.error(response.message)
                }
            });
        };

        self.checkToken = function() {

            ec.utils.eajax('profile', 'views', 'password_reset_verification', {
                token: tokenId
            }, function(response) {
                if (!response.success) {
                    var f = document.getElementById("passwordResetForm");
                    f.parentNode.removeChild(f);
                    self.error(response.message)
                }
                else {}
            });
        };
        self.checkToken();
    }

    _passwordResetViewModel = new PasswordResetViewModel();
    ko.applyBindings(_passwordResetViewModel);
});
