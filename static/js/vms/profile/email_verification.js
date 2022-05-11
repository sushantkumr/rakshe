$(document).ready(function() {

    function EmailVerificationViewModel () {
        var self = this;
        self.error = ko.observable();
        self.success = ko.observable();
        self.loginStatus = ko.observable(false);

        self.init = function() {
            var tokenId = ec.utils.getQueryStringValue('token');
            
            ec.utils.eajax('profile', 'views', 'email_verification', {token: tokenId}, function(response) {
                if (!response.success) {
                    console.log(response);
                    self.error(response.message)
                }
                else {
                    console.log(response);
                    self.success(response.data.message)
                    self.loginStatus(response.data.loginStatus)
                }
            });
        };
        self.init();
    };

    _viewModel = new EmailVerificationViewModel();
    ko.applyBindings(_viewModel);
});
