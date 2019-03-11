#!/usr/bin/env python3
'''
Carla DQN

Based on:
    https://raw.githubusercontent.com/keon/deep-q-learning/master/ddqn.py
    https://medium.com/@apoddar573/making-your-own-custom-environment-in-gym-c3b65ff8cdaa
    https://github.com/carla-simulator/carla/blob/master/PythonAPI/automatic_control.py

'''
import random
import os

import gym
import numpy as np
import pygame

import carla_env
from agent import DQNAgent


EPISODES = 5000

def main():

    env = gym.make('carla-v0')
    state_size = env.image_size_net_chans
    action_size = len(env.action_space)
    agent = DQNAgent(state_size, action_size)

    done = False
    batch_size = 4

    try:

        for episode in range(EPISODES):
            state = env.reset(render=True)
            for time in range(500):
                env.render()
                action = agent.act(state)
                next_state, reward, done = env.step(action)
                reward = reward if not done else -10
                agent.remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    agent.update_target_model()
                    print('episode: {}/{}, score: {}, e: {:.2}'.format(
                        episode, EPISODES, time, agent.epsilon))
                    break
                if len(agent.memory) > batch_size:
                    agent.replay(batch_size)
            if episode % 10 == 0:
                agent.save(os.path.join('..', 'models', 'carla-ddqn.h5'))

    finally:

        env.world.destroy()


if __name__ == '__main__':
    main()

