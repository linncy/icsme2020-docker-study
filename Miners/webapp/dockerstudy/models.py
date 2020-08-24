from django.db import models
from django.utils import timezone
from postgres_copy import CopyManager
from django.contrib.postgres.fields import JSONField

# image Table
class Image(models.Model):
    image_name = models.CharField(max_length=512, blank=False, primary_key=True)
    publisher = models.CharField(max_length=64)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    short_description = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=32, blank=True, null=True)
    certification_status = models.CharField(max_length=32, blank=True, null=True)
    repository_type = models.CharField(max_length=32, blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    is_private = models.BooleanField(blank=True, null=True)
    is_automated = models.BooleanField(blank=True, null=True)
    star_count = models.IntegerField(blank=True, null=True)
    pull_count = models.IntegerField(blank=True, null=True)
    is_migrated = models.BooleanField(blank=True, null=True)
    has_starred = models.BooleanField(blank=True, null=True)
    full_description = models.TextField(blank=True, null=True)
    affiliation = models.CharField(max_length=32, blank=True, null=True)
    tags_count = models.IntegerField(blank=True, null=True)
    tags = JSONField(blank=True, null=True)
    builds_count = models.IntegerField(blank=True, null=True)
    builds = JSONField(blank=True, null=True)
    latest_dockerfile = models.TextField(blank=True, null=True)
    source_repo_id = models.IntegerField(blank=True, null=True)
    source_repo = models.CharField(max_length=512, blank=True, null=True)
    source_repo_location = models.CharField(max_length=16, blank=True, null=True, choices=[('GitHub', 'GitHub'), ('Bitbucket', 'Bitbucket')])
    source_repo_source = models.CharField(max_length=16, blank=True, null=True, choices=[('CI', 'CI'), ('NameMatch', 'NameMatch')])

    last_sent = models.DateTimeField(default=None, blank=True, null=True)
    complete = models.BooleanField(default=False, blank=True, null=True)
    error = models.BooleanField(default=False, blank=True, null=True)
    response = JSONField(blank=True, null=True)
    pagination = JSONField(blank=True, null=True, default=None)


    objects = CopyManager()

    def __unicode__(self):
        return self.image_name

    def __str__(self):
        return self.__unicode__()

    def update_last_sent(self):
        self.refresh_from_db()
        self.last_sent = timezone.now()
        self.save()

    def to_dict(self):
        return {
            'image_name': self.image_name,
            'publisher': self.publisher,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'short_description': self.short_description,
            'source': self.source,
            'certification_status': self.certification_status,
            'repository_type': self.repository_type,
            'status': self.status,
            'is_private': self.is_private,
            'is_automated': self.is_automated,
            'star_count': self.star_count,
            'pull_count': self.pull_count,
            'is_migrated': self.is_migrated,
            'has_starred': self.has_starred,
            'full_description': self.full_description,
            'affiliation': self.affiliation,
            'tags_count': self.tags_count,
            'tags': self.tags,
            'builds_count': self.builds_count,
            'builds': self.builds,
            'latest_dockerfile': self.latest_dockerfile,
            'source_repo_id': self.source_repo_id,
            'source_repo': self.source_repo,
            'source_repo_location': self.source_repo_location,
            'source_repo_source': self.source_repo_source
            }

    def to_task_dict(self):
        return {
            'image_name': self.image_name,
            'publisher': self.publisher,
            'pagination': self.pagination
        }

# tag Table
class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=512, blank=False, null=False)
    tag_name = models.CharField(max_length=512, blank=True, null=True)
    full_size = models.BigIntegerField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    last_updater_username = models.CharField(max_length=64, blank=True, null=True)
    last_updater_id = models.CharField(max_length=128, blank=True, null=True)
    creator_id = models.CharField(max_length=128, blank=True, null=True)
    tag_id = models.CharField(max_length=128, blank=True, null=True)
    architecture = models.CharField(max_length=64, blank=True, null=True)
    features = models.CharField(max_length=512, blank=True, null=True)
    variant = models.CharField(max_length=512, blank=True, null=True)
    digest_sha = models.CharField(max_length=128, blank=True, null=True)
    os = models.CharField(max_length=64, blank=True, null=True)
    os_features = models.CharField(max_length=512, blank=True, null=True)
    os_version = models.CharField(max_length=512, blank=True, null=True)
    image_size = models.BigIntegerField(blank=True, null=True)
    repository_id = models.CharField(max_length=128, blank=True, null=True)
    image_id = models.CharField(max_length=128, blank=True, null=True)
    v2 = models.BooleanField(blank=True, null=True)

    objects = CopyManager()

    def __unicode__(self):
        return self.image_name

    def __str__(self):
        return self.__unicode__()

    def get_id(self):
        return self.id

    def to_dict(self):
        return {
            'id' : self.id,
            'image_name': self.image_name,
            'tag_name': self.tag_name,
            'full_size': self.full_size,
            'last_updated': self.last_updated,
            'last_updater_username': self.last_updater_username,
            'last_updater_id': self.last_updater_id,
            'creator_id': self.creator_id,
            'tag_id': self.tag_id,
            'architecture': self.architecture,
            'features': self.features,
            'variant': self.variant,
            'digest_sha': self.digest_sha,
            'os': self.os,
            'os_features': self.os_features,
            'os_version': self.os_version,
            'image_size': self.image_size,
            'repository_id': self.repository_id,
            'image_id': self.image_id,
            'v2': self.v2
            }


# build Table
class Build(models.Model):
    id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=512, blank=False, null=False)
    build_tag = models.CharField(max_length=512, blank=True, null=True)
    commit_sha = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    source_repo = models.CharField(max_length=512, blank=True, null=True)
    state = models.CharField(max_length=32, blank=True, null=True)
    build_code = models.CharField(max_length=128, blank=True, null=True)
    user = models.CharField(max_length=64, blank=True, null=True)
    uuid = models.CharField(max_length=128, blank=True, null=True)

    objects = CopyManager()

    def __unicode__(self):
        return self.image_name

    def __str__(self):
        return self.__unicode__()

    def get_id(self):
        return self.id

    def to_dict(self):
        return {
            'id': self.id,
            'image_name': self.image_name,
            'build_tag': self.build_tag,
            'commit_sha': self.commit_sha,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'ended_at': self.ended_at,
            'source_repo': self.source_repo,
            'state': self.state,
            'build_code': self.build_code,
            'user': self.user,
            'uuid': self.uuid
            }


# dockerhub_user Table
class DockerHubUser(models.Model):
    username = models.CharField(max_length=64, primary_key=True)
    uid = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    full_name = models.CharField(max_length=512, blank=True, null=True)
    location = models.CharField(max_length=512, blank=True, null=True)
    company = models.CharField(max_length=512, blank=True, null=True)
    profile_url = models.CharField(max_length=512, blank=True, null=True)
    type = models.CharField(max_length=64, blank=True, null=True)

    objects = CopyManager()

    def __str__(self):
        return self.username

    def to_dict(self):
        return {
            'username': self.username,
            'uid': self.uid
        }

# github_user Table
class GitHubUser(models.Model):
    username = models.CharField(max_length=64, primary_key=True)
    user_id = models.CharField(max_length=64, blank=True, null=True)
    user_type = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    company = models.CharField(max_length=512, blank=True, null=True)
    blog = models.CharField(max_length=512, blank=True, null=True)
    location = models.CharField(max_length=512, blank=True, null=True)
    email = models.CharField(max_length=512, blank=True, null=True)
    hireable = models.CharField(max_length=512, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    public_repos = models.IntegerField(blank=True, null=True)
    public_gists = models.IntegerField(blank=True, null=True)
    followers = models.IntegerField(blank=True, null=True)
    following = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    objects = CopyManager()

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.__unicode__()

    def to_dict(self):
        return {
            'username': self.username,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'name': self.name,
            'company': self.company,
            'blog': self.blog,
            'location': self.location,
            'email': self.email,
            'hireable': self.hireable,
            'bio': self.bio,
            'public_repos': self.public_repos,
            'public_gists': self.public_gists,
            'followers': self.followers,
            'following': self.following,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            }

# bitbucket_user Table
class BitbucketUser(models.Model):
    username = models.CharField(max_length=64, primary_key=True)
    user_id = models.CharField(max_length=64, blank=True, null=True)
    user_type = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    objects = CopyManager()

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.__unicode__()

    def to_dict(self):
        return {
            'username': self.username,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'name': self.name,
            'created_at': self.created_at
            }

# repository Table
class Repository(models.Model):
    repo_id = models.AutoField(primary_key=True)
    repo_name = models.CharField(max_length=512, null=False, blank=False)
    full_name = models.CharField(max_length=512, null=True, blank=True)
    repo_location = models.CharField(max_length=16, null=False, blank=False, choices=[('GitHub', 'GitHub'), ('Bitbucket', 'Bitbucket')])
    owner = models.CharField(max_length=64, blank=True, null=True)
    owner_id = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    fork = models.BooleanField(blank=True, null=True)
    branches = JSONField(blank=True, null=True)
    tags = JSONField(blank=True, null=True)
    releases = JSONField(blank=True, null=True)
    languages = JSONField(blank=True, null=True)
    language = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    pushed_at = models.DateTimeField(blank=True, null=True)
    homepage = models.CharField(max_length=512, blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    commits_count = models.IntegerField(blank=True, null=True)
    commits = JSONField(blank=True, null=True)
    stargazers_count = models.IntegerField(blank=True, null=True)
    watchers_count = models.IntegerField(blank=True, null=True)
    has_issues = models.BooleanField(blank=True, null=True)
    has_projects = models.BooleanField(blank=True, null=True)
    has_downloads = models.BooleanField(blank=True, null=True)
    has_wiki = models.BooleanField(blank=True, null=True)
    has_pages = models.BooleanField(blank=True, null=True)
    forks_count = models.IntegerField(blank=True, null=True)
    archived = models.BooleanField(blank=True, null=True)
    disabled = models.BooleanField(blank=True, null=True)
    open_issues_count = models.IntegerField(blank=True, null=True)
    license = models.CharField(max_length=64, blank=True, null=True)
    forks = models.IntegerField(blank=True, null=True)
    open_issues = models.IntegerField(blank=True, null=True)
    watchers = models.IntegerField(blank=True, null=True)
    default_branch = models.CharField(max_length=512, blank=True, null=True)
    network_count = models.IntegerField(blank=True, null=True)
    subscribers_count = models.IntegerField(blank=True, null=True)

    objects = CopyManager()

    def __unicode__(self):
        return self.repo_name

    def __str__(self):
        return self.__unicode__()

    def get_id(self):
        return self.repo_id

    def get_name(self):
        return self.repo_name

    def get_location(self):
        return self.repo_location

    def to_dict(self):
        return {
            'repo_id': self.repo_id,
            'repo_name': self.repo_name,
            'repo_location': self.repo_location,
            'repo_source': self.repo_source,
            'owner': self.owner,
            'owner_id': self.owner_id,
            'description': self.description,
            'fork': self.fork,
            'tags': self.tags,
            'releases': self.releases,
            'languages': self.languages,
            'language': self.language,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'pushed_at': self.pushed_at,
            'homepage': self.homepage,
            'size': self.size,
            'commits_count': self.commits_count,
            'commits': self.commits,
            'stargazers_count': self.stargazers_count,
            'watchers_count': self.watchers_count,
            'has_issues': self.has_issues,
            'has_projects': self.has_projects,
            'has_downloads': self.has_downloads,
            'has_wiki': self.has_wiki,
            'has_pages': self.has_pages,
            'forks_count': self.forks_count,
            'archived': self.archived,
            'disabled': self.disabled,
            'open_issues_count': self.open_issues_count,
            'license': self.license,
            'forks': self.forks,
            'open_issues': self.open_issues,
            'watchers': self.watchers,
            'default_branch': self.default_branch,
            'network_count': self.network_count,
            'subscribers_count': self.subscribers_count
            }


# commit Table
class Commit(models.Model):
    commit_id = models.AutoField(primary_key = True)
    commit_sha = models.CharField(max_length=128)
    repo_id = models.IntegerField(blank=False, null=False)
    parents = JSONField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    author_username = models.CharField(max_length=64, blank=True, null=True)
    committer_username = models.CharField(max_length=64, blank=True, null=True)
    author_id = models.CharField(max_length=64, blank=True, null=True)
    committer_id = models.CharField(max_length=64, blank=True, null=True)
    repo_name = models.CharField(max_length=512, blank=False, null=False)
    repo_location = models.CharField(max_length=16, null=False, blank=False, choices=[('GitHub', 'GitHub'), ('Bitbucket', 'Bitbucket')])
    stats_total = models.IntegerField(blank=True, null=True)
    stats_additions = models.IntegerField(blank=True, null=True)
    stats_deletions = models.IntegerField(blank=True, null=True)
    changed_file_count = models.IntegerField(blank=True, null=True)
    changed_files = JSONField(blank=True, null=True)
    author_committed_at = models.DateTimeField(blank=True, null=True)
    committer_committed_at = models.DateTimeField(blank=True, null=True)

    objects = CopyManager()

    def __unicode__(self):
        return self.repo_name

    def __str__(self):
        return self.__unicode__()

    def get_id(self):
        return self.commit_id

    def to_dict(self):
        return {
            'commit_id': self.commit_id,
            'commit_sha': self.commit_sha,
            'repo_id': self.repo_id,
            'parents': self.parents,
            'message': self.message,
            'author_username': self.author_username,
            'committer_username': self.committer_username,
            'author_id': self.author_id,
            'committer_id': self.committer_id,
            'repo_name': self.repo_name,
            'repo_location': self.repo_location,
            'stats_total': self.stats_total,
            'stats_additions': self.stats_additions,
            'stats_deletions': self.stats_deletions,
            'changed_file_count': self.changed_file_count,
            'changed_files': self.changed_files,
            'author_committed_at': self.author_committed_at,
            'committer_committed_at': self.committer_committed_at
            }

# dockerfile Table
class Dockerfile(models.Model):
    dockerfile_id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=512, blank=False, null=False)
    content = models.TextField(blank=True, null=True)
    filename = models.CharField(max_length=512, blank=True, null=True)
    path = models.CharField(max_length=512, blank=True, null=True)
    repo_id = models.IntegerField(blank=False, null=False)
    repo_name = models.CharField(max_length=512, blank=False, null=False)
    repo_location = models.CharField(max_length=16, null=False, blank=False, choices=[('GitHub', 'GitHub'), ('Bitbucket', 'Bitbucket')])
    commit_sha = models.CharField(max_length=128, blank=False, null=False)
    diff = models.TextField(blank=True, null=True)
    author_committed_at = models.DateTimeField(blank=True, null=True)
    committer_committed_at = models.DateTimeField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    objects = CopyManager()

    def __unicode__(self):
        return self.image_name

    def __str__(self):
        return self.__unicode__()

    def get_id(self):
        return self.dockerfile_id

    def to_dict(self):
        return {
            'dockerfile_id': self.dockerfile_id,
            'image_name': self.image_name,
            'content': self.content,
            'filename': self.filename,
            'path': self.path,
            'repo_id': self.repo_id,
            'repo_name': self.repo_name,
            'repo_location': self.repo_location,
            'commit_sha': self.commit_sha,
            'diff': self.diff
            }

# changed_file Table
class ChangedFile(models.Model):
    changedfile_id = models.AutoField(primary_key=True)
    repo_id = models.IntegerField(blank=True, null=True)
    commit_sha = models.CharField(max_length=128)
    filename = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=64, blank=True, null=True)
    additions_count = models.IntegerField(blank=True, null=True)
    deletions_count = models.IntegerField(blank=True, null=True)
    changes_count = models.IntegerField(blank=True, null=True)
    patch = models.TextField(blank=True, null=True)

    objects = CopyManager()

    def __unicode__(self):
        return self.changedfile_id

    def get_id(self):
        return self.changedfile_id

    def __str__(self):
        return self.__unicode__()

    def to_dict(self):
        return {
            'changedfile_id': self.changedfile_id,
            'commit_sha': self.commit_sha,
            'filename': self.filename,
            'status': self.status,
            'additions_count': self.additions_count,
            'deletions_count': self.deletions_count,
            'changes_count': self.changes_count,
            'patch': self.patch
            }

# image_name_crawler_task Table
class ImageNameCrawlerTask(models.Model):
    keyword = models.CharField(max_length=32, primary_key=True)
    last_sent = models.DateTimeField(default=None, blank=True, null=True)
    complete = models.BooleanField(default=False)
    image_count = models.IntegerField(null=True)
    error_response = models.TextField(blank=True, null=True)    

    objects = CopyManager()

    def update_last_sent(self):
        self.refresh_from_db()
        self.last_sent = timezone.now()
        self.save()

    def __str__(self):
        return self.keyword

    def to_dict(self):
        return {
            'keyword': self.keyword,
            'last_sent': self.last_sent,
            'complete': self.complete,
            'image_count': self.image_count,
            'error_response': self.error_response
        }

    def to_task_dict(self):
        return {
            'keyword': self.keyword
        }

# token Table used for the token pool
class AuthToken(models.Model):
    token = models.CharField(max_length=128, primary_key=True)
    in_use = models.BooleanField(default=False, blank=False, null=False)
    last_sent = models.DateTimeField(default=None, blank=True, null=True)
    last_update = models.DateTimeField(default=None, blank=True, null=True)
    limit_remaining = models.IntegerField(default=None, blank=True, null=True)
    limit_reset_time = models.DateTimeField(default=None, blank=True, null=True)
    token_type = models.CharField(max_length=16, default=None, blank=False, null=True) # GitHub or Bitbucket

    objects = CopyManager()

    def update_last_sent(self):
        self.refresh_from_db()
        self.last_sent = timezone.now()
        self.save()

    def claim_in_use(self):
        self.refresh_from_db()
        self.in_use = True
        self.save()

    def __str__(self):
        return self.token

    def to_dict(self):
        return {
            'token':self.token,
            'in_use':self.in_use,
            'last_sent':self.last_sent,
            'last_update':self.last_update,
            'limit_remaining':self.limit_remaining,
            'limit_reset_time':self.limit_reset_time,
            'token_type':self.token_type
        }