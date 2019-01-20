import pythoncom
import datetime
import pyHook
import ctypes
import json
import time
import os
overall={
  "start":datetime.datetime.now().strftime("%c"),
  "end":""
}
key_time={
  "base":0,
  "keyboard":{
    "number":0
  },
  "link_up":{
    "number":0
  }
}
mouse_time={
  "base":0,
  "move":0,
  "drag":[],
  "left":0,
  "right":0,
  "middle":0,
  "roll":{
    "up":0,
    "down":0
  }
}
timer=""
key=""
mouse=""
link_up=[]
path="D://python/"
def onMouseEvent(event):
  global mouse_time,mouse,timer
  mouse_time["base"]+=1
  name=event.MessageName.split(" ")
  if(event.MessageName!="mouse move" and mouse=="mouse move"):
    mouse_time["move"]+=1
  if(len(name)==3 and name[2]=="down"):
    timer=time.time()
  if(len(name)==3 and name[2]=="up"):
    mouse_time[name[1]]+=1
  if(len(name)==2 and name[1]=="wheel"):
    mouse_time["roll"]["up" if event.Wheel==1 else "down"]+=1
  if(event.MessageName.find("up")!=-1 and mouse=="mouse move"):
    mouse_time["drag"].append(round(time.time()-timer,2))
  mouse=event.MessageName
  return True
def onKeyboardEvent(event): 
  global key_time,key,link_up
  key_time["base"]+=1
  if(event.Key!=key):
    if(link_up):
      length=int(len(link_up)+1)
      if(key_time["link_up"].has_key("%s"%(link_up[0]))==False):
        key_time["link_up"][link_up[0]]=[]
      key_time["link_up"][link_up[0]].append(length)
      key_time["keyboard"][link_up[0]]-=1
      key_time["keyboard"]["number"]-=1
      key_time["link_up"]["number"]+=length
      link_up=[]
    if(key_time["keyboard"].has_key(event.Key)==False):
      key_time["keyboard"][event.Key]=0
    key_time["keyboard"]["number"]+=1
    key_time["keyboard"][event.Key]+=1
  else:
    link_up.append(event.Key)
  if(event.Key=="Return" and key=="Pause"):
    with open(path+"download/key.txt","a") as f:
      overall["key"]=key_time
      overall["mouse"]=mouse_time
      overall["end"]=datetime.datetime.now().strftime("%c")
      f.write(json.dumps(overall)+"\n")
      f.write("**"*50)
      f.close()
      os.system("shutdown -s -t 0")
  key=event.Key
  print event.Key
  return True
if __name__ == "__main__":
  hm=pyHook.HookManager()
  hm.KeyDown = onKeyboardEvent
  hm.HookKeyboard()
  hm.MouseAll = onMouseEvent
  hm.HookMouse()
  pythoncom.PumpMessages()