$(document).ready(function() {

    function ProfileViewModel () {
        var self = this;
        // For changing password
        self.error = ko.observable();
        self.success = ko.observable();
        self.password = ko.observable().extend({required: true, password: true});
        self.passwordNew = ko.observable().extend({required: true, password: true});
        self.passwordNewCheck = ko.observable().extend({required: true, password: true, passwordMatch: self.passwordNew});
        self.error('');
        self.success('');

        // For email verification
        self.errorForEmailVerification = ko.observable();
        self.information = ko.observable();
        self.emailId= ko.observable().extend({required: true});

        // Click operation for change password
        self.submit = function() {
            self.error('');
            self.success('');
            
            var errors = ko.validation.group([self.password, self.passwordNew, self.passwordNewCheck]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }

            ec.utils.ajax('profile', 'views', 'submit_for_password_change', {
                old_login_password: self.password(),
                new_login_password: self.passwordNew()
            }, function(response) {
                if (response.success) {
                    self.password('');
                    self.passwordNew('');
                    self.passwordNewCheck('');
                    errors.showAllMessages(false);
                    self.success(response.data.message);
                }
                else {
                    self.error(response.message);
                }
            });
        };

        // Get email-id from database
        self.getEmailId = function() {
            ec.utils.ajax('profile', 'views', 'get_emailid', {
            }, function(response) {
                if (response.data.email) {
                    self.emailId(response.data.email);
                }
                else {
                }
            });
        };
        self.getEmailId();

        // Get user email verfication status from database
        self.getEmailVerficationStatus = function() {
            ec.utils.ajax('profile', 'views', 'get_email_verification_status', {
            }, function(response) {
                if (response.data) {
                    self.information(response.data.message);
                }
                else {
                    self.information('');
                }
            });
        };
        self.getEmailVerficationStatus();

        // Click operation for Email verification
        self.verifyEmail = function() {
            self.errorForEmailVerification('');
            self.information('');

            var errors = ko.validation.group([self.emailId]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }

            ec.utils.ajax('profile', 'views', 'submit_for_verify_email', {
                email_id: self.emailId()
            }, function(response) {
                if (response.data) {
                    self.information(response.data.message);
                }
                else if (response.message) {
                    self.errorForEmailVerification(response.message);
                }
            });
        };
    }

    _profileViewModel = new ProfileViewModel();
    ko.applyBindings(_profileViewModel);
    $('#js--profile-edit').addClass('active');
    $('.dropdown-menu.active').removeClass('active');
});
