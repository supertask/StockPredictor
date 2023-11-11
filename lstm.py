import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import numpy as np

# データの読み込み
nikkei_data = pd.read_csv('data_creator/fixed_output/fixed_nikkei_225.csv')
unemployment_data = pd.read_csv('data_creator/fixed_output/fixed_unemployment_rate.csv')

# 日付をdatetimeオブジェクトに変換
nikkei_data['Date'] = pd.to_datetime(nikkei_data['Date'])
unemployment_data['公表日時'] = pd.to_datetime(unemployment_data['公表日時'])

# 失業率データのカラム名変更
unemployment_data.rename(columns={'公表日時': 'Date', '結果（%）': 'Unemployment Rate'}, inplace=True)

# 必要なカラムのみを選択
nikkei_data = nikkei_data[['Date', 'Close']]

# データセットの結合
combined_data = pd.merge(nikkei_data, unemployment_data[['Date', 'Unemployment Rate']], on='Date', how='left')
combined_data['Unemployment Rate'] = combined_data['Unemployment Rate'].fillna(method='ffill')

# 欠損値の削除
combined_data.dropna(inplace=True)
combined_data.reset_index(drop=True, inplace=True)

# 特徴量とターゲットの選択
features = combined_data[['Close', 'Unemployment Rate']]
target = combined_data['Close']

# スケーリング
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_features = scaler.fit_transform(features)
scaled_target = scaler.fit_transform(target.values.reshape(-1, 1))

# データセットの準備
def create_dataset(features, target, look_back):
    dataX, dataY = [], []
    for i in range(len(features) - look_back - 1):
        a = features[i:(i + look_back), :]
        dataX.append(a)
        dataY.append(target[i + look_back, 0])
    return np.array(dataX), np.array(dataY)

look_back = 60
X, y = create_dataset(scaled_features, scaled_target, look_back)

# トレーニングセットとテストセットの分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# LSTMモデルの構築
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(units=1))

# モデルのコンパイル
model.compile(optimizer='adam', loss='mean_squared_error')

# モデルのトレーニング
history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test), verbose=1)

# モデルサマリーの表示
model.summary()
