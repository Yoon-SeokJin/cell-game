import tensorflow as tf
from tensorflow import keras
import numpy as np
INPUT = 4
model = keras.Sequential([
    keras.layers.InputLayer((INPUT,)),
    # keras.layers.Dense(100, activation='elu'),
    # keras.layers.Dense(100, activation='elu'),
    # keras.layers.Dense(100, activation='elu'),
    # keras.layers.Dense(100, activation='elu'),
    # keras.layers.Dense(100, activation='elu'),
    keras.layers.Dense(9),
])
def get_observation():
    observation = np.array([3, 2, 3, 1, 3, 2.0])
    left_length = INPUT - len(observation)
    if left_length > 0:
        observation = np.concatenate([observation, np.zeros(left_length)])
    elif left_length < 0:
        observation = observation[:left_length]
    return observation.astype(float)
X = get_observation()
model(X[np.newaxis])