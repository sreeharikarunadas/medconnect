# medconnect

A Patient Health Record Management System Using Blockchain Technology

# 🏥 Blockchain-based Healthcare Record Management System

A decentralized healthcare platform built with Flask, MongoDB, and Web3.py, integrating **Binance Smart Chain (BSC) Testnet**, **MetaMask**, and **IPFS** to securely manage patient records and diagnostic data.

---

 🚀 Key Features

- ✅ Patient & Doctor Registration/Login
- 📄 Patient Admission & Consultation Forms
- 📁 Upload Medical Records (PDF, JPG, PNG, JPEG)
- 🔑 Secure Access via Auto-Generated Access Key
- 📊 Auto-generated Diagnostic Reports (Graph + PDF)
- 📅 Appointment Booking by Specialization
- 🔐 MetaMask Wallet Integration for Blockchain Transactions
- 🛢️ IPFS File Upload with Hash Stored on BSC Testnet

---

 🧱 Tech Stack

| Component       | Technology Used                          |
|----------------|-------------------------------------------|
| Backend         | Flask, Python, MongoDB                   |
| Frontend        | HTML, CSS, Bootstrap, Jinja2             |
| Blockchain      | Solidity Smart Contract on BSC Testnet   |
| Wallet Support  | MetaMask                                 |
| Storage         | IPFS (via Pinata API)                    |
| Blockchain SDK  | Web3.py, Web3.js                         |
| Reporting       | ReportLab, Matplotlib, pdfkit, FPDF      |

---

 📁 Project Structure


📦 project-root
├── app.py                       # Flask backend
├── requirements.txt             # Python dependencies
├── healthCare_.sol             # Solidity Smart Contract
├── templates/                  # HTML pages
├── static/
│   ├── uploads/                # Uploaded medical records
│   ├── reports/                # Diagnostic report images
│   └── logo.png                # Logo used in PDF reports
├── venv/                       # Python virtual environment
└── README.md


---

 🛠️ Setup Instructions

 1. Unzip the project


 2. Create and Activate Virtual Environment
python -m venv venv
venv\Scripts\activate 


 3. Install Required Packages
pip install -r requirements.txt


 4. Run MongoDB Locally
Ensure MongoDB is running at:
mongodb://localhost:27017/


 5. Start the Flask Server
python app.py
Your app will be live at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

 🌐 BSC Testnet & MetaMask Setup

1. Open MetaMask browser extension.
2. Click the network dropdown > **Add Network**.
3. Enter the following details:


Network Name: BSC Testnet
New RPC URL: https://data-seed-prebsc-1-s1.binance.org:8545/
Chain ID: 97
Currency Symbol: BNB
Block Explorer URL: https://testnet.bscscan.com


4. Save and switch to this network.
5. Fund your wallet using a [BSC Testnet Faucet](https://testnet.bnbchain.org/faucet-smart).

---

 🔐 Smart Contract Info

- **File**: `healthCare_.sol`
- **Deployed On**: [BSC Testnet](https://testnet.bscscan.com)
- **Contract Address**: [`0x6b10b1bb38aa4893118318e42940c88ef29ee441`](https://testnet.bscscan.com/address/0x6b10b1bb38aa4893118318e42940c88ef29ee441#readContract)

You can interact with this contract using Web3.js or through MetaMask transactions.

---

 📦 IPFS Integration

- Uses Pinata or IPFS API to upload patient documents.
- Returns a unique hash which is stored in MongoDB and on BSC.
- Doctors and patients can retrieve and validate data using the hash.

---

 🧪 Functional Modules

 🧍 User Module
- Register/Login as Patient or Doctor
- Each user provides a MetaMask wallet address

 📄 Patient Module
- Submit admission forms
- Upload medical records
- View consultation reports
- Book appointments by specialization
- View access-controlled diagnostic reports

 🩺 Doctor Module
- Review pending admissions
- Fill consultation data
- Generate and view diagnostic charts
- Store diagnostic metadata on blockchain

---

 ✅ Sample Login Flow

1. **Patient** logs in → fills admission form → uploads reports → receives access key.
2. **Doctor** logs in → reviews patient data → submits consultation → diagnostic report is generated.
3. Report image + details are turned into PDF → available for download by patient.

---

 🙌 Acknowledgements

- [Binance Smart Chain Testnet](https://testnet.bscscan.com)
- [MetaMask Wallet](https://metamask.io/)
- [IPFS](https://ipfs.tech/)
- [MongoDB](https://www.mongodb.com/)
- [Flask Web Framework](https://flask.palletsprojects.com/)


---
