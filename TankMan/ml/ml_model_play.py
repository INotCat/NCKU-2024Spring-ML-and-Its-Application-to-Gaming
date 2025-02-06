"""
The template of the main script of the machine learning process
"""
from math import sqrt
import random
import pygame
from collections import deque
import numpy as np
from src.env import IS_DEBUG
import pickle
import os,sys

import ml.find_station as fs
import ml.wall_handler as wh
import ml.data_handler as dh

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.side = ai_name
        print(f"Initial Game {ai_name} ml script")
        self.row = 50
        self.col = 30
        self.size = 1000/self.row
        self.map =  np.zeros((self.row, self.col), dtype=int)
        self.find_station = fs.find_station(self.row, self.col, self.size)
        self.wallhandler = wh.WallHandler(self.row, self.col, self.size)
        self.datahandler = dh.DataHandler()
        self.qL = dh.QLearning()

        self.cur_action = 0
        self.cur_state = [0,0,0,0]
        
       
        #For qlearning usage
        path = os.path.join(os.path.dirname(__file__), './')
        filename = "Shooter_Aiming_Qtable1_v3"
        try:
            with open(os.path.join(path, filename), "rb") as f:
                self.model = pickle.load(f)
        except FileNotFoundError:
            self.model = np.zeros((9,2,2,9,5))


    def initmap(self, scene_info):
        walls = scene_info["walls_info"]
        bullets = scene_info["bullet_stations_info"]
        oils = scene_info["oil_stations_info"]
        teams = scene_info['teammate_info']
        animys = scene_info['competitor_info']
        wall_left_size = 1
        wall_right_size = 1
        item_left_size = 0
        item_right_size = 0
        for i in range(0, self.row):
            for j in range(0, self.col):
                self.map[i][j] = 0
        for wall in walls:
            x = int(wall["x"] / self.size) + 1
            y = int(wall["y"] / self.size) + 1
            for i in range(-wall_left_size, wall_right_size+1):
                for j in range(-wall_left_size, wall_right_size+1):
                    if 0 <= x-i < self.row and 0 <= y-j < self.col:
                        self.map[x-i][y-j] = 1
        for bullet in bullets:
            x = int(bullet["x"] / self.size) + 1
            y = int(bullet["y"] / self.size) + 1
            for i in range(-item_left_size, item_right_size+1):
                for j in range(-item_left_size, item_right_size+1):
                    if 0 <= x-i < self.row and 0 <= y-j < self.col:
                        self.map[x-i][y-j] = 2
        for oil in oils:
            x = int(oil["x"] / self.size) + 1
            y = int(oil["y"] / self.size) + 1
            for i in range(-item_left_size, item_right_size+1):
                for j in range(-item_left_size, item_right_size+1):
                    if 0 <= x-i < self.row and 0 <= y-j < self.col:
                        self.map[x-i][y-j] = 3
        for team in teams:
            x = int(team["x"] / self.size) + 1
            y = int(team["y"] / self.size) + 1
            for i in range(-item_left_size, item_right_size+1):
                for j in range(-item_left_size, item_right_size+1):
                    if 0 <= x-i < self.row and 0 <= y-j < self.col:
                        self.map[x-i][y-j] = 4
        for animy in animys:
            x = int(animy["x"] / self.size) + 1
            y = int(animy["y"] / self.size) + 1
            for i in range(-item_left_size, item_right_size+1):
                for j in range(-item_left_size, item_right_size+1):
                    if 0 <= x-i < self.row and 0 <= y-j < self.col:
                        self.map[x-i][y-j] = 5

    def printmap(self):
        for i in range(0, self.row):
            for j in range(0, self.col):
                if self.map[i][j] == 0:
                    print(" ", end='')
                else:
                    print(self.map[i][j], end='')
            print("\n",end='')
        print("\n\n\n\n\n\n\n\n")

    def check_target(self, scene_info):
        x = scene_info['x']
        y = scene_info['y']
        for animy in scene_info['competitor_info']:
            distance = sqrt((animy['x'] - x) ** 2 + (animy['y'] - y) ** 2)
            if distance < 300:
                return "tank"
        return "wall"

    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        self.initmap(scene_info)
        command = []
            
        if scene_info['oil'] <= 40 or scene_info['power'] <= 5:
            angle = scene_info['angle'] if scene_info['angle'] < 360 else 0
            target = 3 if scene_info['oil'] <= 40 else 2
            path = self.find_station.bfs((int(scene_info['x'] / self.size) + 1, int(scene_info['y'] / self.size) + 1, angle), target, self.map)
            if len(path) <= 1:
                command.append("NONE")
                print("\npath <= 1\n")
                return command
            command.append(self.find_station.walk2target(path[0],path[1]))
            return command
        
        else:
            target = self.check_target(scene_info)
            if target == 'tank':
                cloest_target = self.datahandler.target_one_enemy(scene_info)
                angle_diff, turning_direction = self.datahandler.calculate_cosine(cloest_target, scene_info)
                is_cooldown = self.datahandler.check_cooldown(scene_info)
                
                cloest_teamate = self.datahandler.check_one_team(scene_info)
                teammate_angle_diff, turning_direction_teammate = self.datahandler.calculate_cosine( cloest_teamate, scene_info)
                
                self.cur_state[0] = angle_diff
                self.cur_state[1] = turning_direction
                self.cur_state[2] = is_cooldown
                self.cur_state[3] = teammate_angle_diff
                
                self.cur_action = np.argmax(self.model[self.cur_state[0], self.cur_state[1], self.cur_state[2], self.cur_state[3]])
                
                final_action = ""
                #5 actions 0:"SHOOT", 1:"AIM_RIGHT", 2:"AIM_LEFT" 3:"BACKWARD" 4:"wall" 
                if self.cur_action == 0:
                    final_action = "SHOOT"
                elif self.cur_action == 1:
                    final_action = "AIM_RIGHT"
                elif self.cur_action == 2:
                    final_action = "AIM_LEFT"
                elif self.cur_action == 3:
                    final_action = "BACKWARD"
                elif self.cur_action == 4:
                    final_action = "wall"
                            
                if final_action == "wall":
                    command.append(self.wallhandler.aim(scene_info, self.map))
                else:
                    command.append(final_action)
        
                return command
            elif target == 'wall':
                command.append(self.wallhandler.aim(scene_info, self.map))
                return command
            
        return command

    def reset(self):
        """
        Reset the status
        """
        print(f"reset Game {self.side}")