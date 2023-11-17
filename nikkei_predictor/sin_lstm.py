from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras.layers import LSTM
from tensorflow.keras.optimizers.legacy import Adam
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np
import matplotlib.pyplot as plt


#
# データの生成
#
def sin(x, T=100):
    return np.sin(2.0 * np.pi * x / T)

# sin波にノイズを付与する
def toy_problem(offset = 0, T=100, ampl=0.1):
    print("toy problem: ", offset, offset + 2 * T + 1)
    x = np.arange(offset, offset + 2 * T + 1)
    noise = ampl * np.random.uniform(low=-1.0, high=1.0, size=len(x))
    return sin(x) + noise

def make_dataset(y1, y2, maxlen=25):
    data = []
    target = []
    for i in range(len(y1) - maxlen):
        data.append(np.column_stack((y1[i:i + maxlen], y2[i:i + maxlen])))
        target.append(y1[i + maxlen])
    return np.array(data), np.array(target).reshape(len(data), 1)
    
sin_y = toy_problem() #sin
sin_offset_y = toy_problem(180, ampl=6) #sin with offset
#g, h = make_dataset(sin_offset_y) #g -> 学習データ，h -> 学習ラベル
g, h = make_dataset(sin_y, sin_offset_y)

print(g)

#
# モデルの生成
#
length_of_sequence = g.shape[1] # 1つの学習データのStep数(今回は25)
in_out_neurons = 2
n_hidden = 30
model = Sequential()
model.add(LSTM(n_hidden, batch_input_shape=(None, length_of_sequence, in_out_neurons), return_sequences=False))
model.add(Dense(in_out_neurons))
model.add(Activation("linear"))
optimizer = Adam(learning_rate=0.001)
model.compile(loss="mean_squared_error", optimizer=optimizer)

#
# 学習
#
early_stopping = EarlyStopping(monitor='val_loss', mode='auto', patience=20)
model.fit(g, h,
    batch_size=300,
    epochs=100,
    validation_split=0.1,
    callbacks=[early_stopping]
)

#
# 予測
#
predicted = model.predict(g)

plt.figure()
plt.plot(range(25,len(predicted)+25),predicted, color="r", label="predict_data")
plt.plot(range(0, len(sin_y)), sin_y, color="b", label="row_data")
#plt.plot(range(0, len(sin_offset_y)), sin_offset_y, color="b", label="row_data")
plt.legend()
plt.show()

