var ec = ec || {};
ec.utils = {};

ec.utils.get_ajax_url = function(module, file, method) {
    return '/ajax?module=' + module + '&file=' + file + '&method=' + method;
};

ec.utils.get_eajax_url = function(module, file, method) {
    return '/eajax?module=' + module + '&file=' + file + '&method=' + method;
};

ec.utils.ajax = function(module, file, method, data, success, error) {
    success = success || console.log;
    error = error || function() {
        // Tell the server what went wrong?
        console.log(arguments);
        ec.utils.bootboxError('An unexpected error occurred while processing your request. Please try again after some time.');
    };

    if (typeof success === 'function' &&
        typeof error === 'function' &&
        typeof module === 'string' &&
        typeof file === 'string' &&
        typeof method === 'string' &&
        typeof data === 'object') {
        return $.ajax({
            method: 'POST',
            contentType: 'application/json',
            url: ec.utils.get_ajax_url(module, file, method),
            data: JSON.stringify(data),
            success: success,
            error: error
        });
    }
    else {
        console.error('Invalid param type found:', module, file, method, data, success, error);
    }
};

ec.utils.eajax = function(module, file, method, data, success, error) {
    success = success || console.log;
    error = error || function() {
        // Tell the server what went wrong?
        console.log(arguments);
        ec.utils.bootboxError('An unexpected error occurred while processing your request. Please try again after some time.');
    };

    if (typeof success === 'function' &&
        typeof error === 'function' &&
        typeof module === 'string' &&
        typeof file === 'string' &&
        typeof method === 'string' &&
        typeof data === 'object') {
        return $.ajax({
            method: 'POST',
            contentType: 'application/json',
            url: ec.utils.get_eajax_url(module, file, method),
            data: JSON.stringify(data),
            success: success,
            error: error
        });
    }
    else {
        console.error('Invalid param type found:', module, file, method, data, success, error);
    }
};

ec.utils.wait = function(params) {
    var message;
    if (typeof params === 'string') {
        message = params;
    }
    else {
        message = params.message || 'Please wait for the transaction to be finished.';
    }
    bootbox.dialog({
        title: 'Please wait...',
        message: message,
        closeButton: false
    });
};

ec.utils.generateEtherscanAnchorTag = function(type, address, text) {
    return '<a style="font-family: monospace;" href="' + ec.utils.getEtherscanLink(address) + '" target="_blank">' + text + '</a>';
};

ec.utils.refreshPage = function() {
    window.location.reload();
};

ec.utils.doNothing = function() {};

ec.utils.bootboxError = function(message, callback) {
    var _callback = ec.utils.doNothing;
    if (typeof message == 'object') {
        if (message.pageRefresh) {
            _callback = ec.utils.refreshPage;
        }
        else if (message.callback) {
            _callback = message.callback;
        }
        else if (typeof callback === 'function') {
            _callback = callback;
        }
        if (typeof message.message === 'string') {
            message = message.message;
        }
        else {
            message = JSON.stringify(message);
        }
    }
    bootbox.alert({
        title: 'Error',
        message: message,
        callback: _callback
    });
};

ec.utils.bootboxHelp = function(message, callback) {
    if (typeof callback !== 'function') {
        callback = function(){};
    }
    bootbox.alert({title: 'Help', message: message, callback: callback});
};

ec.utils.bootboxInformation = function(message, callback) {
    if (typeof callback !== 'function') {
        callback = function(){};
    }
    bootbox.alert({title: 'Information', message: message, callback: callback});
};

ec.utils.errorHandler = function(response, method) {
    var message = response.message;
    var type = response.type;
    var pageRefresh = response.pageRefresh || false;

    if (typeof message !== 'string') {
        return;
    }

    if (type === 'alert-error') {
        ec.utils.bootboxError({message: message, pageRefresh: pageRefresh});
    }
    else if (type === 'alert-information') {
        ec.utils.bootboxInformation(message);
    }
    else if (typeof method === 'function') {
        method(message);
    }
    else {
        ec.utils.bootboxError(message);
    }
};

ec.utils.linkify = function(link) {
    if (link) {
        if (!(link.startsWith('http://') || link.startsWith('https://'))) {
            return 'http://' + link;
        }
        else {
            return link;
        }
    }
    else {
        return '';
    }
}

ec.utils.toHex = function(s) {
    // utf8 to latin1
    var s = unescape(encodeURIComponent(s));
    var h = '';
    for (var i = 0; i < s.length; i++) {
        h += s.charCodeAt(i).toString(16);
    }
    return h;
}

ec.utils.fromHex = function(h) {
    var s = '';
    for (var i = 0; i < h.length; i+=2) {
        s += String.fromCharCode(parseInt(h.substr(i, 2), 16));
    }
    return decodeURIComponent(escape(s));
}

ec.utils.signMessage = function(message) {
    // TODO: Figure out why this isn't working
    // var hexEncodedMessage = '0x' + ec.utils.toHex(message);
    // web3.personal.sign(hexEncodedMessage, web3.eth.accounts[0], console.log);

    web3.eth.sign(web3.eth.accounts[0], message, console.log);
};

ec.utils.getQueryStringValue = function(key) {
    key = key.replace(/[*+?^$.\[\]{}()|\\\/]/g, "\\$&"); // escape RegEx meta chars
    var match = location.search.match(new RegExp("[?&]"+key+"=([^&]+)(&|$)"));
    return match && decodeURIComponent(match[1].replace(/\+/g, " "));
};

ec.utils.getEtherscanLink = function(value) {

    if (value.startsWith('https://github.com')) {
        // Some DApps have contracts which have to be deployed
        // multiple times, once for each user. Eg: Ethlend.
        // In that case we'll have a link to the source code on
        // Github.
        return value;
    }

    var protocol = 'https://';

    if (Globals.networkName === 'mainnet') {
        var network = '';
    }
    else {
        var network = Globals.networkName + '.';
    }

    if (value.length === 66) {
        var tx_or_address = 'tx/';
    }
    else {
        var tx_or_address = 'address/';
    }

    return protocol + network + 'etherscan.io/' + tx_or_address + value;
}

ec.utils.initWeb3 = function(vm) {
    vm.web3 = {};
    vm.web3.available = ko.observable(false);
    vm.web3.err = ko.observable('');
    vm.web3.unlocked = ko.observable(false);
    vm.web3.usable = ko.observable(false);
    vm.web3.web3 = ko.observable(undefined);
    vm.web3.network = ko.observable('0');
    vm.web3.accounts = ko.observableArray();

    if (typeof web3 === 'undefined') {
        vm.web3.err('Web3 was not found in your browser. Please install MetaMask and refresh the page.');
        return;
    }

    vm.web3.available(true);
    vm.web3.web3 = new Web3(web3.currentProvider);

    vm.web3.web3.eth.getAccounts(function(err, accounts) {
        if (err) {
            vm.web3.err('An error occurred while getting accounts from MetaMask. Please unlock an account and refresh the page.');
            return;
        }
        if (accounts.length === 0) {
            vm.web3.err('No accounts were found in MetaMask. Please unlock an account and refresh the page.');
            return;
        }
        vm.web3.unlocked(true);
        vm.web3.accounts(accounts);
        vm.web3.usable(true);
    });

    function checkNetwork() {
        vm.web3.web3.version.getNetwork(function(err, networkId) {
            if (err || networkId !== Globals.networkId) {
                vm.web3.network('0');
                vm.web3.usable(false);
                vm.web3.err('Please connect to the Ethereum ' + Globals.networkName + ' network and refresh the page.');
            }
        });
    };
    checkNetwork();

    // If everything is set at the beginning
    vm.web3.interval = setInterval(function() {
        vm.web3.web3.eth.getAccounts(function(err, accounts) {
            if (accounts === null || accounts === undefined || accounts.length === 0) {
                vm.web3.err('No accounts were found in MetaMask. Please unlock an account and refresh the page.');
                vm.web3.usable(false);
                vm.web3.unlocked(false);
                vm.web3.accounts([]);
            }
            else if (vm.web3.accounts().length !== accounts.length ||
                     vm.web3.accounts()[0] !== accounts[0]) { // TODO: Check if all accounts are correct
                vm.web3.accounts(accounts);
                vm.web3.unlocked(true);
                vm.web3.usable(true);
                checkNetwork();
            }
        });
    }, 2000);
};
