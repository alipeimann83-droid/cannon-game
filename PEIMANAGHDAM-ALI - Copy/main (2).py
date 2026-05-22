from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, Ellipse, RoundedRectangle
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, ListProperty
from kivy.core.window import Window
from kivy.config import Config
from kivy.vector import Vector
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
import math
import random
from kivy.base import EventLoop
import json
import os

# Define constants for storing hall of fame data
HALL_OF_FAME_FILE = "hall_of_fame.json"

class Gandalf(Widget):
    cannon_angle = NumericProperty(0)
    bullet_speed = NumericProperty(0)
    charge_speed = NumericProperty(0.25)
    max_charge = NumericProperty(30)
    bombshell = BooleanProperty(False)
    bullet_drill = NumericProperty(3)
    laser = BooleanProperty(False)
    ammo = NumericProperty(5)
    maxAmmo = NumericProperty(5)



    
    def __init__(self, **kwargs):
        super(Gandalf, self).__init__(**kwargs)
        self.size = (Window.width/24, Window.height/24)
        self.x = self.width
        self.y = Window.height / 6

        with self.canvas:
            self.color = Color(1, 1, 1, 1)            
            
            self.rect = Rectangle(source="gandalf_the_grey__lotr____transparent__by_speedcam_df8bbo8-pre.png", pos=(self.x, self.y), size=self.size)

            self.color = Color(0.5, 0.1, 0.0, 1)            
            self.cannon_length = self.size[1]*1.3
            self.cannon_width = self.size[0] * 0.10

            self.cannon = Line(points=(self.x - self.width * 0.3, self.top + self.height * 0.3,
                        self.x - self.width * 0.3, self.top + self.height * 0.3), width=self.cannon_width)
            
            self.color = Color(1, 1, 1, 1)            

            self.charge_bar_height = Window.width/30
            self.charge_bar = Rectangle(source="istockphoto-1150547829-170667a.webp", pos=(Window.width/30, Window.height-self.height-Window.height/30), size=(Window.width * (self.bullet_speed / self.max_charge), self.charge_bar_height))

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = (self.x, self.y)
        self.rect.size = self.size

        self.cannon_length = self.size[1]*1.3
        self.cannon_width = self.size[0] * 0.10
        
        self.cannon.points = (self.center_x+self.width*0.4, self.center_y+self.height*0.4, 
                    self.center_x + self.cannon_length * math.cos(self.cannon_angle),
                    self.center_y + self.cannon_length * math.sin(self.cannon_angle))
        self.cannon.width = self.cannon_width

    def set_cannon_angle(self, mouse_pos):
        dx = mouse_pos[0] - self.center_x
        dy = mouse_pos[1] - self.center_y
        self.cannon_angle = math.atan2(dy, dx)  
        
        self.cannon.points = (self.center_x, self.center_y, 
                            self.center_x + self.cannon_length * math.cos(self.cannon_angle),
                            self.center_y + self.cannon_length * math.sin(self.cannon_angle))

    def charge(self):
        if self.bullet_speed < self.max_charge:
            self.bullet_speed += self.charge_speed
            self.charge_bar.size = ((Window.width/4) * (self.bullet_speed / self.max_charge), self.charge_bar_height)

    def shoot(self, game):
        if self.ammo > 0:
            bullet = Bullet()
            
            bullet.angle = self.cannon_angle
            bullet.pos = [self.center_x + (self.cannon_length) * math.cos(self.cannon_angle)-bullet.radius, self.center_y + (self.cannon_length) * math.sin(self.cannon_angle)-bullet.radius]
            bullet.color = (1, 1, 1, 1)
            bullet.speed = self.bullet_speed
            bullet.bombshell = self.bombshell
            bullet.drill  = self.bullet_drill
            bullet.laser = self.laser
            self.bullet_speed = 0
            if self.laser:
                bullet.mass = 0

            game.bullet_group.add(bullet)
            game.add_widget(bullet)  
            self.charge_bar.size = (0, self.charge_bar_height)
            
            self.ammo -= 1
    
    def on_window_resize(self, window, width, height):
        self.size = (Window.width/48, Window.width/48)
        self.x = (width/80) 
        self.y = Window.height / 6
        self.update_rect()     
        self.charge_bar.pos=(Window.width/30, Window.height-self.height-Window.height/30)

class Wormhole(Widget):
    def __init__(self, pos1, pos2, radius=50, color=(0.8, 0.5, 1), **kwargs):
        super(Wormhole, self).__init__(**kwargs)
        self.radius = radius

        with self.canvas:
            Color(color[0], color[1], color[2])
            self.wormhole1 = Ellipse(source="ca95a883b75aa4777c96b8976e4e60892fc51270.png", pos=(pos1[0] - self.radius, pos1[1] - self.radius), size=(2 * self.radius, 2 * self.radius))
            self.wormhole2 = Ellipse(source="ca95a883b75aa4777c96b8976e4e60892fc51270.png", pos=(pos2[0] - self.radius, pos2[1] - self.radius), size=(2 * self.radius, 2 * self.radius))

        self.pos1 = pos1
        self.pos2 = pos2

    def update_wormhole_positions(self):
        self.wormhole1.pos = (self.pos1[0] - self.radius, self.pos1[1] - self.radius)
        self.wormhole2.pos = (self.pos2[0] - self.radius, self.pos2[1] - self.radius)

    def is_bullet_in_wormhole(self, bullet):
        distance1 = math.sqrt((bullet.x - self.pos1[0])**2 + (bullet.y - self.pos1[1])**2)
        distance2 = math.sqrt((bullet.x - self.pos2[0])**2 + (bullet.y - self.pos2[1])**2)
        if distance1 < self.radius:
            return 1
        elif distance2 < self.radius:
            return 2
        return 0

    def teleport_bullet(self, bullet, wormhole_number):
        if wormhole_number == 1:
            bullet.x = self.pos2[0] + self.radius + 2
            bullet.y = self.pos2[1]
        elif wormhole_number == 2:
            bullet.x = self.pos1[0] + self.radius + 2
            bullet.y = self.pos1[1]

class Mirror(Widget):
    position = NumericProperty(0)
    lev_height = NumericProperty(0)
    
    def __init__(self, elastonio=False, **kwargs):
        super(Mirror, self).__init__(**kwargs)
        self.size = (10, Window.height / 4)
        self.x = Window.width / 2
        self.elastonio = elastonio
        
        self.lev_height = random.randint(0, 300)
        
        with self.canvas:
            self.color = Color(0, 0, 1, 0.5) if not self.elastonio else Color(0, 1, 0, 0.5)
            self.rect = Rectangle(source="ca95a883b75aa4777c96b8976e4e60892fc51270.png", pos=(self.x, self.y), size=self.size)
                        
        self.bind(pos=self.update_rect, size=self.update_rect)
        Window.bind(on_resize=self.on_window_resize)
        
    def update_rect(self, *args):
        self.rect.pos = (self.x, self.y)
        self.rect.size = self.size
    
    def on_window_resize(self, window, width, height):
        self.size = (10, height / 4)
        self.x = Window.width/24 * (self.position + 3) + (Window.width/24 - self.width)/2
        self.update_rect()

class Sauron(Widget):
    y_level = NumericProperty(3)
    
    def __init__(self, **kwargs):
        super(Sauron, self).__init__(**kwargs)
        self.y_level = random.randint(0,3)
        self.size = (Window.width/12, Window.width/12)
        self.x = Window.width - self.size[0] - 10
        self.y = Window.height / 6 + self.y_level*self.height
        
        with self.canvas:
            self.color = Color(1, 1, 1, 1)
            self.rect = Rectangle(source="eye_of_sauron__skyrimverse__live_action_render_by_aladdindragonson42_dgfma3j-pre.png", pos=(self.x, self.y), size=self.size)
            self.color = Color(1, 1, 1, 1)
            self.pillar = Rectangle(source="images.jpg", pos=(self.x+self.size[0]/4, Window.height / 6), size=(self.size[0]/2, self.y_level*self.height))
                        
        self.bind(pos=self.update_rect, size=self.update_rect)
        Window.bind(on_resize=self.on_window_resize)
        
    def update_rect(self, *args):
        self.rect.pos = (self.x, self.y)
        self.rect.size = self.size
        self.pillar.pos = (self.x, Window.height / 6)
        self.pillar.size = (self.size[0], self.y_level*self.height)
    
    def on_window_resize(self, window, width, height):
        self.size = (Window.width/24, Window.width/24)
        self.x = width - self.size[0] - (width/80) 
        self.y = Window.height / 6 + self.y_level*self.height
        self.update_rect()

class Stone(Widget):
    position = NumericProperty(0)
    y_level = NumericProperty(0)
    
    def __init__(self, perpetio = False, orc = False, **kwargs):
        super(Stone, self).__init__(**kwargs)
        self.size = (Window.width/24, Window.width/24)
        self.x = Window.width / 3
        self.y = Window.height / 3
        self.perpetio = perpetio
        
        with self.canvas:
            if orc:
                self.color = Color(1,1,1)
                self.source = "./3D-Orc.webp"
                self.rect = Rectangle(source=self.source, pos=(self.x, self.y), size=self.size)
                self.size = (Window.width/12, Window.width/12)

            else:
                self.color = Color(0.9, 0.9, 0.9, 1) if not self.perpetio else Color(0.5, 0.5, 0.5, 1)
                self.source = "445c7126ab593b81c95ce4d193653f98.jpg"
                self.rect = Rectangle(source=self.source, pos=(self.x, self.y), size=self.size)
                            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        self.rect.pos = (self.x, self.y)
        self.rect.size = self.size
    
    def on_window_resize(self, window, width, height, gandalf_y):
        self.size = (Window.width/24, Window.width/24)
        self.x = Window.width/24 * (self.position + 3)
        self.y = gandalf_y + Window.width/24 * self.y_level
        self.update_rect()    

class Bullet(Widget):
    mass = NumericProperty(0.3)
    speed = NumericProperty(25)
    t = NumericProperty(0)
    angle = NumericProperty(0)
    radius = NumericProperty(1)
    bombshell = BooleanProperty(False)
    drill = NumericProperty(3)
    duration = NumericProperty(100)
    rays = ListProperty([])

    def __init__(self, radius=20, **kwargs):
        super().__init__(**kwargs)
        self.prev_coordinates = [self.x,self.y]

        self.radius = radius
        self.size=(self.radius*2, self.radius*2)
        with self.canvas:
            Color(0.7, 0.2, 0.0)
            self.bullet = Ellipse(source="pngtree-lightning-round-frame-blue-plasma-magical-portal-png-image_12012208.png", pos=self.pos)

        self.bind(pos=self.update_bullet_position)

    def update_bullet_position(self, *args):
        self.bullet.pos = self.pos
        self.bullet.size = self.size

    def update_bullet_pos(self):
        self.prev_coordinates = [self.x,self.y]
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle) - self.mass*self.t
        self.t += 1
            
    def is_outside_screen(self, gandalf_y):
        return (self.x < 0 or self.x > Window.width or
                self.y < gandalf_y)

class Game(Widget):
    def __init__(self, screen_manager=None, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.fps = 60
        self.mouse = Vector(Window.mouse_pos)  
        
        self.score = 0
        self.shots = 0
        
        self.bullet_group = set()
        self.stone_group = set()
        self.mirror_group = set()
        self.wormhole_group = set()
        
        self.gandalf = Gandalf()
        self.sauron = Sauron()
                        
        with self.canvas.before:
            self.sky = Rectangle(source="./1072410.jpg", pos=(0, 0),size=(Window.width, Window.height))

            self.ground_color = Color(0.5, 0.5, 0.5, 1)
            self.ground = Rectangle(source="./ground_textures_3d_model_c4d_max_obj_fbx_ma_lwo_3ds_3dm_stl_956046_o.jpg", pos=(0, 0), size=(Window.width, self.gandalf.y))
        
        self.add_widget(self.gandalf)
        self.add_widget(self.sauron)
                        
        Clock.schedule_interval(self.update, 1 / self.fps)
        
        Window.fullscreen = 'auto' #set window to fullscreen
        
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        self.keys_pressed = set()
        self.keys_up = set()
        
        Window.bind(on_resize=self.on_window_resize)
        
        # Create the labels with backgrounds
        self.score_label = self.create_label(f"Score: {self.score}", 70, Window.height - 110)
        self.shots_label = self.create_label(f"Shots: {self.shots}", 70, Window.height - 160)
        self.ammo_label = self.create_label(f"Bullets: {self.gandalf.ammo}/{self.gandalf.maxAmmo}", 70, Window.height - 210)
        
    def create_label(self, text, x, y):
        label = Label(text=text, pos=(x, y), size_hint=(None, None), color=(1, 1, 1, 1), font_size='40sp')
                                        
        self.add_widget(label)
        return label

    def on_window_resize(self, window, width, height):
        self.gandalf.size = (Window.width / 26, Window.height / 10)
        self.gandalf.x = self.gandalf.width
        self.gandalf.y = Window.height / 6
        self.gandalf.update_rect()
        
        self.sauron.size = (Window.width / 24, Window.width / 24)
        self.sauron.x = Window.width - self.sauron.size[0]
        self.sauron.y = Window.height / 6 + self.sauron.size[1] * self.sauron.y_level
        self.sauron.update_rect()
        
        self.sky.size = (width, height - self.gandalf.y)
        self.sky.pos = (0, self.gandalf.y)
        
        self.ground.size = (width, self.gandalf.y)
        self.ground.pos = (0, 0)
                
        for stone in self.stone_group:
            stone.on_window_resize(window, width, height, self.gandalf.y)
        
        for mirror in self.mirror_group:
            mirror.on_window_resize(window, width, height)
            mirror.y = self.gandalf.y + mirror.lev_height
        
        for wormhole in self.wormhole_group:
            wormhole.update_wormhole_positions()
            
        self.score_label.pos = (60, Window.height - 110)
        self.shots_label.pos = (60, Window.height - 160)
        self.ammo_label.pos = (60, Window.height - 210)

        self.gandalf.charge_bar.pos = (0, height - self.gandalf.charge_bar_height)
                
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.keys_pressed.add(keycode[1])
        return True

    def _on_key_up(self, keyboard, keycode):
        self.keys_pressed.discard(keycode[1])
        self.keys_up.add(keycode[1])       
        
        return True

    def update(self, dt):
        self.mouse = Vector(Window.mouse_pos)
        
        if 'spacebar' in self.keys_pressed:
            self.gandalf.charge()
            
        if 'spacebar' in self.keys_up:
            if self.gandalf.ammo > 0:
                self.gandalf.shoot(self)
                self.shots += 1
                self.shots_label.text = f"Shots: {self.shots}"
                self.ammo_label.text = f"Bullets: {self.gandalf.ammo}/{self.gandalf.maxAmmo}"
                                    
        if '1' in self.keys_up:
            self.gandalf.laser = False
            self.gandalf.bombshell = False 
        
        if '2' in self.keys_up:
            self.gandalf.laser = False
            self.gandalf.bombshell = True 

        if '3' in self.keys_up:
            self.gandalf.laser = True
            self.gandalf.bombshell = False
            
        if 'escape' in self.keys_up:  # Check if the pressed key is 'escape'
            self.quit_game()
                        
        self.gandalf.set_cannon_angle(self.mouse)

        bullets_to_remove = []
        stones_to_remove = []
        
        for bullet in self.bullet_group:
            bullet.update_bullet_pos()
            stone_hit, stone = self.is_stone_hit(bullet, self.stone_group)
            
            if bullet.laser:
                new_coordinates = [bullet.x+bullet.radius , bullet.y+bullet.radius]
                prev_coordinates = [bullet.prev_coordinates[0]+bullet.radius, bullet.prev_coordinates[1]+bullet.radius]

                with self.canvas:
                    Color(1,0,0)
                    laser_ray = Line(points=prev_coordinates + new_coordinates, width=bullet.radius)
                    bullet.rays.append(laser_ray)
                    if len(bullet.rays) > 5:
                        self.canvas.remove(bullet.rays[0])
                        bullet.rays.pop(0)
            
            if bullet.is_outside_screen(self.gandalf.y) or (bullet.laser and bullet.t > bullet.duration):
                bullets_to_remove.append(bullet)
            
            elif stone_hit:
                if not stone.perpetio:
                    stones_to_remove.append(stone)

                if (not bullet.bombshell and not bullet.laser) or bullet.drill <= 1 or stone.perpetio:
                    bullets_to_remove.append(bullet)
                elif bullet.bombshell:
                    bullet.drill -= 1

            elif self.is_bullet_hit(bullet, self.sauron):
                self.sauron_hit()
                return
            
            for mirror in self.mirror_group:
            
                if self.is_bullet_hit_mirror(bullet, mirror):
                    if bullet.laser and not mirror.elastonio: 
                        self.reflect_bullet(bullet)
                    elif not bullet.laser and mirror.elastonio: 
                        self.reflect_bullet(bullet)
                    else:
                        bullets_to_remove.append(bullet)

            for wormhole in self.wormhole_group:
                wormhole_number = wormhole.is_bullet_in_wormhole(bullet)
                if wormhole_number:
                    wormhole.teleport_bullet(bullet, wormhole_number)
                    
                        
        for bullet in bullets_to_remove:
            if bullet.laser:
                for r in bullet.rays:
                    self.canvas.remove(r)
            
            self.remove_widget(bullet)
            self.bullet_group.remove(bullet)  
            
            if self.gandalf.ammo < 1 and len(self.bullet_group) == 0:
                self.quit_game()
            
        for stone in stones_to_remove:
            self.remove_widget(stone)
            self.stone_group.remove(stone)
            
        self.keys_up = set()
    
    def is_bullet_hit(self, bullet, sauron):
        return (bullet.x + bullet.radius > sauron.x and
                bullet.x - bullet.radius < sauron.x + sauron.width and
                bullet.y + bullet.radius > sauron.y and
                bullet.y - bullet.radius < sauron.y + sauron.height
        )
    
    def quit_game(self):
        self.save_score_and_shots()
        self.screen_manager.current = 'gameOver'  # Switch to the main menu

    def save_score_and_shots(self):
        hall_of_fame_file = 'hall_of_fame.json'
        entry = {"score": self.score, "shots": self.shots}
        
        if os.path.exists(hall_of_fame_file):
            with open(hall_of_fame_file, 'r') as file:
                hall_of_fame = json.load(file)
        else:
            hall_of_fame = []
        
        hall_of_fame.append(entry)
        
        with open(hall_of_fame_file, 'w') as file:
            json.dump(hall_of_fame, file)

    def sauron_hit(self):
        self.score += 1
        self.score_label.text = f"Score: {self.score}"
        
        self.regenerate_obstacles()
                
    def is_stone_hit(self, bullet, stones):
        for stone in stones:
            if self.is_bullet_hit(bullet, stone):
                return True, stone
        return False, None
    
    def is_bullet_hit_mirror(self, bullet, mirror):
        mirror_x = mirror.center_x
        return (bullet.prev_coordinates[0] < mirror_x < bullet.x or bullet.x < mirror_x < bullet.prev_coordinates[0]) and mirror.y < bullet.y < mirror.y+mirror.height
    
    def reflect_bullet(self, bullet):
        bullet.x = bullet.prev_coordinates[0]
        bullet.angle = math.pi - bullet.angle
        
    def regenerate_obstacles(self):
        self.gandalf.ammo = self.gandalf.maxAmmo
        self.ammo_label.text = f"Bullets: {self.gandalf.ammo}/{self.gandalf.maxAmmo}"
        
        self.score = 0
        self.shots = 0
        self.shots_label.text = f"Shots: {self.shots}"
        self.score_label.text = f"Score: {self.score}"


        self.remove_widget(self.sauron)

        self.sauron = Sauron()
        
        self.add_widget(self.sauron)

        for bullet in self.bullet_group:
            if bullet.laser:
                for r in bullet.rays:
                    self.canvas.remove(r)

            self.remove_widget(bullet)

        for stone in self.stone_group:
            self.remove_widget(stone)

        for mirror in self.mirror_group:
            self.remove_widget(mirror)

        for wormhole in self.wormhole_group:
            self.remove_widget(wormhole)

        self.bullet_group = set()
        self.stone_group = set()
        self.mirror_group = set()
        self.wormhole_group = set()

        cell_number = 24
        cell = Window.width / cell_number
        
        for i in range(cell_number - 6):
            choice = random.randint(0, 12)
            
            if choice == 0 or choice ==  10 or choice == 11 or choice ==  12:            
                n = random.randint(3, 7)
                for n in range(n):
                    stone = Stone(perpetio=False)
                    stone.x = cell * (i+3)
                    stone.y = self.gandalf.y + stone.height * n
                    stone.position = i
                    stone.y_level = n
                    self.stone_group.add(stone)
                    self.add_widget(stone)
            
            elif choice == 1 and i > 4:
                n = random.randint(3, 7)
                for n in range(n):
                    stone = Stone(perpetio=True)
                    stone.x = cell * (i+3)
                    stone.y = self.gandalf.y + stone.height * n
                    stone.position = i
                    stone.y_level = n
                    self.stone_group.add(stone)
                    self.add_widget(stone)
                
            elif choice == 2 and i > 4:
                mirror = Mirror()
                mirror.x = cell * (i+3) + (cell - mirror.width)/2
                mirror.position = i
                mirror.y = self.gandalf.y +mirror.lev_height
                self.mirror_group.add(mirror)
                self.add_widget(mirror)
            
            elif choice == 3 and i > 4:
                mirror = Mirror(elastonio=True)
                mirror.x = cell * (i+3) + (cell - mirror.width)/2
                mirror.position = i
                mirror.y = self.gandalf.y + mirror.lev_height
                self.mirror_group.add(mirror)
                self.add_widget(mirror)
            
            elif choice == 4 and i > 4:
                
                wormhole = Wormhole(
                    pos1=(cell * (i+3) + cell/3, random.uniform(self.gandalf.y + 100, Window.height)),
                    pos2=(
                        (cell * (i+3) + cell/3) + random.randint(400, 800),
                        random.uniform(self.gandalf.y + 100, Window.height)
                    ),
                    color=(random.randint(0,10)*0.1, random.randint(0,10)*0.1, random.randint(0,10)*0.1)
                )
                
                self.add_widget(wormhole)
                self.wormhole_group.add(wormhole)
            
            elif choice == 5 or choice == 6:
                stone = Stone(orc=True)
                stone.x = cell * (i+3)
                stone.y = self.gandalf.y
                stone.position = i
                self.stone_group.add(stone)
                self.add_widget(stone)
                                                
class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_normal = ''  # Remove default background
        self.background_color = (0, 0, 0, 0)  # Set the button to fully transparent
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.9)  # Dark gray color with semi-transparency
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)

        # Outer AnchorLayout to center the inner layout
        outer_layout = AnchorLayout()

        with self.canvas.before:
            self.sky = Rectangle(source="./the-lord-of-the-rings-gandalf-balrog-artwork-wallpaper.jpg", pos=(0, 0), size=(Window.width, Window.height))

        Window.bind(on_resize=self.on_window_resize)

        # Inner BoxLayout for buttons
        self.inner_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.update_button_sizes()

        # Play button
        self.play_button = RoundedButton(text="Play", font_size='40sp')
        self.play_button.bind(on_release=self.play_game)
        self.inner_layout.add_widget(self.play_button)

        # Options button
        self.options_button = RoundedButton(text="Hall of fame", font_size='40sp')
        self.options_button.bind(on_release=self.open_options)
        self.inner_layout.add_widget(self.options_button)

        # Help button
        self.help_button = RoundedButton(text="Help", font_size='40sp')
        self.help_button.bind(on_release=self.open_help)
        self.inner_layout.add_widget(self.help_button)

        # Quit button
        self.quit_button = RoundedButton(text="Quit", font_size='40sp')
        self.quit_button.bind(on_release=self.quit_game)
        self.inner_layout.add_widget(self.quit_button)

        # Add inner layout to outer layout
        outer_layout.add_widget(self.inner_layout)

        self.add_widget(outer_layout)

        # Bind window size changes to update button sizes
        Window.bind(on_size=self.on_window_resize)

    def on_window_resize(self, window, width, height):
        self.sky.size = (width, height)
        self.sky.pos = (0, 0)
        
        self.update_button_sizes()

    def update_button_sizes(self):
        button_width = Window.width * 0.4
        button_height = Window.height * 0.2
        self.inner_layout.size_hint = (None, None)
        self.inner_layout.size = (button_width, 4 * (button_height + self.inner_layout.spacing) - self.inner_layout.spacing)
        for button in self.inner_layout.children:
            button.size_hint = (None, None)
            button.size = (button_width, button_height)

    def play_game(self, instance):
        self.manager.current = 'game'

    def open_options(self, instance):
        self.manager.current = 'hallOfFame'

    def open_help(self, instance):
        self.manager.current = 'help'

    def quit_game(self, instance):
        App.get_running_app().stop()
                                        
class GameScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.game = Game(screen_manager=screen_manager)
        self.add_widget(self.game)

    def on_pre_enter(self, *args):
        self.game.regenerate_obstacles()
        
class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super(HelpScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Help label
        help_label = Label(text="Help", font_size='50sp', color=(1, 1, 1), halign='center', valign='middle', text_size=(Window.width, None))
        layout.add_widget(help_label)

        # Help text
        help_text_content = (
            "Your objective is to defeat Sauron by hitting his eye.\n"
            "Move your cursor to aim, press your spacebar to charge your shot\n"
            "and release it to shoot. The more you charge, the faster the bullet will be.\n"
            "You only have five shots. After that, Sauron will win and it's game over.\n"
            "Press ESC to quit the game.\n"
            "You have three different types of bullets. You can change between them by pressing:\n"
            "1 (bullet), 2 (bombshell), or 3 (laser)."
        )
        help_text = Label(text=help_text_content, font_size='20sp', color=(1, 1, 1))
        layout.add_widget(help_text)

        # Back to main menu button
        main_menu_button = RoundedButton(text="Main Menu", size_hint=(0.3, 0.2), pos_hint={'center_x': 0.5})
        main_menu_button.bind(on_release=self.go_to_main_menu)
        layout.add_widget(main_menu_button)

        # Set background
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            self.rect = Rectangle(source="7646cb03ac8c610345cb3e81974938fb.jpg", size=Window.size, pos=self.pos)

        self.bind(size=self.update_rect, pos=self.update_rect)
        self.add_widget(layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def go_to_main_menu(self, instance):
        self.manager.current = 'start'
                
class GameOverScreen(Screen):
    def __init__(self, **kwargs):
        super(GameOverScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Game Over label
        game_over_label = Label(text="Game Over", font_size='50sp', color=(0, 0, 0))
        layout.add_widget(game_over_label)
        
        # Back to main menu button
        main_menu_button = RoundedButton(text="Main Menu", size_hint=(0.3, 0.2), pos_hint={'center_x': 0.5})
        main_menu_button.bind(on_release=self.go_to_main_menu)
        layout.add_widget(main_menu_button)
        
        # Set red background
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Red color
            self.rect = Rectangle(source="1354113.png", size=Window.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        
        self.add_widget(layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def go_to_main_menu(self, instance):
        self.manager.current = 'start'

class HallOfFameScreen(Screen):
    def __init__(self, **kwargs):
        super(HallOfFameScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Hall of Fame label
        hall_of_fame_label = Label(text="Hall of Fame", font_size='50sp', color=(1, 1, 1))
        

        hall_of_fame_label.bind(size=self.update_label_rect, pos=self.update_label_rect)

        layout.add_widget(hall_of_fame_label)
        
        
        # Display the scores and shots
        self.scores_layout = BoxLayout(orientation='vertical', spacing=5)
        self.load_scores()
        layout.add_widget(self.scores_layout)
        
        # Back to main menu button
        main_menu_button = RoundedButton(text="Main Menu", size_hint=(0.3, 0.2), pos_hint={'center_x': 0.5})
        main_menu_button.bind(on_release=self.go_to_main_menu)
        layout.add_widget(main_menu_button)
        
        # Set background
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White color
            self.rect = Rectangle(source="gate-of-moria-lord-of-the-rings-thumb.jpg", size=Window.size, pos=self.pos)
        
        self.bind(size=self.update_rect, pos=self.update_rect)
        
        self.add_widget(layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def go_to_main_menu(self, instance):
        self.manager.current = 'start'
    
    def load_scores(self):
        hall_of_fame_file = 'hall_of_fame.json'
        
        if os.path.exists(hall_of_fame_file):
            with open(hall_of_fame_file, 'r') as file:
                hall_of_fame = json.load(file)
                
            # Sort by score and take the top 5
            top_scores = sorted(hall_of_fame, key=lambda x: x['score'], reverse=True)[:5]
            
            for entry in top_scores:
                score_label = Label(text=f"Score: {entry['score']} Shots: {entry['shots']}", font_size='20sp', color=(1, 1, 1), size_hint=(None, None), size=(Window.width * 0.5, 70))
                
                with score_label.canvas.before:
                    Color(0, 0, 0, 1)  # Dark color without transparency
                    self.rect = RoundedRectangle(size=score_label.size, pos=score_label.pos, radius=[10])
                
                score_label.bind(size=self.update_label_rect, pos=self.update_label_rect)
                
                self.scores_layout.add_widget(score_label)
                score_label.pos_hint = {'center_x': 0.5}
    
    def update_label_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.1, 0.1, 0.1, 0.85)
            RoundedRectangle(size=instance.size, pos=instance.pos, radius=[10])
                        
class CannonApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(GameScreen(name='game', screen_manager=sm))
        sm.add_widget(GameOverScreen(name='gameOver'))
        sm.add_widget(HallOfFameScreen(name='hallOfFame'))
        sm.add_widget(HelpScreen(name='help'))  # Add the HelpScreen
        return sm
        
if __name__ == '__main__':
    CannonApp().run()