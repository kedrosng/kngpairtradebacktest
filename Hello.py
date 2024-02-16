import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

def run_strategy():
    # Get the stock symbols from the user input
    stock1_symbol = st.text_input("Enter the ticker symbol for Stock1:")
    stock2_symbol = st.text_input("Enter the ticker symbol for Stock2:")
    
    if st.button("Run Pair Trading Strategy"):
        try:
            tickers = [stock1_symbol, stock2_symbol]
            
            # Get today's date and calculate the start date as 6 months before today
            today = datetime.date.today()
            six_months_ago = today - datetime.timedelta(days=6*30)
            start_date = six_months_ago.strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')

            # Download historical data
            df = yf.download(tickers, start=start_date, end=end_date)['Close']

            # Calculate the z-score of the spread
            window_length = 20
            df['Spread'] = df[stock1_symbol] - df[stock2_symbol]
            df['Mean'] = df['Spread'].rolling(window=window_length).mean()
            df['Std'] = df['Spread'].rolling(window=window_length).std()
            df['Z_Score'] = (df['Spread'] - df['Mean']) / df['Std']

            # Define the pair trading strategy
            entry_threshold = 1
            exit_threshold = 0.5
            transaction_cost = 0.0005
            in_position = False
            entry_price = 0
            exits = []
            entries = []
            pnl = []
            spread_values = df['Spread'].values
            z_scores = df['Z_Score'].values

            for i in range(1, len(df)):
                # Entry logic
                if not in_position and abs(z_scores[i]) > entry_threshold:
                    in_position = True
                    entry_price = spread_values[i]
                    entries.append((df.index[i], entry_price))

                # Exit logic
                elif in_position and abs(z_scores[i]) < exit_threshold:
                    in_position = False
                    exit_price = spread_values[i]
                    exits.append((df.index[i], exit_price))
                    trade_pnl = exit_price - entry_price - transaction_cost
                    pnl.append(trade_pnl)

            # Plot results
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.plot(df.index, df[stock1_symbol], label=stock1_symbol, color='blue')
            ax.plot(df.index, df[stock2_symbol], label=stock2_symbol, color='red')
            ax.scatter([e[0] for e in entries], [e[1] for e in entries], marker='^', color='green', label='Buy/Sell')
            ax.scatter([e[0] for e in exits], [e[1] for e in exits], marker='v', color='red')
            ax.legend()
            st.pyplot(fig)

            # Calculate and display performance metrics
            cumulative_returns = np.cumsum(pnl)
            returns = np.diff(np.insert(cumulative_returns, 0, 0))
            sharpe_ratio = np.mean(returns) / np.std(returns)
            max_drawdown = np.max(np.maximum.accumulate(cumulative_returns) - cumulative_returns)
            total_return = cumulative_returns[-1]
            st.info(f"Sharpe Ratio: {sharpe_ratio:.2f}\nMax Drawdown: {max_drawdown:.2f}\nTotal Return: {total_return:.2f}\nBest Entry Threshold: {entry_threshold}\nBest Exit Threshold: {exit_threshold}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

st.title("Pair Trading Strategy")
run_strategy()