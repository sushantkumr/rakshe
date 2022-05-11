$(document).ready(function() {

    function ApplicationDetailsViewModel () {
        var self = this;

        self.application = ko.observable();
        self.error = ko.observable();

        self.cancellable = ko.computed(function() {
            var cancellableStates = [
                'Submitted'
            ];
            if (self.application() && cancellableStates.indexOf(self.application().status) > -1) {
                return true;
            }
            else {
                return false;
            }
        });

        var id = ec.utils.getQueryStringValue('id');
        if (!id) {
            ec.utils.bootboxError('Application id was not found.');
            return;
        }

        self.commonResponseHandler = function(response) {
            if (!response.success) {
                ec.utils.errorHandler(response, self.error);
                return false;
            }

            response.data.source_code_link = ec.utils.linkify(response.data.source_code_link);
            response.data.dapp_website = ec.utils.linkify(response.data.dapp_website);
            self.application(response.data);
            return true;
        }

        self.cancelApplication = function() {
            var cancelApplicationBootbox = bootbox.confirm({
                title: 'Confirmation Required',
                message: 'Are you sure that you want to cancel this application? This action cannot be undone.',
                callback: function(selection) {
                    if (selection) {
                        ec.utils.ajax('audit', 'views', 'cancel_application', {id: id}, function(response) {
                            if (self.commonResponseHandler(response, self.error)) {
                                ec.utils.bootboxInformation('Application has been cancelled.');
                            }
                        });
                    }
                }
            });
        };

        ec.utils.ajax('audit', 'views', 'get_application_details', {id: id}, function(response) {
            self.commonResponseHandler(response);
        });
    };

    _viewModel = new ApplicationDetailsViewModel();
    ko.applyBindings(_viewModel);

    // I don't think we need a section for this in the navbar
    // $('#js--developer-application_details').addClass('active');
});
