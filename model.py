# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    model.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mfiguera <mfiguera@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2020/02/14 09:36:15 by mfiguera          #+#    #+#              #
#    Updated: 2020/02/17 12:18:32 by mfiguera         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import numpy as np
from matplotlib import pyplot as plt
from tqdm import trange

from layers import Dense, ReLU


class Model:
    def __init__(self, n_units):
        network = []

        n_layers = len(n_units) - 1
        for i in range(n_layers):
            network.append(Dense(*n_units[i:i+2]))
        
            if i + 1 < n_layers:
                network.append(ReLU())

        self.network = network


    def forward(self, X):
        activations = []

        input_ = X
        for l in self.network:
            activations.append(l.forward(input_))
            input_ = activations[-1]
        
        assert len(activations) == len(self.network), "Error here"
        
        return activations


    def predict(self, X):
        logits = self.forward(X)[-1]
        return logits.argmax(axis=-1)


    def train(self, X_train, y_train, X_val, y_val, batch_size=32, n_epoch=25, shuffle=True, quiet=False):
        train_log = []
        val_log = []
        cost_log = []

        for ep in trange(n_epoch):
            cost = 0
            for X_batch, y_batch in self.iterate_minibatches(X_train, y_train, batch_size, shuffle):
                cost+=self.train_step(X_batch, y_batch)

            train_log.append(self.score(self.predict(X_train), y_train))
            val_log.append(self.score(self.predict(X_val), y_val))
            cost_log.append(cost)

        if not quiet:
            plt.plot(train_log, label='Train accuracy')
            plt.plot(val_log, label='Validation accuracy')
            plt.legend()
            plt.grid()
            plt.show()
            plt.grid()
            plt.plot(range(len(cost_log)), cost_log, label='Cost')
            plt.show()


    @staticmethod
    def iterate_minibatches(X, y, batch_size, shuffle):
        assert len(X) == len(y), "X and Y have different sizes"
        if shuffle:
            indices = np.random.permutation(len(y))
        for i in range(0, len(y) - batch_size + 1, batch_size):
            if shuffle:
                selection = indices[i:i+batch_size]
            else:
                selection = slice(i, i+batch_size)
            yield X[selection], y[selection]


    def train_step(self, X, y):
        activations = self.forward(X)
        inputs = [X] + activations
        logits = activations[-1]

        loss = self.softmax_crossentropy_logits(logits, y)

        preds = self.softmax(logits)
        # print(f"out: {preds} y: {y}")
        loss_grad = self.gradient_softmax_crossentropy_logits(preds, y)
        for i in range(len(self.network))[::-1]:
            layer = self.network[i]
            loss_grad = layer.backward(inputs[i], loss_grad)

        return np.mean(loss)


    @staticmethod
    def score(y_pred, y_true):
        return np.mean(y_pred==y_true)


    @staticmethod
    def softmax(x):
        exps = np.exp(x - np.max(x))
        return exps / np.sum(exps)


    @staticmethod
    def softmax_crossentropy_logits(pred_logits, y):
        logits_for_answers = pred_logits[:, list(y)]
        return np.log(np.sum(np.exp(pred_logits), axis=-1)) - logits_for_answers


    def gradient_softmax_crossentropy_logits(self, pred_logits, y):
        ones_for_answers = np.zeros_like(pred_logits)
        ones_for_answers[np.arange(len(pred_logits)), list(y)] = 1
        return (pred_logits - ones_for_answers) / pred_logits.shape[0]
