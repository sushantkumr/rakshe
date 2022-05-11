$(document).ready(function() {

    function NewClaimViewModel () {
        var self = this;
        self.error = ko.observable();

        self.claimRemark = ko.observable('').extend({
            validation: {
                validator: function(val) {
                    if (val.length > 10000) {
                        return false;
                    }
                    return true;
                },
                message: 'Description of loss should be less than 10,000 characters long.'
            }
        , required: true});

        self.policyList = ko.observableArray();
        ec.utils.ajax('claim', 'views', 'get_claimable_policy_list', {}, function(response) {
            if (!response.success) {
                ec.utils.errorHandler(response, self.error);
                return;
            }
            self.policyList(response.data);
        });

        self.chosenPolicy = ko.observable();

        self.contracts = ko.observableArray();
        self.contractDetailsReady = ko.computed(function() {
            self.contracts([]);
            if (self.chosenPolicy() === undefined) {
                return false;
            }
            else {
                return ec.utils.ajax('claim', 'views', 'get_contract_info', {dapp_id: self.chosenPolicy().dapp_id}, function(response) {
                    if (!response.success) {
                        ec.utils.errorHandler(response, self.error);
                        return false;
                    }
                    self.contracts(response.data);
                    return false;
                });
            }
        }).extend({deferred: true});

        (function() {
            ec.utils.initWeb3(self);
        })();

        self.message = ko.computed(function() {
            if (!self.chosenPolicy() ||
                !self.contractDetailsReady()) {
                return '';
            }

            // New line character don't render correctly while signing the message so
            // separate sections with stars.
            var padding = ' ************************************************** ';
            var messageHead = [
                'I agree to the terms and conditions mentioned in the New Claim page on Rakshe.com. ',
                'I understand that claim can be delayed unless accepted.',
                padding,
                'Claim information: ',
            ].join('');
            var policyId = 'Warranty ID: ' + self.chosenPolicy().id;
            var signedByInsuree = ' Signed by address (warranty holder): ' + self.web3.accounts()[0];

            var message = [
                messageHead,
                padding,
                padding,
                policyId,
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

            var errors = ko.validation.group([self.claimRemark]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }

            var message = self.message();
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

        self.raiseClaim = function() {
            if (!self.signature() ) {
                self.signatureError('A signature was not found. Please try again.');
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

                var errors = ko.validation.group([self.claimRemark]);
                if (errors().length > 0) {
                    errors.showAllMessages(true);
                    return;
                }

                var data = {
                    policy_id: self.chosenPolicy().id,
                    insuree_address: self.web3.accounts()[0],
                    signature: self.signature(),
                    claim_remark: self.claimRemark()
                };

                ec.utils.ajax('claim', 'views', 'raise_claim', data, function(response) {
                    if (!response.success) {
                        ec.utils.errorHandler(response, self.signatureError);
                        return;
                    }
                    ec.utils.bootboxInformation('Your claim has been raised.', function() {
                        window.location = '/insuree/claim_details?id=' + response.data.id;
                    });
                });
            });
        };
    };

    _viewModel = new NewClaimViewModel();
    ko.applyBindings(_viewModel);
    $('#js--insuree-new_claim').addClass('active');
});
