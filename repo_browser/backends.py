
from repo_browser import commit


class BaseBackend(object):
    "An agnostic VCS backend class. "

    CommitClass = commit.Commit

    def __init__(self, connection_string):
        self.connection_string = connection_string

    def get_commit(self, identifier):
        return self.CommitClass(identifier, self)

    def root(self):
        "The first, parentless commit"
        raise NotImplementedError()

    def tip(self):
        "The tip commit - childless, but not necessarily the only one"
        raise NotImplementedError()

    def heads(self):
        "Commits that have no children"
        raise NotImplementedError()


class MercurialBackend(BaseBackend):

    CommitClass = commit.MercurialCommit

    def __init__(self, *args, **kwargs):
        "Create a Mercurial repo object and keep it around locally"
        import mercurial
        import mercurial.ui
        import mercurial.hg
        import mercurial.node
        self.hexify = mercurial.node.hex

        super(MercurialBackend, self).__init__(*args, **kwargs)
        self.repo = mercurial.hg.repository(
            mercurial.ui.ui(report_untrusted=False, interactive=False),
            self.connection_string)

    def ctx_for(self, identifier):
        return self.repo.changectx(identifier)

    def tip(self):
        return self.CommitClass(self.hexify(self.ctx_for("tip")._node), self)

    def root(self):
        return self.CommitClass(self.hexify(self.ctx_for("0")._node), self)

    def heads(self):
        return [self.CommitClass(self.hexify(node), self) for node in self.repo.heads()]


class GitBackend(BaseBackend):
    "A Git backend"

    CommitClass = commit.GitCommit

    def __init__(self, connection_string):
        from git import Repo
        self.repo = Repo(connection_string)

    def root(self):
        "The first, parentless commit"

        return self.CommitClass(self.repo.log(n=1)[0].id, self)

    def tip(self):
        "The HEAD commit"
        return self.CommitClass(self.repo.commit("HEAD"), self)

    def heads(self):
        "Commits that have no children"
        return [self.CommitClass(head.commit, self) for head in self.repo.heads]


BACKENDS = {
    "mercurial": MercurialBackend,
    "git": GitBackend,
}
