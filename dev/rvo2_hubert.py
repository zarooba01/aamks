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
from include import SimIterations
# }}}

class EvacEnv:
    def __init__(self):# {{{
        self.json=Json()
        self.s=Sqlite("{}/aamks.sqlite".format(os.environ['AAMKS_PROJECT']))


        self.conf = self.json.read("{}/conf.json".format(os.environ['AAMKS_PROJECT']))
        si=SimIterations(self.conf['project_id'], self.conf['scenario_id'], self.conf['number_of_simulations'])
        sim_id = range(*si.get())
        self.simulation_id = (list(range(*si.get())))
        self.path = self.json.read("{}/workers/{}/evac.json".format(os.environ['AAMKS_PROJECT'], *self.simulation_id))

        self.evacuee_radius=self.json.read("{}/inc.json".format(os.environ['AAMKS_PATH']))['evacueeRadius']
        time=1
        self.sim = rvo2.PyRVOSimulator(time     , 40                , 5            , time         , time                  , self.evacuee_radius , 30)
        self._anim={"simulation_id": 1, "simulation_time": 20, "time_shift": 0, "animations": { "evacuees": [], "rooms_opacity": [] }}
        self._create_agents()
        self._load_obstacles()
        self._run()
        self._write_zip()
        Vis({'highlight_geom': None, 'anim': '1/f1.zip', 'title': 'x', 'srv': 1})

# }}}
    def _create_agents(self):# {{{
        z =self.s.query("SELECT * FROM aamks_geom WHERE type_pri='EVACUEE'" )
        #y = self.s.query("SELECT * FROM clustering_info")

        data = self.path
        id=0
        for floor in data["FLOORS_DATA"]:
            agenty = data["FLOORS_DATA"][floor]["EVACUEES"]
        self.agents={}
        for i,j in zip(z,agenty):

            aa=i['name']
            self.agents[aa]={}
            ii=self.sim.addAgent((i['x0'],i['y0']))
            self.agents[aa]['name']=aa
            self.agents[aa]['id']=ii
            self.sim.setAgentPrefVelocity(ii, (0,0))
            self.agents[aa]['behaviour']='random'
            self.agents[aa]['origin'] = (i['x0'], i['y0'])
            self.agents[aa]['target'] = (0,0)
            self.agents[aa]['etype'] = agenty[j]["ETYPE"]
            self.agents[aa]['who_to_follow_id'] = agenty[j]["LEADER"]

            #self.agents[aa]['target']=(i['x0'] + 1000, i['y0']+100)
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

        if a['etype']== 'ACTIVE':
            dx= 12000 - self.sim.getAgentPosition(a['id'])[0]
            dy= 12000 - self.sim.getAgentPosition(a['id'])[1]

            #print("AKTYWNY", "id: ", a['id'],"pozycja: ", self.sim.getAgentPosition(a['id']), "cel: ", a['target'], "vect: ", self.sim.getAgentPrefVelocity(a['id']) )

            print("id=%d, pozycja = %f %f" %(a['id'], self.sim.getAgentPosition(a['id'])[0],self.sim.getAgentPosition(a['id'])[1]) )
        if a['etype'] == 'FOLLOWER':
            follow = a['who_to_follow_id']

            #print("FOLLOWER", "id:", a['id'], "pozycja: ", self.sim.getAgentPosition(a['id']), "cel: ",follow, self.sim.getAgentPosition(follow), "vect: ", (self.sim.getAgentPrefVelocity(a['id'])))

            print("id=%d, pozycja= (%f %f) cel_id = %d cel_pozycja = (%f %f)" %(a['id'], self.sim.getAgentPosition(a['id'])[0],self.sim.getAgentPosition(a['id'])[1], follow, self.sim.getAgentPosition(follow)[0], self.sim.getAgentPosition(follow)[1]))
            dx = self.sim.getAgentPosition(follow)[0]- self.sim.getAgentPosition(a['id'])[0]
            dy = self.sim.getAgentPosition(follow)[1]-self.sim.getAgentPosition(a['id'])[1]

            #print(dx,dy)
        self.sim.setAgentPrefVelocity(a['id'], (dx,dy))
        print(dx,dy,self.sim.getAgentPrefVelocity(a['id']))
        return sqrt(dx**2 + dy**2)
        
# }}}
    def _positions(self):# {{{
        frame=[]
        for k,v in self.agents.items():

            pos=[round(i) for i in self.sim.getAgentPosition(v['id'])]

            frame.append([pos[0],pos[1],0,0,"N",1])
        self._anim["animations"]["evacuees"].append({"0": frame})

# }}}
    def _update(self):# {{{
        for k,v in self.agents.items():
            #print(self.agents[k])
            target_dist=self._velocity(self.agents[k])
            if target_dist <= self.evacuee_radius * 3.5:
                # dd(self.agents[k]['id'], target_dist)
                #print(self.agents[k])
                #print(self.agents[k]['name'], self.agents[k]['target'])
                pass
                #exit()
        self._positions();

# }}}
    def _write_zip(self):# {{{
        d="{}/workers/1".format(os.environ['AAMKS_PROJECT'])
        #pprint(self._anim['animations']['evacuees'])

        zf=zipfile.ZipFile("{}/f1.zip".format(d), 'w')
        zf.writestr("anim.json", json.dumps(self._anim))
        zf.close()
# }}}
    def _run(self):# {{{
        for t in range(100):
            self.sim.doStep()
            self._update()
# }}}

e=EvacEnv()
