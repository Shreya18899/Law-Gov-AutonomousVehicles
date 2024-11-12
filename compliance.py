from pyDatalog import pyDatalog
from pyDatalog.pyDatalog import assert_fact, retract_fact, load, ask

# Define terms (predicates) for traffic signals, obstacles, speed limits, and actions
pyDatalog.create_terms('X, traffic_signal, obstacle, speed, speed_limit, action')

# Define Facts (static information)
# Define traffic signals
+traffic_signal('red')
+traffic_signal('green')
+traffic_signal('yellow')

# Define obstacles and distances (e.g., distance to obstacle in meters)
# +obstacle('ahead', 5)   # Obstacle 5 meters ahead
# +obstacle('side', 3)    # Obstacle 3 meters to the side

# Define speed limits based on the environment
+speed_limit('urban', 50)
+speed_limit('highway', 100)


# Rule Definitions
action('stop') <= traffic_signal('red')
action('slow_down') <= traffic_signal('yellow')
action('go') <= traffic_signal('green')
# action('brake') <= (obstacle('ahead', X) & (X <= 10))
action('set_speed', X) <= speed_limit('urban', X)
action('set_speed', X) <= speed_limit('highway', X)


# # Define Rules (logic-based reasoning)
# # Rule: Stop if the traffic signal is red
# action('stop') <= traffic_signal('red')
# # Rule: Slow down if the traffic signal is yellow
# action('slow_down') <= traffic_signal('yellow')
# # Rule: Proceed if the traffic signal is green
# action('go') <= traffic_signal('green')
# # Rule: Brake if an obstacle is within 10 meters ahead
# action('brake') <= (obstacle('ahead', X) & (X <= 10))
# # Rule: Set speed based on the environment type
# action('set_speed', X) <= speed_limit('urban', X)
# action('set_speed', X) <= speed_limit('highway', X)

# Query actions based on the current facts and rules
#print("Actions based on traffic signals and obstacles:")
#print(action(X)) 

def input_speed_limit(limit):
    +speed_limit('locale', limit)

def input_speed(in_speed):
    +speed(in_speed)

def input_obstacles(obstacles):
    pass

def set_traffic_signal(signal_color):
    print("Setting the traffic signal: ", signal_color)

    # Remove any previous traffic signal facts
    retract_fact('traffic_signal', 'red')
    retract_fact('traffic_signal', 'yellow')
    retract_fact('traffic_signal', 'green')
    
    # Set the current traffic signal
    +traffic_signal(signal_color)

def print_current_facts():
    print("Current traffic signals:", list(traffic_signal(X)))
    # print("Current obstacles ahead:", list(obstacle('ahead', X)))
    # print("Current obstacles to side:", list(obstacle('side', X)))


def update_obstacle(distance_ahead, distance_side=None):
    # Clear all facts for obstacles before updating
    # This clears all facts; you can clear selectively by predicate if needed
    # Add new obstacle facts based on current simulation state
    if distance_ahead is not None:
        print("Distance ahead is  : ", distance_ahead)
        +obstacle('ahead', distance_ahead)
    if distance_side is not None:
        print("Distance to side obstacle is:", distance_side)
        +obstacle('side', distance_side)

def output_action():
    print_current_facts()
    # Priority 1: Check for obstacle within range (brake action)
    if list(action('brake')):
        return "brake"
    
    # Priority 2: Check for traffic light signals
    elif list(action('stop')):
        print("Red light")
        return "stop"
    elif list(action('slow_down')):
        print("Slow down")
        return "slow_down"
    elif list(action('go')):
        return "go"
    
    return "No action determined"


# def output_action():
#     # print_current_facts()
#     # Debug prints to see what's being evaluated
#     # print("Checking compliance actions:")
#     # print("Stop action:", list(action('stop')))
#     # print("Slow down action:", list(action('slow_down')))
#     # print("Go action:", list(action('go')))
#     # print("Brake action:", list(action('brake')))
    
#     # Check for traffic light state first
#     print(list(action))
#     if list(action('stop')):
#         return "stop"
#     elif list(action('slow_down')):
#         return "slow_down"
#     elif list(action('go')) and not list(action('brake')):
#         # Only allow "go" if "brake" is not triggered
#         return "go"
#     elif list(action('brake')):
#         return "brake"
    
#     return "No action determined"