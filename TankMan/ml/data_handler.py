import random
import numpy as np 
import math
import os, sys
import pickle


class DataHandler:
    #def __init__(self):
        
        
    def check_cooldown(self, scene_info: dict) :
        #if is in cooldown situation then 1
        is_cooldown = 0
        if(scene_info['cooldown']>0):
            is_cooldown = 1    
            
        return is_cooldown
       
    def target_one_enemy(self, scene_info):
        enemy_list = []
        enemies = scene_info['competitor_info']
        
        for enemy in enemies: 
            enemy_list.append((enemy['x'], enemy['y'], self.distance(scene_info['x'],scene_info['y'],enemy['x'],enemy['y'])))
        
        enemy_list.sort(key=lambda x: x[2])
        #print(enemy_list[0])
        
        #ensure 300 for training
        #print(f"enemy_list[0][2] {enemy_list[0][2]}")
        if enemy_list and enemy_list[0][2] <= 300:
            return enemy_list[0]
        else:
            return None
        
    def check_one_team(self, scene_info):
        team_list = []
        teams = scene_info['teammate_info']
        
        for team in teams: 
            team_list.append((team['x'], team['y'], self.distance(scene_info['x'],scene_info['y'],team['x'],team['y'])))
        
        team_list.sort(key=lambda x: x[2])

        if team_list and team_list[0][2] <= 300:
            #since distance = 0 is myself
            return team_list[1]
        else:
            return None
    
    def calculate_cosine(self, closest_enemy, scene_info):
        # create vectors -> law of cosines 
        enemy_x, enemy_y, distance = closest_enemy
        self_x, self_y = scene_info['x'], scene_info['y']
        shooter_angle = (scene_info['gun_angle'] + 540) % 360
        
        enemy_vector = ((enemy_x-self_x)/distance, (enemy_y-self_y)/distance)
        
        shooter_vector = (np.cos(shooter_angle), np.sin(shooter_angle))
        
        cosine_value = enemy_vector[0] * shooter_vector[0] + enemy_vector[1] * shooter_vector[1]
        
        #change y coordinate postive 
        correct_enemy_vector =  enemy_vector[0] , -enemy_vector[1]
        
        enemy_angle_rad = np.arctan2(correct_enemy_vector[1], correct_enemy_vector[0])
        enemy_angle_deg = np.degrees(enemy_angle_rad) 
        enemy_angle_deg = (enemy_angle_deg + 360) % 360
        rotation_angle = -enemy_angle_deg  # Negative angle for rotating back
        R = self.rotation_matrix(rotation_angle)
        shooter_vector_aligned = np.dot(R, shooter_vector)
        sine_value = shooter_vector_aligned[1]

        # determine an unique angle by given sine and cosine
        theta_rad = np.arctan2(sine_value, cosine_value)
        theta_deg = np.degrees(theta_rad)
        #print(f"XXXXXRAW: theta_deg{theta_deg}")
        # Ensure it's in the range 0-360 degrees
        theta_deg = (theta_deg + 360) % 360  
    
        # Map the degree to discrete states
        mapped_degree = int((theta_deg + 22.5) // 45) * 45
        angle_diff = int((theta_deg + 22.5) // 45)
        #final process state result
        #0:clockwise   1: counter-clockwise 
        turning_direction = 1 if sine_value >= 0 else 0
        
        return angle_diff, turning_direction
    
    def rotation_matrix(self, angle_deg):
        angle_rad = np.radians(angle_deg)
        cos_theta = np.cos(angle_rad)
        sin_theta = np.sin(angle_rad)
        return np.array([[cos_theta, -sin_theta],
                        [sin_theta, cos_theta]])        
    
    def distance(self, x1, y1, x2,y2):
        distance = math.sqrt((x1-x2) ** 2 + (y1-y2) ** 2)
        return distance
        
    def score(self, distance, base_score, scaling_factor=1):
        return base_score * scaling_factor / (distance + 1)
    
    def rank_directions(self, summed_directions):
        # Sort the summed_directions and get the sorted indices
        sorted_indices = sorted(range(len(summed_directions)), key=lambda x: summed_directions[x], reverse=True)
        # Get ranks in ascending order
        ranks = [sorted_indices.index(i) for i in range(len(summed_directions))]
        return ranks
    
       

class QLearning:
    
    def __init__(self, gamma=0.9):
        self.rewards = 0
    
        self.gamma = gamma
        #5actions 0:"SHOOT", 1:"AIM_RIGHT", 2:"AIM_LEFT" 3:"BACKWARD" 4:"wall" "TURN_RIGHT" "FORWARD"
        self.num_actions = 5
        #4states  0:angle_diff 1:turning_direction  2:is_cooldown 3:teammate_angle_diff
        self.Qform = np.zeros((9,2,2,9,5))
    
        
    def get_action(self, state: list, epsilon):
        if np.random.uniform(0, 1) < epsilon:
            # Explore randomly
            return np.random.randint(self.num_actions)
        else:
            # Exploit learned values
            return np.argmax(self.Qform[state[0], state[1], state[2], state[3]])
     
        
    #cannot shoot if cool  
    def get_reward(self, state: list, action):
        reward = 0
        #print(f"action {action} self.coach(state){self.coach(state)}")
        if action == self.coach(state):
            reward = 10
        elif action == 0:
            reward = 0.01
        else: 
            reward = -0.01
        
        return reward
       

    def coach(self, state: list):
        angle_diff = state[0] * 45  # Convert discrete state back to exact angle difference
        turning_direction = state[1]
        is_cooldown = state[2]
        teammate_angle_diff = state[3]
        
        # all the actual_angle_diff between 22.5~-22.5 is angle_diff 0 
        #if is in cooldown situation then 1
        #6actions 0:"SHOOT", 1:"AIM_RIGHT", 2:"AIM_LEFT" 3:"BACKWARD" 
        #0:clockwise   1: counter-clockwise 
        #1:clockwise   0: counter-clockwise ##do not know why
        if 0<= angle_diff <= 1 and turning_direction == 1:
            return "0"
        elif  angle_diff <= 2 and turning_direction == 0:
            return "2"
        elif 4 <= angle_diff <= 5 and turning_direction == 1:
            return "3"
        elif 4<= angle_diff <= 5 and turning_direction == 0:
            return "3"
        else:
            return "3"

    def update_qtable(self, old_state: list, action, reward, new_state: list, alpha):
        Qvalue = 0
        Qvalue_func = lambda x: (1 - alpha) * self.Qform[old_state[0],old_state[1], old_state[2], old_state[3], x] \
        + alpha * (reward + self.gamma * np.max(self.Qform[new_state[0], new_state[1], new_state[2], new_state[3]]))
            
        Qvalue = Qvalue_func(action)
        self.Qform[old_state[0], old_state[1], old_state[2], old_state[3], action] = Qvalue
          
    def initialize(self):
        self.Qform = np.zeros((9,2,2,9,5))
        
    def get_qtable(self):
        return self.Qform
    
    def output_qtable(self, seq):
        save_path = "/Users/harris/reS/TankMan/Shooter_Aiming_Qtable"+seq
        print(f"path{save_path}")
        with open(save_path, "wb") as file:
            pickle.dump(self.Qform, file)