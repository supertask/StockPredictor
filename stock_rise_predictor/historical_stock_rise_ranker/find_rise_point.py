import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema




def identify_sharp_rise_points(df, short_window=5, long_window=25, volume_increase_factor=2):
    # 短期移動平均と長期移動平均を計算
    df['short_mavg'] = df['Close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['Close'].rolling(window=long_window, min_periods=1).mean()

    # クロスオーバーを見つける
    # 短期が長期をクロスした日をTrueとする
    df['crossover'] = df['short_mavg'] > df['long_mavg']

    # 前日と比較してクロスオーバーが発生したかどうか
    df['crossover_signal'] = df['crossover'] & (~df['crossover'].shift(1))

    # 取引量が急増しているかを確認する
    df['volume_increase'] = df['Volume'] > (df['Volume'].shift(1) * volume_increase_factor)

    # 大きな陽線を確認する（CloseがOpenよりもかなり高い）
    df['large_bull_candle'] = (df['Close'] > df['Open']) & ((df['Close'] - df['Open']) > (df['Close'].shift(1) - df['Open'].shift(1)) * 1.5)

    # 上記条件を全て満たすポイントを特定
    sharp_rise_points = df[df['crossover_signal'] & df['volume_increase'] & df['large_bull_candle']]

    return sharp_rise_points


# 株価データを取得する関数
def get_stock_data(ticker, period='30y'):
    # yfinanceを使用してデータを取得
    data = yf.download(ticker, period=period)
    return data

# 局所的な最小点を求める関数
def find_local_minima(data, window=1):
    # window=平滑化レベル, 月次のトレンドを見たい場合は、20〜22営業日（約1ヶ月）のウィンドウが適切
    # 移動平均を計算（それぞれの日にちのN日後の最小値を取る）
    #data['Min'] = data['Close'].rolling(window=window, center=True).min()
    data['Min'] = data['Low'].rolling(window=window, center=True).min()
    # 局所的な最小点を検出
    local_minima = argrelextrema(data['Min'].values, comparator=np.less_equal, order=window)[0]
    return data.iloc[local_minima]

# 株価データを取得
stock_data = get_stock_data('AAPL')  # 例: Apple Inc.のティッカーシンボルAAPL

# 局所的な最小点を見つける
local_minima_data = find_local_minima(stock_data)


# 極小値間の日数の閾値を設定
min_distance = 90  # 日数

# 最初の極小値を保持
filtered_minima = [local_minima_data.index[0]]

# 次の極小値が前の極小値から指定した日数以上離れているか確認
for current_date in local_minima_data.index[1:]:
    if (current_date - filtered_minima[-1]).days >= min_distance:
        filtered_minima.append(current_date)

# フィルタリングされた極小値のみを含むデータフレームを作成
filtered_local_minima_data = local_minima_data.loc[filtered_minima]





#start_date = '2020-01-01'
#end_date = '2023-11-20'
#local_minima_data_jan_2020 = local_minima_data[start_date:end_date]
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(filtered_local_minima_data)
#print(local_minima_data_jan_2020)