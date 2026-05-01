#!/usr/bin/env python
#

import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behaviors import *
from checks import *
from bt_nodes import Selector, Sequence, Action, Check

def setup_behavior_tree(vehicle, graph):

    # Top-down construction of behavior tree
    root = Selector(name='High Level Driving Strategies')
    
    # TOP LEVEL INTERSECTION SELECTOR
    # Check if at the end of a road (reached Intersection)
    intersection_top_level = Sequence(name='Reached Intersection')
    intersection_strategies = Selector(name='Intersection Strategies')
    reached_intersection_check = Check(front_of_queue, vehicle, graph)
    intersection_top_level.child_nodes = [reached_intersection_check, intersection_strategies]

    # TRAFFIC LIGHT STRATEGIES
    # Stopping at Red Light Sequence
    red_light_sequence = Sequence(name='Stop at Red or Yellow Light')
    red_light_check = Check(get_traffic_light_RY, vehicle, graph)
    stop_action = Action(stop_light, vehicle, graph)
    red_light_sequence.child_nodes = [red_light_check, stop_action]

    # Continue at Green Light Sequence
    green_light_sequence = Sequence(name='Continue at Green Light')
    green_light_check = Check(get_traffic_light_green, vehicle, graph)
    continue_action = Action(pass_intersection, vehicle, graph)
    green_light_sequence.child_nodes = [green_light_check, continue_action]

    # Traffic Light Sequence
    traffic_light_selector = Selector(name='Traffic Light Strategy')
    traffic_light_selector.child_nodes = [red_light_sequence, green_light_sequence]

    # STOP SIGN STRATEGIES
    # Stopping at Stop Sign Sequence
    stop_sign_sequence = Sequence(name='Stop Sign Strategy')
    stop_sign_check = Check(has_stop_sign, vehicle, graph)
    handle_stop_selector = Selector(name='Stop or Move at Sign')

    check_stopped_sequence = Sequence(name='Need to Stop at Stop Sign')
    stopped_check = Check(has_not_stopped, vehicle, graph)
    check_stopped_sequence.child_nodes = [stopped_check, stop_action]

    handle_stop_selector.child_nodes = [check_stopped_sequence, continue_action]

    intersection_clear_check = Check(check_other_vehicles, vehicle, graph)
    stop_sign_sequence.child_nodes = [stop_sign_check, handle_stop_selector]

    # EMPTY INTERSECTION STRATEGIES
    # Stopping at Stop Sign Sequence
    empty_sequence = Sequence(name='Empty Intersection Strategy')
    empty_check = Check(check_empty_intersection, vehicle, graph)
    empty_sequence.child_nodes = [empty_check, continue_action]

    intersection_strategies.child_nodes = [traffic_light_selector, stop_sign_sequence, empty_sequence]

    # MOVEMENT STRATEGY
    # Move forward sequence when not at intersection
    move_forward_sequence = Sequence(name='Move Forward')
    not_at_intersection_check = Check(is_at_intersection, vehicle, graph)
    move_action = Action(move_on_road, vehicle, graph)
    move_forward_sequence.child_nodes = [not_at_intersection_check, move_action]

    
    '''
    # CONGESTION AVOIDANCE STRATEGY
    # Recalc path if next road is busy
    recalc_path_sequence = Sequence(name='Recalculate Path if Congested')
    congestion_check = Check(lambda: is_road_busy(vehicle, graph))
    recalc_action = Action(lambda: recalculate_path_if_congested(vehicle, graph))
    slow_down_action = Action(lambda: slow_for_congestion(vehicle))
    recalc_path_sequence.child_nodes = [congestion_check, recalc_action]
    
    # Slow down if congested and no alt path
    congestion_avoidance_selector = Selector(name='Congestion Avoidance Strategy')
    congestion_avoidance_selector.child_nodes = [recalc_path_sequence, slow_down_action]
    
    # INTERSECTION CLEAR CHECK STRATEGY
    # Ensure intersection clear before crossing
    intersection_clear_sequence = Sequence(name='Intersection Clear Check')
    other_vehicle_check = Check(lambda: check_other_vehicles(vehicle, graph))
    intersection_clear_sequence.child_nodes = [other_vehicle_check, intersection_clear_check, continue_action]
    
    # TIMEOUT FOR STUCK VEHICLE
    # Recalculate path if stuck too long
    timeout_sequence = Sequence(name='Timeout Strategy')
    stuck_check = Action(lambda: recalculate_path_if_congested(vehicle, graph))
    timeout_sequence.child_nodes = [stuck_check]
    '''

    # Adding all strategies to the root selector
    root.child_nodes = [
        intersection_top_level,
        move_action
    ]

    logging.info('\n' + root.tree_to_string())
    return root

