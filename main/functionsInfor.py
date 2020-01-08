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
    variname = req['variname']
    functioninfor = req['functioninfor']
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
        function.objects.get_or_create(funname=funcrionname,funtype=int(functiontype),funinfor=functioninfor,
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
    print request
    funtype = request.GET.get('funtype')
    print funtype
    try:
        alldata = function.objects.filter(funtype=funtype)
        json_data = serializers.serialize('json', alldata)
        print json_data
        json_data = json.loads(json_data)
        result = {"code":0,
                  "msg":"sucess",
                  "alldata":json_data}
    except Exception as e:
        result = {"code": -1,
                  "msg": "error",
                  }
    return JsonResponse(result, safe=False)
def editFunction(request):
    return render(request, 'newfunction.html')


def editFunctionData(request):
    id = request.GET.get('id')
    functionInfor = function.objects.filter(id=id).values_list("id","funinfor")
    print functionInfor
    data = {"id":int(functionInfor[0]),
            "funinfor":functionInfor[1]}
    result = {"code": -1,
              "msg": "success",
              "data":data
              }
    return JsonResponse(result, safe=False)











