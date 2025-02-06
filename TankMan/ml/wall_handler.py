import math
import random

ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]

class WallHandler:
    
    def __init__(self, row, col, size):
        self.row = row
        self.col = col
        self.size = size
        self.direction = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

    def aim(self, scene_info, map):
        x = int(scene_info['x'] / self.size) + 1
        y = int(scene_info['y'] / self.size) + 1

        correct_angle = scene_info['gun_angle'] if scene_info['gun_angle'] < 360 else 0
        gun_angle = correct_angle
        direction = self.direction[int(gun_angle/45)]

        if gun_angle % 90 == 0:
            bullet_range = int(300/self.size) + 1
        else:
            bullet_range = int(300/(self.size * math.sqrt(2))) + 1

        for i in range(0, bullet_range):
            target_x, target_y = x + direction[0]*i, y + direction[1]*i
            if (target_x >=0 and target_x < self.row) and (target_y >=0 and target_y < self.col):
                if map[target_x][target_y] == 1:
                    return "SHOOT"

        for angle in [45, -45, 90, -90, 135, -135, 180]:
            gun_angle = correct_angle + angle
            if gun_angle >= 360:
                gun_angle -= 360
            elif gun_angle < 0:
                gun_angle += 360
            direction = self.direction[int(gun_angle/45)]

            if gun_angle % 90 == 0:
                bullet_range = int(300/self.size) + 1
            else:
                bullet_range = int(300/(self.size * math.sqrt(2))) + 1

            for i in range(0, bullet_range):
                target_x, target_y = x + direction[0]*i, y + direction[1]*i
                if (target_x >=0 and target_x < self.row) and (target_y >=0 and target_y < self.col):
                    if map[target_x][target_y] == 1:
                        if angle > 0:
                            return "AIM_RIGHT"
                        else:
                            return "AIM_RIGHT"
                else:
                    continue

        #no wall -> random move
        move_act = random.randrange(4)
        if move_act == 0:
            return "FORWARD"
        elif move_act == 1:
            return "BACKWARD"
        elif move_act == 2:
            return "TURN_RIGHT"
        elif move_act == 3:
            return "TURN_LEFT"

        return "NONE"


    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
    #range of a bullet is 300 pixels    
    def decide_action(self, scene_info, radius=300):
        self.initialize_record()
        self.initialize_situation()
        
        tankX = 0
        tankY = 0
        tank_guns_angle = 0

        tankX = scene_info['teammate_info'][0]['x']
        tankY = scene_info['teammate_info'][0]['y']
        tank_guns_angle = scene_info['teammate_info'][0]['gun_angle']
        tank_angle = scene_info['teammate_info'][0]['angle']
        
               
        for enemy in scene_info['competitor_info']:
            enemy_dis = self.distance(tankX, tankY, enemy['x'], enemy['y'])
            if  enemy_dis <= radius:

                self.enemies_in_radius = True
                self.enemies_record.append((enemy['x'], enemy['y'], enemy_dis))  
            
       
        for wall in scene_info['walls_info']:
            wall_dis = self.distance(tankX, tankY, wall['x'],wall['y'])
            
            if wall_dis <= radius:
                self.wall_in_radius = True
                self.walls_record.append((wall['x'], wall['y'], wall_dis))
                
                
        angle_list = []      
        for wall in self.walls_record:
            #0:x , 1:y, 2:angle
            angle_list.append((wall[0],wall[1],self.angle_to_target(tankX,tankY,wall[0],wall[1])))
                
        #0:wall_x , 1:wall_y, 2:angle, 3:diff_angle between shooter and wall
        shooting_list = self.find_closest_angle(tank_guns_angle , angle_list)


        # Sort records by distance in ascending order
        #self.walls_record.sort(key=lambda x: x[2])
        #self.enemies_record.sort(key=lambda x: x[2]) 
          
        if self.wall_in_radius and not self.enemy_in_radius:
            return "Hit_Wall"
        elif self.wall_in_radius and self.enemy_in_radius:
            return "Hit_Enemy"
        elif self.enemy_in_radius and not self.wall_in_radius:
            return None
        else:
            return None
        
    def initialize_record(self):
        self.enemies_record = []
        self.walls_record = []
    
    def initialize_situation(self):
        self.wall_in_radius = False
        self.enemy_in_radius = False


    def angle_to_target(self, tank_x, tank_y, target_x, target_y):
        dx = target_x - tank_x
        dy = target_y - tank_y
        angle = math.degrees(math.atan2(dy, dx))
        return angle % 360

    def find_closest_angle(self, gun_angle, target_angle_list):
        diff_list = []
        for target in target_angle_list:
            diff_list.append((target[0], target[1], target[2], abs(target[2]-gun_angle)))
        
        sorted_diff_list = sorted(diff_list, key=lambda x: x[3])
        return sorted_diff_list