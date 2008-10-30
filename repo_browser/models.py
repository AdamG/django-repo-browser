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
        return "%s(%r)" % (self.get_vcs_backend_display(),
                           self.connection_string)

    def __repr__(self):
        return "<%s>" % unicode(self)

    def get_absolute_url(self):
        return self.urls.view

    def get_backend(self):
        import repo_browser.backends
        BackendClass = getattr(repo_browser.backends,
                                "%sBackend" % self.vcs_backend.capitalize())
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

    def full_sync(self):
        """Starting with root and traversing, completely sync the repository

        Should be safe to run multiple times

        """
        pending_commits = [self.backend.root()]
        for commit_id in pending_commits:
            pending_commits.extend(self.backend.children_for(commit_id))
            try:
                commit = self.commits.get(identifier=commit_id)
            except Commit.DoesNotExist:
                commit = Commit(repository=self, identifier=commit_id)

            commit.timestamp = self.backend.datetime_for(commit_id)
            commit.author = self.backend.author_for(commit_id)
            commit.message = self.backend.commit_message_for(commit_id)


class Commit(models.Model):
    """A single commit in a repository

    This is a big denormalization, but can always be cleanly rebuilt
    from the on-disk repository and is needed for any type of
    searching or reporting.

    Everything that should be queryable should be denormalized 'onto'
    instances of Commit. Timestamps, authors, commit messages; maybe
    even diffs (although probably not - dealing with large diffs could
    get hairy)

    """

    repository = models.ForeignKey(Repository, related_name="commits")
    # Hash for DVCS, rev number for svn/cvs
    identifier = models.CharField(max_length=255, db_index=True)
    timestamp = models.DateTimeField()
    message = models.TextField()
    author = models.CharField(max_length=255)

    class Meta:
        unique_together = (
            ("identifier", "id"))
        ordering = ("-timestamp",)
        db_table = "repobrowser_commit"


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
