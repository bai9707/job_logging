# encoding:utf-8
from __future__ import unicode_literals
import pythoncom,pyHook,requests,threading
import json,time,os
import win32con,win32api
filename=__file__.split(".")[0]
path="D://%s"%filename
url="http://127.0.0.1:8888"
overall={
  "start":int(time.time()),
  "end":"",
  "key_time":{},
  "mouse_time":{
    "left":0,
    "move":0,
    "right":0,
    "middle":0,
    "drag":{
      "left":0,
      "right":0,
      "middle":0
    },
    "roll":{
      "up":0,
      "down":0
    },
  }
}
key=""
mouse=""
def error(err):
  with open("%s/error.txt"%path,"a") as f:
    f.write("[%s,%s]\n"%(time.strftime("%Y/%m/%d-%H:%M",time.localtime()),err))
    f.close()
def date(date_str):
  return time.strftime("%Y%m%d",time.localtime(int(date_str or time.time())))
def write_in():
  with open("%s/%s.json"%(path,filename),"w") as f:
    overall["end"]=int(time.time())
    f.write(json.dumps(overall))
    f.close()
def abnormal_(judge,param):
  global overall
  try:
    if(judge):
      val=param.MessageName.split(" ")
      if(val[1]!="move" and mouse=="move"):
        overall["mouse_time"]["move"]+=1
      if(val[1]=="wheel"):
        overall["mouse_time"]["roll"]["up" if param.Wheel==1 else "down"]+=1
      if(len(val)==3 and val[2]=="up"):
        if(mouse=="move"):
          overall["mouse_time"]["drag"][val[1]]+=1
        elif(mouse!="move" and mouse!="wheel"):
          overall["mouse_time"][val[1]]+=1
    else:
      if(overall["key_time"].has_key(param)==False):
        overall["key_time"][param]=0
      if(param!=key):
        overall["key_time"][param]+=1  
  except BaseException,err:
    error(err)
  write_in()
def onMouseEvent(event):
  global mouse
  abnormal_(True,event)
  mouse=event.MessageName.split(" ")[1]
  return True
def onKeyboardEvent(event):
  global key
  abnormal_(False,event.Key)
  key=event.Key
  return True
def monitor_start():
  hm=pyHook.HookManager()
  hm.KeyDown = onKeyboardEvent
  hm.HookKeyboard()
  hm.MouseAll = onMouseEvent
  hm.HookMouse()
  pythoncom.PumpMessages()
def emit_data(data_):
  while True:
    if(abnormal(convey,data_)):
      break
    time.sleep(5)
def initialize(data):
  global overall
  with open("%s/%s.json"%(path,filename),"r+") as f:
    data_=json.loads(f.read())
    f.close()
  if(date(data_["start"])==date(False) or time.time()-int(data_["end"])<3600):
    overall=data_
  else:
    threading.Thread(target=emit_data,args=(json.dumps(data_),)).start()
def abnormal(fn,data):
  try:
    return fn(data)
  except BaseException,err:
    error(err)
    return False
def convey(data):
  if(json.loads(requests.post("%s/post/%s"%(url,json.loads(data)["start"]),data={"data":data}).text)["code"]=="ok"):
    return True
def request_start():
  while True:
    try:
      if(json.loads(requests.post("%s/get/%s"%(url,int(time.time()))).text)["code"]=="off"):
        os.system("shutdown -s -t 0")
    except BaseException,err:
      error(err)
    time.sleep(5)
if __name__ == "__main__":
  if(not(os.path.exists(path))):
    os.mkdir(path)
  win32api.SetFileAttributes(path,win32con.FILE_ATTRIBUTE_HIDDEN)
  abnormal(initialize,False)
  threading.Thread(target=request_start).start()
  threading.Thread(target=monitor_start).start()