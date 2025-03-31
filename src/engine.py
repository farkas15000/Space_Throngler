
class StateMachine:
    states = dict()
    loadins = []
    state = None
    prevstate = None
    app = None

    @classmethod
    def loadin(cls):
        for load in cls.loadins:
            load()
