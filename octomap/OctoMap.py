import math
import time
from tkinter import W

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

from Config import URI, LOGGER, TREE_CENTER, TREE_MAX_DEPTH, TREE_RESOLUTION, WHETHER_FLY
from OctoTree import OctoTree
from MapUtil import get_log_config, parse_log_data, get_end_point


class OctoMap:
    def __init__(self):
        self.octotree = OctoTree(TREE_CENTER, TREE_RESOLUTION, TREE_MAX_DEPTH)
        self.counter = 0
        LOGGER.info("OctoTree has been build, the coordinate range is from {} to {}".
        format(-TREE_RESOLUTION * math.pow(2, TREE_MAX_DEPTH), TREE_RESOLUTION * math.pow(2, TREE_MAX_DEPTH)))
        
    def start(self):
        cflib.crtp.init_drivers()
        self.cf = Crazyflie(ro_cache=None, rw_cache='cache')

        # Connect callbacks from the Crazyflie API
        try:
            self.cf.connected.add_callback(self.connected)
        except:
            LOGGER.info("Connect failed.")
        self.cf.disconnected.add_callback(self.disconnected)

        # Connect to the Crazyflie
        self.cf.open_link(URI)
    
    def connected(self, URI):
        LOGGER.info('We are now connected to {}'.format(URI))

        with SyncCrazyflie(URI, cf=self.cf) as scf:
            try:
                lmap = get_log_config()
                self.cf.log.add_config(lmap)
                lmap.data_received_cb.add_callback(self.update_map)
                lmap.start()
            except KeyError as e:
                LOGGER.error('Could not start log configuration,''{} not found in TOC'.format(str(e)))
            except AttributeError:
                LOGGER.error('Could not add Measurement log config, bad configuration.')
            
            if WHETHER_FLY:
                with MotionCommander(scf, 0.2) as mc:
                    height = 20   # Obstacle height (cm)
                    max_counter = height / 10 
                    loop_counter = 0
                    while loop_counter < max_counter:
                        time.sleep(1)
                        for i in range(4):
                            mc.right(0.5, velocity=0.1)
                            mc.turn_left(90)
                        
                        mc.up(0.1)
                        loop_counter += 1

    def disconnected(self, URI):
        LOGGER.info('Disconnected with {}'.format(URI))

    def update_map(self, timestamp, data, logconf):
        measurement, start_point = parse_log_data(data)
        end_points = get_end_point(start_point, measurement)
        for end_point in end_points:
            self.octotree.ray_casting(tuple(start_point), tuple(end_point))

        # export nodes each 100 times ranging
        self.counter += 1
        # TODO: new a thread to export
        if self.counter % 100 == 0:
            self.octotree.export_known_voxel()
    
    #TODO: Random Search Path Planning
    def plan_path():
        pass