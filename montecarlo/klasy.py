class Agent():
    """the parent agent that has every funtamental param"""

    def __init__(self, param):
        self.param = param





class ConservativeAgent(Agent):

    """"""
    # Dla kazdego wyjscia są parametry takie jak: widzialnosc, czy je zna, warunki przeszkadzające
    # jezeli droga jest w dymie to zmienia drogę
    # wszystkie widoczne i znane wyjscia
    # czas detekcji może byc krótszy niż pre_evac_time jeżeli jest wystarczajaca ilość dymu żeby wyzwolić detekcję
    # dym może być detected kiedy powstaje w pozycji agenta / albo przez czujkę
    # kiedy się zgubi zachowuje się jak HeardingAgent aż do momentu aż znajdzie wyjście
    # gubi się kiedy nie moze znaleźc wyjscia w danej części budynku
    # do tego agenta odnosi się tabela z preferencjami wyjść

    pass

class ActiveAgent(Conservative):
    # podobny do konserwatywnego, ale
    # wszystkie widoczne wyjscia traktuje jednakowo, bez wzgledu czy sa znane czy nie
    # aktywnie obserwują środowisko by znaleźć najszybszą trasę bez względu na to czy wyjście jest znane czy nie
    # może prowadzić heardingowca przez nieznane wyjścia



    pass


class HerdingAgent(Agent):
    # nie znają geometrii budynku i żadnego wyjścia, znają tylko drogę którędy przyszli
    # oglądają się i patrzą co robią inni agenci, jeżeli jakiś idzie do wyjscia też za nim idzie
    # nie będzie się ruszał nawet po detekcji dymu
    # kiedy pre_evac_time sie skonczy, ale nie rozpozna żadnych drzwi jako znane i nie zobaczy nikogo kto idzie to nie będzie się ruszać
    # kiedy jego najbliższy sąsiad zbliża się do jakichś drzwi to od razu za nim biegnie
    # jeżeli agent zna wyjścia to zachowuje się jak ConservativeAgent

    # cały czas się rozgląda i sprawdza gdzie idzie najbliższy sąsiad
    # defaultowo 5 najbliższych sąsiadów w promieniu 5 (można zmieniać) m jest branych pod uwagę, będzie podążał za większością swoich sąsiadów tylko ci co są odwróceni głową: cosinus kąta mniejszy od -0.2
    # nie chcą prowadzić kogoś, chcą za kimś iść
    # jeśli nie moze zebrać informacji od najbliższych sąsiadów to bierze pod uwagę wszyzstkich widocznych, jeżeli ich brak odchodzi od wejścia, i ponownie patrzy
    # uzaleznione jest to od wagi wpływowości (rodzic- dziecko) - nie jest to używane, używana jest tylko odleglość - im bliżej tym większy wpływ


    pass

class FollowerAgent(Conservative):
    # cos pomiedzy ConservativeAgent a HeardingAgent

    # procedura wyjsc taka jak w conservative
    # patrzy też gdzie najbliższy sąsiad się kieruje i dodaje do listy swoich wyjść
    # zmieni swoją drogę, jeżeli nowe wyjście jest lepsze - szybciej się wydostanie, w innym przypadku zachowuje się jak konserwatywny

    pass



# jest takie cos jak social force
# str 98 sfpe
