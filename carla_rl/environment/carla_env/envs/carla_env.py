import time

import carla
import cv2
import gym
import numpy as np
import pygame
from gym import error, spaces, utils
from gym.utils import seeding

from carla_env.world import World

class CarlaEnv(gym.Env):


    metadata = {'render.modes': ['fpv', 'follow']}


    def __init__(self):
        pygame.init()
        pygame.font.init()

        num_samples = 80

        client = carla.Client('127.0.0.1', 2000)
        client.set_timeout(6.0)

        self.world = World(client.get_world(), num_samples)

        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(num_samples*3,), dtype=np.float32)

        self.action_space = spaces.Box(
            np.array([-1, 0]), np.array([1, 1]))

        self.epsilon = 0.30
        self.epsilon_decay = 0.95
        self.count = 0

        self.num_envs = 1

        # limit the timestep the car has to reach certain speed
        # self.num_of_steps_to_reach_speed = 100
        # self.num_of_steps = 0
        # self.speed = 3


    def step(self, action):

        control_autopilot = self.world.get_autopilot_control()

        steer_autopilot, throttle_autopilot = control_autopilot.steer, control_autopilot.throttle

        steer_network, throttle_network = action

        steer = self.epsilon * steer_autopilot + (1.0 - self.epsilon) * steer_network
        throttle = self.epsilon * throttle_autopilot + (1.0 - self.epsilon) * throttle_network

        control = carla.VehicleControl()
        control.steer = float(steer)
        control.throttle = float(throttle)
        control.brake = 0.0
        control.hand_brake = False
        control.manual_gear_shift = False

        self.world.vehicle.apply_control(control)
        self.world.world.tick()
        self.world.world.wait_for_tick()
        next_state = self.world.get_state()

        done = len(self.world.collision_sensor.history) > 0
        done = np.int(done)

        vel_y, vel_x = self.world.get_velocity()
        acc_y, acc_x = self.world.get_acceleration()

        if done:
            reward = -100
        else:
            reward = 0.01 * vel_y + 0.05 * acc_y - 0.005 * (np.abs(vel_x) + np.abs(acc_x))

        return next_state, reward, done, {}


    def reset(self):
        # print('reset')
        self.world.restart()

        self.count += 1
        self.epsilon = max(0.0, self.epsilon * self.epsilon_decay)
        # if self.count % 20 == 0:
        #     print(self.epsilon, steer, throttle)

        return self.world.get_state()



    def render(self, mode='fpv'):
        image = self.world.get_depth_frame()
        cv2.imshow('Image', (image*255).astype(np.uint8))
        cv2.waitKey(1)
        self.world.render(self.render)
        pygame.display.flip()
