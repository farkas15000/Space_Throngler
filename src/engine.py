class StateMachine:
    """holds states and instances. used globally"""

    states = dict()
    loadIns = []
    state = None
    prevState = None
    app = None

    @classmethod
    def loadin(cls):
        """runs states setup"""
        for load in cls.loadIns:
            load()
