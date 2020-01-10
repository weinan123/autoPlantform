# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, projectList,moduleList,reports, users, hostTags, userCookies
import time, re
import json
from django.http.response import JsonResponse
from common import batchstart, batchUntils
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def newOrEditCases(request):
    return render(request, "newOrEditCases.html")


def getDependList(request):
    pid = int(request.GET["pid"])
    caseOwnID_list = []
    modulelist = moduleList.objects.filter(owningListID=pid)
    for module in modulelist:
        caseOwnID_list.append(module.id)
    depend_caseList = batchUntils.getdependCaseList(caseOwnID_list, id)
    result = {'code': 0, 'info': 'success', "depend_caseList": depend_caseList}
    return JsonResponse(result)


def saveApiData(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        data = req["sendData"]
        print(data)
        apiName = data["apiName"]
        method = data["method"]
        host = data["host"]
        url = data["url"]
        if apiName == "" or host == "" or url == "":
            result = {"code": -1, "info": "名称、host、url不能为空"}
            return JsonResponse(result)
        dependcase_apiID = data["dependcase_apiID"]
        dependData = data["dependData"]
        header = str(data["header"]).replace(" ", "")
        body_str = str(data["bodys"]).replace(" ", "")
        cbody = re.sub(r'\${(.*?)}', "0", body_str)
        cheader = re.sub(r'\${(.*?)}', "0", header)
        if cbody != "" and cbody is not None:
            try:
                json.loads(cbody)
            except Exception as e:
                result = {"code": -1, "info": "body格式不正确"}
                return JsonResponse(result)
        if cheader != "" and cheader is not None:
            try:
                json.loads(cheader)
            except Exception as e:
                result = {"code": -1, "info": "header格式不正确"}
                return JsonResponse(result)
        if body_str != "" and body_str is not None and body_str != "{}":
            body = {"showflag": 3,
                    "datas": [{"paramValue": body_str}]
                    }
            body = json.dumps(body)
        else:
            body = "{}"
        if header == "" or header is None:
            header = "{}"
        assertinfo = data["assert"]
        userName = data["user"]
        try:
            hostqa = str(host)
            if re.search('-dev', host) is not None:
                hostqa = host.replace('-dev', '-qa')
            if re.search('-stage', host) is not None:
                hostqa = host.replace('-stage', '-qa')
            hostTags.objects.get_or_create(qa=hostqa)
            pid = data["projectID"]
            moduleName = data["moduleName"]
            mid = moduleList.objects.get(owningListID=int(pid), moduleName=moduleName).id
            hoststr = hostTags.objects.filter(qa=hostqa).values("id")
            hostid = hoststr[0]["id"]
            dependcase_apiID = int(dependcase_apiID)
            if dependcase_apiID == 0:
                depend_t_id = None
            else:
                depend_t_id = apiInfoTable.objects.get(apiID=dependcase_apiID).t_id  # 查询到依赖用例的t_id
                if depend_t_id == "" or depend_t_id is None:
                    depend_t_id = "d" + str(dependcase_apiID)
            checkresult = batchUntils.checkFormat(dependData)
            if checkresult["code"] == 0:
                updataData = checkresult["data"]
            else:
                result = {"code": -1, "info": "输入参数格式有误"}
                return JsonResponse(result)
            apiInfoTable.objects.get_or_create(method=method, headers=header, host=hostid, url=url,
                                               body=body, depend_caseId=depend_t_id,
                                               assertinfo=assertinfo, apiName=apiName,
                                               owningListID=int(mid), creator=userName, depend_casedata=updataData)
            result = {
                "code": 0,
                "info": "保存成功",
            }
        except Exception as e:
            result = {
                "code": -1,
                "info": "保存失败" + str(e),
            }
    return JsonResponse(result)