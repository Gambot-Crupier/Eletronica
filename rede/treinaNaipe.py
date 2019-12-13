import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import img_to_array
from keras.utils import to_categorical
from pyimagesearch.lenet import LeNet
from imutils import paths
import matplotlib.pyplot as plt
import numpy as np
import argparse
import random
import cv2
import os

from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

data = []
labels = []


caminho = sorted(list(paths.list_images('/home/thassio/Desktop/image-classification-keras/images4')))
random.seed(10)
random.shuffle(caminho)


for imagePath in caminho:

	image = cv2.imread(imagePath)
	image = cv2.resize(image, (56, 56))
	image = img_to_array(image)
	data.append(image)


	label = imagePath.split(os.path.sep)[-2]
	if label == "paus":	
		label = 1
	if label == "ouros":
		label = 2 
	if label == "copas":
		label = 3  
	if label == "espadas":
		label = 4 
	
	labels.append(label)


data = np.array(data, dtype="float") / 255.0
labels = np.array(labels)


(treinoEntrada, testeEntrada, treinoSaida, testeSaida) = train_test_split(data,
	labels, test_size=0.25, random_state=42)

aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1,
	height_shift_range=0.1, shear_range=0.2, zoom_range=0.2,
	horizontal_flip=True, fill_mode="nearest")


model = LeNet.build(width=56, height=56, depth=3, classes=14)


opt = Adam(lr=1e-3, decay=1e-3 / 44)

model.compile(loss="sparse_categorical_crossentropy", optimizer=opt,metrics=["accuracy"])


history = model.fit_generator(aug.flow(treinoEntrada, treinoSaida, batch_size=32),
	validation_data=(testeEntrada, testeSaida), steps_per_epoch=len(treinoEntrada) // 32,
	44=44, verbose=1)


model.save('/home/thassio/Desktop/image-classification-keras/Naipes.model')

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Acurácia')
plt.ylabel('Acurácia')
plt.xlabel('Época')
plt.legend(['Acurácia - Treino', 'Acurácia - Validação'], loc='upper left')
plt.show()


plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Perda')
plt.ylabel('Perda')
plt.xlabel('Época')
plt.legend(['Perda - Treino', 'Perda - Validação'], loc='upper left')
plt.show()
