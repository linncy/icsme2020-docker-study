import requests
import json
import os
import time
import pytz
from datetime import datetime, timedelta
from fake_headers import Headers
from requests.auth import HTTPBasicAuth
import string
import itertools


class APIClient(object):
    def __init__(self, **config_options):
        self.tokenpool_query_interval = 10
        self.tokenpool_session = requests.Session()
        self.api_session = requests.Session()
        self.__dict__.update(**config_options)
        self.APIPoolURL = os.getenv('APIPOOL')
        if (self.APIPoolURL == None):
            self.APIPoolURL = 'http://$your-webapp-url:8000/authtoken/'
        if (os.path.exists('token.json')):
            with open('token.json', 'r') as jsonfile:
                previous_token = json.load(jsonfile)
                previous_token['in_use'] = False
                self.tokenpool_session.post(self.APIPoolURL, json=previous_token)
            os.remove("token.json")
        if (self.apiname == 'GitHub'):
            while True:
                try:
                    self.token = self.tokenpool_session.get(self.APIPoolURL + 'github').json()
                    if (self.token['last_update'] == None):
                        self.token['limit_remaining'] = 5000
                        self.token['limit_reset_time'] = (datetime.utcnow() + timedelta(minutes=5)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")
                        break
                    if (time.mktime(datetime.strptime(self.token['limit_reset_time'],
                                                      "%Y-%m-%dT%H:%M:%SZ").timetuple())) <= time.mktime(
                            datetime.strptime(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                              "%Y-%m-%dT%H:%M:%SZ").timetuple()):
                        self.token['limit_remaining'] = 5000
                        self.token['limit_reset_time'] = (datetime.utcnow() + timedelta(minutes=5)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")
                        break
                    if (self.token['limit_remaining'] > 0):
                        break
                except:
                    time.sleep(self.tokenpool_query_interval)
            self.api_session.headers['Authorization'] = 'token {}'.format(self.token['token'])
        elif (self.apiname == 'Bitbucket'):
            while True:
                try:
                    self.token = self.tokenpool_session.get(self.APIPoolURL + 'bitbucket').json()
                    if (self.token['last_update'] == None):
                        self.token['limit_remaining'] = 960
                        self.token['limit_reset_time'] = (datetime.utcnow() + timedelta(hours=1)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")
                        break
                    if (time.mktime(datetime.strptime(self.token['limit_reset_time'],
                                                      "%Y-%m-%dT%H:%M:%SZ").timetuple())) <= time.mktime(
                            datetime.strptime(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                              "%Y-%m-%dT%H:%M:%SZ").timetuple()):
                        self.token['limit_remaining'] = 960
                        self.token['limit_reset_time'] = (datetime.utcnow() + timedelta(hours=1)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")
                        break

                    if (self.token['limit_remaining'] > 0):
                        break
                except:
                    time.sleep(self.tokenpool_query_interval)
        with open('token.json', 'w') as jsonfile:
            json.dump(self.token, jsonfile)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.token['in_use'] = False
        self.tokenpool_session.post(self.APIPoolURL, json=self.token)
        os.remove("token.json")

    def callAPI(self, url):
        if (self.apiname == 'GitHub'):
            self.call_GitHub_API(url)
        elif (self.apiname == 'Bitbucket'):
            self.call_Bitbucket_API(url)

    def call_GitHub_API(self, url, separate_limit=False):
        if not separate_limit:
            time.sleep(0.5)
        else:
            time.sleep(2)
        while True:
            if (self.token['limit_remaining'] == 0 or time.mktime(datetime.strptime(self.token['limit_reset_time'],
                                                      "%Y-%m-%dT%H:%M:%SZ").timetuple())) < time.mktime(
                            datetime.strptime(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                              "%Y-%m-%dT%H:%M:%SZ").timetuple()):
                self.token['in_use'] = False
                self.token['last_update'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                self.tokenpool_session.post(self.APIPoolURL, json=self.token)
                os.remove("token.json")
                self.__init__(apiname=self.apiname)
                continue
            res = self.api_session.get(url)
            headers = res.headers
            try:
                if not separate_limit:
                    self.token['limit_remaining'] = int(headers['X-RateLimit-Remaining'])
                    self.token['limit_reset_time'] = datetime.fromtimestamp(int(headers['X-RateLimit-Reset']), tz = pytz.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ")
            except:
                self.token['limit_remaining'] = 0
            self.token['last_update'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            with open('token.json', 'w') as jsonfile:
                json.dump(self.token, jsonfile)
            if headers.get('Status') == '403 Forbidden':
                try:
                    if res.json().get('message') == 'Sorry. Your account was suspended.':
                        self.token['limit_remaining'] = 0
                        self.token['suspended'] = True
                except:
                    pass
                continue
            return (res, headers)

    def call_Bitbucket_API(self, url):
        time.sleep(0.5)
        while True:
            if (self.token['limit_remaining'] == 0 or time.mktime(datetime.strptime(self.token['limit_reset_time'],
                                                      "%Y-%m-%dT%H:%M:%SZ").timetuple())) < time.mktime(
                            datetime.strptime(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                              "%Y-%m-%dT%H:%M:%SZ").timetuple()):
                self.token['in_use'] = False
                self.token['last_update'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                self.tokenpool_session.post(self.APIPoolURL, json=self.token)
                os.remove("token.json")
                self.__init__(apiname=self.apiname)
                continue
            res = self.api_session.get(url, auth=HTTPBasicAuth(self.token['token'].split(':')[0], self.token['token'].split(':')[-1]))
            headers = res.headers
            self.token['limit_remaining'] -= 1
            self.token['last_update'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            with open('token.json', 'w') as jsonfile:
                json.dump(self.token, jsonfile)
            return (res, headers)

class SourceRepoMiner(object):
    def __init__(self, **config_options):
        self.__dict__.update(**config_options)

        self.WebAppURL = 'http://$your-webapp-url:8000'
        self.ImageAndRepoInfoCrawlerTaskURL = self.WebAppURL + '/image_and_repo_info_crawler_task/'
        self.RepositoryPOSTURL = self.WebAppURL + '/repository'
        self.RepositoryQueryURL = self.WebAppURL + '/query_repository/'

        self.DockerHubSearchAPIURL = "https://hub.docker.com/api/content/v1/products/search"
        self.DockerHubSourceRepoQueryURL = 'https://hub.docker.com/api/build/v1/source/?image={}'
        self.DockerHubUserRepoAPIURL = 'https://hub.docker.com/v2/repositories/{}/?page_size=25&page=1&ordering=last_updated'
        self.DockerHubImageInfoAPIURL = 'https://hub.docker.com/v2/repositories/{}'
        self.DockerHubImageTagAPIURL = 'https://hub.docker.com/v2/repositories/{}/tags?page_size=100'
        self.DockerHubImageBuildAPIURL = 'https://hub.docker.com/api/audit/v1/build/?include_related=true&limit=10&object=%2Fapi%2Frepo%2Fv1%2Frepository%2F{}%2F&offset=0'
        self.DockerHubImageDockerfileAPIURL = 'https://hub.docker.com/v2/repositories/{}/dockerfile'
        self.DockerHubUserInfoAPIURL = 'https://hub.docker.com/v2/users/{}' #username
        self.GitHubAPIRepoInfoAPIURL = 'https://api.github.com/repos/{}'
        self.GitHubAPIRepoTagsAPIURL = 'https://api.github.com/repos/{}/tags'
        self.GitHubAPIRepoReleasesAPIURL = 'https://api.github.com/repos/{}/releases'
        self.GitHubAPIRepoBranchesAPIURL = 'https://api.github.com/repos/{}/branches'
        self.GitHubAPIRepoLanguagesAPIURL = 'https://api.github.com/repos/{}/languages'
        self.GitHubAPISearchDockerfilesURL = 'https://api.github.com/search/code?q=+in:file+language:dockerfile+repo:{}'
        self.GitHubFileHistoryAPIURL = 'https://api.github.com/repos/{}/commits?path={}' # Repo_name, file path
        self.GitHubFileHistoryStartFromAPIURL = 'https://api.github.com/repos/{}/commits?path={}&sha={}' # Repo_name, file path, commit_sha  (start from and include)
        self.GitHubFileContentAPIURL = 'https://raw.githubusercontent.com/{}/{}/{}'  # Repo_name, commit_sha, file_path
        self.GitHubCommitInfoAPIURL = 'https://api.github.com/repos/{}/commits/{}'  # Repo_name, commit_sha
        self.GitHubAPIRepoCommitsURL = 'https://api.github.com/repos/{}/commits'
        self.GitHubCommitInfoAPIURL = 'https://api.github.com/repos/{}/commits/{}'  # Repo_name, commit_sha
        self.GitHubUserInfoAPIURL = 'https://api.github.com/users/{}'  # username
        self.GitHubRepoCommitCountAPIURL = 'https://api.github.com/repos/{}/commits?per_page=1'  # full_name
        self.GitHubAPIRepoCommitsStartFromURL = 'https://api.github.com/repos/{}/commits?sha={}' # full_name, commit_sha (start from and include)


        self.BitbucketAPIRepoInfoAPIURL = 'https://api.bitbucket.org/2.0/repositories/{}' # repo_name
        self.BitbucketFileHistoryAPIURL = 'https://api.bitbucket.org/2.0/repositories/{}/filehistory/master/Dockerfile' # repo_name
        self.BitbucketFileContentAPIURL = 'https://api.bitbucket.org/2.0/repositories/{}/src/{}/Dockerfile'  # repo_name, commit_sha
        self.BitbucketAPIRepoCommitsURL = 'https://api.bitbucket.org/2.0/repositories/{}/commits' # repo_name
        self.BitbucketCommitInfoAPIURL = 'https://api.bitbucket.org/2.0/repositories/{}/diffstat/{}' # repo_name, commit_sha
        self.BitbucketUserInfoAPIURL = 'https://api.bitbucket.org/2.0/users/{}'  # username

        self.HEADER = {
            'Host': 'hub.docker.com',
            'Connection': 'keep-alive',
            'Search-Version': 'v3',
            'Accept': '*/*',
            'Sec-Fetch-Dest': 'empty',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
            'Content-Type': 'application/json',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en'
        }

        self.commit_count_filter = os.getenv('FILTER')
        if(self.commit_count_filter == 'ON'):
            self.commit_count_filter = True
        else:
            self.commit_count_filter = False

    def header_generator(self):
        headers = self.HEADER
        headers['User-Agent'] = Headers(headers=False).generate()['User-Agent']
        return headers

    def get_next_page_link_from_headers(self, headers):
        try:
            url_list_from_headers = requests.utils.parse_header_links(headers['Link'].rstrip('>').replace('>,<', ',<'))
            return [item['url'] for item in url_list_from_headers if item['rel'] == 'next'][0]
        except:
            return None

    # Get Tags -----------------------------------------------------------------------------------
    def taginfo_parser(self, dic, image_name):
        tag = {'image_name': image_name}
        tag['tag_name'] = dic.get('name')
        tag['full_size'] = dic.get('full_size')
        tag['last_updated'] = dic.get('last_updated')
        tag['last_updater_username'] = dic.get('last_updater_username')
        tag['last_updater_id'] = dic.get('last_updater')
        tag['creator_id'] = dic.get('creator')
        if (dic.get('images') != [] and dic.get('images') != None):
            tag['architecture'] = dic.get('images')[0].get('architecture')
            tag['features'] = dic.get('images')[0].get('features')
            tag['variant'] = dic.get('images')[0].get('variant')
            tag['digest_sha'] = dic.get('images')[0].get('digest')
            tag['os'] = dic.get('images')[0].get('os')
            tag['os_features'] = dic.get('images')[0].get('os_features')
            tag['os_version'] = dic.get('images')[0].get('os_version')
            tag['image_size'] = dic.get('images')[0].get('size')
        tag['repository_id'] = dic.get('repository')
        tag['image_id'] = dic.get('id')
        tag['v2'] = dic.get('v2')
        tag = {key: tag[key] for key in tag.keys() if tag[key] != None}
        return tag

    def get_tags(self, image_name):
        query_session = requests.Session()
        query_session.headers.update(self.header_generator())
        tags = []
        try:
            res = query_session.get(self.DockerHubImageTagAPIURL.format(image_name)).json()
            tags += [self.taginfo_parser(tag, image_name) for tag in res['results']]
            while (res['next'] != None):
                time.sleep(1)
                res = query_session.get(res['next']).json()
                tags += [self.taginfo_parser(tag, image_name) for tag in res['results']]
            return {'is_successful': True, 'results': tags}
        except Exception as e:
            return {'is_successful': False, 'results': str(e)}

    # Get Builds -----------------------------------------------------------------------------------
    def buildinfo_parser(self, dic, image_name):
        build = {'image_name': image_name}
        build['build_tag'] = dic.get('build_tag')
        build['commit_sha'] = dic.get('commit')

        build['created_at'] = datetime.strptime(dic.get('created'), '%a, %d %b %Y %H:%M:%S +0000').strftime(
            "%Y-%m-%dT%H:%M:%SZ") if dic.get('created')!=None else None
        build['started_at'] = datetime.strptime(dic.get('start_date'), '%a, %d %b %Y %H:%M:%S +0000').strftime(
            "%Y-%m-%dT%H:%M:%SZ") if dic.get('start_date')!=None else None
        build['ended_at'] = datetime.strptime(dic.get('end_date'), '%a, %d %b %Y %H:%M:%S +0000').strftime(
            "%Y-%m-%dT%H:%M:%SZ") if dic.get('end_date')!=None else None
        build['source_repo'] = dic.get('source_repo')
        build['state'] = dic.get('state')
        build['build_code'] = dic.get('build_code')
        build['user'] = dic.get('user')
        build['uuid'] = dic.get('uuid')
        build = {key: build[key] for key in build.keys() if build[key] != None}
        return build

    def get_builds(self, image_name):
        query_session = requests.Session()
        query_session.headers.update(self.header_generator())
        builds = []
        try:
            res = query_session.get(self.DockerHubImageBuildAPIURL.format(image_name)).json()
            builds += [self.buildinfo_parser(build, image_name) for build in res.get('objects', [])]
            while (res.get('meta', {}).get('next') != None):
                time.sleep(1)
                res = query_session.get('https://hub.docker.com' + res.get('meta').get('next')).json()
                builds += [self.buildinfo_parser(build, image_name) for build in res.get('objects')]
            return {'is_successful': True, 'results': builds}
        except Exception as e:
            return {'is_successful': True, 'results': builds}

    # Get Image Info -----------------------------------------------------------------------------------
    def imageinfo_parser(self, dic, image_name):
        info = {'image_name': image_name}
        info['publisher'] = dic.get('user')
        info['updated_at'] = dic.get('last_updated')
        info['short_description'] = dic.get('description')
        info['repository_type'] = dic.get('repository_type')
        info['status'] = dic.get('status')
        info['is_private'] = dic.get('is_private')
        info['is_automated'] = dic.get('is_automated')
        info['star_count'] = dic.get('star_count')
        info['pull_count'] = dic.get('pull_count')
        info['is_migrated'] = dic.get('is_migrated')
        info['has_starred'] = dic.get('has_starred')
        info['full_description'] = dic.get('full_description')
        info['affiliation'] = dic.get('affiliation')
        info = {key: info[key] for key in info.keys() if info[key] != None}
        return info

    def get_image_info(self, image_name):
        query_session = requests.Session()
        query_session.headers.update(self.header_generator())
        try:
            res = query_session.get(self.DockerHubImageInfoAPIURL.format(image_name)).json()
            if ('{}/{}'.format(res.get('user'), res.get('name'))) == image_name:
                info = self.imageinfo_parser(res, image_name)
                try:
                    res = query_session.get(self.DockerHubImageDockerfileAPIURL.format(image_name)).json()
                    if (res.get('contents') != None):
                        info['latest_dockerfile'] = res.get('contents')
                except:
                    pass
                return {'is_successful': True, 'results': info}
            else:
                return {'is_successful': True, 'results': None}
        except Exception as e:
            return {'is_successful': False, 'results': str(e)}

    # Get DockerHub userinfo -----------------------------------------------------------------------------------
    def dockerhub_userinfo_parser(self, dic, username):
        info = {'username': username}
        info['uid'] = dic.get('id')
        info['full_name'] = dic.get('full_name')
        info['location'] = dic.get('location')
        info['company'] = dic.get('company')
        info['created_at'] = dic.get('date_joined')
        info['type'] = dic.get('type')
        info['profile_url'] = dic.get('profile_url')
        info = {key: info[key] for key in info.keys() if info[key] != None and info[key] != ''}
        return info

    def get_dockerhub_user_info(self, username):
        query_session = requests.Session()
        query_session.headers.update(self.header_generator())
        try:
            res = query_session.get(self.DockerHubUserInfoAPIURL.format(username))
            if(res.text != '"Not Found"'):
                info = self.dockerhub_userinfo_parser(res.json(), username)
                return {'is_successful': True, 'results': info}
            else:
                return {'is_successful': True, 'results': {'username': username}}
        except Exception as e:
            return {'is_successful': False, 'results': str(e)}

    # Get Source Repo (CI Link) -----------------------------------------------------------------------------------
    def get_source_repo_name(self, image_name):
        query_session = requests.Session()
        query_session.headers.update(self.header_generator())
        try:
            res = query_session.get(self.DockerHubSourceRepoQueryURL.format(image_name)).json()
            if (res.get('objects') != None and res.get('objects') != []):
                source_repo_location = res.get('objects')[0].get('provider')
                source_repo_name = '{}/{}'.format(res.get('objects')[0].get('owner'),
                                                  res.get('objects')[0].get('repository'))
                source_repo_location = 'GitHub' if source_repo_location == 'Github' else source_repo_location
                return {'is_successful': True, 'results': (source_repo_location, source_repo_name)}
            else:
                return {'is_successful': True, 'results': None}
        except Exception as e:
            return {'is_successful': False, 'results': str(e)}

    # Get GitHub Repo Info -----------------------------------------------------------------------------------
    def githubrepoinfo_parser(self, dic, repo_name):
        info = {'repo_name': repo_name, 'repo_location': 'GitHub'}
        info['full_name'] = dic.get('full_name')
        info['owner'] = dic.get('owner', {}).get('login') if dic.get('owner')!=None else None
        info['owner_id'] = dic.get('owner', {}).get('id') if dic.get('owner')!=None else None
        info['description'] = dic.get('description')
        info['fork'] = dic.get('fork')
        info['language'] = dic.get('language')
        info['created_at'] = dic.get('created_at')
        info['updated_at'] = dic.get('updated_at')
        info['pushed_at'] = dic.get('pushed_at')
        info['homepage'] = dic.get('homepage')
        info['size'] = dic.get('size')
        info['stargazers_count'] = dic.get('stargazers_count')
        info['watchers_count'] = dic.get('watchers_count')
        info['has_issues'] = dic.get('has_issues')
        info['has_projects'] = dic.get('has_projects')
        info['has_downloads'] = dic.get('has_downloads')
        info['has_wiki'] = dic.get('has_wiki')
        info['has_pages'] = dic.get('has_pages')
        info['forks_count'] = dic.get('forks_count')
        info['mirror_url'] = dic.get('mirror_url')
        info['archived'] = dic.get('archived')
        info['disabled'] = dic.get('disabled')
        info['open_issues_count'] = dic.get('open_issues_count')
        info['license'] = dic.get('license', {}).get('name') if dic.get('license')!=None else None
        info['forks'] = dic.get('forks')
        info['open_issues'] = dic.get('open_issues')
        info['watchers'] = dic.get('watchers')
        info['default_branch'] = dic.get('default_branch')
        info['network_count'] = dic.get('network_count')
        info['subscribers_count'] = dic.get('subscribers_count')
        info = {key: info[key] for key in info.keys() if info[key] != None}
        return info

    def get_github_repo_info(self, repo_name):
        with APIClient(apiname='GitHub') as api_client:
            try:
                res = api_client.call_GitHub_API(self.GitHubAPIRepoInfoAPIURL.format(repo_name))[0].json()
                if(res.get('message')=='Not Found'):
                    return {'is_successful': True, 'results': None}
                info = self.githubrepoinfo_parser(res, repo_name)
                # tags
                try:
                    res = api_client.call_GitHub_API(self.GitHubAPIRepoTagsAPIURL.format(repo_name))
                    tags_list = []
                    tags = res[0].json()
                    tags_list += tags
                    next_page_url = self.get_next_page_link_from_headers(res[1])
                    while next_page_url != None:
                        res = api_client.call_GitHub_API(next_page_url)
                        tags = res[0].json()
                        tags_list += tags
                        next_page_url = self.get_next_page_link_from_headers(res[1])
                    if (tags_list != []):
                        tags_list = [{'name': item.get('name'), 'commit_sha': item.get('commit').get('sha')} for item in
                                     tags_list]
                        info['tags'] = tags_list
                except:
                    pass
                # releases
                try:
                    res = api_client.call_GitHub_API(self.GitHubAPIRepoReleasesAPIURL.format(repo_name))
                    releases_list = []
                    releases = res[0].json()
                    releases_list += releases
                    next_page_url = self.get_next_page_link_from_headers(res[1])
                    while next_page_url != None:
                        res = api_client.call_GitHub_API(next_page_url)
                        releases = res[0].json()
                        releases_list += releases
                        next_page_url = self.get_next_page_link_from_headers(res[1])
                    if (releases_list != []):
                        releases_list = [{'name': item.get('name'), 'tag_name': item.get('tag_name'), 'id': item.get('id'),
                                          'target_commitish': item.get('target_commitish'), 'body': item.get('body'),
                                          'draft': item.get('draft'), 'prerelease': item.get('prerelease'),
                                          'created_at': item.get('created_at'), 'published_at': item.get('published_at'),
                                          'author_username': item.get('author', {}).get('login'),
                                          'author_id': item.get('author', {}).get('id')} for item in releases_list]
                        info['releases'] = releases_list
                except:
                    pass
                # branches
                try:
                    res = api_client.call_GitHub_API(self.GitHubAPIRepoBranchesAPIURL.format(repo_name))
                    branches_list = []
                    branches = res[0].json()
                    branches_list += branches
                    next_page_url = self.get_next_page_link_from_headers(res[1])
                    while next_page_url != None:
                        res = api_client.call_GitHub_API(next_page_url)
                        branches = res[0].json()
                        branches_list += branches
                        next_page_url = self.get_next_page_link_from_headers(res[1])
                    if (branches_list != []):
                        branches_list = [{'name': item.get('name'), 'commit_sha': item.get('commit').get('sha')} for
                                         item in branches_list]
                        info['branches'] = branches_list
                except:
                    pass
                # languages
                try:
                    res = api_client.call_GitHub_API(self.GitHubAPIRepoLanguagesAPIURL.format(repo_name))
                    languages = res[0].json()
                    info['languages'] = languages
                except:
                    pass
                return {'is_successful': True, 'results': info}
            except Exception as e:
                return {'is_successful': False, 'results': str(e)}

    # Get GitHub Repo Commit count -----------------------------------------------------------------------------------
    def get_github_repo_commit_count(self, full_name):
        with APIClient(apiname='GitHub') as api_client:
            try:
                headers = api_client.call_GitHub_API(self.GitHubRepoCommitCountAPIURL.format(full_name))[1]
                url_list_from_headers = requests.utils.parse_header_links(headers['Link'].rstrip('>').replace('>,<', ',<'))
                commit_count = int([item['url'] for item in url_list_from_headers if item['rel'] == 'last'][0].split('page=')[-1])
                return {'is_successful': True, 'results': commit_count}
            except Exception as e:
                return {'is_successful': False, 'results': str(e)}

    # Get Bitbucket Repo Info -----------------------------------------------------------------------------------
    def bitbucketrepoinfo_parser(self, dic, repo_name):
        info = {'repo_name': repo_name, 'repo_location': 'Bitbucket'}
        info['full_name'] = dic.get('full_name')
        info['owner'] = dic.get('owner', {}).get('nickname')
        info['owner_id'] = dic.get('owner', {}).get('account_id')
        info['description'] = dic.get('description')
        info['language'] = dic.get('language')
        info['created_at'] = datetime.strptime(dic.get('created_on'), '%Y-%m-%dT%H:%M:%S.%f+00:00').strftime("%Y-%m-%dT%H:%M:%SZ") if dic.get('created_on')!=None else None
        info['updated_at'] = datetime.strptime(dic.get('updated_on'), '%Y-%m-%dT%H:%M:%S.%f+00:00').strftime("%Y-%m-%dT%H:%M:%SZ") if dic.get('created_on')!=None else None
        info['homepage'] = dic.get('website')
        info['size'] = dic.get('size')
        info['has_issues'] = dic.get('has_issues')
        info['has_wiki'] = dic.get('has_wiki')
        info['default_branch'] = dic.get('mainbranch', {}).get('name')
        info = {key: info[key] for key in info.keys() if info[key] != None and info[key] != ''}
        return info

    def get_bitbucket_repo_info(self, repo_name):
        with APIClient(apiname='Bitbucket') as api_client:
            try:
                info_res = api_client.call_Bitbucket_API(self.BitbucketAPIRepoInfoAPIURL.format(repo_name))[0]
                if 'Access denied.' in info_res.text or 'not found' in info_res.text:
                    return {'is_successful': True, 'results': None}

                info_res = info_res.json()
                info = self.bitbucketrepoinfo_parser(info_res, repo_name)
                # tags
                if(info_res.get('links', {}).get('tags', {}).get('href') != None):
                    try:
                        res = api_client.call_Bitbucket_API(info_res.get('links', {}).get('tags', {}).get('href'))[0].json()
                        tags_list = []
                        tags = res.get('values')
                        tags_list += tags
                        next_page_url = res.get('next')
                        while next_page_url != None:
                            res = api_client.call_Bitbucket_API(next_page_url)[0].json()
                            tags = res.get('values')
                            tags_list += tags
                            next_page_url = res.get('next')
                        if (tags_list != []):
                            tags_list = [{'name': item.get('name'), 'commit_sha': item.get('target').get('hash')} for item in tags_list]
                            info['tags'] = tags_list
                    except:
                        pass
                # branches
                if(info_res.get('links', {}).get('branches', {}).get('href') != None):
                    try:
                        res = api_client.call_Bitbucket_API(info_res.get('links', {}).get('branches', {}).get('href'))[0].json()
                        branches_list = []
                        branches = res.get('values')
                        branches_list += branches
                        next_page_url = res.get('next')
                        while next_page_url != None:
                            res = api_client.call_Bitbucket_API(next_page_url)[0].json()
                            branches = res.get('values')
                            branches_list += branches
                            next_page_url = res.get('next')
                        if (branches_list != []):
                            branches_list = [{'name': item.get('name'), 'commit_sha': item.get('target').get('hash')} for item in branches_list]
                            info['branches'] = branches_list
                    except:
                        pass
                # forks count
                if(info_res.get('links', {}).get('forks', {}).get('href') != None):
                    try:
                        res = api_client.call_Bitbucket_API(info_res.get('links', {}).get('forks', {}).get('href'))[0].json()
                        forks_list = []
                        forks = res.get('values')
                        forks_list += forks
                        next_page_url = res.get('next')
                        while next_page_url != None:
                            res = api_client.call_Bitbucket_API(next_page_url)[0].json()
                            forks = res.get('values')
                            forks_list += forks
                            next_page_url = res.get('next')
                        info['forks'] = len(forks_list)
                    except:
                        pass

                # watchers
                if(info_res.get('links', {}).get('watchers', {}).get('href') != None):
                    try:
                        res = api_client.call_Bitbucket_API(info_res.get('links', {}).get('watchers', {}).get('href'))[0].json()
                        watchers_list = []
                        watchers = res.get('values')
                        watchers_list += watchers
                        next_page_url = res.get('next')
                        while next_page_url != None:
                            res = api_client.call_Bitbucket_API(next_page_url)[0].json()
                            watchers = res.get('values')
                            watchers_list += watchers
                            next_page_url = res.get('next')
                        info['watchers'] = len(watchers_list)
                    except:
                        pass
                return {'is_successful': True, 'results': info}
            except Exception as e:
                return {'is_successful': False, 'results': str(e)}

    # Get all Dockerfiles in the GitHub Repo -----------------------------------------------------------------------------------
    def get_dockerfiles_github_repo(self, image_name, full_name, pagination=None):
        with APIClient(apiname='GitHub') as api_client:
            try:
                res = api_client.call_GitHub_API(self.GitHubAPISearchDockerfilesURL.format(full_name), separate_limit=True)[0]
                dockerfiles_path_list = []
                if pagination is None:
                    dockerfiles_path = res.json().get('items', [])
                    dockerfiles_path = [{'name':item.get('name'), 'path':item.get('path')} for item in dockerfiles_path]
                    dockerfiles_path_list += dockerfiles_path
                    next_page_url = self.get_next_page_link_from_headers(res.headers)
                    while next_page_url is not None:
                        res = api_client.call_GitHub_API(next_page_url, separate_limit=True)[0]
                        dockerfiles_path = res.json().get('items')
                        dockerfiles_path_list += dockerfiles_path
                        next_page_url = self.get_next_page_link_from_headers(res.headers)
                else:
                    dockerfiles_path_list = pagination['dockerfiles_path_list']
                dockerfiles_list = []
                pagination_indicator = False
                for search_result in dockerfiles_path_list:
                    commits_list = []
                    if pagination is None and search_result.get('pagination') is None:
                        res = api_client.call_GitHub_API(self.GitHubFileHistoryAPIURL.format(full_name, search_result['path']))
                    elif pagination is not None and search_result.get('pagination') is not None:
                        res = api_client.call_GitHub_API(self.GitHubFileHistoryStartFromAPIURL.format(full_name, search_result['path'], search_result.get('pagination').get('start_from_sha')))
                    elif pagination is not None and search_result.get('pagination') is None:
                        continue
                    commits = res[0].json()
                    commits = [{'commit_sha': commit.get('sha'),
                                'author_committed_at': commit.get('commit').get('author').get('date'),
                                'committer_committed_at': commit.get('commit').get('committer').get('date'),
                                'message': commit.get('commit').get('message')} for commit in commits]
                    if pagination is None and search_result.get('pagination') is None:
                        commits_list += commits
                    elif pagination is not None and search_result.get('pagination') is not None:
                        commits_list += commits[1:]
                    page_counter = 1
                    next_page_url = self.get_next_page_link_from_headers(res[1])
                    while next_page_url is not None and page_counter<=10:
                        res = api_client.call_GitHub_API(next_page_url)
                        commits = res[0].json()
                        commits = [{'commit_sha': commit.get('sha'),
                                    'author_committed_at': commit.get('commit').get('author').get('date'),
                                    'committer_committed_at': commit.get('commit').get('committer').get('date'),
                                    'message': commit.get('commit').get('message')} for commit in commits]
                        commits_list += commits
                        next_page_url = self.get_next_page_link_from_headers(res[1])
                        page_counter += 1
                    if page_counter > 10 and next_page_url is not None:
                        search_result['pagination'] = {'start_from_sha':commits[-1]['commit_sha']}
                        pagination_indicator = True
                    else:
                        search_result.pop('pagination', None)

                    for commit in commits_list:
                        content = requests.get(self.GitHubFileContentAPIURL.format(full_name, commit.get('commit_sha'),
                                                                                   search_result['path'])).text
                        dockerfile = {'image_name': image_name, 'content': content, 'filename': search_result['name'],
                                      'path': search_result['path'],
                                      'repo_name': full_name, 'repo_location': 'GitHub',
                                      'commit_sha': commit['commit_sha'],
                                      'author_committed_at': commit['author_committed_at'],
                                      'committer_committed_at': commit['committer_committed_at'],
                                      'message': commit['message']}
                        dockerfiles_list.append(dockerfile)
                if pagination_indicator:
                    return {'is_successful': True, 'results': dockerfiles_list, 'pagination':{'dockerfiles_path_list':dockerfiles_path_list, 'image_name':image_name, 'full_name':full_name}}
                else:
                    return {'is_successful': True, 'results': dockerfiles_list}
            except Exception as e:
                return {'is_successful': False, 'results': str(e)}

    # Get all Dockerfiles in the Bitbucket Repo -----------------------------------------------------------------------------------
    def get_dockerfiles_bitbucket_repo(self, image_name, full_name):
        with APIClient(apiname='Bitbucket') as api_client:
            try:
                res = api_client.call_Bitbucket_API(self.BitbucketFileHistoryAPIURL.format(full_name))[0].json()
                if 'No such file' in res.get('error', {}).get('message', ''):
                    return {'is_successful': True, 'results': []}
                commits_list = []
                commits = res.get('values')
                commits_list += commits
                next_page_url = res.get('next')
                while next_page_url != None:
                    res = api_client.call_Bitbucket_API(next_page_url)[0].json()
                    commits = res.get('values')
                    commits_list += commits
                    next_page_url = res.get('next')
                commits_list = [{'image_name': image_name, 'filename':'Dockerfile', 'path':item.get('path'), 'repo_name':full_name,
                                 'repo_location':'Bitbucket', 'commit_sha':item.get('commit', {}).get('hash')} for item in commits_list]
                for commit in commits_list:
                    dockerfile_content = api_client.call_Bitbucket_API(self.BitbucketFileContentAPIURL.format(full_name, commit['commit_sha']))[0].text
                    commit['content'] = dockerfile_content
                return {'is_successful': True, 'results': commits_list}
            except Exception as e:
                return {'is_successful': False, 'results': str(e)}

    # Get all commits in the GitHub Repo -----------------------------------------------------------------------------------
    def github_commit_parser(self, dic, full_name):
        commit = {'commit_sha': dic['sha']}
        commit['parents'] = [parent.get('sha') for parent in dic.get('parents')]
        commit['message'] = (dic.get('commit') or {}).get('message')
        commit['repo_name'] = full_name
        commit['repo_location'] = 'GitHub'
        commit['author_committed_at'] = ((dic.get('commit') or {}).get('author') or {}).get('date')
        commit['committer_committed_at'] = ((dic.get('commit') or {}).get('committer') or {}).get('date')
        commit = {key: commit[key] for key in commit.keys() if commit[key] != None}
        return commit

    def github_commit_info_parser(self, dic):
        commit_info = {}
        commit_info['author_username'] = (dic.get('author') or {}).get('login')
        commit_info['committer_username'] = (dic.get('committer') or {}).get('login')
        commit_info['author_id'] = (dic.get('author') or {}).get('id')
        commit_info['committer_id'] = (dic.get('committer') or {}).get('id')
        commit_info['stats_total'] = (dic.get('stats') or {}).get('total')
        commit_info['stats_additions'] = (dic.get('stats') or {}).get('additions')
        commit_info['stats_deletions'] = (dic.get('stats') or {}).get('deletions')
        commit_info['changed_file_count'] = len(dic.get('files')) if (dic.get('files')!=None) else None
        commit_info['changed_files'] = dic.get('files')
        commit_info = {key: commit_info[key] for key in commit_info.keys() if commit_info[key] != None}
        return commit_info

    def github_changed_file_parser(self, lis, commit_sha, save_all_patches=True, patch_saving_files_list=[]):
        changed_files = []
        for file in lis:
            afile = {'commit_sha': commit_sha}
            afile['filename'] = file.get('filename')
            afile['status'] = file.get('status')
            afile['additions_count'] = file.get('additions')
            afile['deletions_count'] = file.get('deletions')
            afile['changes_count'] = file.get('changes')
            if save_all_patches:
                afile['patch'] = file.get('patch')
            else:
                if afile['filename'] in patch_saving_files_list:
                    afile['patch'] = file.get('patch')
            afile = {key: afile[key] for key in afile.keys() if afile[key] != None}
            if file != {}:
                changed_files.append(afile)
        return changed_files

    def get_commits_github_repo(self, full_name, save_all_patches=True, patch_saving_files_list=[], pagination=None):  # if save_all_patches is false, only save the patch of files whose path is in the patch_saving_files_list
        with APIClient(apiname='GitHub') as api_client:
            try:
                if pagination is None:
                    res = api_client.call_GitHub_API(self.GitHubAPIRepoCommitsURL.format(full_name))
                else:
                    res = api_client.call_GitHub_API(self.GitHubAPIRepoCommitsStartFromURL.format(full_name, pagination['start_from_sha']))
                commits_list = []
                commits = res[0].json()
                if type(commits) == dict:
                    if commits.get('message') == 'Git Repository is empty.':
                        return {'is_successful': True, 'results': []}
                if pagination is None:
                    commits_list += commits
                else:
                    commits_list += commits[1:]
                page_counter = 1
                pagination_indicator = False
                next_page_url = self.get_next_page_link_from_headers(res[1])
                while next_page_url != None and page_counter<=10:
                    res = api_client.call_GitHub_API(next_page_url)
                    commits = res[0].json()
                    commits_list += commits
                    next_page_url = self.get_next_page_link_from_headers(res[1])
                    page_counter += 1
                if next_page_url != None and page_counter>10:
                    pagination_indicator = True
                    last_sha = commits[-1]['sha']
                commits_list = [self.github_commit_parser(commit, full_name) for commit in commits_list]
                if pagination is not None:
                    patch_saving_files_list = pagination['patch_saving_files_list']
                for commit in commits_list:
                    res = api_client.call_GitHub_API(
                        self.GitHubCommitInfoAPIURL.format(full_name, commit['commit_sha']))
                    commit_info = self.github_commit_info_parser(res[0].json())
                    commit.update(commit_info)
                    commit['changed_files'] = self.github_changed_file_parser(commit.get('changed_files', []), commit['commit_sha'], save_all_patches, patch_saving_files_list)
                if pagination_indicator:
                    return {'is_successful': True, 'results': commits_list, 'pagination':{'start_from_sha':last_sha, 'patch_saving_files_list':patch_saving_files_list, 'full_name':full_name}}
                else:
                    return {'is_successful': True, 'results': commits_list}
            except Exception as e:
                return {'is_successful': False, 'results': str(e)}

    # Get all commits in the Bitbucket Repo -----------------------------------------------------------------------------------
    def bitbucket_commit_parser(self, dic, full_name):
        commit = {'commit_sha': dic['hash']}
        commit['parents'] = [parent.get('hash') for parent in dic.get('parents')]
        commit['message'] = dic.get('message')
        commit['repo_name'] = full_name
        commit['repo_location'] = 'Bitbucket'
        commit['author_committed_at'] = datetime.strptime(dic.get('date'), '%Y-%m-%dT%H:%M:%S+00:00').strftime("%Y-%m-%dT%H:%M:%SZ") if dic.get('date')!=None else None
        commit['committer_committed_at'] = commit['author_committed_at']
        commit['author_username'] = commit.get('author', {}).get('user', {}).get('nickname')
        commit['committer_username'] = commit.get('author', {}).get('user', {}).get('nickname')
        commit['author_id'] = commit.get('author', {}).get('user', {}).get('account_id')
        commit['committer_id'] = commit['author_id']
        commit = {key: commit[key] for key in commit.keys() if commit[key] != None}
        return commit

    def bitbucket_commit_info_parser(self, lis, commit_sha):
        commit_info = {}
        commit_info['changed_file_count'] = len(lis) if (lis!=None) else None
        commit_info['changed_files'] = self.bitbucket_changed_file_parser(lis, commit_sha)
        commit_info['stats_total'] = sum([file.get('changes_count') for file in commit_info['changed_files'] if file.get('changes_count')!=None])
        commit_info['stats_additions'] = sum([file.get('additions_count') for file in commit_info['changed_files'] if file.get('additions_count')!=None])
        commit_info['stats_deletions'] = sum([file.get('deletions_count') for file in commit_info['changed_files'] if file.get('deletions_count')!=None])
        commit_info = {key: commit_info[key] for key in commit_info.keys() if commit_info[key] != None}
        return commit_info

    def bitbucket_changed_file_parser(self, lis, commit_sha):
        changed_files = []
        for file in lis:
            afile = {'commit_sha': commit_sha}
            if(file.get('new') != None):
                afile['filename'] = file.get('new', {}).get('path')
            else:
                afile['filename'] = file.get('old', {}).get('path')
            afile['status'] = file.get('status')
            afile['additions_count'] = file.get('lines_added')
            afile['deletions_count'] = file.get('lines_removed')
            if(file.get('lines_removed')!=None and file.get('lines_added')!=None):
                afile['changes_count'] = file.get('lines_added') + file.get('lines_removed')
            changed_files.append(afile)
        return changed_files

    def get_commits_bitbucket_repo(self, full_name):
        with APIClient(apiname='Bitbucket') as api_client:
            try:
                res = api_client.call_Bitbucket_API(self.BitbucketAPIRepoCommitsURL.format(full_name))[0].json()
                commits_list = []
                commits = res.get('values')
                commits_list += commits
                next_page_url = res.get('next')
                while next_page_url != None:
                    res = api_client.call_Bitbucket_API(next_page_url)[0].json()
                    commits = res.get('values')
                    commits_list += commits
                    next_page_url = res.get('next')
                commits_list = [self.bitbucket_commit_parser(commit, full_name) for commit in commits_list]

                for commit in commits_list:
                    res = api_client.call_Bitbucket_API(self.BitbucketCommitInfoAPIURL.format(full_name, commit['commit_sha']))[0].json()
                    commit_info_list = []
                    commit_info = res.get('values')
                    commit_info_list += commit_info
                    next_page_url = res.get('url')
                    while next_page_url!=None:
                        res = api_client.call_Bitbucket_API(
                            self.BitbucketCommitInfoAPIURL.format(full_name, commit['commit_sha']))[0].json()
                        commit_info = res.get('values')
                        commit_info_list += commit_info
                        next_page_url = res.get('url')
                    commit_info_list = self.bitbucket_commit_info_parser(commit_info_list, commit['commit_sha'])
                    commit.update(commit_info_list)
                return {'is_successful': True, 'results': commits_list}
            except Exception as e:
                return {'is_successful': False, 'results': str(e)}


    # Get GitHub userinfo -----------------------------------------------------------------------------------
    def github_userinfo_parser(self, dic, username):
        info = {'username': username}
        info['user_id'] = dic.get('id')
        info['user_type'] = dic.get('type')
        info['name'] = dic.get('name')
        info['company'] = dic.get('company')
        info['blog'] = dic.get('blog')
        info['location'] = dic.get('location')
        info['email'] = dic.get('email')
        info['hireable'] = dic.get('hireable')
        info['bio'] = dic.get('bio')
        info['public_repos'] = dic.get('public_repos')
        info['public_gists'] = dic.get('public_gists')
        info['followers'] = dic.get('followers')
        info['following'] = dic.get('following')
        info['created_at'] = dic.get('created_at')
        info['updated_at'] = dic.get('updated_at')
        info = {key: info[key] for key in info.keys() if info[key] != None}
        return info

    def get_github_user_info(self, username):
        with APIClient(apiname='GitHub') as api_client:
            try:
                res = api_client.call_GitHub_API(self.GitHubUserInfoAPIURL.format(username))
                info = self.github_userinfo_parser(res[0].json(), username)
                return {'is_successful': True, 'results': info}
            except Exception as e:
                return {'is_successful': False, 'results': str(e)}

    # Get Bitbucket userinfo -----------------------------------------------------------------------------------
    def bitbucket_userinfo_parser(self, dic, user_id):
        info = {'user_id': user_id}
        info['username'] = dic.get('nickname')
        info['user_type'] = dic.get('type') if dic.get('type')!='error' else None
        info['name'] = dic.get('display_name')
        info['created_at'] = datetime.strptime(dic.get('created_on'), '%Y-%m-%dT%H:%M:%S.%f+00:00').strftime("%Y-%m-%dT%H:%M:%SZ") if dic.get('created_on')!=None else None
        info = {key: info[key] for key in info.keys() if info[key] != None}
        return info

    def get_bitbucket_user_info(self, user_id):
        with APIClient(apiname='Bitbucket') as api_client:
            try:
                res = api_client.call_Bitbucket_API(self.BitbucketUserInfoAPIURL.format(user_id))[0].json()
                info = self.bitbucket_userinfo_parser(res, user_id)
                return {'is_successful': True, 'results': info}
            except Exception as e:
                return {'is_successful': False, 'results': str(e)}

    def crawler_task(self):
        webapp_session = requests.Session()
        res = webapp_session.get(self.ImageAndRepoInfoCrawlerTaskURL).json()
        with open('task.json', 'w') as jsonfile:
            json.dump(res, jsonfile)
        image_name = res['image_name']
        publisher = res['publisher']
        pagination_task = res.get('pagination_task', False)

        results = {'image_name':{'is_successful':True, 'results':image_name}}

        if pagination_task:
            if (self.commit_count_filter == True):
                return
            results['pagination_task'] = {'is_successful':True, 'results':True}
            pagination = res['pagination']
            if pagination.get('repo_dockerfiles') is not None:
                results['repo_dockerfiles'] = self.get_dockerfiles_github_repo(image_name=image_name,
                                                                               full_name=pagination['repo_dockerfiles']['full_name'],
                                                                               pagination=pagination.get('repo_dockerfiles'))
            if pagination.get('repo_commits') is not None:
                results['repo_commits'] = self.get_commits_github_repo(full_name=pagination['repo_commits']['full_name'],
                                                                       save_all_patches=False,
                                                                       patch_saving_files_list=pagination['repo_commits']['patch_saving_files_list'],
                                                                       pagination=pagination.get('repo_commits'))
            r = requests.post(self.ImageAndRepoInfoCrawlerTaskURL, json=results)
            return

        results['image_info'] = self.get_image_info(image_name)
        if(results['image_info']['is_successful'] == True and results['image_info']['results'] == None):
            r = requests.post(self.ImageAndRepoInfoCrawlerTaskURL, json=results)
            return
        time.sleep(1)
        results['image_tags'] = self.get_tags(image_name)
        time.sleep(1)
        results['image_builds'] = self.get_builds(image_name)
        time.sleep(1)
        results['dockerhub_user_info'] = self.get_dockerhub_user_info(publisher)
        time.sleep(1)
        results['source_repo_name'] = self.get_source_repo_name(image_name) #(source_repo_location, source_repo_name)
        error = {key:results[key]['results'] for key in results.keys() if results[key]['is_successful'] == False}
        if(error!={}):
            r = requests.post(self.ImageAndRepoInfoCrawlerTaskURL, json=results)
            time.sleep(10)
            return
        if(results['source_repo_name']['is_successful'] == True and results['source_repo_name'].get('results') != None):
            # CI Repo
            repo_location, repo_name = results['source_repo_name']['results']
            results['image_info']['results']['source_repo_source'] = 'CI'
            repo_in_db = requests.get(self.RepositoryQueryURL + repo_location + '/' + repo_name).json()
            if(repo_in_db.get('repo_id') is not None):
                results['image_info']['results']['source_repo_id'] = repo_in_db.get('repo_id')
                results['image_info']['results']['source_repo'] = repo_name
                results['image_info']['results']['source_repo_location'] = repo_location
                r = requests.post(self.ImageAndRepoInfoCrawlerTaskURL, json=results)
                return
            if(repo_location=='GitHub'): # if the image has a GitHub source repo
                results['repo_info'] = self.get_github_repo_info(repo_name)
                if(results['repo_info']['is_successful'] == True and results['repo_info']['results']!=None):
                    full_name = results['repo_info']['results'].get('full_name') if results['repo_info']['results'].get('full_name')!=None else repo_name
                    repo_owner = results['repo_info']['results'].get('owner') if results['repo_info']['results'].get('owner')!=None else repo_name.split('/')[0]
                    if (self.commit_count_filter == True):
                        commit_count = self.get_github_repo_commit_count(full_name)
                        if(commit_count['is_successful']==False or commit_count['results']>300):
                            return
                    results['repo_dockerfiles'] = self.get_dockerfiles_github_repo(image_name, full_name)
                    dockerfiles_path_list = list(set([item['path'] for item in results['repo_dockerfiles']['results']])) if results['repo_dockerfiles']['is_successful'] else []
                    results['repo_commits'] = self.get_commits_github_repo(full_name, save_all_patches=False, patch_saving_files_list=dockerfiles_path_list)
                    results['repo_user_info'] = self.get_github_user_info(repo_owner)
            elif(repo_location=='Bitbucket'):
                results['repo_info'] = self.get_bitbucket_repo_info(repo_name)
                if (results['repo_info']['is_successful'] == True and results['repo_info']['results'] != None):
                    full_name = results['repo_info']['results'].get('full_name') if results['repo_info']['results'].get('full_name')!=None else repo_name
                    repo_owner = results['repo_info']['results'].get('owner') if results['repo_info']['results'].get('owner')!=None else repo_name.split('/')[0]
                    repo_owner_id = results['repo_info']['results'].get('owner_id')
                    results['repo_dockerfiles'] = self.get_dockerfiles_bitbucket_repo(image_name, full_name)
                    results['repo_commits'] = self.get_commits_bitbucket_repo(full_name)
                    if(repo_owner_id!=None):
                        results['repo_user_info'] = self.get_bitbucket_user_info(repo_owner_id)
        elif(results['source_repo_name']['is_successful'] == True and results['source_repo_name'].get('results') == None):
            #Name Match Repo
            results['repo_info'] = self.get_github_repo_info(image_name) # Try GitHub repo using the image name
            if (results['repo_info']['is_successful'] == True and results['repo_info']['results'] != None):
                results['image_info']['results']['source_repo_source'] = 'NameMatch'
                repo_in_db = requests.get(self.RepositoryQueryURL + 'GitHub' + '/' + image_name).json()
                if (repo_in_db.get('repo_id') is not None):
                    results['image_info']['results']['source_repo_id'] = repo_in_db.get('repo_id')
                    results['image_info']['results']['source_repo'] = image_name
                    results['image_info']['results']['source_repo_location'] = 'GitHub'
                    r = requests.post(self.ImageAndRepoInfoCrawlerTaskURL, json=results)
                    return
                full_name = results['repo_info']['results'].get('full_name') if results['repo_info']['results'].get('full_name') != None else image_name
                repo_owner = results['repo_info']['results'].get('owner') if results['repo_info']['results'].get('owner') != None else image_name.split('/')[0]
                if(self.commit_count_filter == True):
                    commit_count = self.get_github_repo_commit_count(full_name)
                    if (commit_count['is_successful'] == False or commit_count['results'] > 300):
                        return
                results['repo_dockerfiles'] = self.get_dockerfiles_github_repo(image_name, full_name)
                dockerfiles_path_list = list(set([item['path'] for item in results['repo_dockerfiles']['results']])) if results['repo_dockerfiles']['is_successful'] else []
                if(dockerfiles_path_list != []):
                    results['repo_commits'] = self.get_commits_github_repo(full_name, save_all_patches=False, patch_saving_files_list=dockerfiles_path_list)
                    results['repo_user_info'] = self.get_github_user_info(repo_owner)
                    results['source_repo_name']['results'] = ('GitHub', full_name)
            else: # Try Bitbucket repo using the image name
                results['repo_info'] = self.get_bitbucket_repo_info(image_name)
                if (results['repo_info']['is_successful'] == True and results['repo_info']['results'] != None):
                    results['image_info']['results']['source_repo_source'] = 'NameMatch'
                    repo_in_db = requests.get(self.RepositoryQueryURL + 'Bitbucket' + '/' + image_name).json()
                    if (repo_in_db.get('repo_id') is not None):
                        results['image_info']['results']['source_repo_id'] = repo_in_db.get('repo_id')
                        results['image_info']['results']['source_repo'] = image_name
                        results['image_info']['results']['source_repo_location'] = 'Bitbucket'
                        r = requests.post(self.ImageAndRepoInfoCrawlerTaskURL, json=results)
                        return
                    full_name = results['repo_info']['results'].get('full_name') if results['repo_info']['results'].get('full_name')!=None else image_name
                    repo_owner = results['repo_info']['results'].get('owner') if results['repo_info']['results'].get('owner')!=None else image_name.split('/')[0]
                    repo_owner_id = results['repo_info']['results'].get('owner_id')
                    results['repo_dockerfiles'] = self.get_dockerfiles_bitbucket_repo(image_name, full_name)
                    if(results['repo_dockerfiles']['is_successful'] == True and results['repo_dockerfiles']['results'] != []):
                        results['repo_commits'] = self.get_commits_bitbucket_repo(full_name)
                        if (repo_owner_id != None):
                            results['repo_user_info'] = self.get_bitbucket_user_info(repo_owner_id)
                        results['source_repo_name']['results'] = ('Bitbucket', full_name)
        r = requests.post(self.ImageAndRepoInfoCrawlerTaskURL, json=results)

if __name__ == '__main__':
    miner = SourceRepoMiner()
    while True:
        miner.crawler_task()