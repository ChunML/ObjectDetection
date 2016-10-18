import cv2
import os
import numpy as np

def displayThresh(gray, ratio):
	gray = cv2.GaussianBlur(gray, (3, 3), 1)
	_, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
	thresh = cv2.dilate(thresh, kernel, iterations=2)
	thresh = cv2.resize(thresh, (int(thresh.shape[1] / resize_ratio), int(thresh.shape[0] / resize_ratio)))
	cv2.imshow('thresh', thresh)

image_files = [value for value in os.listdir('.') if 'jpg' in value]
array_files = [str(image_files[i])[:-4] + '.txt' for i in range(len(image_files))]
class_files = [str(image_files[i])[:-4] + '_class.txt' for i in range(len(image_files))]

kernel = np.ones(3)

arrays = [np.loadtxt(array_file, dtype='int') for array_file in array_files]
classes = [np.loadtxt(class_file, dtype='str') for class_file in class_files]

for i, image_file in enumerate(image_files):
	image = cv2.imread(image_file)

	resize_ratio = 1
	if (image.shape[1] > 1280 or image.shape[0] > 1024):
		while (image.shape[1] / resize_ratio > 1280 or image.shape[0] / resize_ratio > 1024):
			resize_ratio += 0.1
	else:
		resize_ratio = 1

	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	displayThresh(gray, resize_ratio)
	
	for array, class_name in zip(arrays[i], classes[i]):
		cv2.rectangle(image, (array[0], array[1]), (array[2], array[3]), (0, 255, 0), 2)
		cv2.putText(image, class_name, (array[0], array[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, 
					(0, 255, 255), 2)
		if (class_name == 'car'):
			roi = gray[array[1]:array[3], array[0]:array[2]]
			if (roi.shape[1] / roi.shape[0] > 2):
				cv2.rectangle(image, (array[0], array[1]), (array[2], array[3]), (0, 0, 255), 2)
				cv2.putText(image, class_name + ': CROSSING !!!', (array[0], array[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.1, 
					(0, 0, 255), 3)

	image = cv2.resize(image, (int(image.shape[1] / resize_ratio), int(image.shape[0] / resize_ratio)))
	cv2.imshow('Result'.format(i), image)
	cv2.waitKey(0)
