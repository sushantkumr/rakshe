ko.components.register('receiver-input', {
    viewModel: function(params) {
        var self = this;

        self.success = params.success || bootbox.hideAll;

        self.walletAddress = ko.observable().extend({required: true, walletAddress: true});
        self.name = ko.observable().extend({required: true});
        self.emailId = ko.observable().extend({required: true});
        self.notes = ko.observable('');

        self.createReceiver = function() {
            if (!self.walletAddress.isValid() ||
                !self.name.isValid() ||
                !self.emailId.isValid()) {
                var html;
                if (!self.name.isValid()) {
                    html = $(`
                        <p>Please enter a name for the receiver.</p>
                        <p>Examples: <kbd>My coinbase</kbd>, <kbd>Mom's Ledger</kbd></p>
                    `);
                }
                else if (!self.walletAddress.isValid()) {
                    html = $(`
                        <p>Please enter a valid Ethereum wallet address.</p>
                    `);
                }
                else {
                    html = $(`
                        <p>Please enter a valid email id.</p>
                    `);
                }
                ec.utils.bootboxError(html);
                return;
            }
            else {
                if (false) {}
                else {
                    var data = {
                        wallet_address: self.walletAddress(),
                        name: self.name(),
                        email_id: self.emailId(),
                        notes: self.notes()
                    };
                    ec.utils.ajax('cocoon', 'views', 'create_receiver', data, function(response) {
                        if (!response.success) {
                            bootbox.alert({title: 'Error', message: 'An error occurred while creating the receiver. Please refresh the page and try again.'});
                        }
                        else {
                            self.success(response.data);
                        }
                    });
                }
            }
        };

        self.nameHelp = function() {
            var html = $(`
                <p>Use a descriptive name for your receivers to help identify where the address points to.</p>
                <p>Examples: <kbd>My coinbase</kbd>, <kbd>Mom's Ledger</kbd></p>
            `);
            ec.utils.bootboxHelp(html);
        };

        self.walletAddressHelp = function() {
            var html = $(`
                <p>This is the address to which your assets can be transfered to from the Cocoon.</p>
            `);
            ec.utils.bootboxHelp(html);
        };

        self.emailHelp = function() {
            var html = $(`
                <p>We will contact this email id if the deadline on your Cocoon passes by and the deadline hasn't been renewed.</p>
                <p>Contents of the Cocoon will be transfered to the receiver once they confirm that they are prepared to receive it.</p>
            `);
            ec.utils.bootboxHelp(html);
        };
    },
    template: {require: 'text!/templates/components/receiver-input.html'}
});


ko.components.register('list-receivers', {
    viewModel: function(params) {
        var self = this;

        self.onSuccess = params.onSuccess || function() {};
        self.receivers = ko.observableArray(params.receivers);

        self.receiversToAdd = ko.observableArray();
        self.addReceiver = function(data, event) {
            var context = ko.contextFor(event.target);
            var index = context.$index();
            self.receiversToAdd.push(self.receivers()[index]);
            self.receivers.splice(index, 1);

            if (self.receivers().length === 0) {
                self.done();
            }
        };

        self.done = function() {
            self.onSuccess(self.receiversToAdd());
        };
    },
    template: {require: 'text!/templates/components/list-receivers.html'}
});


ko.components.register('cocoon-input', {
    viewModel: function(params) {
        var self = this;

        self.success = params.success || bootbox.hideAll;

        self.name = ko.observable().extend({required: true});
        self.pickExistingAccount = ko.observable(true);
        self.walletAddressDropdown = ko.observable('').extend({
            required: {
                onlyIf: function() {
                    return self.pickExistingAccount() === true;
                }
            },
            walletAddress: {
                onlyIf: function() {
                    return self.pickExistingAccount() === false;
                }
            }
        });
        self.walletAddress = ko.observable('').extend({
            required: {
                onlyIf: function() {
                    return self.pickExistingAccount() === false;
                }
            },
            walletAddress: {
                onlyIf: function() {
                    return self.pickExistingAccount() === false;
                }
            }
        });

        self.interval = ko.observable(3).extend({required: true, number: true, cocooonRange: true});

        self.existingAccounts = ko.observableArray(web3.eth.accounts);

        self.createCocoon = function() {
            var errors = ko.validation.group([self.walletAddress, self.name,
                                              self.interval, self.walletAddressDropdown]);
            if (errors().length > 0) {
                errors.showAllMessages(true);
                return;
            }
            else if (self.receivers().length < 2) {
                bootbox.alert({title: 'Error', message: 'Please add at least 2 receivers to the cocoon.'});
                return;
            }
            else if (self.pickExistingAccount() === false) {
                var owner = self.walletAddress();
            }
            else {
                var owner = self.walletAddressDropdown();
            }

            var data = {
                name: self.name(),
                interval: self.interval(),
                owner: owner,
                receiver_ids: self.usedReceiverIds(),
                network_id: window.Globals.networkId
            };
            var receiver_addresses = self.receivers().map(function(i) {
                return i.wallet_address;
            });
            ec.utils.ajax('cocoon', 'views', 'create_cocoon', data, function(response) {
                console.log(response.data)
                ec.utils.wait({message: 'A Cocoon is being created. This operation will take a few minutes, please do not refresh the page or navigate away. We\'ll let you know once the contract has been deployed.'});
                if (!response.success) {
                    console.log('create_cocoon', response)
                    bootbox.alert({
                        title: 'Error',
                        message: 'An error occurred while creating a cocoon. Please try again.'
                    });
                }
                contracts.Cocoon.new(
                    response.data.receiver_addresses,
                    response.data.owner_address,
                    response.data.intermediary_address,
                    {from: web3.eth.accounts[0]}
                ).then(function(contract) {
                    bootbox.hideAll();
                    console.log('ctr', contract);
                    var html = $('<p>Contract created. You can view the transaction on ' +
                        ec.utils.generateEtherscanAnchorTag('tx', contract.transactionHash, 'Etherscan') +
                        '.</p>');
                    bootbox.alert({
                        title: 'Information',
                        message: $(html)
                    });
                    ec.utils.ajax('cocoon', 'views', 'set_cocoon_address', {
                        cocoon_id: response.data.cocoon.id,
                        address: contract.address
                    }, function(response) {
                        self.success(response.data);
                    });
                })
                .catch(function(e) {
                    bootbox.hideAll();
                    if (e.message.indexOf('User denied transaction signature')) {
                        bootbox.alert({
                            title: 'Error',
                            message: 'You have canceled the operation.'
                        });
                    }
                });
            });
        };

        self.receivers = ko.observableArray();
        self.usedReceiverIds = ko.observableArray();
        self.availableReceivers = ko.observableArray();

        self.addedReceivers = function(receivers) {
            self.addReceiversDialog.modal('hide');
            receivers.forEach(self.addReceiverToCocoon);
        };

        self.addReceiverToCocoon = function(receiver) {
            self.receivers.push(receiver);
            self.usedReceiverIds.push(receiver.id);
            self.availableReceivers([]);
        };

        self.newReceiver = function() {
            var html = $('<receiver-input params="success: success"></receiver-input>');
            var params = {
                success: function(data) {
                    self.addReceiverToCocoon(data);
                    self.newReceiverDialog.modal('hide');
                }
            };

            ko.applyBindings(params, html[0]);
            self.newReceiverDialog = bootbox.dialog({
                title: 'Add a New Receiver',
                message: html
            });
        };

        self.listReceivers = function() {
            self.availableReceivers([]);
            ec.utils.ajax('cocoon', 'views', 'list_receivers', {}, function(response) {
                if (!response.success) {
                    bootbox.alert({title: 'Error', message: 'Error fetching list of receivers, please try again.'});
                    return;
                }

                var receivers = response.data.filter(function(receiver) {
                    if (self.usedReceiverIds().indexOf(receiver.id) !== -1) {
                        return false;
                    }
                    if (receiver.archived === 'True') {
                        return false;
                    }
                    return true;
                });

                self.availableReceivers(response.data.filter(function(receiver) {
                    if (self.usedReceiverIds().indexOf(receiver.id) !== -1) {
                        return false;
                    }
                    if (receiver.archived === 'True') {
                        return false;
                    }
                    return true;
                }));
                if (self.availableReceivers().length === 0) {
                    var html = $(`
                        <div class="row">
                            <div class="col-md-offset-1 col-md-10">
                                <p>You've added all the active receivers to this cocoon.</p>
                                <p><a href="/receivers#list" target="_blank">Click here to create a new receiver</a> if you wish to add more receivers to this cocoon.</p>
                            </div>
                        </div>
                    `);
                    bootbox.alert({
                        title: 'Error',
                        message: html
                    });
                    return;
                }
                else {
                    var html = $(`<list-receivers params="receivers: receivers, onSuccess: onSuccess"></list-receivers>`);
                    var options = {
                        receivers: self.availableReceivers(),
                        onSuccess: self.addedReceivers
                    }
                    ko.applyBindings(options, html[0]);
                    self.addReceiversDialog = bootbox.dialog({
                        title: 'Add Receivers to Cocoon',
                        message: html
                    });
                }
            });
        };

        self.removeReceiver = function(data, event) {
            var context = ko.contextFor(event.target);
            var index = context.$index();
            self.receivers.splice(index, 1);
            self.usedReceiverIds.splice(index, 1);
        };

        self.intervalHelp = function() {
            var html = $(`
                <p>
                    You can choose the frequency at which you wish to login to the site and update the deadline of your Cocoon.
                    When a deadline is near we'll remind you to login to the site and update the deadline.
                    If a deadline passes by and you haven't updated the deadline we will contact the email ids associated with the receiver addresseses and initiate a process to transfer your assets to receivers.
                </p>
                <p>
                    Deadlines are not enforced by the contract and is only used for communication purposes.
                    You can transfer the contents of your Cocoon, or ask us to do so, at any point of time.
                </p>
            `);
            ec.utils.bootboxHelp(html);
        };

        self.ownerHelp = function() {
            var html = $(`
                <div class="alert-danger">
                    <p><i class="fa fa-fw fa-warning"></i>WARNING: Do not use an exchange address here.</p>
                </div>
                <p>
                    This should be an address whose private key you control.
                    You do not need to have this key available on the browser for creating the Cocoon or to transfer assets to the Cocoon.
                </p>
                <p>
                    You will have to use it only when you wish to <i>transfer assets from</i> the Cocoon to a receiver address.
                </p>
                <p>
                    If you lose the private key associated with this address you can ask us to transfer all your assets from the Cocoon to a receiver address.
                </p>
            `);
            ec.utils.bootboxHelp(html);
        };

        self.receiverHelp = function() {
            var html = $(`
                <p>
                    These are the only addresses to which your assets can be transfered to from the Cocoon.
                </p>
                <p>
                    If you do not renew the deadline of the Cocoon we will contact the email ids associated with the receiver addresses and transfer the contents of the Cocoon to the receiver once they are prepared to receive it.
                </p>
                <p>
                    You will have to add at least two receiver addresses to the Cocoon to ensure that losing access to one of your receiver will not cause you to lose all your assets.
                </p>
            `);
            ec.utils.bootboxHelp(html);
        };
    },
    template: {require: 'text!/templates/components/cocoon-input.html'}
});


ko.components.register('token-input', {
    viewModel: function(params) {
        var self = this;

        self.onSuccess = params.onSuccess || function() {};

        self.tokenName = ko.observable().extend({required: true});
        self.tokenAddress = ko.observable('').extend({required: true, walletAddress: true});

        self.addToken = function () {
            if (!self.tokenName.isValid()) {
                ec.utils.bootboxError('Please enter a name for the token.');
                return;
            }
            else if (!self.tokenAddress.isValid()) {
                if (self.tokenAddress() === '') {
                    ec.utils.bootboxError('Please enter the address of the token contract.');
                }
                else {
                    ec.utils.bootboxError('The token address you have entered is not a valid ethereum address.');
                }
                return;
            }
            else {
                var data = {
                    network_id: window.Globals.networkId,
                    token_name: self.tokenName(),
                    token_address: self.tokenAddress()
                }
                ec.utils.ajax('contracts', 'views', 'create_token', data, function(response) {
                    if (!response.success) {
                        ec.utils.bootboxError('Could not add the token. Please try again.');
                        return;
                    }
                    self.onSuccess(response.data);
                });
            }
        };
    },
    template: {require: 'text!/templates/components/token-input.html'}
});
