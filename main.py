tags = [chr(i) for i in range(ord('ㄅ'), ord('ㄩ')+1)]
INPUT_SIZE = 128*128*1
OUTPUT_SIZE = len(tags)
HIDDEN_LAYER_LENGTH = 10
HIDDEN_SIZE = 50
TEST_DATA_QUANTITY = 1
LEARNING_RATE = 0.00001

import os
import numpy as np
import tensorflow as tf

from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras import Sequential
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

import cv2

def createModel():
    model = Sequential()
    model.add(Dense(500, Activation('relu'), input_dim = INPUT_SIZE))
    for _ in range(HIDDEN_LAYER_LENGTH):
        model.add(Dense(HIDDEN_SIZE))
    model.add(Dense(OUTPUT_SIZE, Activation('softmax')))
    return model

model = createModel()
model.summary()

def train(trainData, debug:bool = False):
    [x_train, y_train, x_test, y_test, tags] = [trainData['x_train'], trainData['y_train'], trainData['x_test'], trainData['y_test'], trainData['tags']]
    x_train = np.array(x_train).astype(np.float32)
    x_test = np.array(x_test).astype(np.float32)
    y_train = np.array(y_train)
    y_train_one_hot = []
    y_test_one_hot = []
    for y in y_train:
        one_hot = [0 for _ in range(len(tags))]
        one_hot[tags.index(y)] = 1
        y_train_one_hot.append(one_hot)
    y_train_one_hot = np.array(y_train_one_hot).astype(np.float32)
    for y in y_test:
        one_hot = [0 for _ in range(len(tags))]
        one_hot[tags.index(y)] = 1
        y_test_one_hot.append(one_hot)
    y_test_one_hot = np.array(y_test_one_hot).astype(np.float32)

    optim = Adam(learning_rate = LEARNING_RATE)
    model.compile(loss='categorical_crossentropy',
                optimizer=optim,
                metrics=['acc'])
    history = model.fit(x_train, y_train_one_hot,
                        batch_size=100,
                        epochs=25,
                        verbose=1,
                        shuffle=True,
                        validation_split=0.1)

    history_dict = history.history
    history_dict.keys()

    if debug:
        import matplotlib.pyplot as plt

        acc = history_dict['acc']
        val_acc = history_dict['val_acc']
        loss = history_dict['loss']
        val_loss = history_dict['val_loss']
        epochs_ = range(1,len(acc)+1)

        plt.plot(epochs_ , loss , label = 'training loss')
        plt.plot(epochs_ , val_loss , label = 'val los')
        plt.title('training and val loss')
        plt.xlabel('epochs')
        plt.ylabel('loss')
        plt.legend()
        plt.show()

        plt.clf()
        plt.plot(epochs_ , acc , label='train accuracy')
        plt.plot(epochs_ , val_acc , label = 'val accuracy')
        plt.title('train and val acc')
        plt.xlabel('epochs')
        plt.ylabel('acc')
        plt.legend()
        plt.show()
        pred = np.argmax(model.predict(x_test), axis=1)
        print([tags[i] for i in pred])

    return(model)

def method(tags, model):
    def predict(*pathList):
        x_test = []
        for path in pathList:
            img = False
            if type(path) == str:
                img = cv2.imread(path)
            else:
                img = path
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.resize(img, (128, 128), interpolation=cv2.INTER_AREA)
            x_test.append(np.reshape(img, [128*128*1])/255)
        x_test = np.array(x_test).astype(np.float32)
        pred = np.argmax(model.predict(x_test), axis=1)
        return([tags[i] for i in pred])
    return({
        'predict': predict, 
    })

checkpoint_path = './model/cp-{epoch:04d}.ckpt'
if os.path.isfile(checkpoint_path.format(epoch=0) + '.index'):
    model.load_weights(checkpoint_path.format(epoch=0))
if __name__ == '__main__':
    dataDir = './data'
    tagDirList = os.listdir(dataDir)
    x_train = []
    y_train = []
    for tagDir in tagDirList:
        for imgPath in os.listdir(f'{dataDir}/{tagDir}'):
            img = cv2.imread(f'{dataDir}/{tagDir}/{imgPath}')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.resize(img, (128, 128), interpolation=cv2.INTER_AREA)
            x_train.append(np.reshape(img, [128*128*1])/255)
            y_train.append(chr(int(tagDir)))
    trainData = {
        'x_train': x_train[:-TEST_DATA_QUANTITY], 
        'y_train': y_train[:-TEST_DATA_QUANTITY], 
        'x_test': x_train[-TEST_DATA_QUANTITY:], 
        'y_test': y_train[-TEST_DATA_QUANTITY:], 
        'tags': tags
    }
    # train(trainData)
    train(trainData, True)
    model.save_weights(checkpoint_path.format(epoch=0))
modelMethod = method(tags, model)