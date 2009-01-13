class Commit(object):
    def __init__(self, id_, repo):
        self.id = id_
        self.repo = repo

    def __hash__(self):
        return hash(str(self.id)+str(self.repo.connection_string))

    def get_children(self):
        raise NotImplementedError()
    children = property(get_children)

    def get_parents(self):
        raise NotImplementedError()
    parents = property(get_parents)

    def get_timestamp(self):
        raise NotImplementedError()
    timestamp = property(get_timestamp)

    def get_commit_message(self):
        raise NotImplementedError()
    commit_message = property(get_commit_message)

    def get_manifest(self):
        raise NotImplementedError()
    manifest = property(get_manifest)

    def get_files(self):
        raise NotImplementedError()
    files = property(get_files)

    def get_author(self):
        raise NotImplementedError()
    author = property(get_author)

    def get_diffs(self):
        raise NotImplementedError()
    diffs = property(get_diffs)


class MercurialCommit(Commit):
    def __init__(self, *args, **kwargs):
        super(MercurialCommit, self).__init__(*args, **kwargs)
        self.ctx = self.repo.ctx_for(self.id)

    def get_children(self):
        return map(self.repo.get_commit, map(self.repo.hexify, [
                    c._node for c in self.ctx.children()]))
    children = property(get_children)

    def get_parents(self):
        return map(self.repo.get_commit, map(self.repo.hexify, [
                    c._node for c in self.ctx.parents()]))
    parents = property(get_parents)

    def get_timestamp(self):
        import datetime, time
        # TODO: Should this be time.gmtime or time.localtime?
        return datetime.datetime(
            *time.gmtime(
                self.ctx.date()[0])[:6])
    timestamp = property(get_timestamp)

    def get_author(self):
        return self.ctx.user()
    author = property(get_author)

    def get_commit_message(self):
        return self.ctx.description()
    commit_message = property(get_commit_message)

    def get_files(self):
        return self.ctx.files()
    files = property(get_files)

    def get_manifest(self):
        return self.ctx.manifest()
    manifest = property(get_manifest)

    def get_diffs(self):
        from mercurial import mdiff, util, patch
        from repo_browser.integration import Diff

        ctx = self.ctx

        parent = ctx.parents()[0]
        parent_date = util.datestr(parent.date())
        this_date = util.datestr(ctx.date())
        diffopts = patch.diffopts(self.repo.repo.ui, untrusted=True)

        # Returns a tuple of modified, added, removed, deleted, unknown
        # TODO: look up in the api what FIXME* are
        modified, added, removed, deleted, unknown, FIXME, FIXME2 = \
            self.repo.repo.status(
            parent.node(),
            ctx.node(),)

        for modified_file in modified:
            filectx = ctx.filectx(modified_file)
            parent_filectx = parent.filectx(modified_file)
            this_data = filectx.data()
            parent_data = parent_filectx.data()
            yield Diff(mdiff.unidiff(parent_data, parent_date,
                                this_data,this_date,
                                modified_file, modified_file,
                                opts=diffopts))

        for added_file in added:
            filectx = ctx.filectx(added_file)
            this_data = filectx.data()
            yield Diff(mdiff.unidiff(
                None, parent_date, this_data, this_date,
                added_file, added_file, opts=diffopts))

        for removed_file in removed:
            parent_filectx = parent.filectx(removed_file)
            parent_data = parent_filectx.data()
            yield Diff(mdiff.unidiff(
                parent_data, parent_date, None, ctx.date(),
                removed_file, removed_file, opts=diffopts))
    diffs = property(get_diffs)


class GitCommit(Commit):
    def __init__(self, *args, **kwargs):
        super(GitCommit, self).__init__(*args, **kwargs)
        self.commit = self.repo.repo.commit(self.id)

    def get_children(self):
        raise NotImplementedError()
    children = property(get_children)

    def get_parents(self):
        return [self.repo.get_commit(commit.id) for commit in self.commit.parents]
    parents = property(get_parents)

    def get_timestamp(self):
        return self.commit.committed_date
    timestamp = property(get_timestamp)

    def get_commit_message(self):
        return self.commit.message
    commit_message = property(get_commit_message)

    def get_manifest(self):
        raise NotImplementedError()
    manifest = property(get_manifest)

    def get_files(self):
        raise NotImplementedError()
    files = property(get_files)

    def get_author(self):
        self.commit.committer
    author = property(get_author)

    def get_diffs(self):
        return self.commit.diffs
    diffs = property(get_diffs)

