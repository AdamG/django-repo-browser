
class BaseBackend(object):
    "An agnostic VCS backend class. "
    name = "base"

    def __init__(self, connection_string):
        self.connection_string = connection_string

    def parents_for(self, identifier):
        raise NotImplementedError()

    def children_for(self, identifer):
        raise NotImplementedError()

    def root(self):
        "The first, parentless commit"
        raise NotImplementedError()

    def tip(self):
        "The tip commit - childless, but not necessarily the only one"
        raise NotImplementedError()

