$(document).ready(function() {

    function DappDevelopersViewModel () {
        var self = this;
        self.error = ko.observable();
        self.name = ko.observable().extend({required: true, usernameChars: true});
        self.dappLink = ko.observable('');
        self.dappDescription = ko.observable('').extend({
            validation: {
                validator: function(val) {
                    if (val.length > 1000) {
                        return false;
                    }
                    return true;
                },
                message: 'DApp Description should be less than a thousand character long.'
            }
        });
        self.sourceCodeLink = ko.observable().extend({required: true});

        self.submit = function() {
            var errors = ko.validation.group([self.name, self.sourceCodeLink, self.dappDescription, self.dappLink]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }

            self.error('');

            bootbox.confirm({
                title: 'Confirmation Required',
                message: 'The details being submitted cannot be modified later. Are you sure you want to submit?',
                callback: function(selection) {
                    if (selection) {
                        ec.utils.ajax('audit', 'views', 'submit_for_audit', {
                            name: self.name(),
                            source_code_link: self.sourceCodeLink(),
                            dapp_link: self.dappLink(),
                            dapp_description: self.dappDescription()
                        }, function(response) {
                            if (response.data) {
                                window.location = '/developer/application_details?id=' + response.data.id;
                            }
                            else if (response.message) {
                                ec.utils.errorHandler(response, self.error);
                            }
                        });
                    }
                }
            });
        };
    }

    _dappDevelopersViewModel = new DappDevelopersViewModel();
    ko.applyBindings(_dappDevelopersViewModel);
    $('#js--developer-new_application').addClass('active');
});
