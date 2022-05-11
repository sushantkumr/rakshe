$(document).ready(function() {

    function ListApplicationViewModel () {
        var self = this;

        self.applications = ko.observableArray();

        ec.utils.ajax('audit', 'views', 'get_applications_list', {}, function(response) {
            if (!response.success) {
                ec.utils.errorHandler(response);
                return;
            }
            self.applications(response.data);
        });
    };

    _viewModel = new ListApplicationViewModel();
    ko.applyBindings(_viewModel);
    $('#js--developer-list_applications').addClass('active');
    $('.dropdown-menu.active').removeClass('active');
});
