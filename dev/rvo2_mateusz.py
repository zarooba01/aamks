
# MODULES {{{
import warnings
warnings.simplefilter('ignore', RuntimeWarning)
import rvo2
import json
import shutil
import os
import io
import re
import sys
import codecs
import itertools
import zipfile

from pprint import pprint
from collections import OrderedDict
from numpy.random import uniform
from math import sqrt
from include import Sqlite
from include import Json
from include import Dump as dd
from include import Vis
from numpy.random import uniform
# }}}

from schody import Queue 
from schody import Agent
#s.query("select count(name), min(x0), max(x1) from world2d where name LIKE 's4|%'")[0].values()
#s.query("select y0, y1 from world2d where name LIKE 's4|1'")[0].values()

#if something:
#    do with something

# when outside 

class Queue(Queue):
    def set_position(self,positions):
        pass
    def give_index(self, agent_id):
        return self.queue.index(agent_id)
    def pop(self):
        data=self.queue.pop(0)
        self.queue.append(None)
    def check_if_in_que(self, agent_id):
        if agent_id in self.queue:
            return 1
        else:
            return 0

class Prepare_Queues:
    def __init__(self, floors=3, number_queues=1, width=500, height=2965/3, offsetx=1500, offsety=0):# {{{
        self.floors = floors
        self.number_queues = number_queues
        self.width = width
        self.height = height
        self.offsetx = offsetx
        self.offsety = offsety
        self.lenght = (self.width**2+self.height**2)**(1/2)
        self.size = int((self.width+self.lenght)/50)
        self.ques = self.create_queues()
        self.positions = self.create_positions() # }}}
    def create_queues(self):# {{{
        que = []
        for i in range(self.number_queues):
            que.append(Queue(i, self.floors, self.size))
        return que# }}}
    def create_floor_positions(self,floor=0):# {{{
        positions = []
        sin_alfa = self.height/self.lenght
        cos_alfa = self.width/self.lenght
        lenght_steps = (self.width+self.lenght)/self.size
        for i in range(self.size):
            l = i*lenght_steps
            if l>self.lenght:
                x = self.offsetx+lenght_steps*(self.size-i)
                y = self.offsety+floor*self.height+self.height
            else:
                x = self.offsetx+l*cos_alfa
                y = self.offsety+floor*self.height+l*sin_alfa
            positions.append([x,y])
        return positions# }}}
    def create_positions(self):# {{{
        positions = []
        for i in range(self.floors):
            positions.extend(self.create_floor_positions(floor=i))
        positions.reverse()
        return positions# }}}
    def add_to_queues(self, floor, data):# {{{
        for i in self.ques:
            if i.add(floor, data):
                break# }}}
    def move(self):# {{{
        for i in self.ques:
            i.go_on(self.positions)# }}}
    def listed_ques(self):# {{{
        for i in self.ques:
            pass
            #i.give_location()
            #print(i.queue)            
            #print([("poz: ",x," agent: ", i) for x, i in enumerate(i.queue) if i is not None])# }}}
    def check_if_in(self, agent_id):
        for i in self.ques:
            if i.check_if_in_que(agent_id):
                return self.positions[i.give_index(agent_id)]
            else:
                return 0

class EvacEnv:
    def __init__(self):# {{{
        self.Que = Prepare_Queues()
        self.json=Json()
        self.s=Sqlite("{}/aamks.sqlite".format(os.environ['AAMKS_PROJECT']))

        self.evacuee_radius=self.json.read("{}/inc.json".format(os.environ['AAMKS_PATH']))['evacueeRadius']
        time=1
        self.sim = rvo2.PyRVOSimulator(time     , 40                , 5            , time         , time                  , self.evacuee_radius , 30)
        self._anim={"simulation_id": 1, "simulation_time": 20, "time_shift": 0, "animations": { "evacuees": [], "rooms_opacity": [] }}
        self._create_agents()
        self._load_obstacles()
        Vis({'highlight_geom': None, 'anim': '1/f1.zip', 'title': 'x', 'srv': 1})

# }}}
    def _create_agents(self):# {{{
        z=self.s.query("SELECT * FROM aamks_geom WHERE type_pri='EVACUEE'" )
        self.agents={}
        for i in z:
            aa=i['name']
            self.agents[aa]={}
            ii=self.sim.addAgent((i['x0'],i['y0']))
            self.agents[aa]['name']=aa
            self.agents[aa]['id']=ii
            self.sim.setAgentPrefVelocity(ii, (0,0))
            self.agents[aa]['behaviour']='random'
            self.agents[aa]['origin']=(i['x0'],i['y0'])
            self.agents[aa]['target']=(1000, i['y0'])
        self._positions()
# }}}
    def _load_obstacles(self):# {{{
        z=self.json.readdb('obstacles')
        obstacles=z['obstacles']['0']
        for i in obstacles:
            self.sim.addObstacle([ (o[0],o[1]) for o in i[:4] ])
            self.sim.processObstacles()
# }}}
    def _velocity(self,a): # {{{
        '''
        radius=3.5 is the condition for the agent to reach the behind-doors target 
        '''

        dx=a['target'][0] - self.sim.getAgentPosition(a['id'])[0]
        dy=a['target'][1] - self.sim.getAgentPosition(a['id'])[1]
        self.sim.setAgentPrefVelocity(a['id'], (dx,dy))
        if dx < 40:
            if self.sim.getAgentPosition(a['id'])[1] < 705:
                floor = 2
            elif self.sim.getAgentPosition(a['id'])[1] > 705 and self.sim.getAgentPosition(a['id'])[1] < 1850:
                floor = 1
            else:
                floor = 0
            self.Que.add_to_queues(floor, a['id'])
            a['target']=(1750, 2955)
        return sqrt(dx**2 + dy**2)
        
# }}}
    def _positions(self):# {{{
        frame=[]
        for k,v in self.agents.items():
            if self.Que.check_if_in(v['id']):
                pos=self.Que.check_if_in(v['id'])
            else:
                pos=[round(i) for i in self.sim.getAgentPosition(v['id'])]
            frame.append([pos[0],pos[1],0,0,"N",1])
        self._anim["animations"]["evacuees"].append({"0": frame})
# }}}
    def _update(self):# {{{
        for k,v in self.agents.items():
            target_dist=self._velocity(self.agents[k])
            if target_dist <= self.evacuee_radius * 3.5:
                #dd(self.agents[k]['id'], target_dist)
                pass
                #exit()
        self._positions();
# }}}
    def _write_zip(self):# {{{
        d="{}/workers/1".format(os.environ['AAMKS_PROJECT'])
        #dd(self._anim['animations']['evacuees'])

        zf=zipfile.ZipFile("{}/f1.zip".format(d), 'w')
        zf.writestr("anim.json", json.dumps(self._anim))
        zf.close()
# }}}
    def _run(self):# {{{
        for t in range(20):
            self.sim.doStep()
            self._update()
            #print([x for x in self.que.que() if x is not None])
            self.Que.move()
            self.Que.listed_ques()
# }}}

e=EvacEnv()
e._run()
e._write_zip()
