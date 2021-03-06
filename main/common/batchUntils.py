# coding=utf-8
import sys, os, django
sys.path.append(os.path.abspath('%s/../..' % sys.path[0]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_interface.settings")
django.setup()
import unittest
import sys, os
from main.models import apiInfoTable, projectList, hostTags, moduleList
import time
import json
from main.untils.until import mul_bodyData
from main.untils import sendRequests
import getDependData
import authService
import sys, re

reload(sys)
sys.setdefaultencoding('utf8')

'''
获取测试套件
'''
# 获取TestSuite
def getTestSuite(*classes):
    valid_types = (unittest.TestSuite, unittest.TestCase)
    suite = unittest.TestSuite()
    for cls in classes:
        print("6***cls: ", cls)
        if isinstance(cls, str):
            if cls in sys.modules:
                suite.addTest(unittest.findTestCases(sys.modules[cls]))
            else:
                raise ValueError("str arguments must be keys in sys.modules")
        elif isinstance(cls, valid_types):
            suite.addTest(cls)
        else:
            suite.addTest(unittest.makeSuite(cls))
    return suite


'''
查找文件，如果没有，则创建文件
'''
def create(user):
    t = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))  # 将指定格式的当前时间以字符串输出
    suffix = "_result.html"
    relpath = str(user).decode("utf-8") + "_" + t + suffix
    report_path = os.path.dirname(os.path.dirname(__file__)) + "\\report\\" + relpath
    reportname = t
    return report_path, relpath, reportname


'''
根据环境查询host，如果为空，则正则创建
'''
def getHost(id,environment):
    hostdict = hostTags.objects.filter(id=id).values()
    # print hostdict
    hostqa = hostdict[0]["qa"]
    hoststage = hostdict[0]["stage"]
    hostlive = hostdict[0]["live"]
    hostdev = hostdict[0]["dev"]
    match1 = re.search('qa', hostqa)
    match2 = re.search('dev', hostqa)
    match3 = re.search('stage', hostqa)
    host = ""
    lowenvironment = environment.lower()
    if (match1 != None) or (match2 != None) or (match3 != None):
        if lowenvironment=="qa":
                hoststr = hostqa.replace('qa', str(environment).lower())
                hoststr = hoststr.replace('stage', str(environment).lower())
                hoststr = hoststr.replace('dev', str(environment).lower())
                hostTags.objects.filter(id=id).update(qa=hoststr)
                host = hostdict[0]["qa"]
        elif lowenvironment=="stage" :
            if hoststage=="":
                hoststr = hostqa.replace("qa", str(environment).lower())
                hostTags.objects.filter(id=id).update(stage=hoststr)
            host = hostdict[0]["stage"]
        elif lowenvironment == "live":
            if hostlive == "":
                hoststr = hostqa.replace("-qa", "")
                hostTags.objects.filter(id=id).update(live=hoststr)
            host = hostdict[0]["live"]
        elif lowenvironment=="dev" :
            if hostdev=="":
                hoststr = hostqa.replace("qa", str(environment).lower())
                hostTags.objects.filter(id=id).update(dev=hoststr)
            host = hostdict[0]["dev"]
    else:
        hostTags.objects.filter(id=id).update(dev=hostqa,live=hostqa,stage=hostqa)
        host = hostdict[0][str(environment).lower()]
    return host


'''执行用例'''
def getResp(id,environment, dtime, cookices = None):
    try:
        query = apiInfoTable.objects.get(apiID=id)
    except Exception as e:
        result = {"code": -1, "info": "执行用例不存在，" + str(e)}
        return result
    Cookie = cookices
    # 判断是否有关联用例
    depend_flag = query.depend_caseId
    dependData_str = query.depend_casedata
    dependData = {}
    if depend_flag == "" or depend_flag is None:
        print(u"是否有关联接口：否")
        if dependData_str == "" or dependData_str is None:
            print(u"接口是否有自定义参数：否")
        else:
            defindData = getDefindData(dependData_str)
            dependData = defindData
            print(u"接口自定义参数：%s" % str(dependData))
    else:
        dependData = isDependency(depend_flag, dependData_str, environment, Cookie)
    #判断url,header,body等字段是否使用参数，若使用则用依赖值替换，若参数在依赖变量中没有则用空替换
    methods = query.method
    send_url = replaceStrParam(dependData, query.url)
    if methods == "" or send_url == "":
        result = {"code": -1, "info": "参数不能为空"}
        return result
    # headers = query.headers
    # headers_dict = {}
    # if headers != "" and headers is not None and str(headers) != "{}":
    #     headers_dict = replaceParam(dependData, json.loads(headers))
    # bodyinfor = query.body
    # # print("bodyinfor: ", bodyinfor)
    # if bodyinfor != "" and str(bodyinfor) != "{}" and bodyinfor is not None:
    #     bodyinfor = json.loads(bodyinfor)
    headers = replaceStrParam(dependData, str(query.headers))
    bodyinfor = replaceStrParam(dependData, str(query.body))
    headers_dict = {}
    if headers != "" and headers is not None and str(headers) != "{}":
        headers_dict = json.loads(headers)
    if bodyinfor != "" and str(bodyinfor) != "{}" and bodyinfor is not None:
        bodyinfor = json.loads(bodyinfor)
    listid = query.owningListID
    try:
        querylist = moduleList.objects.get(id=int(listid))
        proList = projectList.objects.get(id=int(querylist.owningListID))
        print(u"所属项目-模块：%s - %s" % (proList.projectName, querylist.moduleName))
    except Exception as e:
        result = {"code": -1, "info": str(e)}
        return result
    print u"请求方法：%s" % (methods)
    host = getHost(int(query.host), environment)
    host = replaceStrParam(dependData, host)
    url = str(host) + str(send_url)
    print u"请求地址：%s" % (url)
    # 处理数据类型的方法
    send_body, files, showflag = mul_bodyData(bodyinfor)
    send_body_dict = {}
    if len(send_body) != 0:
        send_body_dict = send_body
    # print json.dumps(dependData)
    print(u"请求头： %s" % str(headers_dict))
    print u"请求体：%s " % (str(send_body_dict).decode('raw_unicode_escape'))
    isRedirect = query.isRedirect
    isScreat = query.isScreat
    key_id = query.key_id
    secret_key = query.secret_key
    timestamp = int(time.time())
    assertinfo = replaceStrParam(dependData, str(query.assertinfo))
    dtime = dtime
    responseText = ""
    # 非加密执行接口
    if isScreat == False or isScreat == "":
        try:
            resp = sendRequests.sendRequest().sendRequest(methods, url, headers_dict, send_body_dict, files, isRedirect, showflag, Cookie)
        except Exception as e:
            infos = {"status_code": 400, "error": str(e)}
            apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
            result = {"code": -1, "info": "run error:" + str(infos)}
            return result
    # 加密执行
    else:
        credentials = authService.BceCredentials(key_id, secret_key)
        # print credentials
        headers_data = {
            'Accept': 'text/html, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
        }
        headersOpt = {'X-Requested-With', 'User-Agent', 'Accept'}
        Authorization = authService.simplify_sign(credentials, methods, send_url, headers_data, timestamp, 300,
                                                  headersOpt)
        try:
            resp = sendRequests.sendRequest().sendSecretRequest(key_id, secret_key, Authorization, methods, url,
                                                                send_url, headers_dict, send_body_dict, files, isRedirect,
                                                                showflag, Cookie)
        except Exception as e:
            infos = {"status_code": 400, "error": str(e)}
            apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
            result = {"code": -1, "info": "run error:" + str(infos)}
            return result
    result = {"code": 0, "info": "success", "response": resp, "assert": assertinfo}
    return result


def isDependency(depend_flag, depend_data, environment, Cookie):
    depend_caseid = depend_flag
    depend_data = depend_data
    print u"依赖用例t_id：%s" % (depend_caseid)
    if depend_data != "" and depend_data is not None:
        dependRes = getDependData.getdepands(depend_caseid, depend_data, environment, Cookie)
        if dependRes["code"] == 0:
            dependData = dependRes["dependdata"]
            print u"依赖数据：%s" % (str(dependData).decode('raw_unicode_escape'))
        else:
            dependData = {}
            print(u"依赖数据：无")
    else:
        dependData = {}
        print(u"依赖数据：无")
    return dependData


def replaceStrParam(dependdata_dict, stringValue):
    strValue = stringValue
    if str(strValue).find("${") != -1:
        strValue = str(strValue)
        param_key = re.findall(r"\${(.*?)}", strValue)[0]
        if param_key != "" and (param_key in dependdata_dict.keys()):
            # print("___dependdata_dict___",strValue,type(strValue),dependdata_dict,dependdata_dict[param_key])
            strValue = strValue.replace("${"+param_key+"}", str(dependdata_dict[param_key]))
            print(u"使用值：%s替换参数${%s}" % (dependdata_dict[param_key], param_key))
        else:
            strValue = strValue.replace("${"+param_key+"}", "null")
            print(u"依赖参数未找到，使用值：'0'替换参数${%s}" % param_key)
        strValue = replaceStrParam(dependdata_dict, strValue)
    else:
        return strValue
    return strValue

# def replaceParam(dependdata_dict, stringValue):
#     strValue = stringValue
#     if str(strValue).find("${") != -1:
#         strValue = str(strValue)
#         param_key = re.findall(r'\${(.*?)}', strValue)[0]
#         if param_key != "" and (param_key in dependdata_dict.keys()):
#             # print("___dependdata_dict___",strValue,type(strValue),dependdata_dict,dependdata_dict[param_key])
#             strValue = strValue.replace('"${'+param_key+'}"', str(dependdata_dict[param_key]))
#             print(u"使用值：%s替换参数${%s}" % (dependdata_dict[param_key], param_key))
#         else:
#             strValue = strValue.replace('"${'+param_key+'}"', "")
#             print(u"使用值：''替换参数${%s}" % param_key)
#         strValue = replaceParam(dependdata_dict, strValue)
#     else:
#         return strValue
#     return strValue
# def replaceParam(dependdata_dict, value_dict):
#     old_dict = value_dict
#     for item_key, item_value in old_dict.items():
#         paramkey_list = re.findall(r"\${(.*?)}", str(item_value))
#         if len(paramkey_list) != 0:
#             paramkey_value = paramkey_list[0]
#             try:
#                 value_dict[item_key] = dependdata_dict[paramkey_value]
#                 print(u"使用值：%s替换参数${%s}" % (dependdata_dict[paramkey_value], paramkey_value))
#             except Exception as e:
#                 value_dict[item_key] = ""
#                 print("error: %s" % str(e))
#                 print(u"使用值空值替换参数${%s}" % paramkey_value)
#     return value_dict


def checkDepend(apiID, dependID):
    flag = False
    # 查询当前选择用例所依赖用例的depend_caseId
    now_dependcaseID = apiInfoTable.objects.get(apiID=dependID).depend_caseId
    # 查看当前选择用例的t_id
    dependID_dependcaseID = apiInfoTable.objects.get(apiID=apiID).t_id
    # print("3**now_dependcaseID: ", now_dependcaseID, apiID, dependID, dependID_dependcaseID)
    if now_dependcaseID == dependID_dependcaseID and now_dependcaseID is not None:
        flag = True
    return flag


def getDefindData(datas_str):
    datas_list = (str(datas_str).replace(" ", "")).split(",")
    data_dict = {}
    for listvalue in datas_list:
        a = str(listvalue).split("=")
        data_dict[a[0]] = a[1]
    return data_dict


def checkFormat(dataValue):
    # print("1...dataValue: ",dataValue)
    if dataValue == "" or dataValue is None:
        updataData = None
    else:
        updataData = ""
        update_dependdata = str(dataValue).replace(" ", "")
        for sdata in update_dependdata.split(";"):
            if re.match(r'^[a-zA-Z](.*?)=(.+?)$', sdata):
                updataData = updataData + str(sdata) + ";"
            else:
                result = {"code": -1, "info": "输入数据格式有误"}
                return result
        updataData = updataData[:-1]
    result = {"code": 0, "data": updataData}
    return result


def checkAssertinfo(assertinfo, respText):
    result = False
    # print("assertinfo: %s, respText: %s" % (assertinfo, respText))
    assertinfo = assertinfo.replace(" ", "")
    assertinfo_list = assertinfo.split(",")
    respText = respText.replace(" ", "")
    # print("assertinfo: %s, respText: %s" % (assertinfo, respText))
    for item in assertinfo_list:
        if item == "":
            continue
        if item in respText:
            result = True
        else:
            result = False
    # print("result: %s" % result)
    return result


def getdependCaseList(ownID_list,id):
    dependCaseList = []
    query = apiInfoTable.objects.filter(owningListID__in=ownID_list).values("apiID", "apiName")
    for item in query:
        if str(item["apiID"]) != str(id):
            dependCaseList.append(item)
    return dependCaseList


def updataDatas(id, datas):
    checkresult = checkFormat(datas)
    # print("3...checkresult: ", checkresult)
    if checkresult["code"] == 0:
        updataData = checkresult["data"]
        # print("2...updataData: ",updataData)
        try:
            if updataData == "":
                apiInfoTable.objects.filter(apiID=id).update(depend_casedata=None)
            else:
                apiInfoTable.objects.filter(apiID=id).update(depend_casedata=updataData)
        except Exception as e:
            result = {"code": -1, "info": "更新失败"}
            return result
        result = {"code": 0, "info": "更新成功"}
    else:
        result = {"code": -1, "info": "依赖数据格式有误"}
    return result


def updatedependcase(id, depend_id):
    apiID = int(id)
    dependID = int(depend_id)
    if dependID == 0:
        apiInfoTable.objects.filter(apiID=apiID).update(depend_caseId=None)
    else:
        # print("1: ", apiID, dependID)
        # 判断用例之间是否构成相互依赖
        flag = checkDepend(apiID, dependID)
        # print("2: ", flag)
        if flag == True:
            result = {"code": -1, "info": "所选接口已与当前用例建立依赖，请重新选择"}
            return result
        try:
            dependcaset_id = apiInfoTable.objects.get(apiID=dependID).t_id  # 查询到依赖用例的t_id
        except Exception as e:
            result = {"code": -1, "info": str(e)}
            return result
        if dependcaset_id == "" or dependcaset_id is None:
            t_id = "d" + str(dependID)
            try:
                apiInfoTable.objects.filter(apiID=dependID).update(t_id=t_id)
                apiInfoTable.objects.filter(apiID=apiID).update(depend_caseId=t_id)
            except Exception as e:
                result = {"code": -1, "info": str(e)}
                return result
        else:
            try:
                apiInfoTable.objects.filter(apiID=apiID).update(depend_caseId=dependcaset_id)
            except Exception as e:
                result = {"code": -1, "info": str(e)}
                return result
    result = {"code": 0, "info": "更新成功"}
    return result