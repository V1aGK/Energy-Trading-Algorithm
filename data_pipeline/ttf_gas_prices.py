import yfinance as yf

ttf = yf.download("TTF=F", start="2018-01-01", end="2025-09-30")
ttf_data = ttf["Close"]["TTF=F"].rename("ttf_gas_price")
ttf_data = ttf_data.resample("D").ffill()
ttf_data = ttf_data.shift(1)  
ttf_data = ttf_data.resample("h").ffill()
ttf_data.index = ttf_data.index.tz_localize("UTC")
ttf_data = ttf_data.to_frame()
ttf_data.to_parquet("data/processed/ttf_gas_prices.parquet")
print(ttf_data.dropna().head(10))
print(ttf_data.shape)
print(ttf_data.index.min(), ttf_data.index.max())