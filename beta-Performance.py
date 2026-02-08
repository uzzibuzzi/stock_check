import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def generate_stock_analysis(ticker_symbol, benchmark_symbol, years=3):
    # 1. Download Historical Data
    print(f"Fetching data for {ticker_symbol} and {benchmark_symbol}...")
    tickers = [ticker_symbol, benchmark_symbol]
    data = yf.download(tickers, period=f"{years}y", interval="1wk")['Close']
    
    # Drop missing values
    df = data.dropna()
    
    # 2. Normalization (Base 100)
    # Formula: (Current Price / Starting Price) * 100
    df_norm = (df / df.iloc[0]) * 100
    
    # 3. Calculate the Difference (Spread)
    # Relative performance: Stock minus Benchmark
    df_norm['Spread'] = df_norm[ticker_symbol] - df_norm[benchmark_symbol]
    
    # 4. Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                   gridspec_kw={'height_ratios': [2, 1]}, 
                                   sharex=True)
    
    # Top Plot: Normalized Prices
    ax1.plot(df_norm.index, df_norm[benchmark_symbol], label=f'{benchmark_symbol} (Normalized)', color='#00a3e0', lw=2)
    ax1.plot(df_norm.index, df_norm[ticker_symbol], label=f'{ticker_symbol} (Normalized)', color='#d31336', lw=2)
    ax1.set_title(f'{years}-Year Performance: {ticker_symbol} vs {benchmark_symbol}', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Index (Start = 100)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Bottom Plot: The Spread (Difference)
    ax2.fill_between(df_norm.index, df_norm['Spread'], 0, 
                     where=(df_norm['Spread'] >= 0), color='green', alpha=0.3, label='Outperforming')
    ax2.fill_between(df_norm.index, df_norm['Spread'], 0, 
                     where=(df_norm['Spread'] < 0), color='red', alpha=0.3, label='Underperforming')
    ax2.plot(df_norm.index, df_norm['Spread'], color='purple', lw=1.5)
    ax2.axhline(0, color='black', lw=1, ls='--')
    ax2.set_title('Performance Spread (Alpha)', fontsize=12)
    ax2.set_ylabel('Difference (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# Run the analysis for Lululemon vs Nasdaq 100
# Tickers: LULU and ^NDX (Nasdaq 100 Index)
generate_stock_analysis('LULU', '^NDX')
