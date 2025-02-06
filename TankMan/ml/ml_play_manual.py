"""
The template of the main script of the machine learning process
"""
from math import sqrt
import random
import pygame
from collections import deque
import numpy as np
from src.env import IS_DEBUG

import ml.find_station as fs
import ml.wall_handler as wh


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
            if distance < 10:
                return "tank"
        return "wall"

    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        self.initmap(scene_info)
        #self.printmap()
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
                print("tank for rl(now distance less than 10)")
                command.append("NONE")
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