
class StateMachine:
    states = dict()
    loadIns = []
    state = None
    prevState = None
    app = None

    @classmethod
    def loadin(cls):
        for load in cls.loadIns:
            load()
