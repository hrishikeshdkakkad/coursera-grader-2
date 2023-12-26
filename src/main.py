import os
import requests
import json

SCORE_SUCCESSFULL_CONTRACT_DEPLOYMENT = 30
SCORE_SUCCESSFULL_NFT_MINT = 30
SCORE_SUCCESSFULL_TRASFER = 40

feedbackRes = []

def send_feedback(score, msg):
    post = {'fractionalScore': score, 'feedback': msg}
    # Optional: this goes to container log and is best practice for debugging purpose
    print(json.dumps(post))
    # This is required for actual feedback to be surfaced
    with open(os.getenv('OUTPUT_PATH'), "w") as outfile:
        json.dump(post, outfile)

def get_transactions_by_address(api_key, address):
    url = "https://api-sepolia.etherscan.io/api"
    params = {
        "module": "account",
        "action": "tokennfttx",
        "contractAddress": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def calculateDeploymentScore(transactions):
    score = 0
    trxs = json.loads(json.dumps(transactions))
    if(len(trxs["result"]) < 1):
       feedbackRes.append("Lost 100 points - contract is not deployed as per standards. Please re-verify.")
       return score
    feedbackRes.append("Successfully contract deployment: 30 points.")
    score += SCORE_SUCCESSFULL_CONTRACT_DEPLOYMENT
    for i in range(len(trxs["result"])):
        del trxs["result"][i]["input"]
    return score

def calculateNftMintScore(transactions, contract_address, decentralized_id):
    score = 0
    trxs = json.loads(json.dumps(transactions))
    if(len(trxs["result"]) < 1):
       return score
    for i in range(len(trxs["result"])):
       curr = trxs["result"][i]
       if(curr["contractAddress"].upper() == contract_address.upper() and curr["to"].upper() == decentralized_id.upper()):
            feedbackRes.append("Successfully minted: 30 points.")
            score += SCORE_SUCCESSFULL_NFT_MINT;
            break
    
    if (score == 0):
        feedbackRes.append("Mint function not implemented as per requirements. Refer to the handout. Lost 30 points for mint.")
    return score

def calculateTransferFromScore(transactions, from_address, benefeciary_id):
    score = 0
    trxs = json.loads(json.dumps(transactions))
    if(len(trxs["result"]) < 1):
       return score
    for i in range(len(trxs["result"])):
       curr = trxs["result"][i]
       if(curr["from"].upper() == from_address.upper() and curr["to"].upper() == benefeciary_id.upper()):
            feedbackRes.append("Successfully transfer: 40 points.")
            score += SCORE_SUCCESSFULL_TRASFER;
            break
       
    if(score == 0):
        feedbackRes.append("Transfer function not implemented as per requirements. Refer to the handout. Lost 30 points for mint.")
    return score

def init(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    contract_address = decentralized_id = beneficiary_address = None
    for line in lines:
        if "contract_address" in line:
            contract_address = line.split('=')[1].strip().replace('"', '')
        elif "decentralized_id" in line:
            decentralized_id = line.split('=')[1].strip().replace('"', '')
        elif "beneficiary_address" in line:
            beneficiary_address = line.split('=')[1].strip().replace('"', '')

    if(beneficiary_address and decentralized_id and beneficiary_address):
        return contract_address, decentralized_id, beneficiary_address
    raise RuntimeError

api_key = "3HZ5V116QT4B7TTASVGFH7A5EZCZGAJTKD"


file_path = os.getenv('USER_FILE_PATH')
if not file_path:
    raise ValueError("Environment variable 'USER_FILE_PATH' not set")
contract_address, decentralized_id, beneficiary_address = init(file_path)
transactions = get_transactions_by_address(api_key, contract_address)


if transactions:
    scores = [
        calculateDeploymentScore(transactions),
        calculateNftMintScore(transactions, contract_address, decentralized_id),
        calculateTransferFromScore(transactions, decentralized_id, beneficiary_address)
    ]

    total = 0
    for j in range(len(scores)):
        total += scores[j]

    separator = " "
    send_feedback(total / 100, separator.join(feedbackRes))
