from django.db import models

from repo_browser.decorators import attrproperty


class Repository(models.Model):
    "A repository"

    name = models.CharField(
        max_length=255,
        help_text="A short name for the repository used in templates "
        "and listings.")
    description = models.TextField(
        help_text="A short description shown on the repository details page")
    connection_string = models.CharField(
        max_length=255,
        help_text="For Mercurial, Git, and Bazaar, the full filesystem path "
        "to the repository.")
    slug = models.SlugField(
        max_length=255, db_index=True,
        help_text="An identifier to use in the URL for this repository")
    show_on_index = models.BooleanField(
        default=True,
        help_text="Whether this repository shows up on the repository index")

    MERCURIAL = 'mercurial'
    CVS = 'cvs'
    SUBVERSION = 'subversion'
    REMOTE_SUBVERSION = 'subversion-remote'
    GIT = 'git'
    VCS_BACKEND_CHOICES = (
        (MERCURIAL, "Mercurial"),
        (CVS, 'CVS'),
        (SUBVERSION, 'Subversion'),
        (REMOTE_SUBVERSION, 'Subversion - Remote'),
        (GIT, 'Git'),
        )
    vcs_backend = models.CharField(
        max_length=128, choices=VCS_BACKEND_CHOICES)

    class Meta:
        db_table = "repobrowser_repository"
        ordering = ("name",)
        verbose_name_plural = "repositories"

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<repo_browser.Repository %s>" % unicode(self)

    def get_absolute_url(self):
        return self.urls.view
    absolute_url = property(get_absolute_url)

    def get_backend(self):
        import repo_browser.backends
        BackendClass = repo_browser.backends.BACKENDS[self.vcs_backend]
        return BackendClass(self.connection_string)

    @property
    def backend(self):
        if not hasattr(self, "_backend"):
            self._backend = self.get_backend()
        return self._backend

    @attrproperty
    def urls(self, name):
        from django.core.urlresolvers import reverse

        if name == "view":
            return reverse("repo-browser-repository-details", args=[self.slug])
        if name == "commitlist":
            return reverse("repo-browser-commit-list", args=[self.slug])

    def sync_from(self, revisions):
        "A starting from ``revisions``, traverse and sync the repository."
        pending_commits = list(revisions)
        for commit_id in pending_commits:
            for child in self.backend.children_for(commit_id):
                if child not in pending_commits:
                    pending_commits.append(child)
            try:
                commit = self.commits.get(identifier=commit_id)
            except Commit.DoesNotExist:
                commit = Commit(repository=self, identifier=commit_id)

            commit.timestamp = self.backend.timestamp_for(commit_id)
            commit.author = self.backend.author_for(commit_id)
            commit.message = self.backend.commit_message_for(commit_id)
            commit.save()

    def full_sync(self):
        "Starting with the initial revision, completely sync the repository"
        self.sync_from([self.backend.root()])

    def incremental_sync(self):
        "Starting with all known heads, sync the repository"
        self.sync_from(self.backend.heads())


class Commit(models.Model):
    """A single commit in a repository

    This is a big denormalization, but can always be cleanly rebuilt
    from the on-disk repository and is needed for any type of
    searching or reporting.

    Everything that should be queryable should be denormalized 'onto'
    instances of Commit. Timestamps, authors, commit messages; maybe
    even diffs (although probably not - dealing with large diffs could
    get hairy)

    Having commits as models also allows for things like
    django-threadedcomments on specific commits.

    """

    repository = models.ForeignKey(Repository, related_name="commits")
    # Hash for DVCS, rev number for svn/cvs
    identifier = models.CharField(max_length=255, db_index=True)
    timestamp = models.DateTimeField()
    message = models.TextField()
    author = models.CharField(max_length=255)

    class Meta:
        unique_together = (
            ("identifier", "repository"))
        ordering = ("-timestamp",)
        db_table = "repobrowser_commit"

    def __unicode__(self):
        return self.identifier

    def __repr__(self):
        return "<repo_browser.Commit %s>" % unicode(self)

    @attrproperty
    def urls(self, name):
        from django.core.urlresolvers import reverse

        if name == "view":
            return reverse("repo-browser-view-commit",
                           args=[self.repository.slug, self.identifier])
        elif name == "diff":
            return "%s?format=diff" % reverse(
                "repo-browser-view-commit",
                args=[self.repository.slug, self.identifier])
        if name == "manifest":
            return reverse("repo-browser-manifest",
                           args=[self.repository.slug, self.identifier])

    @property
    def diffs(self):
        return self.repository.backend.diffs_for(self.identifier)

    @property
    def diff(self):
        return "\n".join(self.diffs)

    @property
    def files(self):
        return self.repository.backend.files_for(self.identifier)

    @property
    def manifest(self):
        return sorted(self.repository.backend.manifest_for(self.identifier).keys())


class CommitRelation(models.Model):
    "A relation between a parent and child commit"

    # Because of graph-based DVCSs, I can't simply use a .parent FK.
    parent = models.ForeignKey(Commit, related_name="child_relations")
    child = models.ForeignKey(Commit, related_name="parent_relations")

    class Meta:
        unique_together = (
            ("parent", "child"))
        db_table = "repobrowser_commit_relation"

    def __unicode__(self):
        return "%s -> %s" % (self.parent.identifier, self.child.identifier)

    def __repr__(self):
        return "<repo_browser.CommitRelation %s>" % unicode(self)
