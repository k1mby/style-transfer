import os
import numpy as np
import scipy.io
import scipy.misc
import tensorflow as tf

VGG = scipy.io.loadmat('imagenet-vgg-verydeep-19.mat')
ITERATIONS = 1000
LEARNING_RATE = 3.0
# Style loss weight
ALPHA = 1
# Content loss weight
BETA = 1000

# Layers used in calculating content loss
CONTENT_LAYERS = ['relu4_2']
# Layers used in calculating style loss
STYLE_LAYERS = ['relu1_1', 'relu2_1', 'relu3_1', 'relu4_1', 'relu5_1']
# Weights for style layers
STYLE_WEIGHTS = [0.2, 0.2, 0.2, 0.2, 0.2]

STYLE = 'img/style/vangogh.jpg'
CONTENT = 'img/content/sunflower.jpg'
WIDTH = 800
HEIGHT = 600

# VGG-19 mean RGB values
RGB_MEANS = np.array([123.68, 116.779, 103.939]).reshape((1,1,1,3))

def noisy_img(content):
    # White noise
    image = np.random.uniform(-255, 255, content.shape).astype('float32')
    return image

def load_img(path):
    image = scipy.misc.imread(path).astype(np.float)
    # Reshape to add the extra dimension the network expects
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    # Subtract the means
    image = image - RGB_MEANS
    return image

def save_img(path, image):
    # Add back the means
    image = image + RGB_MEANS
    # Drop the extra dimension
    image = image.reshape(image.shape[1],image.shape[2],image.shape[3])
    image = np.clip(image, 0, 255).astype('uint8')
    scipy.misc.imsave(path, image)

def gram(input, n, m):
    # Reshape to 2D matrix
    matrix = tf.reshape(input, (m, n))
    return tf.matmul(tf.transpose(matrix), matrix)

def content_loss(sess, model):

    loss = 0

    for layer in CONTENT_LAYERS:
        # F is feature map of generated image
        F = sess.run(model[layer])
        # P is the feature map of the original image
        P = model[layer]
        # Number of filters
        N = F.shape[3]
        # Height x width of feature map
        M = F.shape[1] * F.shape[2]
        # The paper outlines the loss as:
        # (1 / 2) * tf.reduce_sum(tf.pow(F - P, 2))
        # However it seems most people compute the loss as below, with better results
        loss += (1 / (4 * N * M)) * tf.reduce_sum(tf.pow(F - P, 2))

    return loss

def style_loss(sess, model):

    loss = 0

    for layer in STYLE_LAYERS:
        for w in STYLE_WEIGHTS:
            # F is generated image
            # P is original image
            F = sess.run(model[layer])
            P = model[layer]
            # Number of filters
            N = F.shape[3]
            # Height x Width of feature map
            M = F.shape[1] * F.shape[2]
            # Gram matrix of original image
            A = gram(P, N, M)
            # Gram matrix of generated image
            G = gram(F, N, M)
            # E is the style loss for a single layer multiplied by the weight of that layer
            E = (1 / (4 * N**2 * M**2)) * tf.reduce_sum(tf.pow(G - A, 2)) * w
            loss += E

    return loss

def weight(layer):
    vgg_layers = VGG['layers']
    W = vgg_layers[0][layer][0][0][2][0][0]
    return tf.constant(W)

def bias(layer):
    vgg_layers = VGG['layers']
    b = vgg_layers[0][layer][0][0][2][0][1]
    return tf.constant(b.reshape(-1))

def conv(input, layer):
    W = weight(layer)
    b = bias(layer)
    conv = tf.nn.conv2d(input, W, strides=[1, 1, 1, 1], padding='SAME')
    return tf.nn.bias_add(conv, b)

def relu(input):
    return tf.nn.relu(input)

def avgpool(input):
        return tf.nn.avg_pool(input, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

def create_model():

    model = {}
    # Initial input is the image
    model['input']   = tf.Variable(np.zeros((1, HEIGHT, WIDTH, 3)), dtype = 'float32')

    # Convolution and then apply relu
    model['conv1_1']  = conv(model['input'], 0)
    model['relu1_1'] = relu(model['conv1_1'])

    model['conv1_2']  = conv(model['relu1_1'], 2)
    model['relu1_2'] = relu(model['conv1_2'])

    # We're gonna use average pooling instead of max pooling as paper suggests
    model['avgpool1'] = avgpool(model['relu1_2'])

    model['conv2_1']  = conv(model['avgpool1'], 5)
    model['relu2_1'] = relu(model['conv2_1'])

    model['conv2_2']  = conv(model['relu2_1'], 7)
    model['relu2_2'] = relu(model['conv2_2'])

    model['avgpool2'] = avgpool(model['relu2_2'])

    model['conv3_1']  = conv(model['avgpool2'], 10)
    model['relu3_1'] = relu(model['conv3_1'])

    model['conv3_2']  = conv(model['relu3_1'], 12)
    model['relu3_2'] = relu(model['conv3_2'])

    model['conv3_3']  = conv(model['relu3_2'], 14)
    model['relu3_3'] = relu(model['conv3_3'])

    model['conv3_4']  = conv(model['relu3_3'], 16)
    model['relu3_4'] = relu(model['conv3_4'])

    model['avgpool3'] = avgpool(model['relu3_4'])

    model['conv4_1']  = conv(model['avgpool3'], 19)
    model['relu4_1'] = relu(model['conv4_1'])

    model['conv4_2']  = conv(model['relu4_1'], 21)
    model['relu4_2'] = relu(model['conv4_2'])

    model['conv4_3']  = conv(model['relu4_2'], 23)
    model['relu4_3'] = relu(model['conv4_3'])

    model['conv4_4']  = conv(model['relu4_3'], 25)
    model['relu4_4'] = relu(model['conv4_4'])

    model['avgpool4'] = avgpool(model['relu4_4'])

    model['conv5_1']  = conv(model['avgpool4'], 28)
    model['relu5_1'] = relu(model['conv5_1'])

    model['conv5_2']  = conv(model['relu5_1'], 30)
    model['relu5_2'] = relu(model['conv5_2'])

    model['conv5_3']  = conv(model['relu5_2'], 32)
    model['relu5_3'] = relu(model['conv5_3'])

    model['conv5_4']  = conv(model['relu5_3'], 34)
    model['relu5_4'] = relu(model['conv5_4'])

    model['avgpool5'] = avgpool(model['relu5_4'])
    # We don't use any of the fully connected layers

    return model


if __name__ == '__main__':
    with tf.Session() as sess:

        # Load images
        content = load_img(CONTENT)
        style = load_img(STYLE)

        # The input will be a white noise image
        input = noisy_img(content)

        # Create computation graph
        model = create_model()

        # Content loss
        sess.run(tf.global_variables_initializer())
        sess.run(model['input'].assign(content))
        L_content = content_loss(sess, model)

        # Style loss
        sess.run(tf.global_variables_initializer())
        sess.run(model['input'].assign(style))
        L_style = style_loss(sess, model)

        # Total loss
        # ALPHA is style weight, BETA is content weight
        L_total = BETA * L_content + ALPHA * L_style

        # Using Adam Optimizer
        optimizer = tf.train.AdamOptimizer(LEARNING_RATE)
        train_step = optimizer.minimize(L_total)

        # Input the base image
        sess.run(tf.global_variables_initializer())
        sess.run(model['input'].assign(input))

        # Run gradient descent
        for i in range(ITERATIONS):
            sess.run(train_step)

        # Create output folder
        if not os.path.exists('img/results'):
            os.mkdir('img/results')

        # Output the final image and notify we're done
        output = sess.run(model['input'])
        filename = 'img/results/final_image_iteration_%d.png' % (ITERATIONS)
        save_img(filename, output)
        print('Done.')