import json
import pandas as pd
import ast

def extract_amount(data):
    try:
        return float(data.get("amount", 0)) / 1e6 
    except:
        return 0.0

def compute_credit_scores(json_path: str) -> dict:

    with open(json_path, 'r') as f:
        raw_data = json.load(f)

    df = pd.DataFrame(raw_data)

    df.rename(columns={'userWallet': 'wallet'}, inplace=True)

    if isinstance(df.loc[0, 'actionData'], str):
        df['actionData'] = df['actionData'].apply(ast.literal_eval)

    df['amount'] = df['actionData'].apply(extract_amount)

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df['is_liquidation'] = (df['action'] == 'liquidationcall').astype(int)

    agg_df = df.groupby('wallet').agg(
        num_transactions=('action', 'count'),
        num_deposits=('action', lambda x: (x == 'deposit').sum()),
        total_deposit_amount=('amount', lambda x: x[df.loc[x.index, 'action'] == 'deposit'].sum()),
        num_borrows=('action', lambda x: (x == 'borrow').sum()),
        total_borrow_amount=('amount', lambda x: x[df.loc[x.index, 'action'] == 'borrow'].sum()),
        num_repays=('action', lambda x: (x == 'repay').sum()),
        total_repay_amount=('amount', lambda x: x[df.loc[x.index, 'action'] == 'repay'].sum()),
        num_redeems=('action', lambda x: (x == 'redeemunderlying').sum()),
        total_redeem_amount=('amount', lambda x: x[df.loc[x.index, 'action'] == 'redeemunderlying'].sum()),
        num_liquidations=('is_liquidation', 'sum'),
        first_tx_time=('timestamp', 'min'),
        last_tx_time=('timestamp', 'max')
    ).reset_index()

    agg_df['repay_borrow_ratio'] = agg_df['total_repay_amount'] / agg_df['total_borrow_amount'].replace(0, 1)
    agg_df['deposit_redeem_ratio'] = agg_df['total_deposit_amount'] / (agg_df['total_redeem_amount'] + 1)
    agg_df['borrow_deposit_ratio'] = agg_df['total_borrow_amount'] / (agg_df['total_deposit_amount'] + 1)
    agg_df['avg_time_between_txs'] = (
        (agg_df['last_tx_time'] - agg_df['first_tx_time']).dt.total_seconds() / agg_df['num_transactions'].replace(0, 1)
    )
    agg_df['is_liquidated'] = (agg_df['num_liquidations'] > 0).astype(int)

    def score_wallet(row):
        score = 1000
        if row['is_liquidated']:
            score -= 200
        if row['repay_borrow_ratio'] < 0.8:
            score -= 150
        if row['borrow_deposit_ratio'] > 1.2:
            score -= 100
        if row['num_transactions'] < 3:
            score -= 50
        if row['total_deposit_amount'] < 500:
            score -= 50
        return max(0, min(1000, int(score)))

    agg_df['credit_score'] = agg_df.apply(score_wallet, axis=1)

    score_dict = dict(zip(agg_df['wallet'], agg_df['credit_score']))
    return score_dict

if __name__ == "__main__":
    result = compute_credit_scores("user-wallet-transactions.json")
    print(json.dumps(result, indent=2))