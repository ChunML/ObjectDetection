import cv2
import numpy as np

image = cv2.imread('road_2.jpg')
output = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray[:int(gray.shape[0] / 2.3), :] = 0
gray = cv2.GaussianBlur(gray, (3, 3), 1)
cv2.imshow('thresh', gray)
cv2.waitKey(0)

kernel = np.ones((3, 3), np.uint8)

_, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)

thresh = cv2.dilate(thresh, kernel, iterations=2)
cv2.imshow('thresh', thresh)
cv2.waitKey(0)

_, contours, _ = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

new_contours = []

x_lane = []
y_lane = []
x_out = []
y_out = []
for contour in contours:
	rect = cv2.minAreaRect(contour)
	box = cv2.boxPoints(rect)
	box = np.int0(box)
	width = np.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2)
	height = np.sqrt((box[1][0] - box[2][0]) ** 2 + (box[1][1] - box[2][1]) ** 2)
	if width * height < 80000 and width * height > 300 and ~(width / height > 0.8 
		and width / height < 1.2) and (abs(rect[2]) > 20 and abs(rect[2]) < 80):
		cv2.putText(output, str(rect[2]), (box[2][0], box[2][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
		new_contours.append(contour)
		for i in xrange(4):
			if i == 3:
				cv2.line(output, (box[i][0], box[i][1]), (box[0][0], box[0][1]), (0, 255, 0), 1)
			else:
				cv2.line(output, (box[i][0], box[i][1]), (box[i + 1][0], box[i + 1][1]), (0, 255, 0), 1)

		for i, point in enumerate(contour):
				
			if i == len(contour) - 1:
				cv2.line(image, tuple(contour[i][0]), tuple(contour[0][0]), (0, 255, 0), 2)
			else:
				cv2.line(image, tuple(contour[i][0]), tuple(contour[i + 1][0]), (0, 255, 0), 2)

		y = []
		x = []
		for i, point in enumerate(contour):
			y.append(point[0][1])
			x.append(point[0][0])
		x_lane.append(x)
		y_lane.append(y)
		i_max= np.argmax(y)
		x_out.append([value for i, value in enumerate(x) if y[i] == y[i_max]])
		y_out.append(y[i_max])

#print(x_lane)
print(y_out)

x_left = [value for i, value in enumerate(x_out) if all(temp < 400 for temp in x_out[i])]
y_left = [value for i, value in enumerate(y_out) if all(temp < 400 for temp in x_out[i])]
i_left = [i for i, value in enumerate(x_out) if all(temp < 400 for temp in x_out[i])]
x_left = [value for i, value in enumerate(x_left) if y_left[i] == y_left[np.argmax(y_left)]]
i_left = i_left[np.argmax(y_left)]
y_left = y_left[np.argmax(y_left)]
print(x_left)
print(y_left)
print(i_left)
x_right = [value for i, value in enumerate(x_out) if all(temp >= 400 for temp in x_out[i])]
y_right = [value for i, value in enumerate(y_out) if all(temp >= 400 for temp in x_out[i])]
i_right = [i for i, value in enumerate(x_out) if all(temp >= 400 for temp in x_out[i])]
x_right = [value for i, value in enumerate(x_right) if y_right[i] == y_right[np.argmax(y_right)]]
i_right = i_right[np.argmax(y_right)]
y_right = y_right[np.argmax(y_right)]
print(x_right)
print(y_right)
print(i_right)

detected_object_boxes = np.loadtxt('array.txt')
for box in detected_object_boxes:
    x_left = [value for i, value in enumerate(x_lane[i_left]) if y_lane[i_left][i] == int(box[3])]
    x_right = [value for i, value in enumerate(x_lane[i_right]) if y_lane[i_right][i] == int(box[3])]
    print(x_left)
    print(x_right)
    cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), 2)

thresh = np.zeros(thresh.shape)
cv2.drawContours(thresh, new_contours, -1, 255, 1)
cv2.imshow('thresh', thresh)
cv2.imshow('result', image)
cv2.imshow('lines', output)
cv2.waitKey(0)
