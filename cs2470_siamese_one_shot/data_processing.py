import cv2, os, math as m, numpy as np, random as rand
from tensorflow.examples.tutorials.mnist import input_data

def affine_transformation(img, theta, rho_x, rho_y, s_x, s_y, t_x, t_y):
	out = img
	rows, cols = out.shape
	if rand.uniform(0,2) > 1:
		a = m.cos(theta)
		b = m.sin(theta)
		M = np.float32([[a, b, ((1 - a) * 53) - (b * 53)],[-b, a, (b * 53) + ((1 - a) * 53)]])
		out = cv2.warpAffine(img,M,(cols,rows),borderValue=1.0)
	if rand.uniform(0,2) > 1:
		M = np.float32([[1, rho_x, 0],[rho_y, 1, 0]])
		out = cv2.warpAffine(img,M,(cols,rows),borderValue=1.0)
	if rand.uniform(0,2) > 1:
		out = cv2.resize(out,None,fx=s_x, fy=s_y, interpolation = cv2.INTER_CUBIC)
		y_len, x_len = out.shape
		if x_len > 105:
			x_dif = x_len - 105
			out = out[:,int(m.ceil(x_dif / 2.0)):int(m.ceil(x_len - x_dif / 2.0))]
		else:
			x_dif = 105 - x_len
			temp = np.ones((y_len,105))
			temp[:,int(m.ceil(x_dif / 2.0)):int(m.ceil(105 - x_dif / 2.0))] = out
			out = temp
		if y_len > 105:
			y_dif = y_len - 105
			out = out[int(m.ceil(y_dif / 2.0)):int(m.ceil(y_len - y_dif / 2.0)),:]
		else:
			y_dif = 105 - y_len
			temp = np.ones((105,105))
			temp[int(m.ceil(y_dif / 2.0)):int(m.ceil(105 - y_dif / 2.0)),:] = out
			out = temp
		if out.shape != (105, 105):
			print(out.shape)
	if rand.uniform(0,2) > 1:
		M = np.float32([[1,0,t_x],[0,1,t_y]])
		out = cv2.warpAffine(out,M,(cols,rows),borderValue=1.0)
	return out

def get_test_data():
	pairs = []
	labels = []
	base = 'images_evaluation'
	alpha_lb = 0
	alpha_ub = 10
	img_lb = 12
	img_ub = 16
	alphabets = os.listdir(base)
	for i in range(alpha_lb, alpha_ub):
		alpha = os.path.join(base, alphabets[i])
		characters = os.listdir(alpha)
		drawers = list(range(img_lb, img_ub))
		for j in range(2):
			drawer1 = drawers.pop(rand.randint(0,len(drawers) - 1))
			drawer2 = drawers.pop(rand.randint(0,len(drawers) - 1))
			for k in range(20):
				char1 = os.path.join(alpha, characters[k])
				images1 = os.listdir(char1)
				for l in range(20):
					char2 = os.path.join(alpha, characters[l])
					images2 = os.listdir(char2)
					img1 = os.path.join(char1, images1[drawer1])
					img2 = os.path.join(char2, images2[drawer2])
					x = cv2.imread(img1,0) / 255.0
					y = cv2.imread(img2,0) / 255.0
					pairs.append([x, y])
					labels.append(k)
	return (pairs, labels)

def get_image_pair(pair):
	img1 = pair[0]
	img2 = pair[1]
	trans = pair[2]
	x = cv2.imread(img1,0) / 255.0
	y = cv2.imread(img2,0) / 255.0
	if trans:
		x = affine_transformation(x, rand.uniform(-10,10), rand.uniform(-0.3,0.3), rand.uniform(-0.3,0.3), rand.uniform(0.8,1.2), rand.uniform(0.8,1.2), rand.uniform(-2,2), rand.uniform(-2,2))
		y = affine_transformation(y, rand.uniform(-10,10), rand.uniform(-0.3,0.3), rand.uniform(-0.3,0.3), rand.uniform(0.8,1.2), rand.uniform(0.8,1.2), rand.uniform(-2,2), rand.uniform(-2,2))
	return (x, y)

def get_image(img_path, trans):
	x = cv2.imread(img_path,0) / 255.0
	if trans:
		x = affine_transformation(x, rand.uniform(-10,10), rand.uniform(-0.3,0.3), rand.uniform(-0.3,0.3), rand.uniform(0.8,1.2), rand.uniform(0.8,1.2), rand.uniform(-2,2), rand.uniform(-2,2))
	return x

def get_data_paths(num, trans_num, step, match_rate):
	pairs = []
	labels = []
	if step == 'train':
		base = 'images_background'
		img_lb = 0
		img_ub = 12
	alphabets = os.listdir(base)
	for a_ind in range(30):
		alph1 = os.path.join(base, alphabets[a_ind])
		for i in range(num // 30):
			characters1 = os.listdir(alph1)
			char1 = os.path.join(alph1, characters1[rand.randint(0,len(characters1) - 1)])
			images1 = os.listdir(char1)
			img1 = os.path.join(char1, images1[rand.randint(img_lb,img_ub - 1)])
			x = img1
			if rand.uniform(0,1) > (1 - match_rate):
				label = 1
				img2 = os.path.join(char1, images1[rand.randint(img_lb,img_ub - 1)])
				while img2 == img1:
					img2 = os.path.join(char1, images1[rand.randint(img_lb,img_ub - 1)])
				y = img2
			else:
				label = 0
				char2 = os.path.join(alph1, characters1[rand.randint(0,len(characters1) - 1)])
				while char2 == char1:
					char2 = os.path.join(alph1, characters1[rand.randint(0,len(characters1) - 1)])
				images2 = os.listdir(char2)
				img2 = os.path.join(char2, images2[rand.randint(img_lb,img_ub - 1)])
				y = img2
			pairs.append([x, y, False])
			labels.append(label)
			for j in range(trans_num):
				pairs.append([x, y, True])
				labels.append(label)
	return (pairs, labels)
