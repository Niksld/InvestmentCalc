import requests

url= 'https://v6.exchangerate-api.com/v6/372620cbf549ea6f6928b902/latest/USD'
response = requests.get(url)
data = response.json()
# Initialize variables
total_investment = 0
share_price = 0

# Input annual investment (one-time question)
annual_investment = float(input("Enter the total annual investment amount in CZK : "))

# Input share price (asked every time)
share_price = float(input("Enter the current share price: "))
share_price_czk = share_price * data["conversion_rates"]["CZK"]
# Calculate monthly investment
monthly_investment = annual_investment / 12

# Calculate number of shares to buy
shares_to_buy = monthly_investment / share_price_czk

# Display the result
print("-------------------------------------------")
print(f"You should buy {shares_to_buy:.3f} shares this month.")
print("-------------------------------------------")
print("Price per share in CZK:",share_price_czk)
print("Monthly investment:",monthly_investment)