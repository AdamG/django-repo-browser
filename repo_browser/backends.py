
class BaseBackend(object):
    "An agnostic VCS backend class. "
    name = "base"

    def __init__(self, connection_string):
        self.connection_string = connection_string

    def parents_for(self, identifier):
        raise NotImplementedError()

    def children_for(self, identifer):
        raise NotImplementedError()

    def timestamp_for(self, identifier):
        raise NotImplementedError()

    def author_for(self, identifier):
        raise NotImplementedError()

    def commit_message_for(self, identifier):
        raise NotImplementedError()

    def files_for(self, identifier):
        raise NotImplementedError()

    def root(self):
        "The first, parentless commit"
        raise NotImplementedError()

    def tip(self):
        "The tip commit - childless, but not necessarily the only one"
        raise NotImplementedError()


class MercurialBackend(BaseBackend):
    def __init__(self, *args, **kwargs):
        "Create a Mercurial repo object and keep it around locally"
        import mercurial
        import mercurial.ui
        import mercurial.hg
        import mercurial.node
        self.hexify = mercurial.node.hex

        super(MercurialBackend, self).__init__(*args, **kwargs)
        self.repository = mercurial.hg.repository(
            mercurial.ui.ui(report_untrusted=False, interactive=False),
            self.connection_string)

    def parents_for(self, identifier):
        return [
            self.hexify(c._node) for c in
            self.repository.changectx(identifier).parents()]

    def children_for(self, identifier):
        return [
            self.hexify(c._node) for c in
            self.repository.changectx(identifier).children()]

    def timestamp_for(self, identifier):
        return self.repository.changectx(identifier).date()

    def author_for(self, identifier):
        return self.repository.changectx(identifier).user()

    def commit_message_for(self, identifier):
        return self.repository.changectx(identifier).description()

    def files_for(self, identifier):
        return self.repository.changectx(identifier).files()

    def tip(self):
        return self.hexify(self.repository.changectx("tip")._node)

    def root(self):
        return self.hexify(self.repository.changectx("0")._node)
