# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import reports
from django.http.response import JsonResponse
import json, os, time, re


def batchReports(request):
    return render(request, "reports.html")

def getReportList(request):
    result = {}
    if request.method == 'GET':
        # 根据分页获取数据
        pagenum = request.GET["pageNum"]
        count = request.GET["pageCount"]
        startidx = (int(pagenum) - 1) * int(count)
        endidx = int(pagenum) * int(count)
        searchName = request.GET["searchName"]
        searchStartDate = str(request.GET["searchStart"])
        searchEndDate = str(request.GET["searchEnd"])
        searchUser = request.GET["searchUser"]
        # print("searchData: ", searchName, searchStartDate, searchEndDate, searchUser) #2019-12-11T00:00
        startDate = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime("1997-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"))
        endDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if searchStartDate != "":
            searchStartDate_re = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", str(searchStartDate.replace("T", " ")))
            if searchStartDate_re == None:
                result = {'code': -1, 'info': "日期格式不正确，参照格式：2020-12-12 12:12"}
                return JsonResponse(result)
            else:
                startDate = time.strftime('%Y-%m-%d %H:%M:%S',
                            time.strptime(str(searchStartDate_re.group()) + ":00", "%Y-%m-%d %H:%M:%S"))
        if searchEndDate != "":
            searchEndDate_re = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})",
                                           str(searchEndDate.replace("T", " ")))
            if searchEndDate_re == None:
                result = {'code': -1, 'info': "日期格式不正确，参照格式：2020-12-12 12:12"}
                return JsonResponse(result)
            else:
                endDate = time.strftime('%Y-%m-%d %H:%M:%S',
                            time.strptime(str(searchEndDate_re.group()) + ":00", "%Y-%m-%d %H:%M:%S"))
        try:
            if searchName == "" and searchStartDate == "" and searchEndDate == "" and searchUser == "":
                query = reports.objects.all()
                allList = query.order_by("-startTime")[startidx:endidx]
                count = query.count()
            else:
                query = reports.objects.filter(report_runName__contains=searchName, startTime__gte=startDate, endTime__lte=endDate, executor__contains=searchUser)
                allList = query.order_by("-startTime")[startidx:endidx]
                count = query.count()
        except Exception as e:
            result = {'code': -1, 'info': "sql error"}
            return JsonResponse(result)
        # print("alllist: ", allList)
        json_list = []
        for i in allList:
            json_dict = {}
            json_dict["id"] = i.id
            json_dict["report_runName"] = i.report_runName
            json_dict["startTime"] = i.startTime.strftime('%Y-%m-%d %H:%M:%S')
            json_dict["endTime"] = i.endTime.strftime('%Y-%m-%d %H:%M:%S')
            json_dict["totalNum"] = i.totalNum
            json_dict["successNum"] = i.successNum
            json_dict["failNum"] = i.failNum
            json_dict["errorNum"] = i.errorNum
            json_dict["executor"] = i.executor
            json_dict["environment"] = i.environment
            json_dict["report_localName"] = str(i.report_localName).decode("utf-8")
            json_list.append(json_dict)
        result = {
            'datas': json_list,
            'code': 0,
            'info': 'success',
            'totalCount': count,
            'currentPageCount': len(json_list),
        }
    return JsonResponse(result)

def reportDelete(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req['id']
        ainfo = reports.objects.get(id=id)
        reName = str(ainfo.report_localName).decode("utf-8")
        if ainfo:
            try:
                ainfo.delete()
                print("delete success from sql.")
            except BaseException as e:
                result = {'code': -1, 'info': 'delete error' + str(e)}
                return JsonResponse(result)
            a = delReport(reName)
            if a == 0:
                result = {'code': 0, 'info': 'delete success'}
            else:
                result = {'code': 0, 'info': 'The database file is deleted successfully. Please delete the local file manually.'}
        else:
            result = {'code': -2, 'info': 'no exist'}
    return JsonResponse(result)

def reportbatchDelete(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idlist = req['idList']
        # print idlist
        slist = []
        flist = []
        for id in idlist:
            ainfo = reports.objects.get(id=id)
            reName = str(ainfo.report_localName).decode("utf-8")
            if ainfo:
                try:
                    ainfo.delete()
                    slist.append(id)
                except BaseException as e:
                    flist.append(id)
                    print("delete %d failed :%s" % (id, str(e)))
                a = delReport(reName)
                if a == 0:
                    print("delete %d success" % id)
            else:
                flist.append(id)
                print("删除%d失败:不存在" % id)
        infos = "delete success:" + str(len(slist)) + ",fail:" + str(len(flist))
        result = {'code': 0, 'info': infos, 'successNum': len(slist)}
    return JsonResponse(result)

def delReport(rename):
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "\\main\\report\\"
    files = os.listdir(path)
    # print files
    # print "------------"
    report_name = rename
    # print report_name
    # print "--------------"
    res = 0
    for file in files:
        if str(file) == str(report_name):
            os.remove(path + file)
            print(file + " deleted")
            res = 0
            break
        else:
            res = -1
            print("location report delete failed")
    return res

def viewReport(request):
    a = request.GET["report"]
    # print a   # \report\2019-09-20-16_09_01_result.html
    reportName = a
    # print reportName
    return render(request, reportName)