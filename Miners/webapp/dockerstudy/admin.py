from django.contrib import admin

from . import models

class ImageAdmin(admin.ModelAdmin):
    list_display = ['image_name','last_sent', 'complete', 'error', 'response', 'pagination', 'created_at', 'updated_at', 'short_description', 'pull_count', 'tags_count', 'builds_count', 'latest_dockerfile', 'source_repo_id', 'source_repo', 'source_repo_location', 'source_repo_source', 'tags', 'builds']

class DockerHubUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'uid', 'created_at', 'full_name', 'location', 'company', 'profile_url']

class GitHubUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'user_id', 'user_type', 'name', 'company', 'blog', 'location', 'email', 'hireable', 'bio', 'public_repos', 'public_gists', 'followers', 'following', 'created_at', 'updated_at']

class BitbucketUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'user_id', 'user_type', 'name', 'created_at']

class ImageNameCrawlerTaskAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'last_sent', 'complete', 'image_count', 'error_response']

class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ['token', 'in_use', 'last_sent', 'last_update', 'limit_remaining', 'limit_reset_time', 'token_type']

class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_name', 'tag_name', 'full_size', 'last_updated', 'last_updater_username', 'last_updater_id', 'creator_id', 'tag_id', 'architecture', 'features', 'variant', 'digest_sha', 'os', 'os_features', 'os_version', 'image_size', 'repository_id', 'image_id', 'v2']

class BuildAdmin(admin.ModelAdmin):
    list_display = ['id' ,'image_name', 'build_tag', 'commit_sha', 'created_at', 'started_at', 'ended_at', 'source_repo', 'state', 'build_code', 'user', 'uuid']

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['repo_id', 'repo_name', 'repo_location', 'owner', 'owner_id', 'description', 'fork', 'tags', 'releases', 'languages', 'language', 'created_at', 'updated_at', 'pushed_at', 'homepage', 'size', 'commits_count', 'commits', 'stargazers_count', 'watchers_count', 'has_issues', 'has_projects', 'has_downloads', 'has_wiki', 'has_pages', 'forks_count', 'archived', 'disabled', 'open_issues_count', 'license', 'forks', 'open_issues', 'watchers', 'default_branch', 'network_count', 'subscribers_count']

class CommitAdmin(admin.ModelAdmin):
    list_display = ['commit_id', 'commit_sha', 'repo_id', 'parents', 'message', 'author_username', 'committer_username', 'author_id', 'committer_id', 'repo_name', 'repo_location', 'stats_total', 'stats_additions', 'stats_deletions', 'changed_file_count', 'changed_files', 'author_committed_at', 'committer_committed_at']

class DockerfileAdmin(admin.ModelAdmin):
    list_display = ['dockerfile_id', 'image_name', 'content', 'filename', 'path', 'repo_id', 'repo_name', 'repo_location', 'commit_sha', 'diff']

class ChangedFileAdmin(admin.ModelAdmin):
    list_display = ['changedfile_id', 'repo_id', 'commit_sha', 'filename', 'status', 'additions_count', 'deletions_count', 'changes_count', 'patch']

admin.site.register(models.Image, ImageAdmin)
admin.site.register(models.DockerHubUser, DockerHubUserAdmin)
admin.site.register(models.GitHubUser, GitHubUserAdmin)
admin.site.register(models.BitbucketUser, BitbucketUserAdmin)
admin.site.register(models.ImageNameCrawlerTask, ImageNameCrawlerTaskAdmin)
admin.site.register(models.AuthToken, AuthTokenAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Build, BuildAdmin)
admin.site.register(models.Repository, RepositoryAdmin)
admin.site.register(models.Commit, CommitAdmin)
admin.site.register(models.Dockerfile, DockerfileAdmin)
admin.site.register(models.ChangedFile, ChangedFileAdmin)