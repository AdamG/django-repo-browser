from django.db import models


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
        max_length=255, primary_key=True,
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

    def __unicode__(self):
        return "%s(%s)" % (self.get_vcs_backend_display(),
                           self.connection_string)

    def __repr__(self):
        return "<%s>" % unicode(self)

    def get_backend(self):
        backend_module = getattr(
            __import__("repo_browser.backends.%s" % self.vcs_backend
                       ).backends,
                self.vcs_backend)
        BackendClass = getattr(backend_module,
                                "%sBackend" % self.vcs_backend.capitalize())
        return BackendClass(self.connection_string)

    @property
    def backend(self):
        if not hasattr(self, "_backend"):
            self._backend = self.get_backend()
        return self._backend


class Commit(models.Model):
    """A single commit in a repository

    This is a big denormalization, but can always be cleanly rebuilt
    from the on-disk repository and is needed for any type of
    searching or reporting.

    """

    repository = models.ForeignKey(Repository, related_name="commits")
    # Hash for DVCS, rev number for svn/cvs
    identifier = models.CharField(max_length=255, db_index=True)

    class Meta:
        unique_together = (
            ("identifier", "id"))
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
