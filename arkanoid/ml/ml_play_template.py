import sys, random, os, pickle

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):

        self.prev_ballX = 0  
        self.prev_ballY = 0
        self.platformX = 0

        self.level = 0
        #self.run = 0
        self.dataFinal = []
        self.game_status = None
        #print(ai_name)

    def update(self, scene_info, *args, **kwargs):
        ### Grap all the information that we need to make a landing prediction
        self.curr_ballX = scene_info['ball'][0]
        self.curr_ballY = scene_info['ball'][1]
        self.platformX = scene_info['platform'][0]
        # Calculate the direction 
        deltaX = self.curr_ballX - self.prev_ballX
        deltaY = self.curr_ballY - self.prev_ballY
        # Update the previous ball position
        self.prev_ballX = scene_info['ball'][0]
        self.prev_ballY = scene_info['ball'][1]
        # Caculate the direction of velocity and the slope
        direction = self.direction(deltaX, deltaY)
        if not deltaX == 0:
            slope = deltaY / deltaX
        else:
            slope = 1
            
        if not slope == 0:
            brickHitCheck = self.brick_consideration(scene_info, direction, slope)
            #print(brickHitCheck)
        else:
            brickHitCheck = 1
            command = "NONE"    
        
        # Consider if the ball is moving upward, and may hit on ball, we move platform   
        if brickHitCheck != 0 and deltaY <=0:
            landingX = brickHitCheck
            if self.platformX+random.randint(-5,5) <= self.curr_ballX:
                command = "MOVE_RIGHT"
            else:
                    command = "MOVE_LEFT"
          
            #command = self.platform_decision(scene_info, landingX)
        # If ball move upward, then the platform should not move
        elif deltaY >= 0 :
            landingX = self.landing_prediction(slope)
            #print(landingX)
            command = self.platform_decision(scene_info, landingX)
        else:
            command = "NONE"

        ## For auto command usage
        #if(scene_info["status"] == "GAME_PASS"):
        #    self.run +=1
            #print("run=", self.run)  
 
        # Save the game status as a barometer to whether or not save the file  
        if scene_info["status"] == "GAME_PASS":
            self.game_status = "GAME_PASS"
        else:
            self.game_status = "GAME_OVER"
        # Transform the command direction into numeric representation
        if command == "MOVE_LEFT":
            Cvalue = -1
        elif command == "MOVE_RIGHT":
            Cvalue = 1
        else:
            Cvalue = 0
        # Save file    
        dataPerFrame = [self.curr_ballX, self.curr_ballY, deltaX, deltaY,
                          direction, self.platformX, scene_info["frame"] ,Cvalue]
        # Append data per frame to a big list we save to file
        self.dataFinal.append(dataPerFrame)
        # Flush current data for the usage of next frame
        dataPerFrame = []     
               
        # Make the caller to invoke `reset()` for the next round.
        if (scene_info["status"] == "GAME_OVER" or
            scene_info["status"] == "GAME_PASS"):
            return "RESET"
        #serve ball
        if not scene_info["ball_served"]:
            command = "SERVE_TO_LEFT"
        
        return command
    
    def bounce_consideration(self, landingX):
        # According to the even and odd characteristic to predict the x-intercept
        bounce_count = int(landingX/200)
        if bounce_count%2 == 0:
            landingX = abs(landingX-200*bounce_count)
        else:
            landingX = 200-abs(landingX-200*bounce_count)
        return landingX    
        
    def landing_prediction(self, slope):
        # If slope = 0 meaning deltaY is 0 
        if slope == 0:
            landingX = self.curr_ballX+random.randint(-5,5)
        # Calculate the landing point (x-intercept of two lines)
        else:
            landingX = ( (400-self.curr_ballY)/slope ) + self.curr_ballX
            landingX = self.bounce_consideration(landingX)
        return landingX
    
    def platform_decision(self, scene_info,landingX):
        # Make decisions according to the predict landing point with a random threshold
        if landingX > (self.platformX +20+random.randint(-15, 15)):
            command = "MOVE_RIGHT"
        elif landingX < (self.platformX +20+random.randint(-15, 15)):
            command = "MOVE_LEFT"
        else:
            command = "NONE"
        
        return command
    
    def brick_consideration(self, scene_info, direction, slope): 
        for brick in scene_info['bricks']+scene_info['hard_bricks']:
            brickX, brickY = brick
            hitOnBirckX = ((brickY+10) - self.curr_ballY ) / slope + self.curr_ballX
        
            # If the hit on is in this area meaning hit the brick
            if hitOnBirckX - brickX < 25:
                # Calculate the landing point
                beforeReflec_X = (400 - self.curr_ballY) / slope + self.curr_ballX
                afterReflec_X = 2 * hitOnBirckX - beforeReflec_X
                # Check if the landing point is within the boundary
                ##if afterReflec_X >= 200 or afterReflec_X <= 0:
                landingPointX = self.bounce_consideration(afterReflec_X) 
                #print(landingPointX)
                return landingPointX
        return 0
    
    def direction(self, deltaX, deltaY):
    # 0(↘),1(↗),2(↙),3(↖)
        if (deltaX > 0):
            if ( deltaY > 0):
                direction = 0 
            else:
                direction = 1
        else:
            if ( deltaY > 0):
                direction = 2
            else:    
                direction = 3
        return direction

    def reset(self):
        """
        Reset the status
        """
        # Save the file to specific directory
        index = "8"
        filepath = "/Users/harris/MLGame/log" + index
        print(filepath)
        if (self.game_status == "GAME_PASS"):
            filepath = "/Users/harris/MLGame/log" + index
            # one shot is 10, without is 9
            filename = sys.argv[9]+ "-" + index +".pickle"
            print(filename)
            with open(os.path.join(filepath, filename), "wb") as f:   
                pickle.dump(self.dataFinal, f) 
        #if self.run == 1:
        #    sys.exit()  
        #self.ball_served = False