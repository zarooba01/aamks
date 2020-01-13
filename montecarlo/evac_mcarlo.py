# MODULES {{{
import sys
import re
import os
import shutil
import math
import numpy as np
from collections import OrderedDict
import json
import getopt
from pprint import pprint
import codecs
from subprocess import Popen,call
from shapely.geometry import box, Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
import zipfile

from numpy.random import choice
from numpy.random import uniform
from numpy.random import normal
from numpy.random import lognormal
from numpy.random import binomial
from numpy.random import gamma
from numpy.random import triangular
from numpy.random import seed
from numpy import array as npa
from math import sqrt

from include import Sqlite
from include import Json
from include import Dump as dd
from include import SimIterations
from include import Vis

from scipy.stats.distributions import lognorm
from sklearn.cluster import MeanShift


# }}}

class EvacMcarlo():
    def __init__(self):# {{{
        ''' Generate montecarlo evac.conf. '''

        self.s=Sqlite("{}/aamks.sqlite".format(os.environ['AAMKS_PROJECT']))
        self.json=Json()
        self.conf=self.json.read("{}/conf.json".format(os.environ['AAMKS_PROJECT']))
        self.evacuee_radius=self.json.read('{}/inc.json'.format(os.environ['AAMKS_PATH']))['evacueeRadius']
        self.floors=[z['floor'] for z in self.s.query("SELECT DISTINCT floor FROM aamks_geom ORDER BY floor")]
        self._project_name=os.path.basename(os.environ['AAMKS_PROJECT'])

        si=SimIterations(self.conf['project_id'], self.conf['scenario_id'], self.conf['number_of_simulations'])
        sim_ids=range(*si.get())
        for self._sim_id in sim_ids:
            seed(self._sim_id)
            self._fire_obstacle()
            self._static_evac_conf()
            self._dispatch_evacuees()
            self._make_evac_conf()

            self._cluster_coloring()
        self._evacuees_static_animator()


# }}}
    def _static_evac_conf(self):# {{{
        ''' 
        AAMKS_PROJECT must be propagated to worker environment.
        '''

        self._evac_conf=self.conf
        self._evac_conf['AAMKS_PROJECT']=os.environ['AAMKS_PROJECT']
        self._evac_conf['SIM_ID']=self._sim_id
        self._evac_conf['SERVER']=os.environ['AAMKS_SERVER']
        self._evac_conf['FIRE_ORIGIN']=self.s.query("SELECT name FROM fire_origin WHERE sim_id=?", (self._sim_id,))[0]['name']
# }}}
    def _fire_obstacle(self):# {{{
        '''
        Fire Obstacle prevents humans to walk right through the fire. Currently
        we build the rectangle xx * yy around x,y. Perhaps this size could be
        some function of fire properties.
        '''

        xx=150
        yy=150

        z=self.s.query("SELECT * FROM fire_origin") 
        i=z[0]
        points=[ [i['x']-xx, i['y']-yy, 0], [i['x']+xx, i['y']-yy, 0], [i['x']+xx, i['y']+yy, 0], [i['x']-xx, i['y']+yy, 0], [i['x']-xx, i['y']-yy, 0] ]

        obstacles=self.json.readdb("obstacles")
        obstacles['fire']={ i['floor']: points }
        self.s.query("UPDATE obstacles SET json=?", (json.dumps(obstacles),)) 

# }}}
    def _make_pre_evacuation(self,room,type_sec):# {{{
        ''' 
        An evacuee pre_evacuates from either ordinary room or from the room of
        fire origin; type_sec is for future development.
        '''

        if room != self._evac_conf['FIRE_ORIGIN']:
            pe=self.conf['pre_evac']
        else:
            pe=self.conf['pre_evac_fire_origin']
        return round(lognorm(s=1, loc=pe['mean'], scale=pe['sd']).rvs(), 2)
# }}}
    def _get_density(self,name,type_sec,floor):# {{{
        ''' 
        1. See what Apainter says about the density 
        2. See what conf.json says about evacuees density

        Density comes as m^2, but aamks uses 100 * 100 cm^2 
        '''

        r=self.s.query("SELECT evacuees_density FROM aamks_geom WHERE name=?", (name,))[0]
        if r['evacuees_density']  is not None:
            return 1/r['evacuees_density'] * 100 * 100

        z=self.conf['evacuees_density'][type_sec]
        return 1/z * 100 * 100

        raise Exception("Cannot determine the density for {}".format(name))

# }}}
    def _evac_rooms(self,floor): # {{{
        '''
        * probabilistic: probabilistic rooms
        * manual: manually asigned evacuees
        '''

        rooms={}
        probabilistic_rooms={}
        for i in self.s.query("SELECT points, name, type_sec FROM aamks_geom WHERE type_pri='COMPA' AND floor=? AND has_door=1 ORDER BY global_type_id", (floor,)):
            i['points']=json.loads(i['points'])
            probabilistic_rooms[i['name']]=i

        manual_rooms={}
        for i in self.s.query("SELECT name, x0, y0 FROM aamks_geom WHERE type_pri='EVACUEE' AND floor=?", (floor,)):
            q=(floor,i['x0'], i['y0'], i['x0'], i['y0'])
            x=self.s.query("SELECT name,type_sec FROM aamks_geom WHERE type_pri='COMPA' AND floor=? AND x0<=? AND y0<=? AND x1>=? AND y1>=?", q)[0]
            if not x['name'] in manual_rooms:
                manual_rooms[x['name']]={'type_sec': x['type_sec'], 'positions': [] }
                del probabilistic_rooms[x['name']]
            manual_rooms[x['name']]['positions'].append((i['x0'], i['y0'], x['name']))

        rooms['probabilistic']=probabilistic_rooms
        rooms['manual']=manual_rooms
        return rooms
# }}}
    def _dispatch_evacuees(self):# {{{
        ''' 
        We dispatch the evacuees across the building according to the density
        distribution. 
        '''
        self.dispatched_evacuees=OrderedDict()
        self.groups = OrderedDict()
        self.leaders = OrderedDict()
        self.e_type = OrderedDict()
        self.pre_evacuation=OrderedDict() 
        self._make_floor_obstacles()
        for floor in self.floors:
            self.pre_evacuation[floor] = list()
            self.groups[floor] = list()
            self.leaders[floor] = list()
            self.e_type[floor] = list()
            positions = []
            evac_rooms=self._evac_rooms(floor)
            for name,r in evac_rooms['probabilistic'].items():

                density=self._get_density(r['name'],r['type_sec'],floor)
                room_positions=self._dispatch_inside_polygons(density,r['points'], floor, name)
                pos_to_cluster = []
                for i in room_positions:
                    pos_to_cluster.append(i[0:2])  # cutting list to have only necessery elements
                self._clustering(floor,pos_to_cluster)  # parameters from clustering method
                positions += room_positions

                for i in room_positions:
                    self.pre_evacuation[floor].append(self._make_pre_evacuation(r['name'], r['type_sec']))

            for name,r in evac_rooms['manual'].items():

                pos_to_cluster = []
                for i in r['positions']:
                    pos_to_cluster.append(i[0:2])  #cutting list to have only necessery elements
                self._clustering(floor,pos_to_cluster)  # parameters from clustering method

                positions += r['positions']
                for i in r['positions']:
                    self.pre_evacuation[floor].append(self._make_pre_evacuation(name, r['type_sec']))
            self.dispatched_evacuees[floor] = positions



# }}}
    def _make_floor_obstacles(self):# {{{
        self._floor_obstacles={}
        for floor in self.floors:
            obsts=[]
            for x in self.json.readdb("obstacles")['obstacles'][floor]:
                obsts.append([(o[0],o[1]) for o in x])
            try:
                obsts.append(self.json.readdb("obstacles")['fire'][floor])
            except:
                pass
            self._floor_obstacles[floor]=unary_union([ Polygon(i) for i in obsts ])
# }}}
    def _dispatch_inside_polygons(self,density,points,floor,name):# {{{
        exterior=Polygon(points)
        exterior_minus_obsts=exterior.difference(self._floor_obstacles[floor])
        walkable=exterior_minus_obsts.buffer(- self.evacuee_radius - 10 )

        bbox=list(walkable.bounds)
        target=int(walkable.area / density)
        positions=[]
        while len(positions) < target:
            x=uniform(bbox[0], bbox[2])
            y=uniform(bbox[1], bbox[3])
            if walkable.intersects(Point(x,y)):
                positions.append((int(x),int(y), name))
        return positions
# }}}
    def _make_evac_conf(self):# {{{

        ''' Write data to sim_id/evac.json. '''
        self._evac_conf['FLOORS_DATA']=OrderedDict()
        for floor in self.floors:
            self._evac_conf['FLOORS_DATA'][floor]=OrderedDict()
            self._evac_conf['FLOORS_DATA'][floor]['NUM_OF_EVACUEES']=len(self.dispatched_evacuees[floor])
            self._evac_conf['FLOORS_DATA'][floor]['EVACUEES']=OrderedDict()
            z=self.s.query("SELECT z0 FROM aamks_geom WHERE floor=?", (floor,))[0]['z0']
            for i,pos in enumerate(self.dispatched_evacuees[floor]):
                e_id='f{}'.format(i)
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]=OrderedDict()
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['ORIGIN']         = (pos[0], pos[1])
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['COMPA']          = (pos[2])
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['PRE_EVACUATION'] = self.pre_evacuation[floor][i]
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['PRE_EVACUATION'] = self.pre_evacuation[floor][i]

                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['ALPHA_V']        = round(normal(self.conf['evacuees_alpha_v']['mean']     , self.conf['evacuees_alpha_v']['sd'])     , 2)
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['BETA_V']         = round(normal(self.conf['evacuees_beta_v']['mean']      , self.conf['evacuees_beta_v']['sd'])      , 2)
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['H_SPEED']        = round(normal(self.conf['evacuees_max_h_speed']['mean'] , self.conf['evacuees_max_h_speed']['sd']) , 2)
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['V_SPEED']        = round(normal(self.conf['evacuees_max_v_speed']['mean'] , self.conf['evacuees_max_v_speed']['sd']) , 2)
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['CLUSTER'] = int(self.groups[floor][i])
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['LEADER'] = int(self.leaders[floor][i])
                self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['ETYPE'] = self.e_type[floor][i]



                #self._evac_conf['FLOORS_DATA'][floor]['EVACUEES'][e_id]['ETYPE'] = self.groups[floor][i]
        self.json.write(self._evac_conf, "{}/workers/{}/evac.json".format(os.environ['AAMKS_PROJECT'],self._sim_id))
        #print(self._sim_id)

# }}}
    def _evacuees_static_animator(self):# {{{
        ''' 
        For the animator. We just pick a single, newest sim_id and display
        evacuees init positions. Animator can use it when there are no worker
        provided animations (moving evacuees for specific sim_id). 

        '''

        m={}
        for floor in self.floors:
            m[floor]=self.dispatched_evacuees[floor]
        self.s.query('INSERT INTO dispatched_evacuees VALUES (?)', (json.dumps(m),))

    def _cluster_leader(self, center, points):
        leaders = []
        points = tuple(map(tuple, points))
        for num, i in enumerate(center):
            dist_2 = np.sum((points - i) ** 2, axis=1)
            leaders.append(np.argmin(dist_2))
        return leaders

    def _cluster_leader_positions(self, center, points):# {{{
        points = tuple(map(tuple, points))
        dist_2 = np.sum((points - center) ** 2, axis=1)
        return points[np.argmin(dist_2)]

# }}}
    def _clustering(self, floor, positions):# {{{
        """clustering evacuues in the room, finding leaders in groups by cluster_leader method
            which tells who to follow, naming agent is it follower or active"""
        ms = MeanShift()
        z = np.array(positions)
        ms.fit(z)
        cluster_centers = ms.cluster_centers_
        labels = ms.labels_
        leaders = self._cluster_leader(cluster_centers, list(positions)) #list of leaders


        who_to_follow= []
        e_type= []
        for num, i in enumerate(labels):
            who_to_follow.append(leaders[i])
            if num == leaders[i]:
                e_type.append("ACTIVE")
            else:
                e_type.append("FOLLOWER")

        self.groups[floor]+=list(labels)
        self.leaders[floor]+=list(who_to_follow)
        self.e_type[floor]+=list(e_type)

# }}}
    def _make_dispatched_rooms(self):# {{{
        '''
        rooms for dispatched_evacuees
        '''

        self._dispatched_rooms={}
        for floor,evacuees in self.dispatched_evacuees.items():
            self._dispatched_rooms[floor]={}
            for e in evacuees:
                if e[2] not in self._dispatched_rooms[floor]:
                    self._dispatched_rooms[floor][e[2]]=[]
                self._dispatched_rooms[floor][e[2]].append((e[0], e[1]))

    def _cluster_coloring(self):# {{{
        '''
        We have 9 colors for clusters and 1 color for the leader of the cluster
        Colors are defined in aamks/inc.json as color_0, color_1, ...
        '''
        self._make_dispatched_rooms()
        # self._evac_conf['FLOORS_DATA']['0']['EVACUEES']:
        # f0: OrderedDict([('ORIGIN'  , (655  , 1200)) , ('COMPA' , 'r1') , ('CLUSTER' , 0) , ('LEADER' , 1) , ('ETYPE' , 'FOLLOWER')])
        # f1: OrderedDict([('ORIGIN'  , (745  , 1255)) , ('COMPA' , 'r1') , ('CLUSTER' , 0) , ('LEADER' , 1) , ('ETYPE' , 'ACTIVE')])
        # f2: OrderedDict([('ORIGIN'  , (770  , 1185)) , ('COMPA' , 'r1') , ('CLUSTER' , 0) , ('LEADER' , 1) , ('ETYPE' , 'FOLLOWER')])
        # f3: OrderedDict([('ORIGIN'  , (550  , 465))  , ('COMPA' , 'r1') , ('CLUSTER' , 1) , ('LEADER' , 5) , ('ETYPE' , 'FOLLOWER')])

        ms = MeanShift()
        self.clusters = {}
        evacues = []
        leaders = []

        for floor, rooms in self._dispatched_rooms.items():
            self.clusters[floor] = {}
            for room, positions in rooms.items():
                self.clusters[floor][room] = OrderedDict()
                z = np.array(positions)
                ms.fit(z)
                cluster_centers = ms.cluster_centers_
                labels = ms.labels_

                for i in sorted(labels):
                    self.clusters[floor][room][i] = OrderedDict([('agents', [])])
                for idx, i in enumerate(labels):
                    self.clusters[floor][room][i]['agents'].append(self._dispatched_rooms[floor][room][idx])

                    pos_x, pos_y = self._dispatched_rooms[floor][room][idx]
                    self.clusters[floor][room][i]['leader'] = self._cluster_leader_positions(cluster_centers[i],  self.clusters[floor][room][i]['agents'])
                    #print(self.clusters[floor][room][i]['leader'])
                    evacues.append([room, int(i), idx, pos_x, pos_y])
                #print(self.clusters[floor][room][i]['agents'])
                for idx, i in enumerate(labels):
                    self.clusters[floor][room][i]['center'] = cluster_centers[i]
                    self.clusters[floor][room][i]['leader'] = self._cluster_leader_positions(cluster_centers[i], self.clusters[floor][room][i][ 'agents'])
                    leaders.append([self.clusters[floor][room][i]['leader'][0], self.clusters[floor][room][i]['leader'][1]])


        anim=OrderedDict([("simulation_id",1), ("simulation_time",0), ("time_shift",0)])
        anim_evacuees=[OrderedDict(), OrderedDict()]
        anim_rooms_opacity=[OrderedDict(), OrderedDict()]
        color_iterator=0

        for floor, floors in self.clusters.items():
            frame = []
            for room, rooms in floors.items():
                for cid, clusters in rooms.items():
                    color_iterator += 1
                    for agent in clusters['agents']:
                        frame.append([agent[0], agent[1], 0, 0, str(color_iterator % 9), 1])
                    frame.append([clusters['leader'][0], clusters['leader'][1], 0, 0, str(9), 1])


                    anim_evacuees[0][floor] = frame
                    anim_evacuees[1][floor] = frame
                    anim_rooms_opacity[0][floor] = {}
                    anim_rooms_opacity[1][floor] = {}

        anim['animations'] = OrderedDict([("evacuees", anim_evacuees), ("rooms_opacity", anim_rooms_opacity)])
        simulation_name = str(self._sim_id)+"/clustering.zip"
        self._write_anim_zip(anim)
        dd(anim)
        Vis({'highlight_geom': None, 'anim': None, 'title': 'Clustering', 'srv': 1, 'anim':simulation_name})

# }}}
    def _write_anim_zip(self,anim):# {{{
        zf = zipfile.ZipFile("{}/workers/{}/clustering.zip".format(os.environ['AAMKS_PROJECT'], 1) , mode='w', compression=zipfile.ZIP_DEFLATED)
        try:
            zf.writestr("anim.json", json.dumps(anim))
        finally:
            zf.close()

# }}}
