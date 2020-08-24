from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from .models import Image
from .models import DockerHubUser
from .models import ImageNameCrawlerTask
from .models import AuthToken
from .models import Repository
from .models import Tag
from .models import Build
from .models import Dockerfile
from .models import Commit
from .models import ChangedFile
from .models import GitHubUser
from .models import BitbucketUser


import random
import json


@csrf_exempt
def request_image(request):
    if(request.method == 'GET'):
        return HttpResponseBadRequest('GET Method not allowed.')
    elif(request.method == 'POST'):
        body_unicode = request.body.decode('utf-8')
        jsondata = json.loads(body_unicode)
        for item in jsondata:
            Image.objects.update_or_create(image_name = item['image_name'], defaults = item)
        return JsonResponse({
            'msg': 'OK!',
            'code': 200,
    })

@csrf_exempt
def create_image(request):
    if(request.method == 'GET'):
        return HttpResponseBadRequest('GET Method not allowed.')
    elif(request.method == 'POST'):
        body_unicode = request.body.decode('utf-8')
        jsondata = json.loads(body_unicode)
        for item in jsondata:
            Image.objects.get_or_create(image_name = item['image_name'], defaults = item)
        return JsonResponse({
            'msg': 'OK!',
            'code': 200,
    })

@csrf_exempt
def request_dockerhub_user(request):
    if(request.method == 'GET'):
        last_process_threshold = timezone.now() - timezone.timedelta(minutes=2)
        pass
    elif(request.method == 'POST'):
        body_unicode = request.body.decode('utf-8')
        jsondata = json.loads(body_unicode)
        for item in jsondata:
            DockerHubUser.objects.update_or_create(username = item['username'], defaults = item)
        return JsonResponse({
            'msg': 'OK!',
            'code': 200,
    })

@csrf_exempt
def request_repository(request):
    if(request.method == 'GET'):
        return HttpResponseBadRequest('GET Method not allowed.')
    elif(request.method == 'POST'):
        body_unicode = request.body.decode('utf-8')
        jsondata = json.loads(body_unicode)
        if(jsondata.get('repo_id')==None):
            repo, created = Repository.objects.get_or_create(repo_name=jsondata['repo_name'], repo_location=jsondata['repo_location'], defaults=jsondata)
        if created:
            return JsonResponse({
                'msg': 'OK!',
                'code': 200,
                'created': created,
                'repo_id': repo.get_id()
        })
        else:
            latest_commit_id = repo.commits[0]
            latest_commit_sha = Commit.objects.filter(commit_id = latest_commit_id)[0].commit_sha
            return JsonResponse({
                'msg': 'OK!',
                'code': 200,
                'created': created,
                'repo_id': repo.get_id(),
                'latest_commit_sha': latest_commit_sha
            })

@csrf_exempt
def query_repository(request, repo_location, repo_owner, repo_name):
    if(request.method == 'GET'):
        try:
            repo = Repository.objects.filter(repo_location=repo_location, repo_name=repo_owner+'/'+repo_name)[0]
            return JsonResponse({
                'msg': 'OK!',
                'code': 200,
                'repo_id': repo.get_id()
            })
        except IndexError:
            return JsonResponse({
                'msg': 'OK!',
                'code': 404
            })
    elif(request.method == 'POST'):
        return HttpResponseBadRequest('POST Method not allowed.')

@csrf_exempt
def request_image_name_crawler(request):
    if(request.method == 'GET'):
        last_process_threshold = timezone.now() - timezone.timedelta(minutes=2)
        tasks = ImageNameCrawlerTask.objects.filter(Q(last_sent__lte=last_process_threshold, complete=False) | Q(last_sent__isnull=True))
        with transaction.atomic():
            try:
                task = tasks[0]
                task.update_last_sent()
                obj = task.to_task_dict()
                return JsonResponse(obj)
            except Exception as e:
                return HttpResponseBadRequest('No more keywords left. ' + str(e))
    elif(request.method == 'POST'):
        body_unicode = request.body.decode('utf-8')
        jsondata = json.loads(body_unicode)
        for item in jsondata:
            ImageNameCrawlerTask.objects.update_or_create(keyword = item['keyword'], defaults = item)
        return JsonResponse({
            'msg': 'OK!',
            'code': 200,
    })


@csrf_exempt
def request_github_authtoken(request):
    GITHUBAPI_RATELIMIT = 5000
    if(request.method == 'GET'):
        last_updated_threshold = timezone.now() - timezone.timedelta(minutes=60)
        tokens = AuthToken.objects.filter(
            (Q(token_type='GitHub', in_use=False) &
            (Q(limit_remaining__gt=0) | Q(limit_reset_time__lte=timezone.now()) | Q(last_sent__isnull=True))) |
            (Q(token_type='GitHub', last_update__lte=last_updated_threshold, last_sent__lte=last_updated_threshold))
        ).order_by('limit_reset_time')
        with transaction.atomic():
            try:
                token = tokens[0]
                token.update_last_sent()
                token.claim_in_use()
                obj = token.to_dict()
                return JsonResponse(obj)
            except Exception as e:
                return HttpResponseBadRequest('No more GitHub tokens left.')
    elif(request.method == 'POST'):
        return HttpResponseBadRequest('POST Method not allowed.')


@csrf_exempt
def request_bitbucket_authtoken(request):
    BITBUCKETAPI_RATELIMIT = 1000
    if(request.method == 'GET'):
        tokens = AuthToken.objects.filter(
            Q(token_type='Bitbucket', in_use=False) & 
            (Q(limit_remaining__gt=0) | Q(limit_reset_time__lte=timezone.now()) | Q(last_sent__isnull=True))
            ).order_by('limit_reset_time')
        with transaction.atomic():
            try:
                token = tokens[0]
                token.update_last_sent()
                token.claim_in_use()
                obj = token.to_dict()
                return JsonResponse(obj)
            except Exception as e:
                return HttpResponseBadRequest('No more Bitbucket tokens left.')
    elif(request.method == 'POST'):
        return HttpResponseBadRequest('POST Method not allowed.')


@csrf_exempt
def request_update_authtoken(request):
    if(request.method == 'GET'):
        return HttpResponseBadRequest('GET Method not allowed.')
    elif(request.method == 'POST'):
        body_unicode = request.body.decode('utf-8')
        jsondata = json.loads(body_unicode)
        with transaction.atomic():
            if jsondata.get('suspended') == True:
                AuthToken.objects.filter(token=jsondata['token']).delete()
            else:
                AuthToken.objects.update_or_create(token=jsondata['token'], defaults = jsondata)
        return JsonResponse({
            'msg': 'OK!',
            'code': 200,
    })

@csrf_exempt
def request_image_and_repo_info_crawler(request):
    if(request.method == 'GET'):
        last_process_threshold = timezone.now() - timezone.timedelta(minutes=720)
        pagination_process_threshold = timezone.now() - timezone.timedelta(minutes=10)
        images = Image.objects.select_for_update().filter(
            Q(last_sent__lte=last_process_threshold, complete=False)
            | Q(last_sent__isnull=True)
            | Q(pagination__isnull=False, last_sent__lte=pagination_process_threshold, complete=False, error=False)
        )
        with transaction.atomic():
            try:
                image = images[0]
                image.update_last_sent()
                obj = image.to_task_dict()
                if(image.pagination is not None):
                    obj['pagination_task'] = True
                return JsonResponse(obj)
            except Exception as e:
                return HttpResponseBadRequest('No more images left. ' + str(e))
    elif(request.method == 'POST'):
        body_unicode = request.body.decode('utf-8')
        jsondata = json.loads(body_unicode)
        error = {key: jsondata[key]['results'] for key in jsondata.keys() if jsondata[key]['is_successful'] == False}
        if(error!={}):
            Image.objects.update_or_create(image_name = jsondata['image_name']['results'], defaults={'complete':False, 'error':True, 'response':error})
            return JsonResponse({
                    'msg': 'OK! But error exists.',
                    'code': 200,
            })
        if(jsondata.get('pagination_task', {}).get('results') == True):
            with transaction.atomic():
                image = Image.objects.select_for_update().filter(image_name=jsondata['image_name']['results'])[0]
                if jsondata.get('repo_dockerfiles') is not None:
                    objs_list = []
                    commits_list_for_query_diff = jsondata.get('repo_commits', {}).get('results', [])
                    for dockerfile in jsondata.get('repo_dockerfiles', {}).get('results', []): 
                        dockerfile['repo_id'] = image.source_repo_id
                        try:
                            diff_query = [commit for commit in commits_list_for_query_diff if
                                          commit.get('commit_sha') == dockerfile.get('commit_sha')][0]
                            diff_query = [file for file in diff_query.get('changed_files') if
                                          file.get('filename') == dockerfile.get('path')][0].get('patch')
                            dockerfile['diff'] = diff_query
                        except:
                            pass
                        objs_list.append(Dockerfile(**dockerfile))
                    Dockerfile.objects.bulk_create(objs_list)
                if jsondata.get('repo_commits') is not None:
                    objs_list = []
                    for commit in jsondata.get('repo_commits', {}).get('results', []):
                        commit['repo_id'] = image.source_repo_id
                        changedfile_objs_list = [ChangedFile(**file, repo_id=image.source_repo_id) for file in
                                                 commit['changed_files']]
                        ChangedFile.objects.bulk_create(changedfile_objs_list)
                        changedfile_id_list = [file.changedfile_id for file in changedfile_objs_list]
                        commit['changed_files'] = changedfile_id_list
                        objs_list.append(Commit(**commit))
                    Commit.objects.bulk_create(objs_list)
                    commits_id_list = [commit.commit_id for commit in objs_list]
                    with transaction.atomic():
                        repository = Repository.objects.select_for_update().filter(repo_id=image.source_repo_id)[0]
                        repository.commits += commits_id_list
                        repository.commits_count += len(commits_id_list)
                        repository.save()
                new_pagination = {'repo_dockerfiles':jsondata.get('repo_dockerfiles', {}).get('pagination'),
                                  'repo_commits':jsondata.get('repo_commits', {}).get('pagination')}
                new_pagination = {key:new_pagination[key] for key in new_pagination if new_pagination[key] is not None}
                image.pagination = new_pagination
                if new_pagination == {}:
                    image.complete = True
                    image.error = False
                    image.pagination = None
                image.save()
            return JsonResponse({
                'msg': 'OK!',
                'code': 200
            })
        if(jsondata['image_info']['results']==None):
            Image.objects.update_or_create(image_name=jsondata['image_name']['results'],
                                           defaults={'complete': True, 'error': False, 'response': None})
            return JsonResponse({
                'msg': 'OK!',
                'code': 200,
            })

        objs_list = [Tag(**tag) for tag in jsondata['image_tags']['results']]
        Tag.objects.bulk_create(objs_list)
        tags_id_list = [tag.id for tag in objs_list]
        jsondata['image_info']['results']['tags_count'] = len(tags_id_list)
        jsondata['image_info']['results']['tags'] = tags_id_list

        objs_list = [Build(**build) for build in jsondata['image_builds']['results']]
        Build.objects.bulk_create(objs_list)
        builds_id_list = [build.id for build in objs_list]
        jsondata['image_info']['results']['builds_count'] = len(builds_id_list)
        jsondata['image_info']['results']['builds'] = builds_id_list

        DockerHubUser.objects.update_or_create(username= jsondata['dockerhub_user_info']['results']['username'], defaults=jsondata['dockerhub_user_info']['results'])

        if(jsondata['image_info']['results'].get('source_repo_id') is not None and jsondata['image_info']['results'].get('source_repo') is not None and jsondata['image_info']['results'].get('source_repo_location') is not None):
            jsondata['image_info']['results']['complete'] = True
            jsondata['image_info']['results']['error'] = False
            jsondata['image_info']['results']['response'] = None
            jsondata['image_info']['results']['pagination'] = None
            Image.objects.update_or_create(image_name=jsondata['image_name']['results'],
                                           defaults=jsondata['image_info']['results'])
            return JsonResponse({
                'msg': 'OK!',
                'code': 200,
            })

        if(jsondata['source_repo_name']['results']!=None):
            repo_location, repo_name = jsondata['source_repo_name']['results']
            try:
                repo, repo_created = Repository.objects.get_or_create(repo_name=repo_name, repo_location=repo_location, defaults=jsondata['repo_info']['results'])
            except MultipleObjectsReturned:
                Repository.objects.filter(repo_name=repo_name, repo_location=repo_location).update(**jsondata['repo_info']['results'])
                repo = Repository.objects.filter(repo_name=repo_name, repo_location=repo_location)[0]
                repo_created = False
            repo_id = repo.get_id()
            jsondata['image_info']['results']['source_repo_id'] = repo_id
            jsondata['image_info']['results']['source_repo'] = repo.get_name()
            jsondata['image_info']['results']['source_repo_location'] = repo.get_location()

            if not repo_created:
                jsondata['image_info']['results']['complete'] = True
                jsondata['image_info']['results']['error'] = False
                jsondata['image_info']['results']['response'] = None
                jsondata['image_info']['results']['pagination'] = None
                Image.objects.update_or_create(image_name=jsondata['image_name']['results'],
                                               defaults=jsondata['image_info']['results'])
                return JsonResponse({
                    'msg': 'OK!',
                    'code': 200,
                })

            objs_list = []
            commits_list_for_query_diff = jsondata.get('repo_commits', {}).get('results', [])
            for dockerfile in jsondata.get('repo_dockerfiles', {}).get('results', []):
                dockerfile['repo_id'] = repo_id
                try:
                    diff_query = [commit for commit in commits_list_for_query_diff if commit.get('commit_sha')==dockerfile.get('commit_sha')][0]
                    diff_query = [file for file in diff_query.get('changed_files') if file.get('filename')==dockerfile.get('path')][0].get('patch')
                    dockerfile['diff'] = diff_query
                except:
                    pass
                objs_list.append(Dockerfile(**dockerfile))
            Dockerfile.objects.bulk_create(objs_list)

            objs_list = []
            for commit in jsondata.get('repo_commits', {}).get('results', []):
                commit['repo_id'] = repo_id
                changedfile_objs_list = [ChangedFile(**file, repo_id=repo_id) for file in commit['changed_files']]
                ChangedFile.objects.bulk_create(changedfile_objs_list)
                changedfile_id_list = [file.changedfile_id for file in changedfile_objs_list]
                commit['changed_files'] = changedfile_id_list
                objs_list.append(Commit(**commit))
            Commit.objects.bulk_create(objs_list)
            commits_id_list = [commit.commit_id for commit in objs_list]
            Repository.objects.filter(repo_id=repo_id).update(commits=commits_id_list, commits_count=len(commits_id_list))
        Image.objects.update_or_create(image_name = jsondata['image_name']['results'], defaults=jsondata['image_info']['results'])

        if(jsondata['source_repo_name']['results']!=None and jsondata['repo_info']['results']!=None and jsondata.get('repo_user_info')!=None):
            if(repo_location == 'GitHub'):
                GitHubUser.objects.update_or_create(username = jsondata['repo_user_info']['results']['username'], defaults = jsondata['repo_user_info']['results'])
            elif(repo_location == 'Bitbucket'):
                BitbucketUser.objects.update_or_create(user_id=jsondata['repo_user_info']['results']['user_id'], defaults=jsondata['repo_user_info']['results'])

        new_pagination = {'repo_dockerfiles': jsondata.get('repo_dockerfiles', {}).get('pagination'),
                          'repo_commits': jsondata.get('repo_commits', {}).get('pagination')}
        new_pagination = {key: new_pagination[key] for key in new_pagination if new_pagination[key] is not None}
        new_pagination = new_pagination if new_pagination!={} else None
        if new_pagination is None:
            Image.objects.update_or_create(image_name=jsondata['image_name']['results'],
                                       defaults={'complete': True, 'error': False, 'response': None})
        else:
            Image.objects.update_or_create(image_name=jsondata['image_name']['results'],
                                       defaults={'complete': False, 'error': False, 'response': None, 'pagination':new_pagination})
        return JsonResponse({
                'msg': 'OK!',
                'code': 200,
            })