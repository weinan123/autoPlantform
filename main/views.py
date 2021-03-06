# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import json, time, re
from django.http import HttpResponse, JsonResponse
import requests, urllib2
from django.contrib import auth
from .models import *
from .untils.until import my_login, mul_bodyData
from untils import sendRequests
from common import authService, batchUntils
@my_login
def index(request):
    if request.method == 'GET':
        return render(request, 'myindex.html')
def login(request):
    username = request.COOKIES.get('username')
    print (username)
    if username is not None:
        returndata = {"status": "success", "message": "login success", "username": username}
        return JsonResponse(returndata, safe=False)
    else:
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data["username"]
            password = data["password"]
            try:
                url = 'http://10.9.19.212:8888/accounts/ldapVerify/'
                data = {'username': username, 'password': password}
                response = requests.post(url, data=data)
                # print response.text
                if response.text == 'pass':
                    response = redirect('/index/', {'username': username})
                    request.session['username'] = username
                    request.session['password'] = password
                    response.set_cookie('username', username, 3600)
                    response.set_cookie('password', password, 3600)
                    users.objects.get_or_create(username=username)
                    returndata = {"status": "success", "message": "login success", "username": username}
                    return HttpResponse(json.dumps(returndata), content_type="'application/javascript")
                else:
                    returndata = {"status": "fail", "message": "用户名或者密码错误"}
                    return JsonResponse(returndata, safe=False)
                    '''
                    re = auth.authenticate(username = username,password=password)
                    print re
                    if re is not None:
                        auth.login(request,re)
                        #response = redirect('index/',{'username':username })
                        request.session['username'] = username
                        request.session['password'] = password
                        #response.set_cookie('username',username,3600)
                        #response.set_cookie('password', password, 3600)
                        returndata = {"status": "success", "message": "login success","username":username}
                        return JsonResponse(returndata,safe=False)
                    '''
            except:
                print Exception
        return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    response = HttpResponse('/login/')
    response.delete_cookie('username')
    return render(request, "login.html")


'''
没有注册功能
def register(request):
    if request.method == 'POST':
        uf = UserForm(request.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            password2 = uf.cleaned_data['password2']
            print password, password2
            if password == password2:
                User.objects.create_user(username=username, password=password)
                re = auth.authenticate(username=username, password=password)
                auth.login(request, re)
                response = redirect('/', {'username': username})
                request.session['username'] = username
                response.set_cookie('username', username, 3600)
                return redirect('/', {'username': username})
                # return render(request,'index.html',{'username':username })
            else:
                return render(request, 'register.html', {'register_error': '两次输入密码不一致'})
    else:
        uf = UserForm()
    return render(request, 'register.html', {'uf': uf})
    '''


def singleInterface(request):
    return render(request, 'singleInterface.html')


def sendRequest(request):
    data = json.loads(request.body)
    methods = data["methods"]
    send_url = data["url"]
    headers = data["headers"]
    bodyinfor = data["bodyinfor"]
    isRedirect = data["isRediret"]
    Authorization = data["Screatinfor"]["Screatinfor"]
    host = data["host"]
    url = (host + send_url)
    Screatinfor = data["Screatinfor"]
    assertData = data["assertData"].replace(" ", "")
    # 处理数据类型的方法
    send_body, files, showflag = mul_bodyData(bodyinfor)
    isScreat = Screatinfor["isScreat"]
    key_id = Screatinfor["key_id"]
    secret_key = Screatinfor["secret_key"].encode("utf-8")
    response = {}
    try:
        # 非加密执行接口
        if isScreat == "":
            resp = sendRequests.sendRequest().sendRequest(methods, url, headers, send_body, files,
                                                          isRedirect, showflag,Cookie=None)

        # 加密执行
        else:
            resp = sendRequests.sendRequest().sendSecretRequest(key_id, secret_key, Authorization,
                                                                methods, url, send_url, headers,
                                                                send_body, files, isRedirect, showflag,Cookie=None)
            #print (u"输出结果:", (resp.text))
            print resp.text.encode("utf-8")

        if assertData != "" and assertData != None:
            if assertData in resp.text:
                response = {
                    "code": 0,
                    "msg": "请求成功",
                    "data": resp.text,
                    "assert": True
                }
            else:
                response = {
                    "code": 0,
                    "msg": "请求成功",
                    "data": resp.text,
                    "assert": False
                }
        elif assertData == "":
            response = {
                "code": 0,
                "msg": "请求成功",
                "data": resp.text,
                "assert": ""
            }
    except Exception as e:
        print (e)
        response = {
            "code": -1,
            "msg": "请求失败，请检查请求参数",
            "data": {},
            "assert": ""
        }
    return JsonResponse(response, safe=False)


def getProjectList(request):
    project_list = projectList.objects.filter().values("projectName").distinct()
    modellist = moduleList.objects.filter().values("owningListID", "moduleName").distinct()
    # print project_list,model_list
    returnData = {
        "project_list": [],
        "model_list": []
    }
    # print("***project_list,modellist**",project_list,modellist)
    for i in range(0, len(project_list)):
        returnData["project_list"].append(project_list[i])
    for j in modellist:
        projectName = projectList.objects.get(id=int(j["owningListID"])).projectName
        moduleName = j["moduleName"]
        returnData["model_list"].append({"projectName": projectName, "moduleName": moduleName})
    print returnData
    return JsonResponse(returnData, safe=False)


def newCase(request):
    if request.method == "POST":
        reqdata = json.loads(request.body)["params"]
        data = reqdata["data_to_send"]
        methods = data["methods"]
        host = data["host"]
        url = data["url"]
        headers = json.dumps(data["headers"])
        bodyinfor = data["bodyinfor"]
        projectName = data["projectName"]
        moduleName = data["moduleName"]
        caseName = data["caseName"]
        creator = request.session.get('username')
        send_body = json.dumps(bodyinfor)
        flag = reqdata["flag"]
        assertData = data["assertData"]
        # print flag
        if (flag == False):
            try:
                hostTags.objects.get_or_create(qa=host)
                pid = projectList.objects.filter(projectName=projectName).values(
                    "id")
                owningListID = pid[0]["id"]
                mid = moduleList.objects.get(owningListID=owningListID, moduleName=moduleName).id
                print mid
                hoststr = hostTags.objects.filter(qa=host).values("id")
                hostid = hoststr[0]["id"]
                apiInfoTable.objects.get_or_create(method=methods, headers=headers, host=hostid, url=url,
                                                   body=send_body,
                                                   assertinfo=assertData, apiName=caseName,
                                                   owningListID=int(mid), creator=creator)
                data = {
                    "code": 0,
                    "msg": "保存成功"
                }
            except Exception as e:
                print e
                data = {
                    "code": -1,
                    "msg": "保存失败"
                }
        else:
            try:
                hostqa = str(host)
                id1 = int(reqdata["apiId"])
                pid = projectList.objects.get(projectName=projectName).id
                modid = moduleList.objects.get(owningListID=pid, moduleName=moduleName).id    #项目名不能重复可直接取id
                hostid = apiInfoTable.objects.get(apiID=id1).host
                if re.search('-dev', host) is not None:
                    hostqa = host.replace('-dev', '-qa')
                if re.search('-stage', host) is not None:
                    hostqa = host.replace('-stage', '-qa')
                host_exist = hostTags.objects.filter(qa=hostqa).values("id")
                if len(host_exist) == 0:
                    # hoststr = apiInfoTable.objects.filter(apiID=id1).values("host")
                    # hostid = hoststr[0]["host"]
                    hostTags.objects.filter(id=int(hostid)).update(qa=hostqa)
                    apiInfoTable.objects.filter(apiID=id1).update(apiName=caseName, method=methods, url=url,
                                                                  headers=headers, assertinfo=assertData,
                                                                  body=send_body,
                                                                  owningListID=int(modid))
                else:
                    hid = host_exist[0]["id"]
                    if int(hid) == int(hostid):
                        apiInfoTable.objects.filter(apiID=id1).update(apiName=caseName, method=methods, url=url,
                                                                      headers=headers, assertinfo=assertData,
                                                                      body=send_body,
                                                                      owningListID=int(modid))
                    else:
                        apiInfoTable.objects.filter(apiID=id1).update(apiName=caseName, method=methods, url=url,
                                                              headers=headers, assertinfo=assertData,
                                                              body=send_body,
                                                              owningListID=int(modid), host=int(hid))
            except Exception as e:
                data = {
                    "code": -1,
                    "msg": "更新失败" + str(e),
                }
                return JsonResponse(data)
            data = {
                "code": 0,
                "msg": "更新成功"
            }
        return JsonResponse(data, safe=False)


def returnAuthorization(request):
    if request.method == "POST":
        data = json.loads(request.body)
        secret_key = data["secret_key"].encode("utf-8")
        key_id = data["key_id"]
        http_method = data["methods"]
        path = data["url"]
        # headers = data["headers"]
        timestamp = int(time.time())
        credentials = authService.BceCredentials(key_id, secret_key)
        headers = {
            'Accept': 'text/html, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
        }
        headersOpt = {'X-Requested-With', 'User-Agent', 'Accept'}
        result = authService.simplify_sign(credentials, http_method, path, headers, timestamp, 300,
                                           headersOpt)
        # print result
        returnData = {
            "code": 0,
            "data": result
        }
        # return result
        return JsonResponse(returnData, safe=False)


# 首页获取图标数据
def getchartData(request):
    dataList = []
    projectlist = []
    projectName = projectList.objects.filter().values("projectName").distinct()
    for s in projectName:
        projectlist.append(s["projectName"])
    alldata = countCase.objects.all().values()
    # print alldata
    for i in alldata:
        data = {}
        data["projectName"] = i["projectName"]
        data["moduleName"] = i["moduleName"]
        data["allcaseNum"] = i["allcaseNum"]
        data["passcaseNum"] = i["passcaseNum"]
        data["failcaseNum"] = i["failcaseNum"]
        data["blockcaseNum"] = i["blockvaseNum"]
        dataList.append(data)
    returndata = {
        "code": 0,
        "data": dataList,
        "projectList": projectlist
    }
    # print returndata
    return JsonResponse(returndata, safe=False)


# 参数带文件上传
import os


def pararmsFiles(request):
    filename = request.POST.get("filename")
    files = request.FILES.get("files")
    print files
    fpath = r'main/postfiles/%s' % filename
    if not os.path.exists(os.path.split(fpath)[0]):
        # 目录不存在创建，makedirs可以创建多级目录
        os.makedirs(os.path.split(fpath)[0])
    try:
        with open(fpath, 'wb') as pic:
            for c in files.chunks():
                pic.write(c)
        data = {
            'code': 0,
            'msg': "上传文件成功"
        }
    except Exception as e:
        print e
        data = {
            'code': -1,
            'msg': "上传文件失败"
        }
    return JsonResponse(data, safe=False)