#FirstModel(96x96x1)
import numpy as np
import tensorflow as tf
import os
import time

# ---------------------------------------------------------------------------------------------------
start = time.time()
logdir = './logs/TheFaceShot/' + str(time.time())

np.random.seed(int(time.time()))
tf.set_random_seed(777)  # reproducibility

# hyper parameters
inputDataType = "GrayScale"
learning_rate = 0.0003
training_epochs = 50
batch_size = 150
image_depth = 1

# data input
input_data = 'TRAIN96x96_0425.csv'
data_xy = np.loadtxt(input_data, delimiter=',', dtype=np.float32)
np.random.shuffle(data_xy)
data_N = len(data_xy)  # print('data_N: ', data_N)

# lrn(2, 2e-05, 0.75, name='norm1')
radius = 2
alpha = 2e-05
beta = 0.75
bias = 1.0

# ---------------------------------------------------------------------------------------------------
# X: input 96*96*image_depth
# Y: output 0 ~ 6
X = tf.placeholder(tf.float32, [None, 96 * 96 * image_depth])
Y = tf.placeholder(tf.int32, [None, 1])  # 0~6

# 출력 class 개수 = 0(무표정),1(행복),2(슬픔),3(화남),4(놀람),5(두려움),6(역겨움)
nb_classes = 7

# one hot & reshape
Y_one_hot = tf.one_hot(Y, nb_classes)  # print("one_hot", Y_one_hot)
Y_one_hot = tf.reshape(Y_one_hot, [-1, nb_classes])  # print("reshape", Y_one_hot)

# img 96x96x1 (GrayScale)
X_img = tf.reshape(X, [-1, 96, 96, image_depth])

# ---------------------------------------------------------------------------------------------------
# L1 ImgIn shape = (?, 96, 96, image_depth)
W1 = tf.Variable(tf.random_normal([3, 3, image_depth, 64], stddev=0.01))

# Conv1 -> (?, 96, 96, 64)
L1 = tf.nn.conv2d(X_img, W1, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 96, 96, 64)
L1 = tf.nn.conv2d(X_img, W1, strides=[1, 1, 1, 1], padding='SAME')
L1 = tf.nn.relu(L1)

# lrn1
# lrn(2, 2e-05, 0.75, name='norm1')
L1 = tf.nn.local_response_normalization(L1, depth_radius=radius, alpha=alpha, beta=beta, bias=bias)

# Pool -> (?, 48, 48, 64)
L1 = tf.nn.max_pool(L1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# ---------------------------------------------------------------------------------------------------
# L2 ImgIn shape = (?, 48, 48, 64)
W2 = tf.Variable(tf.random_normal([3, 3, 64, 128], stddev=0.01))

# Conv1 -> (?, 48, 48, 128)
L2 = tf.nn.conv2d(L1, W2, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 48, 48, 128)
L2 = tf.nn.conv2d(L1, W2, strides=[1, 1, 1, 1], padding='SAME')
L2 = tf.nn.relu(L2)

# lrn2
# lrn(2, 2e-05, 0.75, name='norm1')
L2 = tf.nn.local_response_normalization(L2, depth_radius=radius, alpha=alpha, beta=beta, bias=bias)

# Pool -> (?, 24, 24, 128)
L2 = tf.nn.max_pool(L2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# ---------------------------------------------------------------------------------------------------
# L3 ImgIn shape = (?, 24, 24, 128)
W3 = tf.Variable(tf.random_normal([3, 3, 128, 256], stddev=0.01))

# Conv1 -> (?, 24, 24, 256)
L3 = tf.nn.conv2d(L2, W3, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 24, 24, 256)
L3 = tf.nn.conv2d(L2, W3, strides=[1, 1, 1, 1], padding='SAME')

# Conv3 -> (?, 24, 24, 256)
L3 = tf.nn.conv2d(L2, W3, strides=[1, 1, 1, 1], padding='SAME')
L3 = tf.nn.relu(L3)

# Pool -> (?, 12, 12, 256)
L3 = tf.nn.max_pool(L3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# ---------------------------------------------------------------------------------------------------
# L4 ImgIn shape = (?, 12, 12, 256)
W4 = tf.Variable(tf.random_normal([3, 3, 256, 512], stddev=0.01))

# Conv1 -> (?, 12, 12, 512)
L4 = tf.nn.conv2d(L3, W4, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 12, 12, 512)
L4 = tf.nn.conv2d(L3, W4, strides=[1, 1, 1, 1], padding='SAME')

# Conv3 -> (?, 12, 12, 512)
L4 = tf.nn.conv2d(L3, W4, strides=[1, 1, 1, 1], padding='SAME')
L4 = tf.nn.relu(L4)

# Pool -> (?, 6, 6, 512)
L4 = tf.nn.max_pool(L4, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# ---------------------------------------------------------------------------------------------------
# L5 ImgIn shape = (?, 6, 6, 512)
W5 = tf.Variable(tf.random_normal([6, 6, 512, 512], stddev=0.01))

# Conv1 -> (?, 6, 6, 512)
L5 = tf.nn.conv2d(L4, W5, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 6, 6, 512)
L5 = tf.nn.conv2d(L4, W5, strides=[1, 1, 1, 1], padding='SAME')

# Conv3 -> (?, 6, 6, 512)
L5 = tf.nn.conv2d(L4, W5, strides=[1, 1, 1, 1], padding='SAME')
L5 = tf.nn.relu(L5)

# Pool -> (?, 1, 1, 512)
L5 = tf.nn.max_pool(L5, ksize=[1, 6, 6, 1], strides=[1, 6, 6, 1], padding='SAME') ############################

# Reshape -> (?, 1 * 1 * 512) - Flatten them for FC
L5_flat = tf.reshape(L5, [-1, 1 * 1 * 512])

# ---------------------------------------------------------------------------------------------------
# L6 FC 1x1x512 inputs ->  4096 outputs
W6 = tf.get_variable("W10", shape=[512 * 1 * 1, 4096], initializer=tf.contrib.layers.xavier_initializer())
b6 = tf.Variable(tf.random_normal([4096]))
L6 = tf.nn.relu(tf.matmul(L5_flat, W6) + b6)

# ---------------------------------------------------------------------------------------------------
# L7 FC 4096 inputs ->  1000 outputs
W7 = tf.get_variable("W7", shape=[4096, 1000], initializer=tf.contrib.layers.xavier_initializer())
b7 = tf.Variable(tf.random_normal([1000]))
L7 = tf.nn.relu(tf.matmul(L6, W7) + b7)

# ---------------------------------------------------------------------------------------------------
# L8 FC 1000 inputs -> 1 outputs
W8 = tf.get_variable("W8", shape=[1000, nb_classes], initializer=tf.contrib.layers.xavier_initializer())
b8 = tf.Variable(tf.random_normal([nb_classes]))
logits = tf.matmul(L7, W8) + b8

# ---------------------------------------------------------------------------------------------------
# define cost/loss & optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y_one_hot))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# define correct_prediction & accuracy
correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(Y_one_hot, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# initialize(GPU 메모리 제한 - 삭제금지)
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
sess.run(tf.global_variables_initializer())

# Summary
cost_sum = tf.summary.scalar("cost", cost)
accuracy_sum = tf.summary.scalar("accuracy", accuracy)
summary = tf.summary.merge_all()
# Create summary writer
writer = tf.summary.FileWriter(logdir)
writer.add_graph(sess.graph)

# Add ops to save and restore all the variables. # ★
saver = tf.train.Saver()

dirName = str(time.time()) + inputDataType + "_rate" + str(learning_rate) + "_epoch" + str(training_epochs) + "_batch" + str(batch_size)
os.mkdir(str(dirName))

# ---------------------------------------------------------------------------------------------------
# train my model and check cost
print('learning_rate / training_epochs:', learning_rate, '/', training_epochs)
print('Learning started...')

train_N = data_N
print('train_N:', train_N, 'input')

saveCkpt = 1
Training_Cost = 0
start = time.time()
for epoch in range(training_epochs):
    i = 0
    while i <= train_N:
        if (i + batch_size) > train_N:
            batch_train_x = data_xy[i:(i + (train_N % batch_size)), 0:-1]
            batch_train_y = data_xy[i:(i + (train_N % batch_size)), [-1]]
        else:
            batch_train_x = data_xy[i:(i + batch_size), 0:-1]
            batch_train_y = data_xy[i:(i + batch_size), [-1]]

        train_feed_dict = {X: batch_train_x, Y: batch_train_y}

        Training_Cost, _ = sess.run([cost, optimizer], feed_dict=train_feed_dict)

        if Training_Cost <= (0.03*saveCkpt):
            saver.save(sess, os.getcwd() + "/" + dirName + ".ckpt")
            saveCkpt = saveCkpt*0.1

        print('train epoch:', epoch, 'batch:', i, 'cost:', Training_Cost)

        i += batch_size

print('Last_Training_Cost:', Training_Cost)
print('Learning Finished!\n')
execution_time = time.time() - start

# ---------------------------------------------------------------------------------------------------
# Summary
print('----------------------------------------------------------------------------------------')
print('Last_Training_Cost:', Training_Cost)
print('execution time(second):', execution_time)
print('logdir:', logdir)
print("\nModel saved in file: %s" % dirName)
sess.close()

# ---------------------------------------------------------------------------------------------------
# file write log
f1 = open(dirName + "/model_log.txt", "a")
f1.write('learning_rate: %f\n' % learning_rate)
f1.write('training_epochs: %d\n' % training_epochs)
f1.write('batch_size: %d\n' % batch_size)
f1.write('Cost: %f\n' % Training_Cost)
f1.write("----------------------------------------------------------------------------------------------\n")
f1.close()

f = open("./TrainHistory.txt", 'a')
f.write('-- FirstModel(96x96x%d)-----------------------\n' % image_depth)
f.write('learning_rate: %f\n' % learning_rate)
f.write('training_epochs: %d\n' % training_epochs)
f.write('batch_size: %d\n' % batch_size)
f.write('Cost: %f\n' % Training_Cost)
f.close()
