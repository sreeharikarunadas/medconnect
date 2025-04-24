from web3 import Web3

# Connect to Ethereum Node (Replace with your provider)
provider_url = "http://127.0.0.1:7545"  # If using Ganache
web3 = Web3(Web3.HTTPProvider(provider_url))

# Ensure connection is successful
if not web3.is_connected():
    raise Exception("Failed to connect to Ethereum network")

# Smart contract details
contract_address = "0x22b138704A9A6668B1a035fbA2CF6C2dD8f4Fc6D"  # Replace with deployed contract address
contract_abi = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "email",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "objectId",
				"type": "string"
			}
		],
		"name": "addData",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "string",
				"name": "email",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "objectId",
				"type": "string"
			}
		],
		"name": "DataAdded",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "email",
				"type": "string"
			}
		],
		"name": "getData",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Wallet details (Replace with your own details)
account = "0xA4822Ea14957203dFc4b91770869E2978b06eD7E"  # Replace with your Ethereum address
private_key = "0xa157095b784a6125eb25146165aff7901692aa30cd9f7124ce60497a624cc0c2"  # Replace with your private key

# Function to add data
def add_data(email, object_id):
    nonce = web3.eth.get_transaction_count(account)
    txn = contract.functions.addData(email, object_id).build_transaction({
        'from': account,
        'gas': 2000000,
        'gasPrice': web3.to_wei('5', 'gwei'),
        'nonce': nonce
    })
    signed_txn = web3.eth.account.sign_transaction(txn, private_key)
    txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    web3.eth.wait_for_transaction_receipt(txn_hash)
    print(f"Transaction successful: {txn_hash.hex()}")

# Function to get data
def get_data(email):
    object_id = contract.functions.getData(email).call()
    print(f"Object ID for {email}: {object_id}")

# Example Usage
add_data("vallivn@gmail.com", "6563c3a9e437d1a6b37b4b09")  # Replace with actual email and ObjectId
get_data("vallivn@gmail.com")
