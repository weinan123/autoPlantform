# coding=utf-8
import sys,os,django, json, time, io, datetime
from httprunner import HttpRunner
from main.models import apiInfoTable, projectList, hostTags, moduleList
import batchUntils, shutil
from main.untils import until
from celery import shared_task



def start_main(batchrun_list, environment, reportflag, exeuser):
    # print(batchrun_list)
    cur_path = os.getcwd()      # F:\apiprojectgit\threeplantform\autoPlantform
    # suite_path = os.path.join(cur_path, "\\main\\common\\testcases")
    suite_path = os.path.join(cur_path, "main\\testcases")
    if not os.path.exists(suite_path):
        os.makedirs(suite_path)
    case_path = os.path.join(suite_path, str(exeuser).decode("utf-8"))
    if not os.path.exists(case_path):
        os.makedirs(case_path)
    # 生成测试用例的json文件
    gen_testcases(batchrun_list, case_path, environment)
    report_name = str(exeuser).decode("utf-8") + "_" + time.strftime("%Y%m%d%H%M%S",
                                                                     time.localtime(time.time())) + "_result.html"

    result = main_hrun(case_path, report_name, reportflag)
    # runner.run(suite_path)
    # shutil.rmtree(suite_path)  # 直接使用remove或rmdir会报错winError5
    # runner.summary = timestamp_to_datetime(runner.summary, type=False)
    # if reportflag == "Y":
    #     report_path = add_test_reports(runner, report_name)  # 不生成报告时注释掉
    #     print("报告路径：", report_path)
    # result = runner.summary["stat"]
    # reportPath为本地生成的文件名称，reportname为UI上用户设置的名称
    # 删除testcase文件夹
    return {"reportPath": report_name, "sNum": result["successes"], "fNum": result["failures"],
                "eNum": result["errors"]}


def main_hrun(testset_path, report_name, reportflag):
    """
    用例运行
    :param testset_path: dict or list
    :param report_name: str
    :return:
    """
    print("listdir: ", os.listdir(testset_path))
    report_name = report_name
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    runner.run(testset_path)
    shutil.rmtree(testset_path)

    runner.summary = timestamp_to_datetime(runner.summary)
    if reportflag == "Y":
        report_path = add_test_reports(runner, report_name=report_name)
        print("report path: %s." % report_path)
    result = runner.summary["stat"]
    return result


def gen_testcases(run_list, path, environment):
    # [{"sname": "有鱼股票", "list": [1,2,3], "cookices": cookices}]
    for test in run_list:
        print("=====1=====", test)
        parameters_list = []
        name = str(test["sname"]).decode("utf-8")
        apilist = test["list"]
        cookices = test["cookices"]
        filecontent = []
        configcontent = {
            "config": {
                "name": name,
                "variables": {},
                "request": {
                    "cookies": cookices
                }
            }
        }
        # 加入全局config
        filecontent.append(configcontent)
        for api in apilist:
            testcontent = {}
            # 获取单个api
            testcontent["test"], param_dict = get_testcontent(api, environment)
            filecontent.append(testcontent)
            if len(dict(param_dict).keys()) != 0:
                parameters_list.append(param_dict)
        t = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        case = os.path.join(path, name + "_" + t + ".json")
        if len(parameters_list) != 0:
            filecontent[0]["config"].update({"parameters": parameters_list})
        print("filecontent: ", filecontent)
        with io.open(case, 'w', encoding='utf-8') as stream:
            stream.write(json.dumps(filecontent).decode('raw_unicode_escape'))


def get_testcontent(api_id, environment):
    try:
        query = apiInfoTable.objects.get(apiID=int(api_id))
    except Exception as e:
        result = {"name": "sql query failed"}
        return result
    methods = query.method
    send_url = query.url
    if methods == "" or send_url == "":
        result = {"name": "method or url is null"}
        return result
    headers = str(query.headers).encode("utf-8")
    bodyinfor = str(query.body)
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
        result = {"name": "sql error"}
        return result
    host = batchUntils.getHost(int(query.host), environment)
    url = str(host) + str(send_url)
    print u"请求地址：%s" % (url)
    # 处理数据类型的方法
    send_body, files, showflag = until.mul_bodyData(bodyinfor)
    send_body_dict = {}
    if len(send_body) != 0:
        send_body_dict = send_body
    assertinfo = query.assertinfo
    apiname = str(query.apiName).decode("utf-8")
    extract_info = []
    dependData_str = query.depend_casedata
    if (dependData_str == "") or (dependData_str is None):
        extract_info = []
        param_dict = {}
    else:
        extract_info, param_dict = getExtractOrParam(str(dependData_str))
    validate_info = [
        {"lt": ["status_code", 300]},
    ]
    if len(assertinfo) != 0:
        assert_dict = getAssertDict(str(assertinfo))
        for i, j in assert_dict.items():
            validate_info.append({"str_eq": [str("content." + i), str(j)]})
    result = {
        "name": apiname,
        "request": {
            "url": url,
            "method": methods,
            "headers": headers_dict,
            "json": send_body_dict,
        },
        "extract": extract_info,
        "validate": validate_info
    }
    return result, param_dict


def getExtractOrParam(dependData_str):
    dependData_list = dependData_str.replace(" ", "").split(";")
    extract_list = []
    paramstrs_dict = {}
    for info in dependData_list:
        if str(info).find("$") != -1:
            extract_item = {}
            info_list = str(info).replace("$", "content.").split("=")
            extract_item[info_list[0]] = info_list[1]
            extract_list.append(extract_item)
        else:
            info_list = info.split("=")
            paramstrs_dict[info_list[0]] = info_list[1].split(",")
    return extract_list, paramstrs_dict


def getAssertDict(assertStr):
    if assertStr.startswith("{") is not True:
        assertStr = "{" + str(assertStr)
    if assertStr.endswith("}") is not True:
        assertStr = assertStr + "}"
    try:
        assert_dict = json.loads(assertStr)
    except Exception as e:
        assert_dict = {}
    return assert_dict


def add_test_reports(runner, report_name=None):
    """
    定时任务或者异步执行报告信息落地
    :param start_at: time: 开始时间
    :param report_name: str: 报告名称，为空默认时间戳命名
    :param kwargs: dict: 报告结果值
    :return:
    """
    time_stamp = int(runner.summary["time"]["start_at"])
    runner.summary['time']['start_datetime'] = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
    if report_name is not None and report_name != "":
        # print("report_name: ", report_name)
        report_name = report_name
    else:
        report_name = int(runner.summary['time']['start_at'])
    # report_name = report_name if report_name else runner.summary['time']['start_datetime']
    runner.summary['html_report_name'] = report_name
    report_path = os.path.join(os.getcwd(), "main\\report{}{}".format("\\", report_name))
    # print("report_path: ", report_path)
    # 自定义报告模板
    runner.gen_html_report(html_report_name=report_name, html_report_template=os.path.join(os.getcwd(), "main\\templates{}extent_report_template.html".format("\\")))
    # runner.gen_html_report(html_report_name=report_name) # 默认报告
    # F:\\apiprojectgit\\threeplantform\\autoPlantform\\main\\common\\reports\\1577417088.html
    return report_path


def timestamp_to_datetime(summary, type=True):
    if not type:
        time_stamp = int(summary["time"]["start_at"])
        summary['time']['start_datetime'] = datetime.datetime. \
            fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

    for detail in summary['details']:
        try:
            time_stamp = int(detail['time']['start_at'])
            detail['time']['start_at'] = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass

        for record in detail['records']:
            try:
                time_stamp = int(record['meta_data']['request']['start_timestamp'])
                record['meta_data']['request']['start_timestamp'] = \
                    datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
    return summary