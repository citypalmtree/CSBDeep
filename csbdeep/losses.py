from __future__ import print_function, unicode_literals, absolute_import, division

import numpy as np
import keras.backend as K



def _mean_or_not(mean):
    # return (lambda x: K.mean(x,axis=(-1 if K.image_data_format()=='channels_last' else 1))) if mean else (lambda x: x)
    # Keras also only averages over axis=-1, see https://github.com/keras-team/keras/blob/master/keras/losses.py
    return (lambda x: K.mean(x,axis=-1)) if mean else (lambda x: x)


def loss_laplace(mean=True, eps=1e-3): # FIXME: add 1e-3 in model itself instead of loss (would also cause change in Fiji/KNIME code)
    R = _mean_or_not(mean)
    C = np.log(2.0) # FIXME: in the supplement, we have dropped C, ie. C = 0
    if K.image_data_format() == 'channels_last':
        def nll_laplace(y_true, y_pred):
            n     = K.shape(y_true)[-1]
            mu    = y_pred[...,:n]
            sigma = y_pred[...,n:] + eps
            return R(K.abs((mu-y_true)/sigma) + K.log(sigma) + C)
        return nll_laplace
    else:
        def nll_laplace(y_true, y_pred):
            n     = K.shape(y_true)[1]
            mu    = y_pred[:,:n,...]
            sigma = y_pred[:,n:,...] + eps
            return R(K.abs((mu-y_true)/sigma) + K.log(sigma) + C)
        return nll_laplace


def loss_mae(mean=True):
    R = _mean_or_not(mean)
    if K.image_data_format() == 'channels_last':
        def mae(y_true, y_pred):
            n = K.shape(y_true)[-1]
            return R(K.abs(y_pred[...,:n] - y_true))
        return mae
    else:
        def mae(y_true, y_pred):
            n = K.shape(y_true)[1]
            return R(K.abs(y_pred[:,:n,...] - y_true))
        return mae


def loss_mse(mean=True):
    R = _mean_or_not(mean)
    if K.image_data_format() == 'channels_last':
        def mse(y_true, y_pred):
            n = K.shape(y_true)[-1]
            return R(K.square(y_pred[...,:n] - y_true))
        return mse
    else:
        def mse(y_true, y_pred):
            n = K.shape(y_true)[1]
            return R(K.square(y_pred[:,:n,...] - y_true))
        return mse


def loss_thresh_weighted_decay(loss_per_pixel, thresh, w1, w2, alpha):
    def _loss(y_true, y_pred):
        val = loss_per_pixel(y_true, y_pred)
        k1 = alpha * w1 + (1 - alpha)
        k2 = alpha * w2 + (1 - alpha)
        return K.mean(K.tf.where(K.tf.less_equal(y_true, thresh), k1 * val, k2 * val),
                      axis=(-1 if K.image_data_format()=='channels_last' else 1))
    return _loss
