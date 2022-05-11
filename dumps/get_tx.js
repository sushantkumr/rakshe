function getTransactionsByAccount(myaccount, startBlockNumber, endBlockNumber) {
  results = [];
  if (endBlockNumber == null) {
    endBlockNumber = eth.blockNumber;
    console.log("Using endBlockNumber: " + endBlockNumber);
  }
  if (startBlockNumber == null) {
    startBlockNumber = endBlockNumber - 1000;
    console.log("Using startBlockNumber: " + startBlockNumber);
  }
  console.log("Searching for transactions to/from account \"" + myaccount + "\" within blocks "  + startBlockNumber + " and " + endBlockNumber);

  for (var i = startBlockNumber; i <= endBlockNumber; i++) {
    if (i % 1000 == 0) {
      console.log("Searching block " + i);
    }
    var block = eth.getBlock(i, true);
    if (block != null && block.transactions != null) {
      block.transactions.forEach( function(e) {
        // if (myaccount == "*" || myaccount == e.from || myaccount == e.to) {
        if (myaccount == "*" || myaccount == e.to) {
          var tx = eth.getTransactionReceipt(e.hash);
          var result = {
            'hash': e.hash,
            'block_number': e.blockNumber,
            'contract': e.to,
            'gas_limit': e.gas,
            'gas_price': e.gasPrice,
            'gas_used': tx.gasUsed,
            'time_stamp': block.timestamp
          };
          k = e
          results.push(result);
          // console.log("  tx hash          : " + e.hash + "\n"
          //   + "   nonce           : " + e.nonce + "\n"
          //   + "   blockHash       : " + e.blockHash + "\n"
          //   + "   blockNumber     : " + e.blockNumber + "\n"
          //   + "   transactionIndex: " + e.transactionIndex + "\n"
          //   + "   from            : " + e.from + "\n" 
          //   + "   to              : " + e.to + "\n"
          //   + "   value           : " + e.value + "\n"
          //   + "   time            : " + block.timestamp + " " + new Date(block.timestamp * 1000).toGMTString() + "\n"
          //   + "   gasPrice        : " + e.gasPrice + "\n"
          //   + "   gas             : " + e.gas + "\n"
          //   + "   input           : " + e.input);
        }
      })
    }
  }
  console.log(JSON.stringify(results))
}

// getTransactionsByAccount('0x8d12a197cb00d4747a1fe03395095ce2a5cc6819', 5024061, 5024062)
// results
// getTransactionsByAccount('0x805129c7144688224c122c924e3855d5b4fa01d8', 3174909, 4130612);
getTransactionsByAccount('0x805129c7144688224c122c924e3855d5b4fa01d8', 3174910, 4130611);

