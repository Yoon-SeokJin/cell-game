import pygame
import numpy as np
from common import *
from random import randint
import tensorflow as tf
from tensorflow import keras
from tqdm import tqdm
import os
import argparse


def play_one_step(env, obs, model, loss_fn):
    with tf.GradientTape() as tape:
        pred = model(obs[np.newaxis])
        action = tf.random.categorical(pred, 1)
        y_target = tf.one_hot(action[0], len(pred[0]))
        loss = tf.reduce_mean(loss_fn(y_target, pred))
    grads = tape.gradient(loss, model.trainable_variables)

    click_coord = None
    direction = tf.cast(action[0, 0], float)
    if direction > 0:
        rad = (direction - 1) * 2 * np.pi / 8
        click_coord = np.array([np.cos(rad), np.sin(rad)]) + np.array([obs[1], obs[2]])
    obs, reward, done = env.step(click_coord)
    return obs, reward ** 3, done, grads


def play_multiple_episodes(env, n_episodes, n_max_steps, model, loss_fn):
    all_rewards = []
    all_grads = []
    for episode in range(n_episodes):
        current_rewards = []
        current_grads = []
        obs = env.reset()
        for step in range(n_max_steps):
            obs, reward, done, grads = play_one_step(env, obs, model, loss_fn)
            if Settings.RENDERING:
                env.render()
            if not Settings.NO_GRAD:
                current_rewards.append(reward)
                current_grads.append(grads)
            if done:
                break
        all_rewards.append(current_rewards)
        all_grads.append(current_grads)
    return all_rewards, all_grads


def discount_rewards(rewards, discount_factor):
    discounted = np.array(rewards)
    for step in range(len(rewards) - 2, -1, -1):
        discounted[step] += discounted[step + 1] * discount_factor
    return discounted


def discount_and_normalize_rewards(all_rewards, discount_factor):
    all_discounted_rewards = [discount_rewards(rewards, discount_factor) for rewards in all_rewards]
    flat_rewards = np.concatenate(all_discounted_rewards)
    reward_mean = flat_rewards.mean()
    reward_std = flat_rewards.std()
    return [(discounted_rewards - reward_mean) / reward_std for discounted_rewards in all_discounted_rewards]


if __name__ == '__main__':
    try:
        import google.colab
        running_in_COLAB = True
    except:
        running_in_COLAB = False
    if not running_in_COLAB:
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=512)])
            except RuntimeError as e:
                print(e)
        Settings.RENDERING = True
        Settings.NO_GRAD = True # My local gpu is too poor to calculate gradient.
    else:
        Settings.RENDERING = False # Google colab can't display graphic panel.
        Settings.NO_GRAD = False

    parser = argparse.ArgumentParser()
    parser.add_argument('--load_path', default='', help='load path when resume training.')
    parser.add_argument('--save_path', default='', help='save path.')
    parser.add_argument('--name', default='default', help='detail name used by finding load or save model in specified path.')

    load_path = parser.parse_args().load_path
    save_path = parser.parse_args().save_path
    detail_name = parser.parse_args().name

    do_load = load_path != ''
    do_save = save_path != ''

    load_path = os.path.join(load_path, detail_name)
    save_path = os.path.join(save_path, detail_name)

    model = keras.Sequential([
        keras.layers.InputLayer((301,)),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(9),
    ])
    if do_load and os.path.exists(load_path + '.index'):
        model.load_weights(load_path)
    loss_fn = keras.losses.binary_crossentropy
    env = Environment()
    obs = env.reset()

    n_iterations = 150
    n_episodes_per_update = 10
    n_max_steps = 200
    discount_factor = 0.95
    optimizer = keras.optimizers.Adam(learning_rate=0.01)
    loss_fn = keras.losses.binary_crossentropy

    for iteration in tqdm(range(n_iterations)):
        all_rewards, all_grads = play_multiple_episodes(env, n_episodes_per_update, n_max_steps, model, loss_fn)
        if not Settings.NO_GRAD:
            all_final_rewards = discount_and_normalize_rewards(all_rewards, discount_factor)
            all_mean_grads = []
            for var_index in range(len(model.trainable_variables)):
                mean_grads = tf.reduce_mean([final_reward * all_grads[episode_index][step][var_index]
                for episode_index, final_rewards in enumerate(all_final_rewards)for step, final_reward in enumerate(final_rewards)], axis=0)
                all_mean_grads.append(mean_grads)
            optimizer.apply_gradients(zip(all_mean_grads, model.trainable_variables))
            if do_save:
                model.save_weights(save_path)