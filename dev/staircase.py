# === Modelowanie kolejki na klatce schodowej ===
import numpy.random as random
from math import ceil
"""
Importowanie niezbędnych modułów:<br>
    numpy.random -generowanie losowych liczb
"""
class Queue:
    """
    <b>Klasa Queue</b> (kolejka) reprezentuje bieg schodów o szerokości jednej osoby. Używana jest kilukrotnie w klasie Staircase
    (klatka schodowa), by zwirtualizować wygląd klatki schodowej. Dana kolejka jest zmodyfikowaną wersją kolejki FIFO (first in
     - first out), gdzie pierwszy dodany element jest usuwany również jako pierwszy, gdyż istnieje możliwość dodania (funkcje add, insert)
    do kolejki na różnych piętrach. Z kolejki usuwani są agenci (funkcje pop, only_pop),a także puste pola (funkcja pop_none). Istnieje 
    możliwość sprawdzenia czy dany agent znajduje się w kolejce (funkcja check_if_in_que), zwrócenie miejsca w którym się znajduje
    (funkcja give_index),jak również obliczania jak długo agent znajduje się w kolejce, na jakiej pozycji i czy już ją opuścił
    (funkcja count, count_completed). 
    """
    def __init__(self,name, floor, floor_space):# {{{
        """
        Generując daną kolejkę przypisywana jest jej nazwa, 
        liczba pięter, ilość miejsc między piętrami. Tworzony jest wskaźnik określający czy nastąpiło przesunięcie,
        licznik poszczególnych agentów, a także formowana jest sama kolejka wypełniona pustymi polami. 
        """
        self.name = name
        self.floor = floor
        self.floor_space = floor_space
        self.moved = False
        self.counter = {}
        self.queue = ((floor-1)*floor_space+2)*[None]# }}}
    def __repr__(self):# {{{
        """<b>Funkcja __repr__ </b> zwraca nazwę danej kolejki """
        return str(self.name)+"-queue"# }}}
    def __len__(self):# {{{
        """<b>Funkcja __len__</b> zwraca długość danej kolejki """
        return len(self.queue)# }}}
    def add(self, floor, data):# {{{
        """
        <b>Funkcja add</b> pobierająca parametry:<br>
        floor -numer piętra na którym dodany ma być agent, <br>
        data -dany agent<br>
        W momencie dodawania sprawdzane jest czy miejsce do którego
        ma być dodany agent jest wolne oraz czy komórka powyżej jest pusta,
        gdy warunki są spełnione funkcja wstawia agenta do kolejki, zapisuje 
        jego miejsce dodania, zwraca 1. <br>
        Jeżeli komórka do której agent chce zostać dodany jest wolna lecz inny agent schodzi
        z góry następuje losowanie miejsca między nimi w proporcji 1 do 3, gdy dodawany agent 
        wylosuje miejsce, jak we wcześniejszym przypadku wstawiany jest do kolejki, zapisywane 
        jest jego miejsce dodania, zwracana jest wartość 1.<br>
        Jeżeli komórka do której agent chce zostać dodany jest zajęta również następuje
        losowanie 1 do 3 z agentem przebywającym w kolejce, gdy agent wygra, funkcja zwraca 
        wartość 2.<br>
        W przypadku nie dodania agenta do kolejki funkcja zwraca 0.
        """

        if self.queue[floor*self.floor_space] is None:
            if self.queue[floor*self.floor_space+1] is None:
                self.queue[floor*self.floor_space] = data
                self.counter[data] = [floor*self.floor_space, 0, 0]
                return 1
            else:
                if not random.randint(0,3):
                    self.queue[floor*self.floor_space] = data
                    self.counter[data] = [floor*self.floor_space, 0, 0]
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
        """
        <b>Funkcja insert</b> pobierająca parametry:<br>
        floor -numer piętra na którym dodany ma być agent, <br>
        data -dany agent<br>
        Stosowana jest w przypadku gdy agent wylosuje dostanie się do kolejki, 
        w której nie ma wolnego miejsca. Funkcja zmienia wartość wskaźnika
        przesunięcia kolejki, wstawia agenta do kolejki oraz zapisuje 
        jego miejsce dodania.
        """
        self.moved = True
        self.queue.insert(floor*self.floor_space, data)
        self.counter[data] = [floor*self.floor_space, 0, 0]# }}}
    def pop(self):# {{{
        """
        <b>Funckja pop</b> usuwa pierwszy element z kolejki i dodaje puste pole
        na końcu w celu zachowania stałej wielkości kolejki. W przypadku gdy
        usuwany jest agent, zapisywany jest fakt ukończenia kolejki, funkcja zwraca True.
        Gdy usuwane jest puste miejsce funkcja zwraca False.
        """
        data = self.queue.pop(0)
        self.queue.append(None)
        if data is not None:
            self.counter[data].append("Done")
            return True
        return False# }}}
    def pop_none(self):# {{{
        """
        <b>Funkcja pop_none</b> w sytuacji gdy na pierwszym miejscu nie znajduje się 
        agent, usuwa pierwszą komórkę i dodaje pustą na końcu aby agenci przesunęli 
        się o jedną pozycję do przodu. Gdy pierwszy jest agent funkcja przeszukuje 
        kolejkę, gdy znajdzie wolną komórkę usuwa ją.
        """
        if self.queue[0] is None:
            self.queue.pop(0)
            self.queue.append(None)
        else:
            for i in range(len(self.queue)):
                if self.queue[i] == None:
                    del self.queue[i]
                    self.queue.append(None)
                    break# }}}
    def only_pop(self):# {{{
        """
        <b>Funkcja only_pop</b> usuwa pierwszy element z kolejki. Gdy usuwa agenta,
        zapisuje, iż opuścił on kolejkę oraz zwraca True, w przeciwnym wypadku zwraca False
        """
        data = self.queue.pop(0)
        if data is not None:
            self.counter[data].append("Done")
            return True
        else:
            return False# }}}
    def count(self):# {{{
        """
        <b>Funkcja count</b> zlicza poszczególnym agentom jak długo znajdują się w kolejce,
        a także zapisuje na którym miejscu się znajdują w danej chwili.
        """
        for x, i in enumerate(self.queue):
            if i is not None:
                self.counter[i][1] += 1
                self.counter[i][2] = x# }}}
    def print_count(self):# {{{
        """<b>Funckja print_count</b> służy do wyświetlania na ekranie licznika."""
        for i in self.counter.keys():
            if len(self.counter[i])<4:
                print("{:5}: \tenter  {} \tsteps  {} \tposition  {}".format(i,*self.counter[i]))
            else:
                print("{:5}: \tenter  {} \tsteps  {} \tposition  {} -- {}".format(i,*self.counter[i]))#}}}
    def count_completed(self):# {{{
        """<b>Funkcja count_completed</b> zwraca liczbę agentów, którzy już opuścili kolejkę."""
        return len([x for x in self.counter.values() if len(x)==4])# }}}
    def count_insiders(self):# {{{
        """<b>Funkcja count_insiders</b> zwraca liczbę agentów, którzy przebywają w kolejce."""
        return len([x for x in self.queue if x is not None])# }}}
    def give_index(self, agent_id):# {{{
        """
        <b>Funkcja give_index</b> pobiera parametr:<br>
        agent_id - identyfikator danego agenta,<br>
        Zwraca pozycję na której znajduje się agent.
        """
        return self.queue.index(agent_id)# }}}
    def check_if_in_que(self, agent_id):# {{{
        """
        <b>Funkcja check_if_in_que</b> pobiera parametr:<br>
        agent_id - identyfikator danego agenta,<br>
        Sprawdza, czy agent znajduje się w kolejce, jeżeli tak zwraca True, w przeciwnym wypadku zwraca False.
        """
        if agent_id in self.queue:
            return True
        else:
            return False# }}}


class Staircase:
    """
    <b>Klasa Staircase</b> reprezentuje klatkę schodową. Tutaj tworzone są obiekty klasy <b>Queue</b> (funkcja create_queues) 
    w zależności jak pojemna jest klatka schodowa. Obliczane są położenia poszczególnych miejsc kolejki (funkcja create_floor_positions, 
    create_positions). Dodawani są agenci (funkcja add_to_queues). Sprawdzane jest czy dany agent znajduje się w klatce 
    schodowej (funkcja check_if_in). Zliczana jest liczba agentów przebywających na klatce, jak również tych którzy ukończyli 
    schodzenie (funkcja total_number_of_people, total_completed). Następuje przesunięcie kolejek (funkcja move). 
    Istnieje opcja wyświetlenia stanu poszczególnych kolejek (funkcja show_status), obliczenia gęstości zapełnienia klatki
    (funkcja density2) oraz przepływu agentów przez wyjście (funkcja flow).
    """
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
        self.positions = self.create_positions() 
        self.Atotal = width/100*height/100
        self.Dexit = (self.lenght+self.width)/100*floors# }}}
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
    def check_if_in(self, agent_id):# {{{
        for i in range(len(self.ques)):
            if self.ques[i].check_if_in_que(agent_id):
                x,y = self.positions[self.ques[i].give_index(agent_id)]
                x += i*100
                y += i*100
                return [x,y]# }}}
    def total_number_of_people(self):# {{{
        Ptotal=0
        for i in self.ques:
            Ptotal+=i.count_insiders()
        return Ptotal# }}}
    def total_completed(self):# {{{
        number = 0
        for i in self.ques:
            number+=i.count_completed()
        return number# }}}
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
    def show_status(self):# {{{
        for i in self.ques:
            print(i)
            i.print_count()
        print("\n\n")# }}}
    def density2(self, x):# {{{
        return ceil(x/((self.size-2)*self.number_queues)*100)# }}}
    def flow(self):# {{{
        Fave = 0.42*(self.total_completed()/self.Dexit)**(1/3)
        return Fave# }}}
    def speed(self):# {{{
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
        return v/60# }}}}}}
