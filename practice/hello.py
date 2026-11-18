loan_amount = 800000
interest_rate = 0.11
years = 5

yearly_interest = loan_amount * interest_rate
total_interest = yearly_interest * years
monthly_interest = yearly_interest / 12

print("Loan amount: ", loan_amount, " Monthly interest: ", monthly_interest)
print("Total interest over ", years, " years: ", total_interest)