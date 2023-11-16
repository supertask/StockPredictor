from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout

from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import os

NIKKEI_MODEL_PATH = 'traned_models/my_nikkei_model.h5'

# データセットの準備
def create_dataset(features, target, look_back):
    dataX, dataY = [], []
    for i in range(len(features) - look_back - 1):
        a = features[i:(i + look_back), :]
        dataX.append(a)
        dataY.append(target[i + look_back, 0])
    return np.array(dataX), np.array(dataY)

def prepare_dataset():
    nikkei_data = pd.read_csv('data_creator/fixed_output/fixed_nikkei_225.csv')
    unemployment_data = pd.read_csv('data_creator/fixed_output/fixed_unemployment_rate.csv')

    nikkei_data['Date'] = pd.to_datetime(nikkei_data['Date'])
    unemployment_data['Date'] = pd.to_datetime(unemployment_data['Date'])
    unemployment_data.rename(columns={'Result(%)': 'Unemployment Rate'}, inplace=True)
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
    scaler_features = MinMaxScaler(feature_range=(0, 1))
    scaler_target = MinMaxScaler(feature_range=(0, 1)) # ターゲット用の別のスケーラー

    scaled_features = scaler_features.fit_transform(features)
    scaled_target = scaler_target.fit_transform(target.values.reshape(-1, 1))

    # データセットの準備
    look_back = 60 #何日間
    X, y = create_dataset(scaled_features, scaled_target, look_back)
    dates = combined_data['Date'].values

    # トレーニングセットとテストセットの分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(X_train.shape[1], X_train.shape[2])

    return X_train, X_test, y_train, y_test, scaler_features, scaler_target, dates


def create_model(model_path):
    if os.path.exists(model_path):
        return load_model(model_path)

    X_train, X_test, y_train, y_test, scaler_features, scaler_target, dates = prepare_dataset()

    # LSTMモデルの構築
    print(X_train.shape[1], X_train.shape[2])

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test), verbose=1)
    model.summary()
    model.save(model_path) # HDF5ファイルとして保存
    
    return model


def evaluate_and_predict(model):

    X_train, X_test, y_train, y_test, scaler_features, scaler_target, dates = prepare_dataset()

    # モデルの評価
    train_predict = model.predict(X_train)
    test_predict = model.predict(X_test)

    # 予測値のスケーリングを元に戻す
    train_predict = scaler_target.inverse_transform(train_predict)
    test_predict = scaler_target.inverse_transform(test_predict)
    y_train_inv = scaler_target.inverse_transform(y_train.reshape(-1, 1))
    y_test_inv = scaler_target.inverse_transform(y_test.reshape(-1, 1))

    np.set_printoptions(linewidth=200)  # 行の幅を200文字に設定
    print(test_predict)
    #print(y_train_inv)
    #print(y_test_inv)

    # 評価指標の計算
    train_score = mean_squared_error(y_train_inv, train_predict, squared=False)
    test_score = mean_squared_error(y_test_inv, test_predict, squared=False)
    print(f'Train RMSE: {train_score:.2f}')
    print(f'Test RMSE: {test_score:.2f}')

    # Convert indices back to dates for plotting
    train_dates = dates[:len(y_train)]
    test_dates = dates[len(y_train):len(y_train) + len(y_test)]

    # 予測結果のプロット
    plt.figure(figsize=(10,6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #plt.gca().xaxis.set_major_locator(mdates.MonthLocator())  # 1ヶ月ごとに日付を表示
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())  # 1年ごとに日付を表示

    #plt.plot(train_dates, y_train_inv, label='Actual Train', linestyle='-', marker='')
    plt.plot(train_dates, train_predict, label='Predicted Train', linestyle='-', marker='')
    #plt.plot(test_dates, y_test_inv, label='Actual Test', linestyle='-', marker='')
    plt.plot(test_dates, test_predict, label='Predicted Test', linestyle='-', marker='')
    plt.title('Nikkei Stock Price Prediction')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()


model = create_model(NIKKEI_MODEL_PATH)
evaluate_and_predict(model)
