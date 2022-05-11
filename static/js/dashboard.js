$(document).ready(function() {

    function DashboardViewModel () {
        var self = this;
        self.activePolicies = ko.observable();
        self.claimsPending = ko.observable();
        self.totalCoverage = ko.observable();
        self.buyPolicy = ko.observable(false);
        self.emailVerification = ko.observable(false);

        self.getDashboardData = function() {
            ec.utils.ajax('user', 'views', 'get_dashboard_data', {}, function(response) {
                console.log(response);
                if (response.success) {
                    self.activePolicies(response.data.activePolicies);
                    self.claimsPending(response.data.claimsPending);
                    self.totalCoverage(response.data.totalCoverage);
                    self.buyPolicy(response.data.buyPolicy);
                    self.emailVerification(response.data.emailVerification);
                }
                else {
                    self.activePolicies('0');
                    self.claimsPending('0');
                    self.totalCoverage('0');
                    self.buyPolicy(true);
                    self.emailVerification(true);
                }
            });
        }
        self.getDashboardData();

    };

    _viewModel = new DashboardViewModel();
    ko.applyBindings(_viewModel);
});
