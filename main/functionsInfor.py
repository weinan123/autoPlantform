# -*- coding: utf-8 -*-
import xlrd
from django.shortcuts import render, redirect
import json
import time
import re
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from main.models import *
from forms import UserForm, projectForm, firstProjectForm
from common import mulExcel
from untils import until
from common.batchUntils import checkFormat
def debugtalk(request):
    return render(request,'newfunction.html')
def basicfunction(request):
    return render(request, 'basicFunction.html')
def privtefunction(request):
    return render(request, 'privteFunction.html')
def savefunction(request):
    req = json.loads(request.body)
    id = req['funid']
    variname = req['variname']

    functiontype = req['functiontype']
    procontain = req['procontain']
    funcrionname = req['funcrionname']
    print req
    if procontain!="" and procontain !=None:
        projectid = int(projectList.objects.filter(projectName=procontain).values("id")[0]["id"])
        print projectid
    else:
        projectid=0
    try:
        if id=="":
            functioninfor = req['functioninfor'].replace('new_line', '\r\n')
            ispro = function.objects.filter(procontain=(projectid)).values()
            if len(ispro)==0:
                function.objects.get_or_create(funname=funcrionname,funtype=int(functiontype),funinfor=functioninfor,
                                procontain=(projectid),variblename=variname)
            else:
                funinfor = ispro[0]["funinfor"]+'\r\n'+functioninfor
                function.objects.filter(procontain=(projectid)).update(funname="debugtalk.py", funtype=int(functiontype),
                                                           funinfor=funinfor,
                                                           procontain=(projectid), variblename=variname)
        else:
            functioninfor = req['functioninfor']
            function.objects.filter(id=int(id)).update(funname=funcrionname,funtype=int(functiontype),funinfor=functioninfor,
                            procontain=(projectid),variblename=variname)
        result = {
            "msg":"保存成功",
            "code":0
        }
    except Exception as e:
        result = {
            "msg": "保存失败"+ e,
            "code": -1
        }
    return JsonResponse(result, safe=False)
def getfunction(request):
    funtype = request.GET.get('funtype')
    print funtype
    result = {}
    if int(funtype)==1:
        alldata = function.objects.filter(funtype=funtype)
        json_data = serializers.serialize('json', alldata)
        print json_data
        json_data = json.loads(json_data)
        result = {"code":0,
                  "msg":"sucess",
                  "alldata":json_data}
    elif int(funtype)==2:
        print 11111
        datas = {}
        alldataList = []
        alldata = function.objects.filter(funtype=funtype).values("id","funname","procontain")
        print alldata
        for i in alldata:
            datas["id"] =i["id"]
            datas["funname"] = i["funname"]
            datas["projectname"] = projectList.objects.filter(id=int(i["procontain"])).values("projectName")[0]["projectName"]
            alldataList.append(datas)
        result = {"code": 0,
                  "msg": "sucess",
                  "alldata": alldataList}
    return JsonResponse(result, safe=False)
def editFunction(request):
    return render(request, 'newfunction.html')


def editFunctionData(request):
    id = request.GET.get('id')
    functionInfor = function.objects.filter(id=id).values()[0]
    print functionInfor
    if int(functionInfor["procontain"])==0:
        projectName = ""
    else:
        projectName = projectList.objects.filter(id=int(functionInfor["procontain"])).values("projectName")[0]["projectName"]
    print functionInfor
    data = {"id":id,
            "funinfor":functionInfor["funinfor"],
            "funname": functionInfor["funname"],
            "variblename": functionInfor["variblename"],
            "projectName": projectName,
            "funtype": functionInfor["funtype"],
            }
    result = {"code": 0,
              "msg": "success",
              "data":data
              }
    return JsonResponse(result, safe=False)

def delfunction(request):
    req = json.loads(request.body)
    id = req['id']
    try:
        function.objects.filter(id = id).delete()
        result = {"code": 0,
                "msg": "success",
                }
    except Exception as e:
        result = {"code": -1,
                  "msg": "failed",
                  }
    return JsonResponse(result, safe=False)














