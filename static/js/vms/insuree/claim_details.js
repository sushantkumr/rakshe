$(document).ready(function() {

    function ClaimDetailsViewModel () {
        var self = this;
        self.error = ko.observable();

        self.claim = ko.observable();
        self.dapp = ko.observable();

        self.init = function() {
            var claimId = ec.utils.getQueryStringValue('id');
            if (!claimId) {
                self.error('Claim id not found.');
                return;
            }
            ec.utils.ajax('claim', 'views', 'get_claim_details', {id: claimId}, function(response) {
                if (!response.success) {
                    return ec.utils.errorHandler(response, self.error);
                }
                self.claim(response.data.claim);
                self.dapp(response.data.dapp);
            });
        };
        self.init();
    };

    _viewModel = new ClaimDetailsViewModel();
    ko.applyBindings(_viewModel);
});
