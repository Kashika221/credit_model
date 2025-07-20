# Wallet Credit Scoring

This project provides a one-step Python pipeline to compute **credit scores (0-1000)** for Ethereum wallets interacting with the Aave V2 protocol based on their **historical DeFi transaction behavior**. The script processes raw JSON transaction data and outputs credit scores for each wallet.

---

##  Project Overview

The goal is to assess the reliability of DeFi users through their historical behavior on the Aave V2 protocol. This is useful for risk analysis, DeFi lending platforms, and DeFi-native credit underwriting.

---

## ⚙ Features Engineered

The following features are extracted for each wallet:

* **Total deposits, borrows, repayments, redemptions (USD value)**
* **Number of each action type**
* **Repayment rate** = total repaid / total borrowed
* **Redemption rate** = total redeemed / total deposited
* **Activity diversity** = number of distinct action types used
* **Average transaction size**
* **Engagement score** = number of transactions

---

## Scoring Logic

The credit score (0–1000) is calculated using a weighted function of normalized behavioral features:

* Higher repayment rate, redemption rate, and deposit size → higher score.
* Low activity, heavy borrowing without repayment → lower score.
* Wallets involved in liquidation or only performing borrow without repayment are penalized.

You can plug in your own scoring model as needed (e.g., train a classifier or regressor).

---

## Input Format

The input is a `.json` file containing a list of wallet transaction records with the following structure:

```json
[
  {
    "userWallet": "0x...",
    "action": "deposit",
    "timestamp": 1629178166,
    "actionData": {
      "amount": "2000000000",
      "assetSymbol": "USDC",
      "assetPriceUSD": "0.99"
    }
  },
  ...
]
```

---

## 🛠 Installation

```bash
git clone https://github.com/yourname/aave-credit-score
cd aave-credit-score
pip install -r requirements.txt
```

### `requirements.txt`

```txt
pandas
numpy
```

---

## 🚀 Usage

```bash
python app.py
```

Or directly in Python:

```python
from app import compute_credit_scores

scores = compute_credit_scores("user-wallet-transactions.json")
print(scores.head())
```

---

## Output

The result is a `DataFrame` (or CSV) with:

| userWallet                                 | credit\_score |
| ------------------------------------------ | ------------- |
| 0x00000000001accfa9cef68cf5371a23025b6d4b6 | 812           |
| 0x1a2b3c4d5e6f...                          | 593           |

---

##  Notes

* All amounts are converted to **USD** using `assetPriceUSD`.
* Make sure the `amount` field is interpreted in its correct unit (usually needs dividing by `10^asset_decimals`).
* Script is currently **rule-based**, but can be extended to supervised learning using labeled examples.

---
