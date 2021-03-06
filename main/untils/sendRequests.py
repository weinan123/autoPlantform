# -*- coding: utf-8 -*-
import json
import requests,time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
requests.packages.urllib3.disable_warnings()
from main.common import authService
class sendRequest():
    def __init__(self):
        pass
    def mulBody(self,headerType,send_body,showflag):
        if("application/json" in headerType):
            postbody = json.dumps(send_body)
        #带文件传输的post请求key=value格式数据
        elif("multipart/form-data" in headerType):
            postbody=send_body
        else:
            postbody = send_body
        return postbody
    def isRedirect(self,isRedirect):
        # 判断是否需要重定向
        if isRedirect == "":
            redirect = False
        else:
            redirect = True
        return redirect
    def sendRequest(self,methods,url,headers,send_body,files,isRedirect,showflag,Cookie=None):
        #print files
        s = requests.session()
        response = ""
        if (methods == "GET"):

            redirect = self.isRedirect(isRedirect)
            response = s.get(url, headers=headers, params=send_body, verify=False,
                                    allow_redirects=redirect, cookies=Cookie)

            #resp = response.text
        elif (methods == "POST"):
            try:
                headerType = headers["Content-Type"]
            except Exception as e:
                headerType = ""
            postbody = self.mulBody(headerType, send_body,showflag)
            # print postbody
            redirect = self.isRedirect(isRedirect)
            response = s.post(url, headers=headers, files=files, data=postbody, verify=False,
                              allow_redirects=redirect,cookies=Cookie)
            # resp = response.text
        return response
    def sendSecretRequest(self,key_id,secret_key,Authorization,methods,url,send_url,headers,send_body,files,isRedirect,showflag,Cookie):
        headerType = headers["Content-Type"]
        postbody = self.mulBody(headerType, send_body,showflag)
        redirect = self.isRedirect(isRedirect)
        timestamp = int(time.time())
        credentials = authService.BceCredentials(key_id, secret_key)
        #加密请求体
        body = postbody.decode('unicode-escape')
        #body = json.dumps(send_body).decode('unicode-escape')
        #print body
        headersOpt = {'X-Requested-With', 'User-Agent', 'Accept'}
        if Authorization == "":
            result = authService.simplify_sign(credentials, methods, send_url, json.dumps(headers), timestamp, 300,
                                               headersOpt)
            #print result
            headers['X-encryptflag'] = '1'
            headers['Authorization'] = result
        else:
            headers['Authorization'] = Authorization
        if headers.get('X-encryptflag') == '1' and body:
            #print 'body before encrypted: '
            #print body
            body = authService.aes_encrypt(body)
        if (methods == "GET"):
            response = requests.get(url, headers=headers, params=body, verify=False,allow_redirects=redirect,cookies=Cookie)
        elif (methods == "POST"):
            response = requests.post(url, headers=headers,files=files, data=body, verify=False,allow_redirects=redirect,cookies=Cookie)
        resp = response.text
        if headers.get('X-encryptflag') != '1':
            pass
            #print 'response: '
        else:
            #print 'response before decrypt: '
            #print resp
            resp = authService.aes_decrypt(resp)
        print('response: ')
        return resp







