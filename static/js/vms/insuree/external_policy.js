$(document).ready(function() {

    function ExternalPolicyViewModel () {
        var self = this;
        self.error = ko.observable();

        self.importantNote = ko.observable(true);

        self.chosenDapp = ko.observable();

        var source = ec.utils.getQueryStringValue('source');
        var dappId = ec.utils.getQueryStringValue('dapp_id');

        self.init = function() {
            ec.utils.eajax('policy', 'views', 'get_approved_dapps', {dapp_id: dappId}, function(response) {
                if (!response.success) {
                    ec.utils.errorHandler(response, self.error);
                    return;
                }
                self.chosenDapp(response.data);
            });
        };

        self.init();
        
        self.contracts = ko.observableArray();

        self.contractDetailsReady = ko.computed(function() {
            self.contracts([]);
            if (self.chosenDapp() === undefined) {
                return false;
            }
            else {
                return ec.utils.eajax('policy', 'views', 'get_contract_info', {dapp_id: dappId}, function(response) {
                    if (!response.success) {
                        ec.utils.errorHandler(response, self.error);
                        return false;
                    }

                    self.contracts(response.data);
                    return true;
                });
            }
        }).extend({async: true});

        self.coverageLimit = ko.observable().extend({number: true, validation: {
                validator: function(val) {
                    if (self.chosenDapp() && (
                            Number(val) > self.chosenDapp().policy_coverage_max ||
                            Number(val) < self.chosenDapp().policy_coverage_min
                            )
                        ) {
                        return false;
                    }
                    return true;
                },
                message: function() {
                    if (self.chosenDapp()) {
                        return 'Coverage limit should be in the range: ' + self.chosenDapp().policy_coverage_min + ' to ' + self.chosenDapp().policy_coverage_max + ' ETH.'
                    }
                    return '';
                }
            }
        });

        self.fee = ko.computed(function() {
            // In the future this will be a more complex calculation
            // Probably something that's done on the server side
            var coverageLimit = Number(self.coverageLimit());
            if (isFinite(coverageLimit)) {
                var fee = Math.max(0.0001, Math.ceil(coverageLimit * 10000) / 1000000);
                return fee;
            }
            return 0;
        });

        (function() {
            ec.utils.initWeb3(self);
        })();

        self.message = ko.computed(function() {
            var errors = ko.validation.group([self.coverageLimit]);
            if (!self.chosenDapp() ||
                !self.contractDetailsReady() ||
                errors().length > 0) {
                return '';
            }

            // New line character don't render correctly while signing the message so
            // separate sections with stars.
            var padding = ' ************************************************** ';
            var messageHead = [
                'I agree to the terms and conditions mentioned in the New Policy page on Rakshe.com. ',
                'I understand that coverage is active only after I receive a signature on ',
                'this message by a Rakshe underwriter.',
                padding,
                'Policy information: ',
            ].join('');
            var dappName = 'DApp name: ' + self.chosenDapp().name;

            var contractAddresses = '';
            if (self.contracts[0]) {
                contractAddresses = self.contracts[0].address;
            }

            var contractsCovered = ' Contracts covered: ';
            self.contracts().forEach(function(contract, idx) {
                if (contract.address) {
                    contractsCovered += contract.address;
                }
                else if (contract.github_source) {
                    contractsCovered += contract.github_source;
                }

                if (self.contracts().length > 1) {
                    if (idx === self.contracts().length - 2) {
                        contractsCovered += ' and '
                    }
                    else if (idx < self.contracts().length - 2) {
                        contractsCovered += ', '
                    }
                }
            });

            var coverageLimitMessage = ' Coverage Limit: ' + self.coverageLimit() + ' ETH.';
            var feeMessage = ' Fee: ' + self.fee() + ' ETH';
            var signedByInsuree = ' Signed by address (insuree): ' + self.web3.accounts()[0];

            var message = [
                messageHead,
                padding,
                dappName,
                padding,
                contractsCovered,
                padding,
                coverageLimitMessage,
                feeMessage,
                padding,
                signedByInsuree,
            ].join('');

            return message;
        });

        self.signature = ko.observable();
        self.signatureError = ko.observable();
        self.message.subscribe(function(e) {
            // Discard the signature if the message changes.
            self.signature('');
        });

        self.signMessage = function() {
            self.signatureError('');

            var message = self.message();
            console.log(message);
            message = '0x' + ec.utils.toHex(message);
            self.web3.web3.personal.sign(message, self.web3.accounts()[0], function(err, signature) {
                if (err) {
                    if (err.message.indexOf('User denied message signature') > -1) {
                        self.signatureError('Please click on the "Sign" button when you are prompted by Metamask.');
                    }
                    else {
                        self.signatureError('An error occurred while you were signing the message. Please try again.');
                    }
                }
                else {
                    self.signature(signature);
                }
            });
        };

        self.submitApplication = function() {
            if (!self.signature() ) {
                self.signatureError('A signature was not found. Please try again.');
            }

            var errors = ko.validation.group([self.coverageLimit]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }

            // This shouldn't be necessary but considering that it's really critical
            // to get the right signature we'll be verifying the signature on the
            // front end as well as the back end.
            var address = self.web3.web3.personal.ecRecover(self.message(), self.signature(), function(err, address) {
                if (err) {
                    console.log(err);
                    self.signatureError('An error occurred while verifying your signature. Please check the web console for error details or try again.');
                    return;
                }
                if (address !== self.web3.accounts()[0]) {
                    self.signature('');
                    self.signatureError('Signature could not be verified please try again.');
                }

                var data = {
                    dapp_id: self.chosenDapp().id,
                    contract_addresses: self.contracts().map(function(c){return c.address || c.github_source}),
                    insuree_address: self.web3.accounts()[0],
                    coverage_limit: Number(self.coverageLimit()),
                    signature: self.signature()
                };

                ec.utils.eajax('policy', 'views', 'submit_policy_application', data, function(response) {
                    if (!response.success) {
                        ec.utils.errorHandler(response, self.signatureError);
                        return;
                    }
                    ec.utils.bootboxInformation('Your application has been submitted.', function() {
                        window.location = '/ext/insuree/external_policy_details?id=' + response.data.id;
                    });
                });
            });
        };
    };

    _viewModel = new ExternalPolicyViewModel();
    ko.applyBindings(_viewModel);
});
