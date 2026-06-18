import pdfplumber
import pandas as pd
import re

# STEP 1: Extract
with pdfplumber.open("gpay_statement.pdf") as pdf:
    all_text = ""
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text += text

# STEP 2: Fix spacing
spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', all_text)
spaced = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', spaced)

# STEP 3: Parse line by line
lines = spaced.split('\n')
transactions = []

for line in lines:
    # Match lines like: 01Mar,2026 Paidto Welcome Medical Stores ₹20
    match = re.match(r'(\d{2}[A-Za-z]{3},\d{4})\s+(Paidto|Receivedfrom)\s+(.+?)\s+(₹[\d,]+\.?\d*)$', line.strip())
    if match:
        date, txn_type, merchant, amount = match.groups()
        transactions.append({
            'Date': date,
            'Type': 'Paid' if 'Paid' in txn_type else 'Received',
            'Merchant': merchant.strip(),
            'Amount': float(amount.replace('₹','').replace(',',''))
        })

df = pd.DataFrame(transactions)
print(f"Transactions found: {len(df)}")
print(df.head(10))

df.to_csv('transactions.csv', index=False)
print("\nSaved transactions.csv")

import matplotlib.pyplot as plt
import seaborn as sns

# STEP 5: Categorize
def categorize(merchant):
    merchant = merchant.lower()
    if any(x in merchant for x in ['food', 'cafe', 'restaurant', 'hotel', 'juice', 'biryani', 'sweets', 'justin']):
        return 'Food'
    elif any(x in merchant for x in ['college', 'school', 'fees', 'sdsm']):
        return 'Education'
    elif any(x in merchant for x in ['medical', 'pharmacy', 'hospital', 'clinic']):
        return 'Medical'
    elif any(x in merchant for x in ['railway', 'uts', 'travel', 'bus']):
        return 'Travel'
    elif any(x in merchant for x in ['apple', 'google', 'amazon', 'netflix', 'spotify']):
        return 'Subscriptions'
    elif any(x in merchant for x in ['nitin', 'satyam', 'gayatri', 'patil', 'gaikwad']):
        return 'People'
    else:
        return 'Others'

df['Category'] = df['Merchant'].apply(categorize)
df['Date'] = pd.to_datetime(df['Date'], format='%d%b,%Y')
df['Month'] = df['Date'].dt.strftime('%B')

paid_df = df[df['Type'] == 'Paid']

# GRAPH 1: Spending by Category
plt.figure(figsize=(8,5))
cat_spend = paid_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
sns.barplot(x=cat_spend.values, y=cat_spend.index, palette='magma')
plt.title('Total Spending by Category')
plt.xlabel('Amount (₹)')
plt.tight_layout()
plt.savefig('graph1_category.png')
plt.show()

# GRAPH 2: Monthly Spending
plt.figure(figsize=(8,5))
month_spend = paid_df.groupby('Month')['Amount'].sum()
sns.barplot(x=month_spend.index, y=month_spend.values, palette='Blues_d')
plt.title('Monthly Spending')
plt.ylabel('Amount (₹)')
plt.tight_layout()
plt.savefig('graph2_monthly.png')
plt.show()

# GRAPH 3: Top 10 Merchants
plt.figure(figsize=(8,5))
top_merchants = paid_df.groupby('Merchant')['Amount'].sum().sort_values(ascending=False).head(10)
sns.barplot(x=top_merchants.values, y=top_merchants.index, palette='rocket')
plt.title('Top 10 Merchants')
plt.xlabel('Amount (₹)')
plt.tight_layout()
plt.savefig('graph3_merchants.png')
plt.show()

# GRAPH 4: Paid vs Received
plt.figure(figsize=(5,5))
summary = df.groupby('Type')['Amount'].sum()
plt.pie(summary.values, labels=summary.index, autopct='%1.1f%%', colors=['#ff6b6b','#6bcb77'])
plt.title('Paid vs Received')
plt.tight_layout()
plt.savefig('graph4_paidvsreceived.png')
plt.show()

# GRAPH 5: Spending Over Time
plt.figure(figsize=(10,4))
daily = paid_df.groupby('Date')['Amount'].sum()
plt.plot(daily.index, daily.values, marker='o', color='steelblue')
plt.title('Daily Spending Over Time')
plt.xlabel('Date')
plt.ylabel('Amount (₹)')
plt.tight_layout()
plt.savefig('graph5_timeline.png')
plt.show()

print("\nAll 5 graphs saved!")
print(f"\nTotal Spent: ₹{paid_df['Amount'].sum():,.2f}")
print(f"Total Received: ₹{df[df['Type']=='Received']['Amount'].sum():,.2f}")
print(f"\nTop category: {cat_spend.index[0]} (₹{cat_spend.values[0]:,.2f})")