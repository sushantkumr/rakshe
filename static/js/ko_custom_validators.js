ko.validation.rules['number'] = {
    validator: function(val) {
        return $.isNumeric(val);
    },
    message: 'This field must have a numerical value.'
};

ko.validation.rules['positive'] = {
    validator: function(val) {
        return Number(val) > 0;
    },
    message: 'This field must have a positive numerical value.'
};

ko.validation.rules['nonNegative'] = {
    validator: function(val) {
        return val >= 0;
    },
    message: 'This field must have a non-negative numerical value.'
};

ko.validation.rules['lessThanOrEqual'] = {
    validator: function(val, otherVal) {
        if (typeof otherVal === 'function') {
            otherVal = otherVal();
        }
        return Number(val) <= Number(otherVal);
    },
    message: function(otherVal) {
        if (typeof otherVal === 'function') {
            otherVal = otherVal();
        }
        return 'Value should be less than or equal to ' + otherVal;
    }
};

ko.validation.rules['emailId'] = {
    validator: function(val) {
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(val).toLowerCase());
    },
    message: 'Enter a valid Email-id'
};

ko.validation.rules['passwordMatch'] = {
    validator: function(val, otherVal) {
        return val === otherVal;
    },
    message: 'Passwords do not match.'
};

ko.validation.rules['cocooonRange'] = {
    validator: function(val) {
        return Number(val) >= 2 && Number(val) <= 7;
    },
    message: 'Cocoon interval should be between 2 and 7 months.'
};

ko.validation.rules['walletAddress'] = {
    // https://github.com/ethereum/web3.js/blob/306680f8d917f912d9c6ed632d133274909cee87/lib/utils/utils.js#L402
    validator: function (address) {
        var isChecksumAddress = function (address) {
            // Check each case
            address = address.replace('0x','');
            var addressHash = sha3(address.toLowerCase());

            for (var i = 0; i < 40; i++ ) {
                // the nth letter should be uppercase if the nth digit of casemap is 1
                if ((parseInt(addressHash[i], 16) > 7 && address[i].toUpperCase() !== address[i]) || (parseInt(addressHash[i], 16) <= 7 && address[i].toLowerCase() !== address[i])) {
                    return false;
                }
            }
            return true;
        }

        if (!/^(0x)?[0-9a-f]{40}$/i.test(address)) {
            // check if it has the basic requirements of an address
            return false;
        } else if (/^(0x)?[0-9a-f]{40}$/.test(address) || /^(0x)?[0-9A-F]{40}$/.test(address)) {
            // If it's all small caps or all all caps, return true
            return true;
        } else {
            // Otherwise check each case
            return isChecksumAddress(address);
        }
    },
    message: 'This is not a valid Ethereum wallet address.'
};

ko.validation.rules['password'] = {
    validator: function(val) {
        return (val.length >= 12 && val.length <= 100);
    },
    message: 'Password should be 12 to 100 characters long.'
};

ko.validation.rules['username'] = {
    validator: function(val) {
        return (val.length >= 5 && val.length <= 100);
    },
    message: 'Username should be 5 to 100 characters long.'
};

ko.validation.rules['usernameChars'] = {
    validator: function(val) {
        return /^[a-zA-Z0-9_]*$/.test(val);
    },
    message: 'Only characters a-z, A-Z, 0-9 and _ are allowed.'
};

ko.validation.registerExtenders();
