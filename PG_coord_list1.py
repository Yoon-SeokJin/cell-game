import pygame
import numpy as np
from common import *
from random import randint, random
import tensorflow as tf
from tensorflow import keras
from tqdm import tqdm

class Environment:
    def reset(self):
        radius_list = [70, 70, 70]
        # radius_list = np.geomspace(10, 100, 100)
        # radius_list = np.concatenate([
        #     np.ones(shape=8) * 100,
        #     np.ones(shape=16) * 75,
        #     np.ones(shape=64) * 50,
        #     np.ones(shape=128) * 25,
        #     np.ones(shape=128) * 12.5,
        # ])
        self.cells = []
        self.cells.append(Cell((Settings.WIDTH / 2, Settings.HEIGHT / 2), 100, control=True))
        for r in radius_list:
            r = int(r)
            pos = (randint(r, Settings.WIDTH - r), randint(r, Settings.HEIGHT - r))
            self.cells.append(Cell(pos, r))
        self._relocate_no_overlap()
        return self.get_observation()


    def step(self, action):
        if isinstance(action, np.ndarray):
            self.cells[0].propel(self.cells, action)
        for sprite in self.cells:
            sprite.motion()
        collision_pair = self._get_collision_pair()
        for i, j in collision_pair:
            i.drain(j)
            j.drain(i)

        obs = self.get_observation()

        if self.cells[0].radius <= 0:
            return obs, 0, True
        self.cells[:] = [e for e in self.cells if e.radius > 0]
        return obs, float(self.cells[0].radius), False


    @Renderer()
    def render(self, renderer):
        renderer.debug_string.append(f'Count = {len(self.cells)}')
        volume = 0
        for cell in self.cells:
            volume += cell.radius * cell.radius * cell.radius
        renderer.debug_string.append(f'Volume = {volume}')
        for sprite in self.cells:
            if sprite.radius < self.cells[0].radius:
                color = '#AEAE55'
            elif sprite.radius > self.cells[0].radius:
                color = '#AE5555'
            else:
                color = '#55AEAE'
            pygame.draw.circle(renderer.screen, color, sprite.pos.astype(float), float(sprite.radius))


    def get_observation(self):
        observation = np.array([len(self.cells)])
        for cell in self.cells:
            observation = np.concatenate([observation, cell.pos, cell.velocity, [cell.radius, int(cell.control), int(not cell.control)]])

        left_length = 301 - len(observation)
        if left_length > 0:
            observation = np.concatenate([observation, np.zeros(left_length)])
        elif left_length < 0:
            observation = observation[:left_length]
        return observation.astype(float)


    def _get_collision_pair(self):
        tile_width = 40
        tile_height = 40
        tile_wcount = Settings.WIDTH // tile_width + 1
        tile_hcount = Settings.HEIGHT // tile_height + 1
        bucket = [[[] for _ in range(tile_wcount)] for _ in range(tile_hcount)]
        for e in self.cells:
            x1 = int(e.pos[0] - e.radius) // tile_width
            x2 = int(e.pos[0] + e.radius) // tile_width
            y1 = int(e.pos[1] - e.radius) // tile_height
            y2 = int(e.pos[1] + e.radius) // tile_height
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    if 0 <= y < tile_hcount and 0 <= x < tile_wcount:
                        bucket[y][x].append(e)
        pairs = []
        for row in bucket:
            for items in row:
                n = len(items)
                for i in range(n):
                    for j in range(i + 1, n):
                        pairs.append((items[i], items[j]))
        return pairs
    

    def _place_extra_cells(self, radius_list, try_count=100):
        sorted(radius_list, reverse=True)
        for radius in radius_list:
            for _ in range(try_count):
                r = int(radius)
                pos = (randint(r, Settings.WIDTH - r), randint(r, Settings.HEIGHT - r))
                for cell in self.cells:
                    dpos = cell.pos - pos
                    k = (dpos[0] * dpos[0] + dpos[1] * dpos[1]).sqrt()
                    a = int(radius)
                    b = cell.radius
                    if k < a + b:
                        break
                else:
                    self.cells.append(Cell(pos, radius, (0, 0)))
                    break


    def _relocate_no_overlap(self, iter_num=100, extra_radius=10):
        for cell in self.cells:
            cell.radius += extra_radius
        for _ in range(iter_num):
            collision_pair = self._get_collision_pair()
            if len(collision_pair) == 0:
                break
            for i, j in collision_pair:
                dpos = j.pos - i.pos
                k = (dpos[0] * dpos[0] + dpos[1] * dpos[1]).sqrt()
                a = i.radius
                b = j.radius
                force = a + b - k
                if force > 0:
                    force = force * force / 10000
                    i.pos -= dpos * force
                    j.pos += dpos * force
            for cell in self.cells:
                cell.motion()
        for cell in self.cells:
            cell.radius -= extra_radius


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
    return obs, reward, done, grads


def play_multiple_episodes(env, n_episodes, n_max_steps, model, loss_fn):
    all_rewards = []
    all_grads = []
    for episode in range(n_episodes):
        current_rewards = []
        current_grads = []
        obs = env.reset()
        for step in range(n_max_steps):
            obs, reward, done, grads = play_one_step(env, obs, model, loss_fn)
            env.render()
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
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024)])
        except RuntimeError as e:
            print(e)
    load_path = 'PG_coord_list1_0'
    save_path = 'PG_coord_list1_0'

    model = keras.Sequential([
        keras.layers.InputLayer((301,)),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(100, activation='elu'),
        keras.layers.Dense(9),
    ])
    # model.load_weights(load_path)
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
        all_final_rewards = discount_and_normalize_rewards(all_rewards, discount_factor)
        all_mean_grads = []
        for var_index in range(len(model.trainable_variables)):
            mean_grads = tf.reduce_mean([final_reward * all_grads[episode_index][step][var_index]
            for episode_index, final_rewards in enumerate(all_final_rewards)for step, final_reward in enumerate(final_rewards)], axis=0)
            all_mean_grads.append(mean_grads)
        optimizer.apply_gradients(zip(all_mean_grads, model.trainable_variables))
        model.save_weights(save_path)