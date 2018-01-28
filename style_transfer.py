import os
import numpy as np

from image import noisy_img
from image import load_img
from image import save_img
from model import create_model
from model import content_loss
from model import style_loss

import tensorflow as tf

ITERATIONS = 1000
LEARNING_RATE = 5.0
ALPHA = 10000
BETA = 1

STYLE = 'img/style/vangogh.jpg'
CONTENT = 'img/content/sunflower.jpg'

if __name__ == '__main__':
    with tf.Session() as sess:

        # Load images
        content = load_img(CONTENT)
        style = load_img(STYLE)
        #input = noisy_img(content)
        input = content

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
        L_total = BETA * L_content + ALPHA * L_style

        # Minimize loss
        optimizer = tf.train.AdamOptimizer(LEARNING_RATE)
        train_step = optimizer.minimize(L_total)

        # Stylize the image
        sess.run(tf.global_variables_initializer())
        sess.run(model['input'].assign(input))

        for _ in range(ITERATIONS):
            sess.run(train_step)

        # Output final image and notify we're done
        output = sess.run(model['input'])
        filename = 'results/stylized.png'
        save_img(filename, output)
        print('Done.')
