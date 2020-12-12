# Tensorflow adapted from API reference as well as tensorflow udemy course


import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import feature_column
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split

csv_file = 'datasets/pattern_outputs/CDLENGULFING_records.csv'
dataframe = pd.read_csv(csv_file)
dataframe['result'] = 0
for i, row in dataframe.iterrows():
    if dataframe.at[i, 'Percent Change'] > 0:
        dataframe.at[i, 'result'] = 1
    else:
        dataframe.at[i, 'result'] = 0
print(dataframe)
# setting the darget
dataframe['target'] = np.where(dataframe['result'] == 1, 0, 1)

# dropping unused columns
dataframe = dataframe.drop(columns=['CDL Pattern', 'Date', 'Symbol', 'result', 'Profit', 'Percent Change', 'Trend',
                                    'bb upper', 'bb middle', 'bb close'])

train, test = train_test_split(dataframe, test_size=0.15)
train, val = train_test_split(train, test_size=0.15)
print(len(train), 'train examples')
print(len(val), 'validation examples')
print(len(test), 'test examples')


# A method that alters a pandas dataframe to tf.data dataset
def df_to_dataset(dataframe, shuffle=True, batch_size=10):
    dataframe = dataframe.copy()
    labels = dataframe.pop('target')
    ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(dataframe))
    ds = ds.batch(batch_size)
    return ds


batch_size = 5  # A small batch sized is used for demonstration purposes
train_ds = df_to_dataset(train, batch_size=batch_size)
val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)

for feature_batch, label_batch in train_ds.take(1):
    print('Every feature:', list(feature_batch.keys()))
    #print('A batch of WMA:', feature_batch['WMA'])
    print('A batch of targets:', label_batch)

# We will use this batch to demonstrate several types of feature columns
example_batch = next(iter(train_ds))[0]


# A utility method to create a feature column
# and to transform a batch of data
def demo(feature_column):
    feature_layer = layers.DenseFeatures(feature_column)
    print(feature_layer(example_batch).numpy())


#ADX_num = feature_column.numeric_column('ADX')
#demo(ADX_num)

# trend_type = feature_column.categorical_column_with_vocabulary_list('Type', ['Bullish', 'Bearish'])

# group_type_one_hot = feature_column.indicator_column(group_type)
# demo(group_type_one_hot)


# crossed_feature = feature_column.crossed_column(['WMA', 'Close'], hash_bucket_size=10)
# demo(feature_column.indicator_column(crossed_feature))

feature_columns = []

# numeric cols
# 'Open', 'Close', 'WMA', 'ADX', 'APO', 'DX', 'ADOSC', 'NATR', 'bb upper', 'bb middle', 'bb close'
for header in ['Open', 'Close', 'WMA', 'ADX', 'APO', 'DX', 'ADOSC', 'NATR']:
    feature_columns.append(feature_column.numeric_column(header))

# crossed columns
crossed_2_feature = feature_column.crossed_column(['ADX', 'APO'], hash_bucket_size=10)
feature_columns.append(feature_column.indicator_column(crossed_2_feature))

feature_layer = tf.keras.layers.DenseFeatures(feature_columns)

batch_size = 32
train_ds = df_to_dataset(train, batch_size=batch_size)
val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)

model = tf.keras.Sequential([
    feature_layer,
    layers.Dense(128, activation='relu'),
    layers.Dense(128, activation='relu'),
    layers.Dropout(.1),
    layers.Dense(1)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
              metrics=['accuracy'])

model.fit(train_ds,
          validation_data=val_ds,
          epochs=50)

loss, accuracy = model.evaluate(test_ds)
print("Accuracy", accuracy)
