from logging import getLevelName
import os
import urllib
import gzip
import json
import tensorflow as tf
from tensorflow import keras
import tensorflow
from tensorflow.keras.layers import Conv2D, BatchNormalization, Activation, Dense, Flatten, Add
from tensorflow.keras.activations import relu
import numpy as np
import random
import Goban

from keras.models import Model
from keras.layers.convolutional import Conv2D

model = None

def getModel():
  global model
  if model is None:
    model = keras.models.load_model("models/current_model.h5")
  return model

def getEvaluation( plates ):
  plates = np.reshape(plates, (1, 9, 9, 9))
  val, policy = getModel().predict(plates)
  return val, policy