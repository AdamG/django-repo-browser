from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
import django.core.paginator

import repo_browser.models


def list_repositories(request):
    "List the available repositories"

    repositories = repo_browser.models.Repository.objects.filter(
        show_on_index=True)
    return direct_to_template(request, "repo_browser/list_repositories.html")


def repository_details(request, repository_slug):
    "Summary detail page for a repository"
    repository = get_object_or_404(
        repo_browser.models.Repository,
        slug=str(repository_slug))
    return direct_to_template(request, "repo_browser/repository_details.html",
                              {"repository": repository})


def commitlist(request, repository_slug):
    "View a set of commits in a repo"

    repository = get_object_or_404(
        repo_browser.models.Repository,
        slug=str(repository_slug))
    commit_paginator = django.core.paginator.Paginator(
        repository.commits.all(),
        int(request.GET.get("per_page", 50)))
    commits = commit_paginator.page(int(request.GET.get("page", 1)))

    return direct_to_template(request, "repo_browser/commit_list.html",
                              {"repository": repository,
                               "commits": commits})


def view_commit(request, repository_slug, commit_identifier):
    "View a single commit"

    repository = get_object_or_404(
        repo_browser.models.Repository,
        slug=str(repository_slug))
    commit = get_object_or_404(
        repository.commits.all(),
        identifier=str(commit_identifier))

    return direct_to_template(request, "repo_browser/commit_details.html",
                              {"repository": repository,
                               "commit": commit})


