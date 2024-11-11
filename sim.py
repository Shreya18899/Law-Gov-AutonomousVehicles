import pygame
import sys
import math
import random
import compliance

pygame.init()

WIDTH = 800
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Driving Simulation - Highway & City")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (80, 80, 80)
DARKER_GRAY = (50, 50, 50)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
BUILDING_COLOR = (160, 160, 160)
WINDOW_COLOR = (255, 255, 153)
YELLOW = (255, 255, 0)
INFO_BOX_COLOR = (0, 0, 0, 150)  # Semi-transparent black

HIGHWAY = "highway"
CITY = "city"
current_environment = HIGHWAY

class GameObject:
    def __init__(self, x, y, w, h):
        self.bounds = pygame.Rect(x, y, w, h)        

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

    def collide(self, other_obj):
        return self.bounds.colliderect(other_obj.bounds)

class TrafficLight(GameObject):
    def __init__(self, x):
        super().__init__(x, HEIGHT//2 - 100, 20, 80)
        self.state = "red"  # red, yellow, green
        self.timer = random.randint(100, 200)
        self.pole_height = 80

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            if self.state == "red":
                self.state = "green"
                self.timer = random.randint(150, 250)
            elif self.state == "yellow":
                self.state = "red"
                self.timer = random.randint(100, 200)
            elif self.state == "green":
                self.state = "yellow"
                self.timer = 50

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, (self.x, self.y, 10, self.pole_height))
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y - self.height, self.width, self.height))
        
        light_radius = 8
        positions = {
            "red": self.y - self.height + 10,
            "yellow": self.y - self.height + 30,
            "green": self.y - self.height + 50
        }
        
        color = RED if self.state == "red" else DARKER_GRAY
        pygame.draw.circle(screen, color, (self.x + 5, positions["red"]), light_radius)
        
        color = YELLOW if self.state == "yellow" else DARKER_GRAY
        pygame.draw.circle(screen, color, (self.x + 5, positions["yellow"]), light_radius)
        
        color = GREEN if self.state == "green" else DARKER_GRAY
        pygame.draw.circle(screen, color, (self.x + 5, positions["green"]), light_radius)

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
        self.windows = []
        self.generate_windows()

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
    car_colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]

    def __init__(self):
        road_height = HEIGHT//2
        super().__init__(random.randint(WIDTH, WIDTH * 2), HEIGHT//2 + random.choice([-1, 0, 1]) * road_height//3, 50, 30)
        self.speed = random.randint(5, 15)
        self.color = random.choice(Vehicle.car_colors)
        self.stopped = False

    def reset(self):
        self.__init__()

class Environment:
    def __init__(self, name, speed_limit):
        self.lane_markers = []
        self.trees = []
        self.buildings = []
        self.vehicles = []
        self.traffic_lights = []
        self.road_height = HEIGHT // 2
        self.name = name
        self.speed_limit = speed_limit

    def setup_highway(self):
        self.lane_markers.clear()
        self.trees.clear()
        self.buildings.clear()
        self.vehicles.clear()
        self.traffic_lights.clear()

        # Create lane markers
        marker_spacing = 80
        for i in range(20):
            x_pos = i * marker_spacing
            self.lane_markers.append(LaneMarker(x_pos, HEIGHT//2 - self.road_height//6))
            self.lane_markers.append(LaneMarker(x_pos, HEIGHT//2 + self.road_height//6))

        # Create trees
        for i in range(30):
            side = random.choice([-1, 1])
            x = random.randint(0, WIDTH)
            y = HEIGHT//2 + (self.road_height//2 + random.randint(20, 100)) * side
            size = random.randint(30, 50)
            self.trees.append(Tree(x, y, size))

        # Create vehicles
        for i in range(3):
            self.vehicles.append(Vehicle())

    def setup_city(self):
        self.lane_markers.clear()
        self.trees.clear()
        self.buildings.clear()
        self.vehicles.clear()
        self.traffic_lights.clear()

        # Create lane markers
        marker_spacing = 60
        for i in range(25):
            x_pos = i * marker_spacing
            self.lane_markers.append(LaneMarker(x_pos, HEIGHT//2 - self.road_height//2))
            self.lane_markers.append(LaneMarker(x_pos, HEIGHT//2 + self.road_height//2))

        # Only one traffic light at a specific position
        traffic_light_position = WIDTH // 3  # Position at one location only
        self.traffic_lights.append(TrafficLight(traffic_light_position))

        # Create buildings
        for i in range(8):
            # Left side buildings
            width = random.randint(60, 100)
            height = random.randint(100, 200)
            x = i * width
            self.buildings.append(Building(x, HEIGHT//2 - height - self.road_height//2, width, height))
            
            # Right side buildings
            width = random.randint(60, 100)
            height = random.randint(100, 200)
            x = i * width
            self.buildings.append(Building(x, HEIGHT//2 + self.road_height//2, width, height))

        # Create vehicles
        for i in range(4):
            self.vehicles.append(Vehicle())

class PlayerVehicle(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 30)
        self.speed = 0
        self.acceleration = 0.2
        self.max_speed = 120
        self.deceleration = 0.075
        self.brake_decel = 0.5
        self.braking = False
        self.vertical_speed = 4

class Game:
    def __init__(self):
        self.highway_env = Environment('highway', 60)
        self.city_env = Environment('urban', 30)
        self.highway_env.setup_highway()
        self.city_env.setup_city()
        self.car = PlayerVehicle(100, HEIGHT//2)
        self.current_environment = HIGHWAY
        self.target_y = self.car.y
        self.stopped_at_light = False
        self.collisions = set()
        self.game_frame = 0
        self.compliance_action = None

    def get_current_env(self):
        return self.highway_env if self.current_environment == HIGHWAY else self.city_env

    def check_traffic_lights(self):
        if self.current_environment == CITY:
            for light in self.get_current_env().traffic_lights:
                if abs(light.x - self.car.x) < 30:  # If car is near traffic light
                    return light.state == "red" or light.state == "yellow"
        return False

    def get_next_traffic_light_state(self):
        if self.current_environment != CITY:
            return None
        env = self.get_current_env()
        next_light = None
        min_distance = float('inf')
        for light in env.traffic_lights:
            distance = light.x - self.car.x
            if distance > 0 and distance < min_distance:
                min_distance = distance
                next_light = light
        if next_light:
            return next_light.state
        return None

    def draw_tree(self, tree):
        pygame.draw.rect(screen, BROWN, 
                        (tree.x - tree.size//8, tree.y - tree.size//2, 
                         tree.size//4, tree.size))
        pygame.draw.circle(screen, GREEN, 
                          (tree.x, tree.y - tree.size//2), 
                          tree.size//2)

    def draw_building(self, building):
        pygame.draw.rect(screen, BUILDING_COLOR, 
                        (building.x, building.y, building.width, building.height))
        for window in building.windows:
            pygame.draw.rect(screen, WINDOW_COLOR, window)

    def draw_vehicle(self, vehicle):
        pygame.draw.rect(screen, vehicle.color, 
                        (vehicle.x, vehicle.y - vehicle.height//2, 
                         vehicle.width, vehicle.height))
        pygame.draw.circle(screen, BLACK, 
                          (int(vehicle.x + 10), int(vehicle.y - vehicle.height//2)), 5)
        pygame.draw.circle(screen, BLACK, 
                          (int(vehicle.x + 40), int(vehicle.y - vehicle.height//2)), 5)
        pygame.draw.circle(screen, BLACK, 
                          (int(vehicle.x + 10), int(vehicle.y + vehicle.height//2)), 5)
        pygame.draw.circle(screen, BLACK, 
                          (int(vehicle.x + 40), int(vehicle.y + vehicle.height//2)), 5)

    def draw_player_car(self):
        bounce = math.sin(pygame.time.get_ticks() * 0.1) * (self.car.speed/self.car.max_speed) * 2
        points = [
            (self.car.x, self.car.y - self.car.height//2),
            (self.car.x + self.car.width, self.car.y),
            (self.car.x, self.car.y + self.car.height//2)
        ]
        pygame.draw.polygon(screen, RED, points)
        pygame.draw.circle(screen, BLACK, 
                          (int(self.car.x + 10), int(self.car.y - self.car.height//2 + bounce)), 5)
        pygame.draw.circle(screen, BLACK, 
                          (int(self.car.x + 10), int(self.car.y + self.car.height//2 + bounce)), 5)

    def update(self):
        env = self.get_current_env()
        
        # Update traffic lights in city mode
        if self.current_environment == CITY:
            for light in env.traffic_lights:
                light.update()
                light.x -= self.car.speed/2
                if light.x < -50:
                    light.x = WIDTH + 50

        # Update lane markers
        for marker in env.lane_markers:
            marker.x -= self.car.speed/2
            if marker.x < -40:
                marker.x = WIDTH + 40

        # Update vehicles
        for vehicle in env.vehicles:
            if not vehicle.stopped:
                vehicle.x -= (self.car.speed - vehicle.speed)
            if vehicle.x < -100:
                vehicle.reset()
            if vehicle.collide(self.car):
                vehicle.speed = 0
                self.car.speed = 0
                self.collisions.add(self.game_frame)
            
        # Update trees (highway only)
        if self.current_environment == HIGHWAY:
            for tree in env.trees:
                tree.x -= self.car.speed/4
                if tree.x < -50:
                    tree.x = WIDTH + 50
                    tree.y = HEIGHT//2 + (env.road_height//2 + random.randint(20, 100)) * random.choice([-1, 1])

        # Update buildings (city only)
        if self.current_environment == CITY:
            for building in env.buildings:
                building.x -= self.car.speed/4
                if building.x + building.width < 0:
                    building.x = WIDTH
                    building.height = random.randint(100, 200)
                    building.windows = []
                    building.generate_windows()

        # Update collisions
        for f in self.collisions.copy():
            if self.game_frame - f > 60:
                self.collisions.remove(f)

        # Update frame counter
        self.game_frame = self.game_frame + 1

    def draw(self):
        screen.fill(DARKER_GRAY)
        env = self.get_current_env()

        if self.current_environment == HIGHWAY:
            for tree in env.trees:
                if tree.y < HEIGHT//2:
                    self.draw_tree(tree)

        if self.current_environment == CITY:
            for building in env.buildings:
                self.draw_building(building)

        # Draw road
        pygame.draw.rect(screen, GRAY, (0, HEIGHT//2 - env.road_height//2, WIDTH, env.road_height))
        pygame.draw.line(screen, WHITE, (0, HEIGHT//2 - env.road_height//2), (WIDTH, HEIGHT//2 - env.road_height//2), 3)
        pygame.draw.line(screen, WHITE, (0, HEIGHT//2 + env.road_height//2), (WIDTH, HEIGHT//2 + env.road_height//2), 3)

        for marker in env.lane_markers:
            pygame.draw.rect(screen, WHITE, (marker.x, marker.y - marker.height//2, marker.width, marker.height))

        if self.current_environment == CITY:
            for light in env.traffic_lights:
                light.draw(screen)

        for vehicle in env.vehicles:
            self.draw_vehicle(vehicle)

        self.draw_player_car()

        if self.current_environment == HIGHWAY:
            for tree in env.trees:
                if tree.y >= HEIGHT//2:
                    self.draw_tree(tree)

        font = pygame.font.Font(None, 36)
        speed_text = f"Speed: {int(self.car.speed)} mph"
        # env_text = f"Environment: {self.current_environment.title()}"
        env_text = f'Environment: {env.name} ({env.speed_limit} mph)'
        next_light_state = self.get_next_traffic_light_state()
        if next_light_state:
            light_text = f"Next Light: {next_light_state.title()}"
        else:
            light_text = ""

        speed_surface = font.render(speed_text, True, WHITE)
        env_surface = font.render(env_text, True, WHITE)
        light_surface = font.render(light_text, True, WHITE) if light_text else None
        col_surface = font.render('* Collision Detected! *', True, WHITE) if len(self.collisions) > 0 else None
        brake_surface = font.render('* Braking! *', True, WHITE) if self.car.braking else None
        
        if light_surface:
            screen.blit(light_surface, (20, 10))
        if brake_surface:
            screen.blit(brake_surface, (20, 30))
        if col_surface:
            screen.blit(col_surface, (20, 50))

        info_box_width = 600
        info_box_height = 50
        info_box_surface = pygame.Surface((info_box_width, info_box_height), pygame.SRCALPHA)
        info_box_surface.fill(INFO_BOX_COLOR)
        screen.blit(info_box_surface, (10, HEIGHT - (font.get_height() + 10)))
        screen.blit(speed_surface, (20, HEIGHT - font.get_height()))
        screen.blit(env_surface, (220, HEIGHT - font.get_height()))

        cp_width = 350
        cp_box = pygame.Rect(WIDTH-(cp_width+10), 10, cp_width, font.get_height())
        cp_surface = pygame.Surface((cp_box.width, cp_box.height), pygame.SRCALPHA)
        cp_surface.fill(INFO_BOX_COLOR)
        cp_text = font.render(f'Compliance: {self.compliance_action}', True, WHITE)
        screen.blit(cp_surface, cp_box)
        screen.blit(cp_text, cp_box)

    def get_next_traffic_light_state(self):
        if self.current_environment != CITY:
            return None
        env = self.get_current_env()
        next_light = None
        min_distance = float('inf')
        for light in env.traffic_lights:
            distance = light.x - self.car.x
            if distance > 0 and distance < min_distance:
                min_distance = distance
                next_light = light
        if next_light:
            return next_light.state
        return None

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.current_environment = CITY if game.current_environment == HIGHWAY else HIGHWAY
                    game.car.y = HEIGHT//2
                    game.target_y = HEIGHT//2
                    game.car.speed = 0
                    if game.current_environment == CITY:
                        game.city_env.setup_city()
                    else:
                        game.highway_env.setup_highway()

        keys = pygame.key.get_pressed()
        
        should_stop = game.check_traffic_lights()
        game.car.braking = False
        
        if not should_stop:
            if keys[pygame.K_RIGHT]:
                game.car.speed = min(game.car.speed + game.car.acceleration, game.car.max_speed)
            if keys[pygame.K_LEFT]:
                game.car.speed = max(game.car.speed - game.car.brake_decel, 0)
                game.car.braking = True
            if not (keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]):
                game.car.speed = max(0, game.car.speed - game.car.deceleration)
        else:
            game.car.speed = max(0, game.car.speed - game.car.deceleration * 2)  # Faster deceleration at red lights

        if keys[pygame.K_UP]:
            game.target_y = max(HEIGHT//2 - game.get_current_env().road_height//3, game.target_y - game.car.vertical_speed)
        if keys[pygame.K_DOWN]:
            game.target_y = min(HEIGHT//2 + game.get_current_env().road_height//3, game.target_y + game.car.vertical_speed)

        if game.car.y < game.target_y:
            game.car.y = min(game.car.y + game.car.vertical_speed, game.target_y)
        elif game.car.y > game.target_y:
            game.car.y = max(game.car.y - game.car.vertical_speed, game.target_y)

        game.update()
        compliance.input_speed(game.car.speed)
        compliance.input_speed_limit(game.get_current_env().speed_limit)

        game.compliance_action = compliance.output_action()

        game.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
