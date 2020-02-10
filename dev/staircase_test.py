from staircase import Queue
from staircase import Staircase
class Test_Queue():
    que = Queue("1", 2, 3)
    def test_instance(self):
        assert isinstance(self.que, Queue)
    def test_parameters(self):
        assert self.que.name == "1"
        assert self.que.floor == 2
        assert self.que.floor_space == 3
        assert self.que.moved == False
        assert self.que.counter == dict()
    def test_len(self):
        assert len(self.que) == (2-1)*3+2
    def test_name(self):
        assert repr(self.que) == "1-queue"
    def test_add(self):
        add =  self.que.add(0, "agent0")
        if add == 1:
            assert "agent0" in self.que.queue 
            assert self.que.counter["agent0"] == [0, 0, 0]
        elif add == 2:
            self.que.insert(0, "agent0")
            assert self.que.moved == True
            assert self.que.counter["agent0"] == [0, 0, 0]
        else:
            assert "agent0" not in self.que.queue
    def test_count_insiders(self):
        assert self.que.count_insiders() == 1
    def test_give_index(self):
        assert self.que.give_index("agent0") == 0
    def test_check_if_in_que(self):
        assert self.que.check_if_in_que("agent0") == True
    def test_pop(self):
        assert self.que.pop() == True
        assert self.que.counter["agent0"] == [0, 0, 0, "Done"]
    def test_check_if_in_que(self):
        assert self.que.check_if_in_que("agent0") == False
    def test_pop_none(self):
        assert self.que.pop_none() == None  
    def test_only_pop(self):
        assert self.que.only_pop() == False
        self.que.add(0, "agent0")
        assert self.que.only_pop() == True
    def test_count_completed(self):
        assert self.que.count_completed() == 1 
class Test_Staircase():
    stair = Staircase()
    def test_instance(self):
        assert isinstance(self.stair, Staircase)
    def test_parameters(self):
        assert self.stair.name == "Str1"
        assert self.stair.floors == 3
        assert self.stair.number_queues == 2
        assert self.stair.doors == 1
        assert self.stair.width == 500
        assert self.stair.height == 2965/3
        assert self.stair.offsetx == 1500
        assert self.stair.offsety == 0
        assert self.stair.insert == 0
        assert self.stair.lenght == (self.stair.width**2+self.stair.height**2)**(1/2)
        #assert self.stair.floor_space == int((self.stair.width+self.stair.lenght)/50)
        assert self.stair.floor_space == 10
    def test_create_queues(self):
        assert isinstance(self.stair.create_queues()[0], Queue)
        assert isinstance(self.stair.create_queues()[1], Queue)
    def test_create_floor_positions(self):
        assert len(self.stair.create_floor_positions()) == 10
    def test_create_positions(self):
        assert len(self.stair.create_positions()) == 30
    def test_add_to_queues(self):
        assert self.stair.add_to_queues(0, "agent0") == True
    def test_check_if_in(self):
        assert type(self.stair.check_if_in("agent0")) == type(list())
    def test_total_number_of_people(self):
        assert self.stair.total_number_of_people() == 1
    def test_move(self):
        assert self.stair.move() == None
    def test_total_completed(self):
        assert self.stair.total_completed() == 1
    def test_density(self):
        assert self.stair.density2(40) == 100  

