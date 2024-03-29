# -*- coding: utf-8 -*-
"""kernel0c324c70f2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1z6iEJPWA7BbwF-HJ17u6LCy4G5tz1H_m
"""

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

import numpy as np
import pandas as pd
from tqdm import tqdm
from keras.models import Model
from keras.layers import Input, Dense, Embedding, SpatialDropout1D, Dropout, add, concatenate
from keras.layers import CuDNNLSTM, Bidirectional, GlobalMaxPooling1D, GlobalAveragePooling1D
from keras.optimizers import Adam
from keras.preprocessing import text, sequence
from keras.callbacks import LearningRateScheduler

EMBEDDING_FILES = [
    '../input/fasttext-crawl-300d-2m/crawl-300d-2M.vec',
    '../input/glove840b300dtxt/glove.840B.300d.txt'
]
NUM_MODELS = 2

# the maximum number of different words to keep in the original texts
# 100_000 seems good too
MAX_FEATURES = 100000 

#this is the number of training sample to put in theo model each step
BATCH_SIZE = 512

#units parameters in Keras.layers.LSTM/cuDNNLSTM
#it is the dimension of the output vector of each LSTM cell.
LSTM_UNITS = 128
DENSE_HIDDEN_UNITS = 4 * LSTM_UNITS

EPOCHS = 4

#we will convert each word in a comment_text to a number.
#So a comment_text is a list of number. 
MAX_LEN = 220


IDENTITY_COLUMNS = [
    'male', 'female', 'homosexual_gay_or_lesbian', 'christian', 'jewish',
    'muslim', 'black', 'white', 'psychiatric_or_mental_illness'
]
AUX_COLUMNS = ['target', 'severe_toxicity', 'obscene', 'identity_attack', 'insult', 'threat']
TEXT_COLUMN = 'comment_text'
TARGET_COLUMN = 'target'
CHARS_TO_REMOVE = '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n“”’\'∞θ÷α•à−β∅³π‘₹´°£€\×™√²—'

def get_coefs(word, *arr):
    return word, np.asarray(arr, dtype='float32')

def load_embeddings(path):

    with open(path) as f:
        return dict(get_coefs(*o.strip().split(" ")) for o in tqdm(f))

def build_matrix(word_index, path):

    #we will construct an embedding_matrix for the words in word_index
    #using pre-trained embedding word vectors from 'path'

    embedding_index = load_embeddings(path)

    embedding_matrix = np.zeros((len(word_index) + 1, 300))

    # word_index is a dict. Each element is (word:i) where i is the index
    # of the word
    for word, i in word_index.items():
        try:
            #RHS is a vector of 300d
            embedding_matrix[i] = embedding_index[word]
        except KeyError:
            pass
    return embedding_matrix

def build_model(embedding_matrix, num_aux_targets):
    words = Input(shape=(MAX_LEN,))

    #Embedding is the keras layer. We use the pre-trained embbeding_matrix
    # x is a vector of 600 dimension
    x = Embedding(*embedding_matrix.shape, weights=[embedding_matrix], trainable=False)(words)

    #*embedding_matrix.shape is a short way for 
    #input_dim = embedding_matrix.shape[0], output_dim  = embedding_matrix.shape[1] output_dim is 600 for embing dim

    #https://stackoverflow.com/questions/50393666/how-to-understand-spatialdropout1d-and-when-to-use-it
    x = SpatialDropout1D(0.25)(x)

    x = Bidirectional(CuDNNLSTM(LSTM_UNITS, return_sequences=True))(x)

    x = Bidirectional(CuDNNLSTM(LSTM_UNITS, return_sequences=True))(x)

    hidden = concatenate([
        GlobalMaxPooling1D()(x),
        GlobalAveragePooling1D()(x),
    ])
    
    # here is skip connection like resnet to overcome the vanishing gradient problem especially for deeper RNN 
    hidden = add([hidden, Dense(DENSE_HIDDEN_UNITS, activation='tanh')(hidden)])
    hidden = add([hidden, Dense(DENSE_HIDDEN_UNITS, activation='relu')(hidden)])
    result = Dense(1, activation='sigmoid', name = 'main_output')(hidden)

    #num_aux_targets = 6 since y_aux_train has 6 columns, here activation use sigmoid becasue this is not muticlass
    # just binary to each aux prediction 
    aux_result = Dense(num_aux_targets, activation='sigmoid', name = 'aux_ouput')(hidden)

    model = Model(inputs=words, outputs=[result, aux_result])
    # model.summary()

    model.compile(
        loss='binary_crossentropy',
        optimizer=Adam(clipnorm=0.1),
        metrics=['accuracy'])



    return model

train = pd.read_csv('/kaggle/input/jigsaw-unintended-bias-in-toxicity-classification/train.csv')
test = pd.read_csv('/kaggle/input/jigsaw-unintended-bias-in-toxicity-classification/test.csv')

#Take the columns 'comment_text' from train,
# then fillall NaN values by emtpy string '' (redundant)
x_train = train[TEXT_COLUMN].fillna('').values

#if true, y_train[i] =1, if false, it is = 0
y_train = np.where(train[TARGET_COLUMN] >= 0.5, 1, 0)

y_aux_train = train[AUX_COLUMNS]

#Take the columns 'comment_text' from test,
# then fillall NaN values by emtpy string '' (redundant)
x_test = test[TEXT_COLUMN].fillna('').values

# In here we don't use oov_token argument becasue we will tokenizer all train and test comment together. 
tokenizer = text.Tokenizer(num_words=MAX_FEATURES)

#we apply method fit_on_texts of tokenizer on x_train and x_test
#it will initialize some parameters/attribute inside tokenizer
tokenizer.fit_on_texts(list(x_train) + list(x_test))

#tokenizer.index_word: the inverse of tokenizer.word_index

#we will convert each word in a comment_text to a number.
#So a comment_text is a list of number corresponding to their original word 

x_train = tokenizer.texts_to_sequences(x_train)
x_test = tokenizer.texts_to_sequences(x_test)

# we want the length of this list is a constant -> MAX_LEN
# if the list is longer, then we cut/trim it 
# if shorter, then we add/pad it with 0's at the beginning
x_train = sequence.pad_sequences(x_train, maxlen=MAX_LEN)
x_test = sequence.pad_sequences(x_test, maxlen=MAX_LEN)

# create an embedding_matrix 
#after this, embedding_matrix is a matrix of size
# len(tokenizer.word_index)+1   x 600
# we concatenate two matrices, 600 = 300+300
embedding_matrix = np.concatenate(
    [build_matrix(tokenizer.word_index, f) for f in EMBEDDING_FILES], axis=-1)
#embedding_matrix.shape 
#== (410047, 600)

checkpoint_predictions = []
weights = []

for model_idx in range(NUM_MODELS):
  # build the same models
    model = build_model(embedding_matrix, y_aux_train.shape[-1])
  # We train each model EPOCHS times
  # After each epoch, we reset learning rate (we are using Adam Optimizer)  
  # Summary model: build 2 same nlp model, in each model run 4 times fit and in each fit only run 1 time epoch. 
    for global_epoch in range(EPOCHS):
        model.fit(
            x_train,
            [y_train, y_aux_train],
            batch_size=BATCH_SIZE,
            epochs=1,
            verbose=1,
            callbacks=[
                LearningRateScheduler(lambda epoch: 1e-3 * (0.6 ** global_epoch), verbose = 1)
            ]
        )
        #model.predict will give two outputs: main_output (target) and aux_output
        #we only take main_output
        checkpoint_predictions.append(model.predict(x_test, batch_size=2048)[0].flatten())
        weights.append(2 ** global_epoch)

# weights is [1, 2, 4, 8, 1, 2, 4, 8]
#predictions is an np.array, len is 97320 same as test 
predictions = np.average(checkpoint_predictions, weights=weights, axis=0)

# try more epochs
model.fit(
            x_train,
            [y_train, y_aux_train],
            batch_size=BATCH_SIZE,
            epochs=10,
            verbose=1,
            callbacks=[
                LearningRateScheduler(lambda epoch: 1e-3 * (0.6 ** epoch), verbose = 1)
            ]