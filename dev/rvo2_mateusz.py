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
import copy
import math
import matplotlib.pyplot as plt
from staircase import Staircase, Queue
#s.query("select count(name), min(x0), max(x1) from world2d where name LIKE 's4|%'")[0].values()
#s.query("select y0, y1 from world2d where name LIKE 's4|1'")[0].values()

class EvacEnv:
    def __init__(self):# {{{
        self.Que = Staircase()
        self.json=Json()
        self.s=Sqlite("{}/aamks.sqlite".format(os.environ['AAMKS_PROJECT']))

        self.evacuee_radius=self.json.read("{}/inc.json".format(os.environ['AAMKS_PATH']))['evacueeRadius']
        time=1
        #self.sim rvo2.PyRVOSimulator TIME_STEP , NEIGHBOR_DISTANCE , MAX_NEIGHBOR , TIME_HORIZON , TIME_HORIZON_OBSTACLE , RADIUS , MAX_SPEED
        self.sim = rvo2.PyRVOSimulator(time     , 40                , 5            , time         , time                  , self.evacuee_radius , 30)
        self._anim={"simulation_id": 1, "simulation_time": 20, "time_shift": 0, "animations": { "evacuees": [], "rooms_opacity": [] }}
        self._create_agents()
        self._load_obstacles()
        Vis({'highlight_geom': None, 'anim': '1/f1.zip', 'title': 'x', 'srv': 1})
        self.waitings = {}

# }}}
    def _create_agents(self):# {{{
        #self.s.query("INSERT INTO aamks_geom (name, type_pri, x0, y0) VALUES ('f500', 'EVACUEE', '690', '2300')")
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
            if int(aa[1:])<69:
                self.agents[aa]['target']=(990, 325)
            elif int(aa[1:])>=69 and int(aa[1:])<132:
                self.agents[aa]['target']=(990, 1510)
            elif int(aa[1:])>=132 and int(aa[1:])<199:
                self.agents[aa]['target']=(2300, 335)
            elif int(aa[1:])>=199 and int(aa[1:])<=269:
                self.agents[aa]['target']=(2300, 1480)
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
        if abs(dx) < 60:
            if self.sim.getAgentPosition(a['id'])[1] < 705:
                floor = 2
            elif self.sim.getAgentPosition(a['id'])[1] > 705 and self.sim.getAgentPosition(a['id'])[1] < 1850:
                floor = 1
            else:
                floor = 0
            try:
                if (a['name'], a['id']) not in self.waitings[floor]:
                    self.waitings[floor].append((a['name'],a['id']))
            except:
                self.waitings.setdefault(floor, []).append((a['name'],a['id']))
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
        zf.close()# }}}
        #self.json.write(self._anim, "/home/mateusz/Pulpit/praca/anim3.json")
    def _add_to_staircase(self):# {{{
        try:
            for floor in sorted(self.waitings.keys()):
                #print(floor, len(self.waitings[floor]))
#liczba oczekujących na danym piętrze
                agentname, agentid = self.waitings[floor][0]
                if self.Que.add_to_queues(floor, agentid):
                    self.agents[agentname]['target']=(19750, 3570)
                    self.sim.setAgentPosition(agentid, (1750,3570))
                    del self.waitings[floor][0]
                    if len(self.waitings[floor])==0:
                        del self.waitings[floor]
        except:
            pass# }}}
    def _run(self):# {{{
        x = []
        y = []
        for t in range(320):
            self.sim.doStep()
            self._update()
            self._add_to_staircase()

            K = [copy.deepcopy(k.counter) for k in self.Que.ques]
            wszyscy = self.Que.total_number_of_people()

            self.Que.move()

            J = [j.counter for j in self.Que.ques]
            krok = 0
            stop = 0
            for i in range(len(K)):
                krok += len([x[0] for x, y in zip(K[i].items(), J[i].items()) if x[1][2] != y[1][2] and len(y[1])<4])
                krok += len([x for x,y in zip(K[i].items(), J[i].items()) if len(x[1]) != len(y[1])])
                stop += len([x[0] for x, y in zip(K[i].items(), J[i].items()) if x[1][2] == y[1][2] and len(y[1])<4])
            if wszyscy>0:
                x.append(self.Que.density2(wszyscy))
                y.append(round(krok/wszyscy*100, 2))

        plt.plot(x,y, "o")
        plt.xlabel('Density [%]')
        plt.ylabel('Speed [%]')
        #plt.show()# }}}
        #plt.savefig("/home/mateusz/Pulpit/praca/Fig_3.png")

        #self.Que.count()
        #print(self.Que.flow())
        #print(self.Que.speed())
e=EvacEnv()
e._run()
e._write_zip()
