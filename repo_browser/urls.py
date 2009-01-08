from django.conf.urls.defaults import *

urlpatterns = patterns(
    'repo_browser.views',
    url('^$', 'list_repositories', {}, 'repo-browser-list-repositories'),
    url('^([-\w]+)/$', 'repository_details', {}, 'repo-browser-repository-details'),
    url('^([-\w]+)/commits/$', 'commitlist', {}, 'repo-browser-commit-list'),
    url('^([-\w]+)/([-\w]+)/$', 'view_commit', {}, 'repo-browser-view-commit'),
    url('^([-\w]+)/([-\w]+)/manifest/$', 'manifest', {}, 'repo-browser-manifest'),
    url('^([-\w]+)/([-\w]+)/manifest/(.+)$', 'manifest'),
)
