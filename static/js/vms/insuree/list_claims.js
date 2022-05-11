$(document).ready(function() {

    function ListClaimsViewModel () {
        var self = this;

        self.claims = ko.observableArray();

        ec.utils.ajax('claim', 'views', 'get_claims_list', {}, function(response) {
            if (!response.success) {
                ec.utils.errorHandler(response);
                return;
            }
            self.claims(response.data);
        });
    };

    _viewModel = new ListClaimsViewModel();
    ko.applyBindings(_viewModel);
    $('#js--insuree-list_claims').addClass('active');
    $('.dropdown-menu.active').removeClass('active');
});
