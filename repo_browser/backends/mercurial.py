import mercurial
import mercurial.ui
import mercurial.hg

import repo_browser.backends


class MercurialBackend(repo_browser.backends.BaseBackend):
    def __init__(self, *args, **kwargs):
        "Create a Mercurial repo object and keep it around locally"

        super(MercurialBackend, self).__init__(*args, **kwargs)
        self.repository = mercurial.hg.repository(
            mercurial.ui.ui(report_untrusted=False, interactive=False),
            self.connection_string)

    def parents_for(self, identifier):
        return [
            c._node for c in self.repository.changectx(identifier).parents()]

    def children_for(self, identifier):
        return [
            c._node for c in self.repository.changectx(identifier).children()]

    def tip(self):
        return self.repository.changectx("tip")._node

    def root(self):
        return self.repository.changectx("0")._node
