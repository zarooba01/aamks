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
from schody import Queue 
from schody import Agent
#s.query("select count(name), min(x0), max(x1) from world2d where name LIKE 's4|%'")[0].values()
#s.query("select y0, y1 from world2d where name LIKE 's4|1'")[0].values()

class Queue(Queue):
    def set_position(self,positions):# {{{
        pass# }}}
    def give_index(self, agent_id):# {{{
        return self.queue.index(agent_id)# }}}
    def check_if_in_que(self, agent_id):# {{{
        if agent_id in self.queue:
            return True
        else:
            return False# }}}
    def pop(self):# {{{
        data = self.queue.pop(0)
        self.queue.append(None)
        if data is not None:
            self.counter[data].append("Done")
            return True# }}}
    def pop_none(self):# {{{
        if self.queue[0] is None:
            self.queue.pop(0)
            self.queue.append(None)
        else:
            for i in range(len(self.queue)):
                if self.queue[i] == None:
                    del self.queue[i]
                    break# }}}
    def only_pop(self):# {{{
        data = self.queue.pop(0)
        if data is not None:
            self.counter[data].append("Done")
            return True
        else:
            return False# }}}


class Prepare_Queues:
    def __init__(self, name="Str1", floors=3, number_queues=2, doors=1, width=500, height=2965/3, offsetx=1500, offsety=0):# {{{
        self.name = name
        self.floors = floors
        self.number_queues = number_queues
        self.doors = doors
        self.insert = 0
        self.width = width
        self.height = height
        self.offsetx = offsetx
        self.offsety = offsety
        self.lenght = (self.width**2+self.height**2)**(1/2)
        self.floor_space = int((self.width+self.lenght)/50)
        self.ques = self.create_queues()
        self.size = len(self.ques[0])
        self.positions = self.create_positions() # }}}
        self.Atotal = width/100*height/100
        self.Dexit = (self.lenght+self.width)/100*floors
    def create_queues(self):# {{{
        que = []
        for i in range(self.number_queues):
            que.append(Queue(i, self.floors, self.floor_space))
        return que# }}}
    def create_floor_positions(self,floor=0):# {{{
        positions = []
        sin_alfa = self.height/self.lenght
        cos_alfa = self.width/self.lenght
        lenght_steps = (self.width+self.lenght)/self.floor_space
        for i in range(self.floor_space):
            l = i*lenght_steps
            if l>self.lenght:
                x = self.offsetx+lenght_steps*(self.floor_space-i)
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
            output = i.add(floor, data)
            if output == 1:
                return True
            elif output == 2:
                if self.insert < self.doors:
                    self.insert += 1
                    i.insert(floor, data)
                    return True
        return False
                # }}}
    def move(self):# {{{
        self.insert = 0
        agent_dropped = 0
        for que in sorted(self.ques, key=lambda x: x.moved, reverse=True):
            que.count()
            if que.moved:
                que.moved = False
                if que.only_pop():
                    agent_dropped += 1
            else: 
                if agent_dropped < self.doors:
                    if que.pop():
                        agent_dropped += 1
                else:
                    que.pop_none()# }}}
    def listed_ques(self):# {{{
        for i in self.ques:
            print(i.give_position())
            #print(i.queue)            
            #print([("poz: ",x," agent: ", i) for x, i in enumerate(i.queue) if i is not None])# }}}
    def check_if_in(self, agent_id):# {{{
        for i in range(len(self.ques)):
            if self.ques[i].check_if_in_que(agent_id):
                x,y = self.positions[self.ques[i].give_index(agent_id)]
                x += i*100
                y += i*100
                return [x,y]
    def count(self):
        self.ques[0].print_count()
        #for i in self.ques:
        #    print(i)
        #    i.print_count()
        #print("\n\n")
# }}}
    def total_number_of_people(self):# {{{
        Ptotal=0
        for i in self.ques:
            Ptotal+=i.capacity()
        return Ptotal
    def total_completed(self):
        number = 0
        for i in self.ques:
            number+=i.count_completed()
        return number
    def density(self):
        Aevacuees = self.total_number_of_people()*3.14*0.25**2
        densit = Aevacuees/self.Atotal
        return densit
    def density2(self, x):
        return math.ceil(x/((self.size-2)*self.number_queues)*100)
    def density3(self):
        return self.ques[0].capacity()/(self.size-2)*100
    def flow(self):
        Fave = 0.42*(self.total_completed()/self.Dexit)**(1/3)
        return Fave
    def speed(self):
        'speed m/s'
        #G = lenght of the stair tread going/tread depth
        #R = riser height of each step
        G = 254
        R = 190
        if self.density() > 0.54:
            kt = 51.8*(G/R)**0.5 #84 for corridor or doorways
            v = kt*(1-0.266*self.density())
        else:
            v = 72
        return v/60# }}}

# suma tych co się ruszyli/wszystkich = vektor prędkości
# wykres gęstość/prędkość
            

class EvacEnv:
    def __init__(self):# {{{
        self.Que = Prepare_Queues()
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
            if int(aa[1:])<21:
                self.agents[aa]['target']=(990, 325)
            elif int(aa[1:])>=21 and int(aa[1:])<40:
                self.agents[aa]['target']=(990, 1510)
            elif int(aa[1:])>=40 and int(aa[1:])<60:
                self.agents[aa]['target']=(2300, 335)
            elif int(aa[1:])>=60 and int(aa[1:])<=80:
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
                
            #if self.Que.add_to_queues(floor, a['id']):
            #    a['target']=(1750, 2955)
            #    self.sim.setAgentPosition(a['id'], (0,0))
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
    def _add_to_staircase(self):# {{{
        try:
            for floor in sorted(self.waitings.keys()):
                #print(floor, len(self.waitings[floor]))
#liczba oczekujących na danym piętrze
                agentname, agentid = self.waitings[floor][0]
                if self.Que.add_to_queues(floor, agentid):
                    self.agents[agentname]['target']=(9750, 3570)
                    self.sim.setAgentPosition(agentid, (1750,3570))
                    del self.waitings[floor][0]
                    if len(self.waitings[floor])==0:
                        del self.waitings[floor]
        except:
            pass# }}}
    def _run(self):# {{{
        x = []
        y = []
        for t in range(150):
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
        #plt.show()
        #plt.savefig("Fig_1.png")


            #print(self.Que.density3())
            #print(self.Que.ques[0].poj())# {{{
            #self.Que.listed_ques()

        #self.Que.count()
        #print(self.Que.total_completed())
        #print(self.Que.total_number_of_people())
        #print(self.Que.density())
        #print(self.Que.flow())
        #print(self.Que.speed())# }}}
# }}}

e=EvacEnv()# {{{
e._run()
e._write_zip()
# prędkość od gęstośći, zmierzyć w ilu krokach wychodzi
# z 3 piętra wyjście na 2 piętro
# wchodzenie pod górę
# część wspólna z poprzedniej kolejki, prędkość 0, reszta jeden krok


# filmik ewakuacji
# kryteria oceniania modeli  ewakuacji w klatkach
# jakościowe, ilościowe
# http://sci-hub.tw/
# do-.org wkleić na sci hub
# https://scholar.google.com
# simple video recorder
# gęstość/prędkość
# łączenie strumieni}}}
