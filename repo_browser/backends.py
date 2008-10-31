
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

    def diffs_for(self, identifier):
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
        import datetime, time
        # TODO: Should this be time.gmtime or time.localtime?
        return datetime.datetime(
            *time.gmtime(
                self.repository.changectx(identifier).date()[0])[:6])

    def author_for(self, identifier):
        return self.repository.changectx(identifier).user()

    def commit_message_for(self, identifier):
        return self.repository.changectx(identifier).description()

    def files_for(self, identifier):
        return self.repository.changectx(identifier).files()

    def diffs_for(self, identifier):
        from mercurial import mdiff, util, patch

        ctx = self.repository.changectx(identifier)
        # TODO: Check the hgweb implementation on this
        parent = ctx.parents()[0]
        parent_date = util.datestr(parent.date())
        this_date = util.datestr(ctx.date())
        diffopts = patch.diffopts(self.repository.ui, untrusted=True)

        # Returns a tuple of modified, added, removed, deleted, unknown
        # TODO: look up in the api what FIXME* are
        modified, added, removed, deleted, unknown, FIXME, FIXME2 = \
            self.repository.status(
            parent.node(),
            ctx.node(),)

        for modified_file in modified:
            filectx = ctx.filectx(modified_file)
            parent_filectx = parent.filectx(modified_file)
            this_data = filectx.data()
            parent_data = parent_filectx.data()
            yield mdiff.unidiff(parent_data, parent_date,
                                this_data,this_date,
                                modified_file, modified_file,
                                opts=diffopts)

        for added_file in added:
            filectx = ctx.filectx(added_file)
            this_data = filectx.data()
            yield mdiff.unidiff(
                None, parent_date, this_data, this_date,
                added_file, added_file, opts=diffopts)

        for removed_file in removed:
            parent_filectx = parent.filectx(removed_file)
            parent_data = parent_filectx.data()
            yield mdiff.unidiff(
                parent_data, parent_date, None, ctx.date(),
                removed_file, removed_file, opts=diffopts)

    def tip(self):
        return self.hexify(self.repository.changectx("tip")._node)

    def root(self):
        return self.hexify(self.repository.changectx("0")._node)
