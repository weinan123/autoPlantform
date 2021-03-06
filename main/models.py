#!/usr/bin/env  python
# --*--coding:utf-8 --*--

from django.db import models


class projectList(models.Model):
    """
    项目表
    """
    projectName = models.CharField(max_length=50, verbose_name='项目名称')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    cookieFlag = models.IntegerField(null=False, blank=False, verbose_name='登陆接口', default=0)


class moduleList(models.Model):
    """
    模块表
    """
    owningListID = models.IntegerField(blank=False, null=False, verbose_name='所属项目')
    moduleName = models.CharField(max_length=50, verbose_name='模块名称')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')


class caseList(models.Model):
    """
    用例表
    """
    owningProject = models.CharField(max_length=50, verbose_name='项目名称', default='')
    caseName = models.CharField(max_length=50, verbose_name='用例名称')
    includeAPI = models.CharField(max_length=200, null=True, blank=True, verbose_name='包含接口')
    creator = models.CharField(max_length=50, null=False, verbose_name='创建者')
    executor = models.CharField(max_length=50, null=True, blank=True, verbose_name='最近执行者')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    lastRunTime = models.DateTimeField(null=True, blank=True, verbose_name='最后运行时间')
    runResult = models.TextField(null=True, blank=True, verbose_name='运行结果')
    reportLocation = models.CharField(max_length=200, null=True, blank=True, verbose_name='报告地址')


class hostTags(models.Model):
    """
    host
    """

    qa = models.CharField(max_length=50, verbose_name='QA')
    stage = models.CharField(max_length=50, verbose_name='STAGE')
    live = models.CharField(max_length=50, verbose_name='live')
    dev = models.CharField(max_length=50, verbose_name='DEV')


class apiInfoTable(models.Model):
    """
    接口用例详情
    """
    apiID = models.AutoField(max_length=4, primary_key=True)
    apiName = models.CharField(max_length=100, null=False, error_messages={'required': '名称不能为空'})
    lastRunResult = models.IntegerField(null=True, blank=True, default=0)
    lastRunTime = models.DateTimeField(null=True, blank=True)
    creator = models.CharField(max_length=20, null=False)
    owningListID = models.IntegerField(blank=True, null=True, )
    method = models.CharField(max_length=10)
    host = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    headers = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    assertinfo = models.CharField(max_length=200, blank=True)
    secret_key = models.CharField(max_length=200, blank=True, null=True, )
    key_id = models.CharField(max_length=200, blank=True, null=True, )
    isScreat = models.BooleanField(default=False)
    isRedirect = models.BooleanField(default=False)
    t_id = models.CharField(max_length=200, blank=True, null=True, unique=True)
    depend_caseId = models.CharField(max_length=200, null=True, blank=True)
    depend_casedata = models.CharField(max_length=500, null=True, blank=True)
    response = models.TextField(null=True, blank=True)


class countCase(models.Model):
    pmID = models.AutoField(max_length=4, primary_key=True)
    allcaseNum = models.IntegerField(blank=True, null=True, )
    passcaseNum = models.IntegerField(blank=True, null=True, )
    failcaseNum = models.IntegerField(blank=True, null=True, )
    blockvaseNum = models.IntegerField(blank=True, null=True, )
    projectName = models.CharField(max_length=50, verbose_name='项目名称', blank=True)
    moduleName = models.CharField(max_length=50, verbose_name='模块名称', blank=True)
    update = models.DateTimeField(auto_now_add=True, verbose_name='更新时间', blank=True)


class reports(models.Model):
    report_runName = models.CharField(max_length=200)
    startTime = models.DateTimeField(null=True, blank=True)
    endTime = models.DateTimeField(null=True, blank=True)
    totalNum = models.IntegerField()
    successNum = models.IntegerField()
    failNum = models.IntegerField()
    errorNum = models.IntegerField()
    executor = models.CharField(max_length=50)
    environment = models.CharField(max_length=50)
    report_localName = models.CharField(max_length=200)


class users(models.Model):
    username = models.CharField(max_length=200, null=True)
    department = models.CharField(max_length=100, null=True, default='测试工程师')
    depart_lever = models.IntegerField(default=3)
    group = models.CharField(max_length=50, null=True)
    batch_check = models.BooleanField(default=True)
    batch_run = models.BooleanField(default=False)
    batch_del = models.BooleanField(default=False)
    configer_permit = models.BooleanField(default=False)


class userCookies(models.Model):
    user = models.CharField(max_length=50, null=True, blank=True)
    cookiename = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    projectname = models.CharField(max_length=100, null=True, blank=True)
    evirment = models.CharField(max_length=100, null=True, blank=True)
    cookies = models.CharField(max_length=200, blank=True, null=True)
    iseffect = models.IntegerField(blank=True, null=True, )
    updateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')


class department(models.Model):
    depart_lever = models.IntegerField()
    depart_name = models.CharField(max_length=50)


class projectschedule(models.Model):
    projectname = models.CharField(max_length=50, null=True, blank=True)
    runcaseId = models.TextField(null=True, blank=True)
    evirment = models.CharField(max_length=50, null=True, blank=True)
    reporter = models.TextField(null=True, blank=True)
    cookies = models.CharField(max_length=200, null=True, blank=True)
    timeDay = models.CharField(max_length=50, null=True, blank=True)
    timeTime = models.CharField(max_length=50, null=True, blank=True)
class function(models.Model):
    funname=models.CharField(max_length=50, null=True, blank=True)
    funtype=models.IntegerField()
    funinfor = models.TextField(null=True, blank=True)
    procontain=models.IntegerField()
    variblename = models.CharField(max_length=50, null=True, blank=True)