class Queue:
    def __init__(self,name, floor, floor_space):# {{{
        self.name = name
        self.floor = floor
        self.floor_space = floor_space
        self.queue = floor*floor_space*[None]
        self.moved = False# }}}
    def __repr__(self):# {{{
        return str(self.name)+"-queue"# }}}
    def add(self, floor, data):# {{{
        ''' Add append data on the floor when the space
        at the floor is free and above cell is free, 
        if above cell is taken, there is lottery between
        appended and resident - 33%
        if the space at the floor and above cell is taken, 
        data is insert into queue in cause of winning the lottery
        '''

        if self.queue[floor*self.floor_space] is None:
            if self.queue[floor*self.floor_space+1] is None:
                self.queue[floor*self.floor_space] = data
                return 1
            else:
                if not random.randint(0,3):
                    self.queue[floor*self.floor_space] = data
                    return 1
                else:
                    return 0
        else:
            if not random.randint(0,3):
                if not self.moved:
                    return 2
                else:
                    return 0
            else:
                return 0# }}}
    def insert(self, floor, data):# {{{
        self.moved = True
        self.queue.insert(floor*self.floor_space, data)# }}}
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
            return True# }}}
    def pop_none(self):# {{{
        if self.queue[0] is None:
            self.queue.pop(0)
            self.queue.append(None)# }}}
    def only_pop(self):# {{{
        data = self.queue.pop(0)
        if data is not None:
            return True
        else:
            return False# }}}

class Staircase:
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
        #awaitings = [(que.queue[0], que.moved, que) for que in sorted(self.ques, key=lambda x: x.moved, reverse=True)]
        for que in sorted(self.ques, key=lambda x: x.moved, reverse=True):
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
    def check_if_in(self, agent_id):# {{{
        for i in range(len(self.ques)):
            if self.ques[i].check_if_in_que(agent_id):
                x,y = self.positions[self.ques[i].give_index(agent_id)]
                x += i*100
                y += i*100
                return [x,y]
# }}}
