import pygame
import sys
import math
import random
from compliance import ComplianceModule
from enum import Enum

pygame.init()

WIDTH = 1600
HEIGHT = 600
ROAD_MIDDLE = HEIGHT//2
ROAD_TOP = HEIGHT//2 - ROAD_MIDDLE//2
ROAD_BOTTOM = HEIGHT//2 + ROAD_MIDDLE//2
ROAD_HEIGHT = ROAD_BOTTOM - ROAD_TOP
CAR_SCREEN_POSITION = WIDTH//6
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Driving Simulation - Highway & City")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (160, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 160)
GRAY = (80, 80, 80)
DARKER_GRAY = (50, 50, 50)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
BUILDING_COLOR = (160, 160, 160)
WINDOW_COLOR = (255, 255, 153)
YELLOW = (255, 255, 0)
PURPLE = (238, 130, 238)
TAN = (210, 180, 140)
LIGHT_TAN = (255, 228, 196)
LIGHT_BROWN = (255, 222, 173)
INFO_BOX_COLOR = (0, 0, 0, 150)  # Semi-transparent black

HIGHWAY = "highway"
CITY = "city"
current_environment = CITY

class Weather(Enum):
    Clear = 'clear'
    Rain = 'rain'
    Snow = 'snow'

class IncidentType(Enum):
    Collision = 1
    TrafficLightViolation = 2
    SpeedViolation = 3
    CollisionInvolvingPedestrian = 4

class Incident:
    def __init__(self, incident_time: int, incident_type: IncidentType, data: dict):
        self.incident_time = incident_time
        self.incident_type = incident_type
        self.data = data
    
    def __str__(self):
        return f"{self.incident_time}: {self.incident_type} - {self.data}"

class IncidentReport:
    def __init__(self):
        self.event_log = []

    def add_incident(self, incident: Incident):
        self.event_log.append(str(incident))
        print(incident)

    def print_report(self):
        print("Incident Report:")
        for event in self.event_log:
            print(event)

class GameObject:
    _current_object_id = 0
    def __init__(self, x=0, y=0, w=10, h=10):
        self.bounds = pygame.Rect(x, y, w, h)        
        self.init_id()

    def init_id(self):
        self.id = GameObject._current_object_id
        GameObject._current_object_id += 1

    def reset(self, game):
        pass

    def update(self, game):
        pass

    def draw(self, game):
        pass

    @property
    def x(self):
        return self.bounds.x
    
    @x.setter
    def x(self, nx):
        self.bounds.x = nx
    
    @property
    def y(self):
        return self.bounds.y
    
    @y.setter
    def y(self, ny):
        self.bounds.y = ny

    @property
    def width(self):
        return self.bounds.width
    
    @width.setter
    def width(self, nw):
        self.bounds.width = nw

    @property
    def height(self):
        return self.bounds.height

    @height.setter
    def height(self, nh):
        self.bounds.height = nh

    def get_collision_bounds(self):
        return self.bounds

    def update_collisions(self, game):
        pass

    def collide(self, other_obj):
        return self.bounds.colliderect(other_obj.get_collision_bounds())
    
class TrafficLight(GameObject):
    def __init__(self, game):
        super().__init__(0, ROAD_TOP, 10, ROAD_BOTTOM - ROAD_TOP)
        self.reset(game)

    def reset(self, game):
        self.state = random.choice(["red", "yellow", "green"])
        self.timer = random.randint(100, 200)
        self.x = random.randint(2, 5) * WIDTH + game.car.x
        self.flashed = False

    def update(self, game):
        self.timer -= 1
        if self.timer <= 0:
            if self.state == "red":
                self.state = "green"
                self.timer = 200
            elif self.state == "yellow":
                self.state = "red"
                self.timer = 200
            elif self.state == "green":
                self.state = "yellow"
                self.timer = 100
        
        # Add collision check and flash effect for red light violations
        if not self.flashed and self.collide(game.car) and self.state == "red":
            game.flash_frame = game.game_frame
            self.flashed = True
            incident_data = {'traffic_light_id': self.id, 'traffic_light_x': self.x}
            game.car.handle_incident(game, IncidentType.TrafficLightViolation, incident_data)

        if game.get_screen_x(self.x) < -50:
            self.reset(game)

    def draw(self, game):
        # Traffic light should not handle weather drawing
        screen_x = game.get_screen_x(self.x)
        road_width = HEIGHT // 2
        stop_line_y = HEIGHT // 2 - road_width // 2
        stop_line_rect = self.bounds.copy()
        stop_line_rect.x = screen_x
        stop_line_rect.y = stop_line_y
        stop_line_rect.height = road_width
        pygame.draw.rect(screen, WHITE, stop_line_rect, 10)
        pygame.draw.rect(screen, BLACK, (screen_x - 5, self.y - 60, 20, 60))
        
        if game.draw_collisions:
            screen_bounds = self.bounds.copy()
            screen_bounds.x = game.get_screen_x(screen_bounds.x)
            pygame.draw.rect(screen, YELLOW, screen_bounds, width=3)

        light_radius = 8
        box_start = self.y - 60
        positions = {
            "red": box_start + 10,
            "yellow": box_start + 30,
            "green": box_start + 50
        }
        
        color = RED if self.state == "red" else DARKER_GRAY
        pygame.draw.circle(screen, color, (screen_x + 5, positions["red"]), light_radius)
        
        color = YELLOW if self.state == "yellow" else DARKER_GRAY
        pygame.draw.circle(screen, color, (screen_x + 5, positions["yellow"]), light_radius)
        
        color = GREEN if self.state == "green" else DARKER_GRAY
        pygame.draw.circle(screen, color, (screen_x + 5, positions["green"]), light_radius)

class LaneMarker(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 8)

class Tree(GameObject):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        self.size = size

class Building(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        #self.windows = []
        #self.generate_windows()

    def generate_windows(self):
        window_rows = self.height // 30
        window_cols = self.width // 30
        for row in range(window_rows):
            for col in range(window_cols):
                if random.random() > 0.3:  # 70% chance of window
                    self.windows.append((
                        self.x + col * 30 + 5,
                        self.y + row * 30 + 5,
                        20, 20
                    ))

class Vehicle(GameObject):
    class ThrottleCommand:
        Accel = 'accel'
        Coast = 'coast'
        Brake = 'brake'

    vehicle_profiles = {
        'sedan': {
            'width': 45,
            'height': 35,
            'acceleration': 0.2,
            'max_speed': 120,
            'deceleration': 0.075,
            'brake_decel': 0.5,
            'vertical_speed': 4,
            'color': DARK_GREEN
        },
        'sports_car': {
            'width': 55,
            'height': 30,
            'acceleration': 0.3,
            'max_speed': 150,
            'deceleration': 0.075,
            'brake_decel': 0.75,
            'vertical_speed': 6,
            'color': DARK_RED
        },
        'delivery_truck': {
            'width': 100,
            'height': 40,
            'acceleration': 0.1,
            'max_speed': 90,
            'deceleration': 0.06,
            'brake_decel': 0.25,
            'vertical_speed': 3,
            'color': DARK_BLUE
        }
    }

    light_detection_range = WIDTH * 0.5
    obstacle_detection_range = WIDTH * 0.75
    sensor_profiles = {
        'perfect':
        {
            'light_detection': 1.0,
            'obstacle_detection': 1.0,
            'speed_accuracy': 1.0,
        },
        'speedy':
        {
            'light_detection': 0.9,
            'obstacle_detection': 0.85,
            'speed_accuracy': 0.6,
        },
        'smashy':
        {
            'light_detection': 0.9,
            'obstacle_detection': 0.5,
            'speed_accuracy': 0.85,
        },
        'clumsy':
        {
            'light_detection': 0.6,
            'obstacle_detection': 0.8,
            'speed_accuracy': 0.9,
        }
    }

    def __init__(self, game):
        super().__init__()
        self.reset(game)

    def reset(self, game):
        self.init_id()
        road_height = HEIGHT // 2
        spawn_side = random.choice([-1, 0, 1])
        spawn_x = random.randint(1, 2) * WIDTH + game.car.x
        spawn_y = HEIGHT // 2 + spawn_side * road_height // 3
        self.type = random.choice(['sedan', 'sports_car', 'delivery_truck'])
        self.set_profile(self.type)
        self.bounds = pygame.Rect(spawn_x, spawn_y, Vehicle.vehicle_profiles[self.type]['width'], Vehicle.vehicle_profiles[self.type]['height']) 
        self.desired_speed = min((random.randrange(75, 120)/100) * game.env.speed_limit, self.max_speed)
        self.speed = self.desired_speed
        self.crashed = False
        self.braking = False

    def set_profile(self, profile_name):
        profile = Vehicle.vehicle_profiles[profile_name]
        self.profile_name = profile_name
        self.width = profile['width']
        self.height = profile['height']
        self.color = profile['color']
        self.acceleration = profile['acceleration']
        self.max_speed = profile['max_speed']
        self.deceleration = profile['deceleration']
        self.brake_decel = profile['brake_decel']
        self.vertical_speed = profile['vertical_speed']

    def calculate_accel(self, desired_speed, dt):
        dv = desired_speed - self.speed
        a = dv / min(20, max(1, dt))
        return min(self.acceleration - self.deceleration, max(-(self.deceleration + self.brake_decel), a))

    @staticmethod
    def calc_time_to_intercept(target_position, obstacle_predicted_position, self_speed, obstacle_speed):
        return max(0, ((obstacle_predicted_position - target_position) / (self_speed - obstacle_speed)) if self_speed - obstacle_speed > 0 else 100000)

    def get_sensor_rect(self):
        extra_sensor_height = 20
        return pygame.Rect(self.x, self.y-extra_sensor_height//2, Vehicle.obstacle_detection_range, self.height+extra_sensor_height)

    def update_sensors(self, game):
        vehicle_sensor = self.get_sensor_rect()
        target_position = self.x + self.width * 2
        time_to_intercept = 100000
        target_speed = self.speed
        target_object = None
        for vehicle in game.get_current_env().vehicles:
            if vehicle != self:
                if vehicle_sensor.colliderect(vehicle.get_collision_bounds()):
                    tti = Vehicle.calc_time_to_intercept(target_position, vehicle.x, self.speed, vehicle.speed)
                    if tti < time_to_intercept:
                        time_to_intercept = tti
                        target_speed = vehicle.speed
                        target_object = vehicle

        for light in game.get_current_env().traffic_lights:
            if vehicle_sensor.colliderect(light.get_collision_bounds()):
                if light.x > self.x and light.state == "red":
                    tti = Vehicle.calc_time_to_intercept(target_position, light.x, self.speed, 0)
                    if tti < time_to_intercept:
                        time_to_intercept = tti
                        target_speed = 0
                        target_object = light

        for pedestrian in game.get_current_env().pedestrians:
            if vehicle_sensor.colliderect(pedestrian.get_collision_bounds()):
                tti = Vehicle.calc_time_to_intercept(target_position, pedestrian.x, self.speed, 0)
                if tti < time_to_intercept:
                    time_to_intercept = tti
                    target_speed = 0
                    target_object = pedestrian

        target_accel = self.calculate_accel(target_speed, time_to_intercept)
        return target_speed, target_accel, time_to_intercept, target_object

    def handle_incident(self, game, incident_type:IncidentType, incident_data:dict):
        if incident_type == IncidentType.Collision:
            self.crashed = True
            self.speed = 0
        incident_data[self.id] = {'x': self.x, 'y': self.y, 'speed': self.speed, 'vehicle_type': self.profile_name}

    def update_collisions(self, game):
        for vehicle in game.get_current_env().vehicles:
            if vehicle != self:
                if (not self.crashed or not vehicle.crashed) and self.collide(vehicle):
                    incident_data = {}
                    self.handle_incident(game, IncidentType.Collision, incident_data)
                    vehicle.handle_incident(game, IncidentType.Collision, incident_data)

        for pedestrian in game.get_current_env().pedestrians:
            if not pedestrian.crashed and self.collide(pedestrian):
                incident_data = {}
                self.handle_incident(game, IncidentType.CollisionInvolvingPedestrian, incident_data)
                pedestrian.handle_incident(game, IncidentType.CollisionInvolvingPedestrian, incident_data)

    def update(self, game):
        cur_speed = self.speed
        if not self.crashed:
            target_speed, target_accel, time_to_intercept, target_object = self.update_sensors(game)
            self.speed += target_accel
            self.x += self.speed
        
        self.braking = (self.speed - cur_speed) < 0

        screen_x = game.get_screen_x(self.x)
        if screen_x < -WIDTH * 3 or screen_x > WIDTH * 3:
            self.reset(game)

    def draw(self, game):
        bounds = self.bounds.copy()
        bounds.x = game.get_screen_x(bounds.x)

        # Draw the wheels
        pygame.draw.circle(screen, BLACK, (bounds.x + int(bounds.width * 0.2), bounds.y), 5)
        pygame.draw.circle(screen, BLACK, (bounds.x + int(bounds.width * 0.8), bounds.y), 5)
        pygame.draw.circle(screen, BLACK, (bounds.x + int(bounds.width * 0.2), bounds.y + bounds.height), 5)
        pygame.draw.circle(screen, BLACK, (bounds.x + int(bounds.width * 0.8), bounds.y + bounds.height), 5) 
        
        # Draw the body
        pygame.draw.rect(screen, self.color, bounds)

        # Draw the brake lights
        brake_color = RED if self.braking else DARKER_GRAY
        tail_light_width = 3
        tail_light_height = 6
        pygame.draw.rect(screen, brake_color, (bounds.x - tail_light_width, bounds.y, tail_light_width, tail_light_height))
        pygame.draw.rect(screen, brake_color, (bounds.x - tail_light_width, bounds.y + bounds.height - tail_light_height, tail_light_width, tail_light_height))

        # Battle damage
        if self.crashed:
            pygame.draw.line(screen, BLACK, bounds.topleft, bounds.bottomright, 3)
            pygame.draw.line(screen, BLACK, bounds.topright, bounds.bottomleft, 3)

        # Draw collisions
        if game.draw_collisions:
            screen_bounds = self.bounds.copy()
            screen_bounds.x = game.get_screen_x(screen_bounds.x)
            pygame.draw.rect(screen, YELLOW, screen_bounds, width=3)
            screen_sensor_bounds = self.get_sensor_rect().copy()
            screen_sensor_bounds.x = game.get_screen_x(screen_sensor_bounds.x)
            pygame.draw.rect(screen, YELLOW, screen_sensor_bounds, width=3)

class PlayerVehicle(Vehicle):
    def __init__(self, game):
        super().__init__(game)
        self.incident_report = IncidentReport()

    def reset(self, game):
        self.set_sensor_profile('perfect')
        self.set_profile('sedan')
        self.bounds = pygame.Rect(0, HEIGHT // 2, Vehicle.vehicle_profiles['sedan']['width'], Vehicle.vehicle_profiles['sedan']['height']) 
        self.speed = 0
        self.crashed = False
        self.throttle = Vehicle.ThrottleCommand.Coast
        self.braking = False

    def get_sensor_speed(self):
        speed_range = self.speed * (1 - self.speed_accuracy) 
        return self.speed - speed_range + random.random() * 2 * speed_range

    def set_sensor_profile(self, profile_name):
        profile = Vehicle.sensor_profiles[profile_name]
        self.sensor_profile_name = profile_name
        self.light_detection = profile['light_detection']
        self.obstacle_detection = profile['obstacle_detection']
        self.speed_accuracy = profile['speed_accuracy']

    def handle_incident(self, game, incident_type: IncidentType, incident_data: dict):
        super().handle_incident(game, incident_type, incident_data)
        self.incident_report.add_incident(Incident(game.game_frame, incident_type, incident_data))

    def update(self, game):
        target_speed = self.speed
        self.braking = False
        if game.keys[pygame.K_LEFT]:
            target_speed = max(0, target_speed - self.brake_decel)
            self.throttle = Vehicle.ThrottleCommand.Brake
        elif game.keys[pygame.K_RIGHT]:
            target_speed = min(self.max_speed, target_speed + self.acceleration)
            self.throttle = Vehicle.ThrottleCommand.Accel
        else:
            self.throttle = Vehicle.ThrottleCommand.Coast

        target_y = self.y
        if game.keys[pygame.K_UP]:
            target_y = max(HEIGHT//2 - game.get_current_env().road_height//3, self.y - self.vertical_speed)
        if game.keys[pygame.K_DOWN]:
            target_y = min(HEIGHT//2 + game.get_current_env().road_height//3, self.y + self.vertical_speed)

        if self.y < target_y:
            self.y = min(self.y + self.vertical_speed, target_y)
        elif self.y > target_y:
            self.y = max(self.y - self.vertical_speed, target_y)
            
        target_speed, target_accel, time_to_intercept, target_object = self.update_sensors(game)
        if isinstance(target_object, Vehicle):
            ComplianceModule.add_fact('obstacle', target_object.id, target_object.speed, target_object.x, target_object.y)
        elif isinstance(target_object, TrafficLight):
            ComplianceModule.add_fact('traffic_signal', target_object.id, target_object.x, target_object.state)
        elif isinstance(target_object, Pedestrian):
            ComplianceModule.add_fact('obstacle', target_object.id, 0, target_object.x, target_object.y)

        if game.enforce_compliance:
            for a in game.compliance_actions:
                if a.startswith('slow'):
                    self.throttle = Vehicle.ThrottleCommand.Coast
                elif a.startswith('brake'):
                    self.throttle = Vehicle.ThrottleCommand.Brake

        match self.throttle:
            case Vehicle.ThrottleCommand.Coast:
                self.speed = max(0, self.speed - self.deceleration)                
            case Vehicle.ThrottleCommand.Accel:
                self.speed = min(self.speed + self.acceleration, self.max_speed)
            case Vehicle.ThrottleCommand.Brake:
                self.speed = max(self.speed - self.brake_decel, 0)
                self.braking = True

        self.x += self.speed

class Pedestrian(GameObject):

    pedestrian_profiles = {
        'normal': {'speed': 1, 'width': 10, 'height': 30},
        'slow': {'speed': 0.5, 'width': 8, 'height': 25},
        'fast': {'speed': 2, 'width': 12, 'height': 35},
        'deer': {'speed': 4, 'width': 20, 'height': 45}
    }

    def __init__(self, game):
        super().__init__()
        self.reset(game)
    
    def reset(self, game):
        self.init_id()
        self.x = random.randint(2, 5) * WIDTH + game.car.x
        self.y = ROAD_TOP
        self.width = 20
        self.height = ROAD_HEIGHT
        self.person_pct = random.random()
        self.direction = random.choice([-1, 1])
        self.clothing_color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE])
        self.head_color = random.choice([LIGHT_TAN, LIGHT_BROWN, BROWN, TAN])
        self.crashed = False

        if game.current_environment == HIGHWAY:
            self.set_profile(game, 'deer')
        else:
            self.set_profile(game, random.choice(list(Pedestrian.pedestrian_profiles.keys())))

    def set_profile(self, game, profile_name):
        profile = Pedestrian.pedestrian_profiles[profile_name]
        if profile_name == 'deer' and game.current_environment != HIGHWAY:
            profile_name = 'normal'
        self.profile_name = profile_name
        profile = Pedestrian.pedestrian_profiles[profile_name]
        self.walking_speed = profile['speed']
        self.person_width = profile['width']
        self.person_height = profile['height']

    def handle_incident(self, game, incident_type:IncidentType, incident_data:dict):
        if incident_type == IncidentType.CollisionInvolvingPedestrian:
            self.crashed = True
            incident_data[self.id] = {'x': self.x, 'y': self.y}

    def update(self, game):
        if not self.crashed:
            self.person_pct += self.walking_speed * 0.001 * self.direction
            self.person_pct = max(-0.2, min(1.2, self.person_pct))

        screen_x = game.get_screen_x(self.x)
        if screen_x < -WIDTH:
            self.reset(game)

    def get_collision_bounds(self):
        person_x = self.bounds.centerx
        person_y = ROAD_TOP + self.person_pct*ROAD_HEIGHT
        bounds = pygame.Rect(person_x-self.person_width//2, person_y-self.person_height//2, self.person_width, self.person_height)
        return bounds

    def draw(self, game):
        screen_bounds = self.bounds.copy()
        screen_bounds.x = game.get_screen_x(screen_bounds.x)

        if game.current_environment == CITY:
            #draw the crosswalk
            pygame.draw.rect(screen, WHITE, (screen_bounds.x, ROAD_TOP, screen_bounds.width, ROAD_HEIGHT), 2)
            num_lines = 10
            for i in range(1, num_lines):
                pygame.draw.line(screen, WHITE, (screen_bounds.x, ROAD_TOP + i*(ROAD_HEIGHT//num_lines)), (screen_bounds.x + screen_bounds.width, ROAD_TOP + i*(ROAD_HEIGHT//num_lines)), 2)
    
        # draw the person
        person_y = ROAD_TOP + self.person_pct*ROAD_HEIGHT
        person_width = self.person_width
        person_height = self.person_height
    
        if self.profile_name != 'deer':
            pygame.draw.circle(screen, self.head_color, (screen_bounds.centerx, person_y - person_height//5), person_height//4)
            pygame.draw.rect(screen, self.clothing_color, (screen_bounds.centerx-person_width//2, person_y, person_width, person_height//2))
            pygame.draw.rect(screen, BLACK, (screen_bounds.centerx-person_width//2, person_y+person_height//2, person_width//5, person_height//2))
            pygame.draw.rect(screen, BLACK, (screen_bounds.centerx+person_width//2, person_y+person_height//2, person_width//5, person_height//2))
        else:
            pygame.draw.rect(screen, BROWN, (screen_bounds.centerx-person_width//2, person_y, person_width, person_height//2))
            pygame.draw.rect(screen, TAN, (screen_bounds.centerx-person_width//2, person_y+person_height//2, person_width//5, person_height//2))
            pygame.draw.rect(screen, LIGHT_BROWN, (screen_bounds.centerx+person_width//2, person_y+person_height//2, person_width//5, person_height//2))
            pygame.draw.circle(screen, BROWN, (screen_bounds.centerx, person_y - person_height//5), person_height//4)
            pygame.draw.circle(screen, BLACK, (screen_bounds.centerx, person_y - person_height//5), person_height//8)
            pygame.draw.rect(screen, LIGHT_BROWN, (screen_bounds.centerx-person_width, person_y-person_height//2-4, 2*person_width, 4))

        collision_bounds = self.get_collision_bounds()

        collision_bounds.x = game.get_screen_x(collision_bounds.x)
        if self.crashed:
            pygame.draw.line(screen, BLACK, collision_bounds.topleft, collision_bounds.bottomright, 3)
            pygame.draw.line(screen, BLACK, collision_bounds.topright, collision_bounds.bottomleft, 3)

        if game.draw_collisions:
            pygame.draw.rect(screen, YELLOW, collision_bounds, width=3)

class Environment:

    environments = {
        'highway': 
        {
            'speed_limit': 60, 
            'road_height': HEIGHT // 2,
            'num_lane_markers': 20,
            'marker_spacing': 80,
            'num_trees': 30,
            'num_buildings': 2,
            'num_vehicles': 2,
            'num_pedestrians': 3,
            'num_traffic_lights': 0
        },
        'city': 
        {
            'speed_limit': 30, 
            'road_height': HEIGHT // 2,
            'marker_spacing': 60,
            'num_lane_markers': 25,
            'num_buildings': 8,
            'num_trees': 2,
            'num_vehicles': 4,
            'num_pedestrians': 1,
            'num_traffic_lights': 1
        }
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.lane_markers = []
        self.trees = []
        self.buildings = []
        self.vehicles = []
        self.traffic_lights = []
        self.pedestrians = []
        self.road_height = HEIGHT // 2

    def set_environment(self, game, name):
        env = Environment.environments[name]
        self.reset()
        self.name = name
        self.speed_limit = env['speed_limit']
        self.road_height = env['road_height']
        self.marker_spacing = env['marker_spacing']
        self.num_lane_markers = env['num_lane_markers']
        self.num_trees = env['num_trees']
        self.num_buildings = env['num_buildings']
        self.num_vehicles = env['num_vehicles']
        self.num_pedestrians = env['num_pedestrians']
        self.num_traffic_lights = env['num_traffic_lights']
        
        # Create lane markers
        for i in range(self.num_lane_markers):
            x_pos = i * self.marker_spacing
            self.lane_markers.append(LaneMarker(x_pos, HEIGHT // 2 - self.road_height // 6))
            self.lane_markers.append(LaneMarker(x_pos, HEIGHT // 2 + self.road_height // 6))

        # Create trees
        for i in range(self.num_trees):
            side = random.choice([-1, 1])
            x = random.randint(0, WIDTH)
            y = HEIGHT // 2 + (self.road_height // 2 + random.randint(20, 100)) * side
            size = random.randint(30, 50)
            self.trees.append(Tree(x, y, size))

        # Create buildings
        for i in range(self.num_buildings):
            # Left side buildings
            width = random.randint(60, 100)
            height = random.randint(100, 200)
            x = i * (width + 50)  # Added spacing between buildings
            self.buildings.append(Building(x, HEIGHT // 2 - height - self.road_height // 2, width, height))
            
            # Right side buildings
            width = random.randint(60, 100)
            height = random.randint(100, 200)
            x = i * (width + 50)  # Added spacing between buildings
            self.buildings.append(Building(x, HEIGHT // 2 + self.road_height // 2, width, height))

        # Create traffic lights
        for i in range(self.num_traffic_lights):
            self.traffic_lights.append(TrafficLight(game))

        # Create vehicles
        for i in range(self.num_vehicles):
            self.vehicles.append(Vehicle(game))
            
        # Create pedestrians
        for i in range(self.num_pedestrians):
            self.pedestrians.append(Pedestrian(game))

    def update(self, game):

        # Update traffic lights
        for light in self.traffic_lights:
            light.update(game)
            if(game.car.x < light.x):
                if abs(game.car.x - light.x) < game.car.light_detection * Vehicle.light_detection_range:
                    ComplianceModule.add_fact('traffic_signal', light.id, light.x, light.state)

        # Update lane markers
        for marker in self.lane_markers:
            marker.x -= game.car.speed
            if marker.x < -40:
                marker.x = WIDTH + 40

        # Update vehicles
        for vehicle in self.vehicles:
            vehicle.update(game)                

        # Update pedestrians
        for pedestrian in self.pedestrians:
            pedestrian.update(game) 

        # Update trees
        for tree in self.trees:
            tree.x -= game.car.speed / 4
            if tree.x < -50:
                tree.x = random.randint(1, 3) * WIDTH
                tree.y = HEIGHT // 2 + (self.road_height // 2 + random.randint(20, 100)) * random.choice([-1, 1])

        # Update buildings
        for building in self.buildings:
            building.x -= game.car.speed / 4
            if building.x + building.width < 0:
                building.x = WIDTH
                building.height = random.randint(100, 200)
                #building.windows = []
                #building.generate_windows()

        # Update collisions
        for v in self.vehicles:
            v.update_collisions(game)

class Game:
    def __init__(self):
        self.env = Environment()
        self.car = PlayerVehicle(self)
        self.setup_environment(CITY)
        self.draw_collisions = False
        self.collisions = set()
        self.game_frame = 0
        self.compliance_actions = []
        self.enforce_compliance = True
        self.flash_frame = -1  # Track when the flash started
        self.flash_duration = 10  # How many frames the flash lasts
        self.keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False}
        self.weather = Weather.Clear  # Initialize weather as clear

    def toggle_weather(self):
        if self.weather == Weather.Clear:
            self.weather = Weather.Rain
        elif self.weather == Weather.Rain:
            self.weather = Weather.Snow
        else:
            self.weather = Weather.Clear

    def get_screen_x(self, query_x):
        return query_x - (self.car.x - CAR_SCREEN_POSITION)

    def setup_environment(self, environment):
        self.current_environment = environment
        self.env.set_environment(self, environment)
        self.env.vehicles.append(self.car)
        self.car.reset(self)

    def get_current_env(self):
        return self.env

    def draw_tree(self, tree):
        pygame.draw.rect(screen, BROWN, 
                        (tree.x - tree.size // 8, tree.y - tree.size // 2, 
                         tree.size // 4, tree.size))
        pygame.draw.circle(screen, GREEN, 
                          (tree.x, tree.y - tree.size // 2), 
                          tree.size // 2)

    def draw_building(self, building):
        pygame.draw.rect(screen, BUILDING_COLOR, 
                        (building.x, building.y, building.width, building.height))
        #for window in building.windows:
        #    pygame.draw.rect(screen, WINDOW_COLOR, window)

    def draw_weather(self):
        if self.weather == Weather.Rain:
            for _ in range(100):  # Increased density for better visibility
                x_start = random.randint(0, WIDTH)
                y_start = random.randint(0, HEIGHT)
                x_end = x_start + random.randint(-5, 5)
                y_end = y_start + 10
                pygame.draw.line(screen, BLUE, (x_start, y_start), (x_end, y_end), 2)
        elif self.weather == Weather.Snow:
            for _ in range(100):  # Increased density for better visibility
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                pygame.draw.circle(screen, WHITE, (x, y), 2)

    def update(self):
        env = self.get_current_env()
        env.update(self)
        
        for f in self.collisions.copy():
            if self.game_frame - f > 60:
                self.collisions.remove(f)

        # Update compliance system with speed, speed limit, and weather
        ComplianceModule.add_fact('ego_speed', self.car.get_sensor_speed())
        ComplianceModule.add_fact('ego_position', self.car.x+self.car.width, self.car.y)
        ComplianceModule.add_fact('speed_limit', env.speed_limit)
        ComplianceModule.add_fact('collision', len(self.collisions) > 0)
        
        # Add the current weather to the compliance module
        ComplianceModule.add_fact('weather', self.weather.name)

        # Get the compliance action based on the updated environment and obstacle information
        self.compliance_actions = ComplianceModule.update()
        
        # Update frame counter
        self.game_frame += 1

    def draw(self):
        # Fill background once
        screen.fill(DARKER_GRAY)
        env = self.get_current_env()

        # Draw weather effects
        self.draw_weather()

        if self.current_environment == HIGHWAY:
            for tree in env.trees:
                if tree.y < HEIGHT // 2:
                    self.draw_tree(tree)

        if self.current_environment == CITY:
            for building in env.buildings:
                self.draw_building(building)

        # Draw road
        pygame.draw.rect(screen, GRAY, (0, HEIGHT // 2 - env.road_height // 2, WIDTH, env.road_height))
        pygame.draw.line(screen, WHITE, (0, HEIGHT // 2 - env.road_height // 2), (WIDTH, HEIGHT // 2 - env.road_height // 2), 3)
        pygame.draw.line(screen, WHITE, (0, HEIGHT // 2 + env.road_height // 2), (WIDTH, HEIGHT // 2 + env.road_height // 2), 3)

        for marker in env.lane_markers:
            pygame.draw.rect(screen, WHITE, (marker.x, marker.y - marker.height // 2, marker.width, marker.height))

        for light in env.traffic_lights:
            light.draw(self)

        for vehicle in env.vehicles:
            vehicle.draw(self)

        for pedestrian in env.pedestrians:
            pedestrian.draw(self)

        for tree in env.trees:
            if tree.y >= HEIGHT // 2:
                self.draw_tree(tree)

        font = pygame.font.Font(None, 36)
        text_height = font.get_height()

        speed_text = f"Speed: {int(self.car.speed)} mph"
        env_text = f'Environment: {env.name} ({env.speed_limit} mph)'

        speed_surface = font.render(speed_text, True, WHITE)
        env_surface = font.render(env_text, True, WHITE)
        car_profile_surface = font.render(f'Vehicle: {self.car.profile_name}', True, WHITE)
        sensor_profile_surface = font.render(f'Sensor: {self.car.sensor_profile_name}', True, WHITE)
        col_surface = font.render('* Collision Detected! *', True, WHITE) if len(self.collisions) > 0 else None
        brake_surface = font.render('* Braking! *', True, WHITE) if (self.car.throttle == Vehicle.ThrottleCommand.Brake) else None

        if brake_surface:
            screen.blit(brake_surface, (20, 30))
        if col_surface:
            screen.blit(col_surface, (20, 50))

        bottom_row_y = HEIGHT - text_height
        info_box_width = 600
        info_box_height = 20 + 3 * text_height
        info_box_surface = pygame.Surface((info_box_width, info_box_height), pygame.SRCALPHA)
        info_box_surface.fill(INFO_BOX_COLOR)
        screen.blit(info_box_surface, (10, HEIGHT - info_box_height))

        screen.blit(speed_surface, (20, bottom_row_y))
        screen.blit(env_surface, (220, bottom_row_y))
        screen.blit(car_profile_surface, (20, bottom_row_y - text_height))
        screen.blit(sensor_profile_surface, (20, bottom_row_y - 2 * text_height))

        cp_width = 700
        cp_box = pygame.Rect(WIDTH - (cp_width + 10), 10, cp_width, text_height)
        cp_surface = pygame.Surface((cp_box.width, cp_box.height), pygame.SRCALPHA)
        cp_surface.fill(INFO_BOX_COLOR)
        cp_active_text = 'active' if self.enforce_compliance else 'inactive'
        cp_text = font.render(f'Compliance <{cp_active_text}>: {self.compliance_actions}', True, WHITE)
        screen.blit(cp_surface, cp_box)
        screen.blit(cp_text, cp_box)

        # Draw the flash effect overlay
        if 0 <= (self.game_frame - self.flash_frame) < self.flash_duration:
            flash_alpha = 255 * (1 - (self.game_frame - self.flash_frame) / self.flash_duration)
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, int(flash_alpha)))
            screen.blit(flash_surface, (0, 0))

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True
    current_environment_index = 1
    current_profile_index = 0
    current_sensor_index = 0
    vehicle_profiles = list(Vehicle.vehicle_profiles.keys())
    sensor_profiles = list(Vehicle.sensor_profiles.keys())
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    current_environment_index = (current_environment_index + 1) % len(Environment.environments)
                    game.setup_environment(list(Environment.environments.keys())[current_environment_index])
                elif event.key == pygame.K_TAB:
                    game.enforce_compliance = not game.enforce_compliance
                elif event.key == pygame.K_p:
                    current_profile_index = (current_profile_index + 1) % len(vehicle_profiles)
                    game.car.set_profile(vehicle_profiles[current_profile_index])
                elif event.key == pygame.K_s:
                    current_sensor_index = (current_sensor_index + 1) % len(sensor_profiles)
                    game.car.set_sensor_profile(sensor_profiles[current_sensor_index])
                elif event.key == pygame.K_c:
                    game.draw_collisions = not game.draw_collisions
                elif event.key == pygame.K_i:
                    game.car.incident_report.print_report()
                elif event.key == pygame.K_w:
                    game.toggle_weather()

        game.keys = pygame.key.get_pressed()
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()