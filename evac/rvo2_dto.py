import warnings
from collections import OrderedDict

warnings.simplefilter('ignore', RuntimeWarning)
import rvo2
from evac.evacuees import Evacuees
from math import ceil
import json
from geom.nav import Navmesh
from shapely.geometry import LineString
from include import Sqlite
from include import Json
import os
from scipy.stats import norm
from math import log
from numpy import array, prod
from scipy.spatial.distance import cdist


class EvacEnv:

    def __init__(self, aamks_vars):
        self.json = Json()
        self.evacuees = Evacuees
        self.max_speed = 0
        self.current_time = 0
        self.positions = []
        self.velocities = []
        self.velocity_vector = []
        self.speed_vec = []
        self.fed = []
        self.fed_nummeric = []
        self.fed_vec = []
        self.finished = []
        self.finished_vec = []
        self.trajectory = []
        self.focus = []
        self.smoke_query = None
        self.rset = 0
        self.per_9 = 0
        self.floor = 0
        self.nav = None
        self.room_list = OrderedDict()
        self.rooms_in_smoke = []

        f = open('{}/{}/config.json'.format(os.environ['AAMKS_PATH'], 'evac'), 'r')
        self.config = json.load(f)

        self.general = aamks_vars

        self.sim = rvo2.PyRVOSimulator(self.config['TIME_STEP'], self.config['NEIGHBOR_DISTANCE'],
                                       self.config['MAX_NEIGHBOR'], self.config['TIME_HORIZON'],
                                       self.config['TIME_HORIZON_OBSTACLE'], self.config['RADIUS'],
                                       self.max_speed)
        self.elog = self.general['logger']
        self.elog.info('ORCA on {} floor initiated'.format(self.floor))
        self.prev_fed = [] 
        self.position_fed_tables_information = []
        self.position_fed_to_insert = []
        self.steps_fed_positions_data = []
        #simulation_id = 1 #przykladowa symulacja
        #self.evac_data = self.json.read("{}/workers/{}/evac.json".format(os.environ['AAMKS_PROJECT'], simulation_id))
        #self.all_evac = self.evac_data["FLOORS_DATA"]["0"]["EVACUEES"]

    def _find_closest_exit(self, evacuee):
        '''
        It finds the closest exit from the set of available exits.
        :param evacuee: object evacuee with the defined parameters.
        :return: coordinates of the closest exit.
        '''
        paths, paths_free_of_smoke = list(), list()

        for door in self.general['doors']:
            if door['floor'] != str(self.floor):
                continue
            x, y = door['center_x'], door['center_y']
            path = self.nav.nav_query(src=self.evacuees.get_position_of_pedestrian(evacuee), dst=(x, y), maxStraightPath=999)
            dist = int(((door['center_x'] - path[-1][0])**2 + (door['center_y'] - path[-1][1])**2)**(1/2))
            if path[0] == 'err' or dist > 100:
                continue
            if self._next_room_in_smoke(evacuee, path) is not True:
                try:
                    paths_free_of_smoke.append([x, y, LineString(path).length])
                except:
                    self.evacuees.set_finish_to_agent(evacuee)
                    paths_free_of_smoke.append([x, y, 0])

                # paths.append([x, y, LineString(path).length])
            else:
                paths.append([x, y, LineString(path).length])

        if len(paths_free_of_smoke) > 0:
            exits = list(zip(*paths_free_of_smoke))[-1]
            return paths_free_of_smoke[exits.index(min(exits))][0], paths_free_of_smoke[exits.index(min(exits))][1]
        else:
            #print(evacuee, self.evacuees.get_position_of_pedestrian(evacuee))
            exits = list(zip(*paths))[0]
            return paths[exits.index(min(exits))][0], paths[exits.index(min(exits))][1]

    def _next_room_in_smoke(self, evacuee, path):
        try:
            s=self.evacuees.get_position_of_pedestrian(evacuee)
            od_at_agent_position = self.smoke_query.get_visibility(self.evacuees.get_position_of_pedestrian(evacuee))
        except:
            od_at_agent_position = 0, 'outside'

        self.evacuees.set_optical_density(evacuee, od_at_agent_position[0])
        self.room = od_at_agent_position[1]

        if self.config['SMOKE_AWARENESS'] and len(path) > 1:
            od_next_room = self.smoke_query.get_visibility(path[1])
            if od_at_agent_position[0] < od_next_room[0]:
                return True
            else:
                return False
        else:
            return False

    def read_cfast_record(self, time):
        self.smoke_query.read_cfast_record(time)

    def place_evacuees(self, evacuees):
        assert isinstance(evacuees, Evacuees), '%evacuees is not type of Evacuees'
        self.evacuees = evacuees
        [self.sim.addAgent(self.evacuees.get_origin_of_pedestrian(i))
         for (i) in range(self.evacuees.get_number_of_pedestrians())]

        [self.sim.setAgentPrefVelocity(i, self.evacuees.get_velocity_of_pedestrian(i))
         for (i) in range(self.evacuees.get_number_of_pedestrians())]

        [self.sim.setAgentMaxSpeed(i, self.evacuees.get_speed_max_of_pedestrian(i))
         for i in range(self.evacuees.get_number_of_pedestrians())]

    @staticmethod
    def discretize_time(time):
        return int(ceil(time / 10.0)) * 10

    def get_data_for_visualization(self):
        data_row=[]
        for n in range(self.sim.getNumAgents()):
            data_row.append([int(self.positions[n][0]), int(self.positions[n][1]), self.velocities[n][0], self.velocities[n][1], self.fed[n], self.finished[n]])
        return data_row

    def update_agents_position(self):
        for i in range(self.evacuees.get_number_of_pedestrians()):
            if (self.evacuees.get_finshed_of_pedestrian(i)) == 0:
                self.sim.setAgentPosition(i, (10000 + i * 200, 10000))
                # Tu agent opuszcza pietro
                continue
            else:
                self.evacuees.set_position_to_pedestrian(i, (int(self.sim.getAgentPosition(i)[0]),
                                                             int(self.sim.getAgentPosition(i)[1])))

        self.positions = [tuple((int(self.sim.getAgentPosition(i)[0]), int(self.sim.getAgentPosition(i)[1]))) for (i)
                          in range(self.sim.getNumAgents())]

    def update_agents_velocity(self):
        for i in range(self.evacuees.get_number_of_pedestrians()):
            self.evacuees.set_num_of_obstacle_neighbours(i, self.sim.getAgentNumObstacleNeighbors(i))
            self.evacuees.set_num_of_orca_lines(i, self.sim.getAgentNumORCALines(i))
            #if i == 210:
                #self.evacuees.dump_evacuee_vars(i)
            self.evacuees.calculate_pedestrian_velocity(i, self.current_time)
        for i in range(self.evacuees.get_number_of_pedestrians()):
            self.sim.setAgentPrefVelocity(i, self.evacuees.get_velocity_of_pedestrian(i))
        self.velocities = [tuple((int(self.sim.getAgentPrefVelocity(i)[0]), int(self.sim.getAgentPrefVelocity(i)[1])))
                           for (i)
                           in range(self.sim.getNumAgents())]

    def set_goal(self):
        for e in range(self.evacuees.get_number_of_pedestrians()):
            if (self.evacuees.get_finshed_of_pedestrian(e)) == 0:
                continue
            else:
                # TODO: mimooh temporary fix
                position = self.evacuees.get_position_of_pedestrian(e)
                goal = self.nav.nav_query(src=position, dst=self._find_closest_exit(e), maxStraightPath=32)

                try:
                    vis = self.sim.queryVisibility(position, goal[2], 15)
                    if vis:
                        self.evacuees.set_goal(ped_no=e, goal=goal[1:])
                    else:
                        self.evacuees.set_goal(ped_no=e, goal=goal)
                except:
                    self.evacuees.set_goal(ped_no=e, goal=goal)

        self.finished = [self.evacuees.get_finshed_of_pedestrian(i) for i in range(self.sim.getNumAgents())]
        for e in range(self.sim.getNumAgents()):
            self.focus.append(self.evacuees.get_goal_of_pedestrian(e))

    def update_speed(self):
        for i in range(self.evacuees.get_number_of_pedestrians()):
            self.elog.debug('Number of neigbouring agents: {}'.format(self.sim.getAgentNumAgentNeighbors(i)))
            self.elog.debug('Neigbouring distance: {}'.format(self.sim.getAgentNeighborDist(i)))
            if (self.evacuees.get_finshed_of_pedestrian(i)) == 0:
                continue
            else:
                self.evacuees.update_speed_of_pedestrian(i)
                self.sim.setAgentMaxSpeed(i, self.evacuees.get_speed_of_pedestrian(i))

    def update_fed(self):
        for i in range(self.evacuees.get_number_of_pedestrians()):
            if (self.evacuees.get_finshed_of_pedestrian(i)) == 0:
                continue
            else:
                try:
                    fed = self.smoke_query.get_fed(self.evacuees.get_position_of_pedestrian(i))
                    if i == 0:
                        self.elog.info('FED calculated: {}'.format(fed))
                except:
                    self.elog.warning('Simulation without FED')
                    fed = 0.0
                self.evacuees.update_fed_of_pedestrian(i, fed * self.config['SMOKE_QUERY_RESOLUTION'])

        fed = [self.evacuees.get_fed_of_pedestrian(i) for i in range(self.sim.getNumAgents())]
        self.fed_nummeric = fed
        c = None
        fed_symbilic = []
        for i in fed:
            if i < 0.01:
                c = 'N'
            elif i < 0.3:
                c = 'L'
            elif i < 1:
                c = 'M'
            else:
                c = 'H'
            fed_symbilic.append(c)
        self.fed = fed_symbilic

    def process_obstacle(self, obstacles):
        for i in range(len(obstacles)):
            obst = list()
            for n in obstacles[i]:
                obst.append(n[0:2])
            self.sim.addObstacle(obst)
        self.sim.processObstacles()
        return self.sim.getNumObstacleVertices(), 2

    def generate_nav_mesh(self):
        self.nav = Navmesh()
        self.nav.build(floor=str(self.floor))

    def prepare_rooms_list(self):
        self.s = Sqlite("{}/aamks.sqlite".format(os.environ['AAMKS_PROJECT']))
        rooms_f = self.s.query('SELECT name from aamks_geom where type_pri="COMPA" and floor = "{}"'.format(self.floor))
        for item in rooms_f:
            self.room_list.update({item['name']: 0.0})


    def update_room_opacity(self):
        smoke_opacity = dict()
        for room in self.room_list.keys():
            opacity =  0.0
            hgt = self.smoke_query.compa_conditions[str(room)]['HGT']
            if hgt == None:
                opacity = self._OD_to_VIS(self.smoke_query.compa_conditions[str(room).split('.')[0]]['ULOD'])
            elif hgt <= self.config['LAYER_HEIGHT']:
                opacity = self._OD_to_VIS(self.smoke_query.compa_conditions[str(room)]['ULOD'])
            else:
                od = self.smoke_query.compa_conditions[str(room)]['LLOD']
                opacity = self._OD_to_VIS(self.smoke_query.compa_conditions[str(room)]['LLOD'])
            if opacity > 0.0 and room not in self.rooms_in_smoke:
                self.rooms_in_smoke.append(room)
            smoke_opacity.update({room: round(opacity, 2)})
            self.elog.debug('ROOM: {}, opacity: {}'.format(room, round(opacity, 2)))
        return smoke_opacity

    def _OD_to_VIS(self, OD):
        self.elog.debug('TIME: {}, optical density: {}'.format(self.current_time, OD))
        if OD <= 1:
            return 0.0
        else:
            vis = self.general['c_const'] / log(OD)
            if vis <= 3:
                return 1.0
            elif vis >= 30:
                return 0.0
            else:
                return (30-vis)/30

    def get_number_of_evacuees(self):
        return self.sim.getNumAgents()

    def update_time(self):
        self.current_time += self.config['TIME_STEP']

    def get_simulation_time(self):
        return self.sim.getGlobalTime()

    def get_rset_time(self) -> None:
        exited = self.finished.count(0)
        if (exited > len(self.finished) * 0.98) and self.per_9 == 0:
            self.rset = self.current_time + 30
        if all(x == 0 for x in self.finished) and self.rset == 0:
            self.rset = self.current_time + 30

    def calculate_individual_risk(self):
        p = list()
        for i in self.fed_nummeric:
            if i == 0:
                i = 1e-7
            p.append(1 - norm.cdf(log(i)))
        return 1 - prod(array(p))

    def save_positions_with_fed(self):
        if len(self.prev_fed) == 0:
            self.prev_fed = [0 for i in range(self.sim.getNumAgents())]
        for i in range(self.sim.getNumAgents()):
            fed = self.fed_nummeric[i]
            x = int(self.positions[i][0])
            y = int(self.positions[i][1])
            fed_growth = round((fed - self.prev_fed[i]),2)
            self.steps_fed_positions_data.append({'x':x, 'y':y, 'fed_growth': fed_growth, 'floor': int(self.floor)})
            self.prev_fed[i] = fed

    def insert_into_database_positions_fed_growth(self):
        for row in self.steps_fed_positions_data:
            self.find_proper_cell_and_append(row['x'],row['y'],row['fed_growth'], row['floor'])
        self.insert_positions_fed_growth_into_database()

    def insert_positions_fed_growth_into_database(self):
        self.position_fed_db = Sqlite(os.environ['AAMKS_PROJECT'] + "/fed_mesh.sqlite")
        unique_cell_numbers = set(map(lambda x:x['cell_number'], self.position_fed_to_insert))
        fed_growth_grouped_by_cell = [{'sum':sum([row['fed_growth'] for row in self.position_fed_to_insert if row['cell_number']==cell_number]),'count':len([row['fed_growth'] for row in self.position_fed_to_insert if row['cell_number']==cell_number]), 'cell_number':cell_number} for cell_number in unique_cell_numbers]
        for fed_growth in fed_growth_grouped_by_cell:
            self.position_fed_db.query("UPDATE mesh_cells SET fed_growth_sum = fed_growth_sum + {}, samples_count = samples_count + {} WHERE number={}".format(fed_growth['sum'], fed_growth['count'], fed_growth['cell_number']))

    def find_proper_cell_and_append(self, x, y, fed_growth, floor):
        for j in range(len(self.position_fed_tables_information)):
            for k in range(len(self.position_fed_tables_information[0])):
                if self.position_fed_tables_information[j][k]['x_min'] < x <= self.position_fed_tables_information[j][k]['x_max'] and self.position_fed_tables_information[j][k]['y_min'] < y <= self.position_fed_tables_information[j][k]['y_max']:
                    value = {'fed_growth':fed_growth, 'cell_number':self.position_fed_tables_information[j][k]['number']}
                    self.position_fed_to_insert.append(value)
                    return;

    def do_simulation(self, step):
        if (step % self.config['SMOKE_QUERY_RESOLUTION']) == 0:
            self.set_goal()
            self.update_speed()
        self.update_agents_velocity()
        self.sim.doStep()

        self.update_agents_position()
        self.update_time()
        #self.elog.info(self.current_time)
        if (step % self.config['SMOKE_QUERY_RESOLUTION']) == 0:
            self.update_fed()
            self.save_positions_with_fed()
        if self.rset == 0:
            self.get_rset_time()
