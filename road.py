import cv2
import numpy as np

image = cv2.imread('road_2.jpg')
source = image.copy()
output = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray[:int(gray.shape[0] / 2.3), :] = 0
gray = cv2.GaussianBlur(gray, (3, 3), 1)
#cv2.imshow('thresh', gray)
#cv2.waitKey(0)

kernel = np.ones((3, 3), np.uint8)

_, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)

thresh = cv2.dilate(thresh, kernel, iterations=2)
#cv2.imshow('thresh', thresh)
#cv2.waitKey(0)

contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

new_contours = []

x_lane = []
y_lane = []
x_out = []
y_out = []
for contour in contours:
	rect = cv2.minAreaRect(contour)
	box = cv2.cv.BoxPoints(rect)
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

x_left = [value for i, value in enumerate(x_out) if all(temp < 400 for temp in x_out[i])]
y_left = [value for i, value in enumerate(y_out) if all(temp < 400 for temp in x_out[i])]
i_left = [i for i, value in enumerate(x_out) if all(temp < 400 for temp in x_out[i])]
x_left = [value for i, value in enumerate(x_left) if y_left[i] == y_left[np.argmax(y_left)]]
i_left = i_left[np.argmax(y_left)]
y_left = y_left[np.argmax(y_left)]

x_right = [value for i, value in enumerate(x_out) if all(temp >= 400 for temp in x_out[i])]
y_right = [value for i, value in enumerate(y_out) if all(temp >= 400 for temp in x_out[i])]
i_right = [i for i, value in enumerate(x_out) if all(temp >= 400 for temp in x_out[i])]
x_right = [value for i, value in enumerate(x_right) if y_right[i] == y_right[np.argmax(y_right)]]
i_right = i_right[np.argmax(y_right)]
y_right = y_right[np.argmax(y_right)]

x_lane_left = x_lane[i_left]
y_lane_left = y_lane[i_left]
x_lane_right = x_lane[i_right]
y_lane_right = y_lane[i_right]

#x_min_right = x_lane_right[np.argmin(x_lane_right)]
x_min_right = np.amin(x_lane_right)
y_min_right = [value for i, value in enumerate(y_lane_right) if (x_lane_right[i] == x_min_right)][0]

#print(x_min_right)
#print(x_lane_right[np.argmin(x_lane_right) + 50])
#print(y_min_right)
#print(y_lane_right[np.argmin(y_lane_right) + 50])
ratio_right = (x_lane_right[np.argmin(x_lane_right) + 50] - x_min_right) / (y_lane_right[np.argmin(y_lane_right) + 50] - y_min_right)

detected_object_boxes = np.loadtxt('road.txt')
for box in detected_object_boxes:
    x_left = [value for i, value in enumerate(x_lane_left) if y_lane_left[i] == int(box[3])]
    x_right = [value for i, value in enumerate(x_lane_right) if y_lane_right[i] == int(box[3])]
    if (len(x_left) == 0):
    	for i in range(1, y_min_left - int(box[3]) + 1):
    		y_new = y_min_left - i
    		x_new = int(i*ratio_right) + x_min_left
    		x_lane_left.append(x_new)
    		y_lane_left.append(y_new)
    	x_left = [value for i, value in enumerate(x_lane_left) if y_lane_left[i] == int(box[3])]
    if (len(x_right) == 0):
    	for i in range(1, y_min_right - int(box[3]) + 1):
    		y_new = y_min_right - i
    		x_new = int(i*ratio_right) + x_min_right
    		x_lane_right.append(x_new)
    		y_lane_right.append(y_new)
    	x_right = [value for i, value in enumerate(x_lane_right) if y_lane_right[i] == int(box[3])]
    x_left = np.amax(x_left)
    x_right = np.amin(x_right)
    if (x_left <= int(box[0]) and x_right >= int(box[0])) or ((x_left <= int(box[2]) and x_right >= int(box[2]))):
    	cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), 2)
    	cv2.putText(image, 'CAR AHEAD!!!', (int(box[0]) - 20, int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
					(10, 10, 255), 2)
    else:
    	cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
    	cv2.putText(image, 'Car', (int(box[0]) + 5, int(box[1]) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
					(0, 255, 255), 2)

thresh = np.zeros(thresh.shape)
cv2.drawContours(thresh, new_contours, -1, 255, 1)
cv2.imshow('thresh', thresh)
cv2.imshow('result', image)
cv2.imshow('source', source)
cv2.waitKey(0)