from django.contrib import admin

import repo_browser.models

class RepositoryAdmin(admin.ModelAdmin):
    fieldsets = [
            (None, {"fields":
                        ("name", "description", "connection_string",
                         "slug", "show_on_index", "vcs_backend")})]


admin.site.register(repo_browser.models.Repository, RepositoryAdmin)
