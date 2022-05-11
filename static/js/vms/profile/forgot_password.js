$(document).ready(function() {

    function ForgotPasswordViewModel () {
        var self = this;
        self.error = ko.observable();
        self.information = ko.observable();
        self.emailId = ko.observable().extend({emailId:true, required: true});
        self.error('');
        self.information('');

        self.submit = function() {
            var errors = ko.validation.group([self.emailId]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }

            self.error('');
            self.information('');
            ec.utils.eajax('profile', 'views', 'send_password_reset_mail', {
                email_id: self.emailId()
            }, function(response) {
                if (response.data) {
                    self.information(response.data.message);
                }
                else {
                    self.error(response.message);
                }
            });
        };
    }

    _forgotPasswordViewModel = new ForgotPasswordViewModel();
    ko.applyBindings(_forgotPasswordViewModel);
});
