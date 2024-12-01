# from pyDatalog import pyDatalog
# import math

# #def distance(A, B):
# #    return A - B

# pyDatalog.create_terms(
#     """
#     math,
#     X, Y, Z, D, 
#     ID,
#     D1, D2, D3, D4,
#     S1, S2, 
#     X1, X2, 
#     Y1, Y2,
#     Z1, Z2,
#     DX, DY,
#     traffic_signal, 
#     obstacle, 
#     collision,
#     ego_speed, 
#     ego_position,
#     speed_limit, 
#     action,
#     moving,
#     close_to,
#     predict_collision,
#     current_compliance_action,
#     distance,
#     weather
#     """)

# # Fact Definitions
# +traffic_signal(-1, -1, 'green')
# +obstacle(-1, -1, 1000000, 0)
# +collision(False)


# # Rule Definitions
# moving() <= ego_speed(X) & (X > 0)
# #close_to(X1, Y1, D1, D2) <= ego_position(X2, Y2) & (DX==math.dist(X1,X2)) & (DX < D1)
# #predict_collision(X1, Y1, S1, D1, D2) <= ego_speed(S2) & close_to(X1+S1, Y1, D1-S2, D2)
# close_to(X1, Y1, D1, D2) <= ego_position(X2, Y2) & ((X1 - X2) < D1)
# predict_collision(X1, Y1, S1, D1, D2) <= ego_position(X2, Y2) & ego_speed(S2) & (((X1 + S1) - (X2 + S2)) < D1)


# action('stop_collision') <= collision(True)
# action('slow_signal') <= traffic_signal(ID, X1, 'yellow') & moving() & close_to(X1, 0, 500, 1000)
# action('slow_limit') <= ego_speed(X) & speed_limit(Y) & (X > Y)
# action('slow_obstacle') <= obstacle(ID, S1, X1, Y1) & moving() & predict_collision(X1, Y1, S1, 500, 50)
# action('brake_signal') <= traffic_signal(ID, X1, 'red') & moving() & close_to(X1, Y1, 200, 1000)
# action('brake_obstacle') <= obstacle(ID, S1, X1, Y1) & moving() & predict_collision(X1, Y1, S1, 200, 50)

# current_compliance_action(X) <= action(X)

# class ComplianceModule():
#     _facts = []

#     @staticmethod
#     def add_fact(fact, *values):
#         ComplianceModule._facts.append((fact, values))
#         pyDatalog.assert_fact(fact, *values)

#     @staticmethod
#     def update():
#         actions = current_compliance_action(X)
#         if not actions:
#             actions = ['None']
#         else:
#             actions = [str(a[0]) for a in actions]

#         for f, v in ComplianceModule._facts:
#             pyDatalog.retract_fact(f, *v)

#         ComplianceModule._facts = []

#         return actions
from pyDatalog import pyDatalog
import math

pyDatalog.create_terms(
    """
    math,
    X, Y, Z, D, 
    ID,
    D1, D2, D3, D4,
    S1, S2, 
    X1, X2, 
    Y1, Y2,
    Z1, Z2,
    DX, DY,
    traffic_signal, 
    obstacle, 
    collision,
    ego_speed, 
    ego_position,
    speed_limit, 
    action,
    moving,
    close_to,
    predict_collision,
    current_compliance_action,
    distance,
    weather
    """)

# Fact Definitions
+traffic_signal(-1, -1, 'green')
+obstacle(-1, -1, 1000000, 0)
+collision(False)

# Rule Definitions
moving() <= ego_speed(X) & (X > 0)

close_to(X1, Y1, D1, D2) <= ego_position(X2, Y2) & ((X1 - X2) < D1)
predict_collision(X1, Y1, S1, D1, D2) <= ego_position(X2, Y2) & ego_speed(S2) & (((X1 + S1) - (X2 + S2)) < D1)

action('stop_collision') <= collision(True)
action('slow_signal') <= traffic_signal(ID, X1, 'yellow') & moving() & close_to(X1, 0, 500, 1000)
action('slow_limit') <= ego_speed(X) & speed_limit(Y) & (X > Y)
action('slow_obstacle') <= obstacle(ID, S1, X1, Y1) & moving() & predict_collision(X1, Y1, S1, 500, 50)
action('brake_signal') <= traffic_signal(ID, X1, 'red') & moving() & close_to(X1, Y1, 200, 1000)
action('brake_obstacle') <= obstacle(ID, S1, X1, Y1) & moving() & predict_collision(X1, Y1, S1, 200, 50)

# New Rule for Weather Conditions
action('slow_weather') <= weather('Rain')
action('slow_weather') <= weather('Snow')

current_compliance_action(X) <= action(X)

class ComplianceModule():
    _facts = []

    @staticmethod
    def add_fact(fact, *values):
        ComplianceModule._facts.append((fact, values))
        pyDatalog.assert_fact(fact, *values)
    @staticmethod
    def update():
        actions = current_compliance_action(X)
        if not actions:
            actions = ['None']
        else:
            actions = [str(a[0]) for a in actions]

        for f, v in ComplianceModule._facts:
            pyDatalog.retract_fact(f, *v)

        ComplianceModule._facts = []

        return actions
