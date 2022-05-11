$(document).ready(function() {

    function PolicyDetailsViewModel () {
        var self = this;
        self.error = ko.observable();

        self.policy = ko.observable();
        self.dapp = ko.observable();

        self.feeTx = ko.observable();

        self.txHash = ko.observable().extend({
            required: {
                onlyIf: function() {
                    return self.policy() && self.policy().fee_received !== 'true';
                }
            }
        });

        self.submit = function(retry_attempt) {
            if (retry_attempt === undefined) {
                retry_attempt = 0;
            }
            var data = {
                tx_hash: self.txHash(),
                policy_id: self.policy().id
            };

            ec.utils.eajax('policy', 'views', 'check_fee_paid', data, function(response) {
                if (!response.success) {
                    if (self.feeTx() && self.response.message === 'The tx with corresponding hash could not be found. Please verify the hash or try again after sometime.') {
                        if (retry_attempt < 2) {
                            bootbox.hideAll();
                            bootbox.alert('Transaction could not be found. Retrying in ' + (retry_attempt + 1) * 5 + ' seconds...');
                            self.submit(retry_attempt + 1);
                            return;
                        }
                    }
                    ec.utils.errorHandler(response, self.error);
                    return;
                }
                window.location.reload();
            });
        };

        self.init = function() {
            ec.utils.initWeb3(self);

            var policyId = ec.utils.getQueryStringValue('id');
            if (!policyId) {
                self.error('Policy id not found.');
                return;
            }
            ec.utils.eajax('policy', 'views', 'get_policy_details', {id: policyId}, function(response) {
                if (!response.success) {
                    return ec.utils.errorHandler(response, self.error);
                }
                self.policy(response.data.policy);
                self.dapp(response.data.dapp);
            });
        };
        self.init();

        self.web3.accounts.subscribe(function(accounts) {
            if (accounts.length === 0) {
                self.error('');
                return;
            }
            if (self.policy() && accounts.indexOf(self.policy().insuree_address) === -1) {
                var msg = 'Please unlock the address ' + self.policy().insuree_address + ' in MetaMask and refresh the page.';
                self.error(msg);
            }
            else {
                self.error('');
            }
        });

        self.payFee = function() {
            self.web3.web3.eth.sendTransaction({
                from: self.policy().insuree_address,
                to: '0x4de22441e9bdc4901235d9c2b83947c562114355',
                value: self.web3.web3.toWei(self.policy().fee, 'ether'),
                gas: 22000,
                gasPrice: self.web3.web3.toWei(40, 'gwei'),
            }, function(err, data) {
                if (err) {
                    self.error('An error occurred while attempting to pay fees. Please try again.');
                }
                else {
                    self.feeTx(data);
                    // Wait for tx to get mined
                    var interval = setInterval(function() {
                        self.web3.web3.eth.getTransaction(self.feeTx(), function(err, data) {
                            if (data.blockNumber) {
                                clearInterval(interval);

                                // Wait for a few seconds so that etherscan is updated
                                setTimeout(function() {
                                    self.txHash(self.feeTx());
                                    self.submit();
                                }, 5000);
                            }
                        });
                    }, 1000);
                }
            });
        };
    };

    _viewModel = new PolicyDetailsViewModel();
    ko.applyBindings(_viewModel);
});
