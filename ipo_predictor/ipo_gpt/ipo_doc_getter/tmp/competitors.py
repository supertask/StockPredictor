from yahoo_fin import stock_info as si

ticker = "5588.T"
competitors = si.get_company_info(ticker)["Competitors"]
print("Competitors of", ticker, "are:", competitors)
