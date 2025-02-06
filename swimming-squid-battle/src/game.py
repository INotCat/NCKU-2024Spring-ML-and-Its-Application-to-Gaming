import copy
import json
import os.path

import pygame

from mlgame.game.paia_game import PaiaGame, GameResultState, GameStatus
from mlgame.utils.enum import get_ai_name
from mlgame.view.decorator import check_game_progress, check_game_result
from mlgame.view.view_model import *
from .foods import *
from .game_object import Squid, LevelParams
from .sound_controller import SoundController


def revise_ball(ball: Squid, playground: pygame.Rect):
    ball_rect = copy.deepcopy(ball.rect)
    if ball_rect.left < playground.left:
        ball_rect.left = playground.left
    elif ball_rect.right > playground.right:
        ball_rect.right = playground.right

    if ball_rect.top < playground.top:
        ball_rect.top = playground.top
    elif ball_rect.bottom > playground.bottom:
        ball_rect.bottom = playground.bottom
    ball.rect = ball_rect
    pass

FOOD_LIST = [Food1, Food2, Food3, Garbage1, Garbage2, Garbage3]


class SwimmingSquid(PaiaGame):
    """
    This is a Interface of a game
    """

    def __init__(
            self,
            level: int = -1,
            level_file: str = "",
            game_times: int = 1,
            sound: str = "off",
            *args, **kwargs):
        super().__init__(user_num=1)
        self.game_result_state = GameResultState.FAIL
        self.scene = Scene(width=WIDTH, height=HEIGHT, color=BG_COLOR, bias_x=0, bias_y=0)
        self._level = level
        self._level_file = level_file
        self._used_file = ""
        self.foods = pygame.sprite.Group()
        self.sound_controller = SoundController(sound)
        self._overtime_count = 0
        self._game_times = game_times
        self._winner = []
        self._foods_num = []
        self._foods_max_num = []
        self._add_score = {"1P":0, "2P":0}

        self._init_game()

    def _init_game_by_file(self, level_file_path: str):
        try:
            with open(level_file_path) as f:
                game_params = LevelParams(**json.load(f))
                self._used_file = level_file_path

        except:
            # If the file doesn't exist, use default parameters
            print("此關卡檔案不存在，遊戲將會會自動使用第一關檔案 001.json。")
            print("This level file is not existed , game will load 001.json automatically.")
            with open(os.path.join(LEVEL_PATH, "001.json")) as f:
                game_params = LevelParams(**json.load(f))
                self._level = 1
                self._level_file = ""
                self._used_file = "001.json"
        finally:
            # set game params
            self._foods_num.extend([game_params.food_1, game_params.food_2, game_params.food_3, game_params.garbage_1, game_params.garbage_2, game_params.garbage_3])
            self._foods_max_num.extend([game_params.food_1_max, game_params.food_2_max, game_params.food_3_max, game_params.garbage_1_max, game_params.garbage_2_max, game_params.garbage_3_max])
            if game_params.playground_size_w > 700:
                game_params.playground_size_w = 700
            self.playground = pygame.Rect(
                0, 0,
                game_params.playground_size_w,
                game_params.playground_size_h
            )

            self._score_to_pass = game_params.score_to_pass
            self._frame_limit = game_params.time_to_play

            self.playground.center = ((WIDTH - WIDTH_OF_INFO) / 2, HEIGHT / 2)

            # init game
            self.squid1 = Squid(1, 200, 300)
            self.squid2 = Squid(2, 500, 300)
            self.foods.empty()
            for i in range(6):
                self._create_foods(FOOD_LIST[i], self._foods_num[i])
            # self._create_foods(Food1, game_params.food_1)
            # self._create_foods(Food2, game_params.food_2)
            # self._create_foods(Food3, game_params.food_3)
            # self._create_foods(Garbage1, game_params.garbage_1)
            # self._create_foods(Garbage2, game_params.garbage_2)
            # self._create_foods(Garbage3, game_params.garbage_3)

            self.frame_count = 0
            self._frame_count_down = self._frame_limit
            self._new_food_frame = 0
            self._overtime_count = 0
            self.sound_controller.play_music()

    def update(self, commands):
        # handle command
        ai_1p_cmd = commands[get_ai_name(0)]
        if ai_1p_cmd is not None:
            action_1 = ai_1p_cmd[0]
        else:
            action_1 = "NONE"

        ai_2p_cmd = commands[get_ai_name(1)]
        if ai_2p_cmd is not None:
            action_2 = ai_2p_cmd[0]
        else:
            action_2 = "NONE"


        self.squid1.update(self.frame_count, action_1)
        self.squid2.update(self.frame_count, action_2)
        revise_ball(self.squid1, self.playground)
        revise_ball(self.squid2, self.playground)
        # create new food
        if self.frame_count - self._new_food_frame > 150:
            for i in range(6):
                if self._foods_max_num[i] > self._foods_num[i]:
                    self._foods_num[i] += 1
                    self._create_foods(FOOD_LIST[i], 1)
            self._new_food_frame = self.frame_count

        # update sprite
        self.foods.update(playground=self.playground, squid=self.squid1)

        # handle collision

        self._check_foods_collision()
        # self._timer = round(time.time() - self._begin_time, 3)
        self._check_squids_collision()

        self.frame_count += 1
        self._frame_count_down = self._frame_limit - self.frame_count
        # self.draw()

        if not self.is_running:
            return "RESET"

    def _check_foods_collision(self):
        hits = pygame.sprite.spritecollide(self.squid1, self.foods, True)
        if hits:
            for food in hits:
                # growth play special sound
                self.squid1.eat_food_and_change_level_and_play_sound(food, self.sound_controller)
                self._create_foods(food.__class__, 1)
                if isinstance(food, (Food1, Food2, Food3,)):
                    self.sound_controller.play_eating_good()
                elif isinstance(food, (Garbage1, Garbage2, Garbage3,)):
                    self.sound_controller.play_eating_bad()
        hits = pygame.sprite.spritecollide(self.squid2, self.foods, True)
        if hits:
            for food in hits:
                # growth play special sound
                self.squid2.eat_food_and_change_level_and_play_sound(food, self.sound_controller)
                self._create_foods(food.__class__, 1)
                if isinstance(food, (Food1, Food2, Food3,)):
                    self.sound_controller.play_eating_good()
                elif isinstance(food, (Garbage1, Garbage2, Garbage3,)):
                    self.sound_controller.play_eating_bad()

    def _check_squids_collision(self):
        hit = pygame.sprite.collide_rect(self.squid1, self.squid2)
        if hit:
            if self.squid1.lv > self.squid2.lv:
                self.squid1.collision_between_squids(COLLISION_SCORE["WIN"], self.frame_count, self.sound_controller)
                self.squid2.collision_between_squids(COLLISION_SCORE["LOSE"], self.frame_count, self.sound_controller)
            elif self.squid1.lv < self.squid2.lv:
                self.squid1.collision_between_squids(COLLISION_SCORE["LOSE"], self.frame_count, self.sound_controller)
                self.squid2.collision_between_squids(COLLISION_SCORE["WIN"], self.frame_count, self.sound_controller)
            else:
                # draw
                self.squid1.collision_between_squids(COLLISION_SCORE["DRAW"], self.frame_count, self.sound_controller)
                self.squid2.collision_between_squids(COLLISION_SCORE["DRAW"], self.frame_count, self.sound_controller)

    def get_data_from_game_to_player(self):
        """
        send something to game AI
        we could send different data to different ai
        """
        to_players_data = {}
        foods_data = []
        for food in self.foods:
            foods_data.append(
                {"x": food.rect.centerx, "y": food.rect.centery,
                 "w": food.rect.width, "h": food.rect.height,
                 "type": str(food.type), "score": food.score}
            )

        data_to_1p = {
            "frame": self.frame_count,
            "self_x": self.squid1.rect.centerx,
            "self_y": self.squid1.rect.centery,
            "self_w": self.squid1.rect.width,
            "self_h": self.squid1.rect.height,
            "self_vel": self.squid1.vel,
            "self_lv": self.squid1.lv,
            "opponent_x":self.squid2.rect.centerx,
            "opponent_y":self.squid2.rect.centery,
            "opponent_lv": self.squid2.lv,
            "foods": foods_data,
            "score": self.squid1.score,
            "score_to_pass": self._score_to_pass,
            "status": self.get_game_status()

        }

        data_to_2p = {
            "frame": self.frame_count,
            "self_x": self.squid2.rect.centerx,
            "self_y": self.squid2.rect.centery,
            "self_w": self.squid2.rect.width,
            "self_h": self.squid2.rect.height,
            "self_vel": self.squid2.vel,
            "self_lv": self.squid2.lv,
            "opponent_x": self.squid1.rect.centerx,
            "opponent_y": self.squid1.rect.centery,
            "opponent_lv": self.squid1.lv,
            "foods": foods_data,
            "score": self.squid2.score,
            "score_to_pass": self._score_to_pass,
            "status": self.get_game_status()

        }

        to_players_data[get_ai_name(0)] = data_to_1p
        to_players_data[get_ai_name(1)] = data_to_2p
        # should be equal to config. GAME_SETUP["ml_clients"][0]["name"]

        return to_players_data

    def get_game_status(self):

        if self.is_running:
            status = GameStatus.GAME_ALIVE
        elif self.is_passed:
            status = GameStatus.GAME_PASS
        else:
            status = GameStatus.GAME_OVER
        return status

    def reset(self):
        if self.is_passed:
            self.sound_controller.play_cheer()
        else:
            self.sound_controller.play_fail()

        if self._winner.count("1P") > self._game_times/2: # 1P 贏
            self._winner.clear()
            print("玩家 1 獲勝！開啟新一輪對戰！")
        elif self._winner.count("2P") > self._game_times/2: # 2P 贏
            self._winner.clear()
            print("玩家 2 獲勝！開啟新一輪對戰！")
        else:
            pass
        self._init_game()


    def _init_game(self):
        if path.isfile(self._level_file):
            # set by injected file
            self._init_game_by_file(self._level_file)
        else:
            level_file_path = os.path.join(LEVEL_PATH, f"{self._level:03d}.json")
            self._init_game_by_file(level_file_path)

    @property
    def is_passed(self):
        if self.squid1.score >= self._score_to_pass or self.squid2.score >= self._score_to_pass: # 達成目標分數
            if self.squid1.score == self.squid2.score and self._overtime_count < 1: # 延長賽
                self._frame_limit += 600
                self._score_to_pass += 50
                self._overtime_count += 1
                print("同分延長賽")
                return False
            return True
        else:
            return False

    @property
    def time_out(self):
        if self.frame_count >= self._frame_limit:
            if self.squid1.score == self.squid2.score and self._overtime_count < 1:  # 延長賽
                self._frame_limit += 300
                self._overtime_count += 1
                print("超時延長賽")
                return False
            else:
                print("時間到")
                return True
        else:
            return False


    @property
    def is_running(self):

        # return self.frame_count < self._frame_limit
        return (not self.time_out) and (not self.is_passed)

    def get_scene_init_data(self):
        """
        Get the initial scene and object information for drawing on the web
        """
        # bg_path = path.join(ASSET_PATH, "img/background.jpg")
        # background = create_asset_init_data(
        #     "background", WIDTH, HEIGHT, bg_path,
        #     github_raw_url="https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/easy_game/main/asset/img/background.jpg")

        scene_init_data = {
            "scene": self.scene.__dict__,
            "assets": [
                create_asset_init_data("bg", 1000, 1000, BG_PATH, BG_URL),
                create_asset_init_data("squid1", SQUID_W, SQUID_H, SQUID_PATH, SQUID_URL),
                create_asset_init_data("squid2", SQUID_W, SQUID_H, SQUID2_PATH, SQUID2_URL),
                create_asset_init_data(IMG_ID_FOOD01_L, FOOD_LV1_SIZE, FOOD_LV1_SIZE, FOOD01_L_PATH, FOOD01_L_URL),
                create_asset_init_data(IMG_ID_FOOD02_L, FOOD_LV2_SIZE, FOOD_LV2_SIZE, FOOD02_L_PATH, FOOD02_L_URL),
                create_asset_init_data(IMG_ID_FOOD03_L, FOOD_LV3_SIZE, FOOD_LV3_SIZE, FOOD03_L_PATH, FOOD03_L_URL),
                create_asset_init_data(IMG_ID_FOOD01_R, FOOD_LV1_SIZE, FOOD_LV1_SIZE, FOOD01_R_PATH, FOOD01_R_URL),
                create_asset_init_data(IMG_ID_FOOD02_R, FOOD_LV2_SIZE, FOOD_LV2_SIZE, FOOD02_R_PATH, FOOD02_R_URL),
                create_asset_init_data(IMG_ID_FOOD03_R, FOOD_LV3_SIZE, FOOD_LV3_SIZE, FOOD03_R_PATH, FOOD03_R_URL),
                create_asset_init_data("garbage01", FOOD_LV1_SIZE, FOOD_LV1_SIZE, GARBAGE01_PATH, GARBAGE01_URL),
                create_asset_init_data("garbage02", FOOD_LV2_SIZE, FOOD_LV2_SIZE, GARBAGE02_PATH, GARBAGE02_URL),
                create_asset_init_data("garbage03", FOOD_LV3_SIZE, FOOD_LV3_SIZE, GARBAGE03_PATH, GARBAGE03_URL),
            ],
            "background": [
                # create_image_view_data(
                #     'bg', self.playground.x, self.playground.y,
                #     self.playground.w, self.playground.h)
            ]
            # "audios": {}
        }
        return scene_init_data

    @check_game_progress
    def get_scene_progress_data(self):
        """
        Get the position of game objects for drawing on the web
        """
        foods_data = []
        for food in self.foods:
            foods_data.append(food.game_object_data)
        game_obj_list = [self.squid1.game_object_data, self.squid2.game_object_data]
        toggle_objs = [
            create_text_view_data(f"{self._winner.count('1P')}:{self._winner.count('2P')}", 795, 20, "#EEEEEE",
                                  "36px Consolas BOLD"),
            create_text_view_data(f"Timer:{self._frame_count_down:04d}", 745, 80, "#EEEEEE", "20px Consolas BOLD"),
            # create_text_view_data(f"", 785, 80, "#EEEEEE", "18px Consolas BOLD"),
            create_text_view_data(f"File :{os.path.basename(self._used_file)}", 745, 120, "#EEEEEE", "20px Consolas BOLD"),
            # create_text_view_data(f"File :{self._level_file}", 605, 80, "#EEEEEE", "10px Consolas BOLD"),
            create_text_view_data(f"Goal :{self._score_to_pass:04d} pt", 745, 160, "#EEEEEE", "20px Consolas BOLD"),
            # create_text_view_data(f"", 785, 140, "#EEEEEE", "18px Consolas BOLD"),
            create_image_view_data("squid1", 705, 220, 76, 114),
            # create_text_view_data("1P", 705, 130, "#EEEEEE", "22px Consolas BOLD"),
            create_text_view_data(f"Lv     : {self.squid1.lv}", 785, 220, "#EEEEEE", "16px Consolas BOLD"),
            create_text_view_data(f"Next Lv: {LEVEL_THRESHOLDS[self.squid1.lv - 1]-self.squid1.score :04d} pt", 785, 250, "#EEEEEE", "16px Consolas BOLD"),
            create_text_view_data(f"Vel    : {self.squid1.vel:2d}", 785, 280, "#EEEEEE", "16px Consolas BOLD"),
            create_text_view_data(f"Score  : {self.squid1.score:04d} pt", 785, 310, "#EEEEEE", "16px Consolas BOLD"),
            # create_text_view_data("2P", 705, 310, "#EEEEEE", "22px Consolas BOLD"),
            create_image_view_data("squid2", 705, 410, 76, 114),
            create_text_view_data(f"Lv     : {self.squid2.lv}", 785, 410, "#EEEEEE", "16px Consolas BOLD"),
            create_text_view_data(f"Next Lv: {LEVEL_THRESHOLDS[self.squid2.lv - 1] - self.squid2.score :04d} pt", 785,
                                  440, "#EEEEEE", "16px Consolas BOLD"),
            create_text_view_data(f"Vel    : {self.squid2.vel:2d}", 785, 470, "#EEEEEE", "16px Consolas BOLD"),
            create_text_view_data(f"Score  : {self.squid2.score:04d} pt", 785, 500, "#EEEEEE", "16px Consolas BOLD"),
        ]
        game_obj_list.extend(foods_data)
        backgrounds = [
            create_image_view_data(
                'bg', self.playground.x, self.playground.y,
                self.playground.w, self.playground.h)
        ]
        foregrounds = [

        ]

        scene_progress = create_scene_progress_data(
            frame=self.frame_count, background=backgrounds,
            object_list=game_obj_list,
            foreground=foregrounds, toggle=toggle_objs)
        return scene_progress

    @check_game_result
    def get_game_result(self):
        """
        send game result
        """
        if self.get_game_status() == GameStatus.GAME_PASS:
            self.game_result_state = GameResultState.FINISH
        self.rank()
        return {"frame_used": self.frame_count,
                "state": self.game_result_state,
                "attachment": [
                    {
                        "player": get_ai_name(0),
                        "rank": self.squid1.rank,
                        "score": self.squid1.score,
                        "wins":f"{self._winner.count('1P')} / {self._game_times}"
                        # "passed": self.is_passed
                    },
                    {
                        "player": get_ai_name(1),
                        "rank": self.squid2.rank,
                        "score": self.squid2.score,
                        "wins":f"{self._winner.count('2P')} / {self._game_times}"
                        # "passed": self.is_passed
                    }
                ]

                }

    def get_keyboard_command(self):
        """
        Define how your game will run by your keyboard
        """
        cmd_1p = []
        cmd_2p = []
        key_pressed_list = pygame.key.get_pressed()
        if key_pressed_list[pygame.K_UP]:
            cmd_1p.append("UP")
        elif key_pressed_list[pygame.K_DOWN]:
            cmd_1p.append("DOWN")
        elif key_pressed_list[pygame.K_LEFT]:
            cmd_1p.append("LEFT")
        elif key_pressed_list[pygame.K_RIGHT]:
            cmd_1p.append("RIGHT")
        else:
            cmd_1p.append("NONE")

        if key_pressed_list[pygame.K_w]:
            cmd_2p.append("UP")
        elif key_pressed_list[pygame.K_s]:
            cmd_2p.append("DOWN")
        elif key_pressed_list[pygame.K_a]:
            cmd_2p.append("LEFT")
        elif key_pressed_list[pygame.K_d]:
            cmd_2p.append("RIGHT")
        else:
            cmd_2p.append("NONE")

        return {get_ai_name(0): cmd_1p, get_ai_name(1):cmd_2p}

    def _create_foods(self, FOOD_TYPE, count: int = 5):
        for i in range(count):
            # add food to group
            food = FOOD_TYPE(self.foods)
            food.set_center_x_and_y(
                random.randint(self.playground.left, self.playground.right),
                random.randint(self.playground.top, self.playground.bottom)
            )

        pass

    def rank(self):
        '''

        '''
        if self.squid1.score > self.squid2.score:
            self.squid1.rank = 1
            self.squid2.rank = 2
            self._winner.append("1P")
        elif self.squid1.score < self.squid2.score:
            self.squid1.rank = 2
            self.squid2.rank = 1
            self._winner.append("2P")
        else:
            self.squid1.rank = 1
            self.squid2.rank = 1
            self._winner.append("DRAW")
