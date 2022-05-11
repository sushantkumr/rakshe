$(document).ready(function() {

    function ListPoliciesViewModel () {
        var self = this;

        self.policies = ko.observableArray();

        ec.utils.ajax('policy', 'views', 'get_policies_list', {}, function(response) {
            if (!response.success) {
                ec.utils.errorHandler(response);
                return;
            }
            self.policies(response.data);
        });
    };

    _viewModel = new ListPoliciesViewModel();
    ko.applyBindings(_viewModel);
    $('#js--insuree-list_policies').addClass('active');
    $('.dropdown-menu.active').removeClass('active');
});
