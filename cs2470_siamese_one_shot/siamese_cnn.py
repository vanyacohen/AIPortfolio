import numpy as np
import tensorflow as tf
import data_processing as dp
import argparse
import random as rand

IMG_SZ = 105
TRAIN_SZ = 30000
TRIAL_SZ = 8000

parser = argparse.ArgumentParser(description="siamese cnn for one shot classification")
parser.add_argument('--train', action='store_true', help="include to train the model, leave out to test")
parser.add_argument("-learningrate", help="Learning rate", type=float, default=1e-4)
parser.add_argument("-epochs", help="Epochs to train for", type=int, default=100)
args = parser.parse_args()

bSz = 20
if args.train:
    bSz = 128

imgBatchA = tf.placeholder(tf.float32, [bSz, IMG_SZ, IMG_SZ, 1])
imgBatchB = tf.placeholder(tf.float32, [bSz, IMG_SZ, IMG_SZ, 1])
labels = tf.placeholder(tf.float32, [bSz, 1])

def cnn(imgBatch):
    conv1 = tf.layers.conv2d(
        inputs=imgBatch,
        filters=64,
        kernel_size=[10, 10],
        padding="valid",
        activation=tf.nn.relu)
    pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)
    conv2 = tf.layers.conv2d(
        inputs=pool1,
        filters=128,
        kernel_size=[7, 7],
        padding="valid",
        activation=tf.nn.relu)
    pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)
    conv3 = tf.layers.conv2d(
        inputs=pool2,
        filters=128,
        kernel_size=[4, 4],
        padding="valid",
        activation=tf.nn.relu)
    pool3 = tf.layers.max_pooling2d(inputs=conv3, pool_size=[2, 2], strides=2)
    conv4 = tf.layers.conv2d(
        inputs=pool3,
        filters=256,
        kernel_size=[4, 4],
        padding="valid",
        activation=tf.nn.relu)

    conv4_flat = tf.reshape(conv4, [bSz, 6 * 6 * 256])
    feature_vector = tf.layers.dense(inputs=conv4_flat, units=4096, activation=tf.nn.sigmoid)
    return feature_vector

L1_distance_vector = tf.abs(tf.subtract(cnn(imgBatchA), cnn(imgBatchB)))
logits = tf.layers.dense(inputs=L1_distance_vector, units=1)
conf = tf.sigmoid(logits)
loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=logits))
train = tf.train.AdamOptimizer(args.learningrate).minimize(loss)

sess = tf.Session()
sess.run(tf.global_variables_initializer())
saver = tf.train.Saver()

if args.train:
    train_pairs, train_labels = dp.get_data_paths(TRAIN_SZ, 8, 'train', 0.5)
    for e in xrange(args.epochs):
        sumL = 0.0
        for i in xrange(TRAIN_SZ // bSz):
            imgs1 = []
            imgs2 = []
            for j in xrange(i*bSz, (i+1)*bSz):
                pair = dp.get_image_pair(train_pairs[j])
                imgs1 += [pair[0]]
                imgs2 += [pair[1]]
            imgs1 = np.array(imgs1).reshape(bSz, IMG_SZ, IMG_SZ, 1)
            imgs2 = np.array(imgs2).reshape(bSz, IMG_SZ, IMG_SZ, 1)
            y = np.array(train_labels[i*bSz:(i+1)*bSz]).reshape(bSz, 1)
            _, l = sess.run([train, loss], feed_dict={imgBatchA : imgs1, imgBatchB : imgs2, labels: y})
            sumL += l
        print(e, sumL)
        zipped = list(zip(train_pairs, train_labels))
        rand.shuffle(zipped)
        train_pairs, train_labels = zip(*zipped)
    save_path = saver.save(sess, "tmp/model.ckpt")
    print "Saved to tmp/model.ckpt"
else:
    test_pairs, test_labels = dp.get_test_data()
    right = 0
    trials = TRIAL_SZ // bSz
    for i in xrange(trials):
        imgs1 = []
        imgs2 = []
        for j in xrange(i*bSz, (i+1)*bSz):
            pair = test_pairs[j]
            imgs1 += [pair[0]]
            imgs2 += [pair[1]]
        imgs1 = np.array(imgs1).reshape(bSz, IMG_SZ, IMG_SZ, 1)
        imgs2 = np.array(imgs2).reshape(bSz, IMG_SZ, IMG_SZ, 1)
        y = np.array(test_labels[i*bSz:(i+1)*bSz]).reshape(bSz, 1)
        c = sess.run(conf, feed_dict={imgBatchA : imgs1, imgBatchB : imgs2})
        l = np.argmax(c)
        if l == y[0]:
            right += 1
    print "Accuracy", right / float(trials)
