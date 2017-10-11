#!/usr/bin/env python3
###
#
###

import os
import json
import sys
try:
	import xmlrpc.client as n4d
except ImportError:
	raise ImportError("xmlrpc not available. Disabling server queries")
import ssl

class clientScheduler():
	def __init__(self):
		self.dbg=1
		self.sw_n4d=1
		if hasattr(sys,'last_value'):
		#If there's any error at this point it only could be an ImportError caused by xmlrpc
			self.sw_n4d=0
		else:
			self.n4dclient=self._n4d_connect()
		self.taskDir="/etc/scheduler/tasks.d"
		self.schedTasksDir=self.taskDir+"/scheduled"
		self.localTasksDir=self.schedTasksDir+"/local"
		self.wrkfile="/home/lliurex/borrar/ltasks.json"
	#def __init__

	def _debug(self,msg):
		if (self.dbg):
			print("Scheduler Client: %s" % msg)
	#def _debug

	def get_available_tasks(self):
		tasks=[]
		wrkfiles=self._get_wrkfiles('available')
		for wrkfile in wrkfiles:
			task=self._read_tasks_file(wrkfile)
			if task:
				tasks.append(task)
		self._debug(str(tasks))
		return tasks

	def get_scheduled_tasks(self,taskFilter):
		tasks=[]
		self._debug("Connecting to N4d")
		if taskFilter=='remote':
			if self.sw_n4d:
				tasks=self._get_server_tasks()
		else:
			tasks=self._get_local_tasks()
		return tasks

	def _get_server_tasks(self):
		tasks=[]
		self._debug("Retrieving task list")
		tasks=self.n4dclient.get_tasks("","ServerScheduler",'remote')
#		self._debug(str(tasks))
		return tasks
	#def _get_server_tasks

	def _get_local_tasks(self):
		tasks=[]
		wrkfiles=self._get_wrkfiles()
		for wrkfile in wrkfiles:
			task=self._sanitize_fields(self._read_tasks_file(wrkfile))
			if task:
				tasks.append(task)
		return tasks
	#def _get_local_tasks

	def _get_wrkfiles(self,type=None):
		if type=='available':
			wrkDir=self.taskDir
		else:
			wrkDir=self.localTasksDir
		wrkfiles=[]
		self._debug("Opening %s"%wrkDir)
		if os.path.isdir(wrkDir):
			for f in os.listdir(wrkDir):
				wrkfiles.append(wrkDir+'/'+f)
		else:
			wrkfiles.append(self.wrkfile)
		return wrkfiles
	
	def _read_tasks_file(self,wrkfile):
		self._debug("Opening %s" % wrkfile)
		tasks=None
		if os.path.isfile(wrkfile):
			try:
				tasks=json.loads(open(wrkfile).read())
			except Exception as e:
				print(e)
				self.errormsg=(("unable to open %s") % wrkfile)
				self.status=1
				self._debug(self.errormsg)
		return(tasks)
	#def _read_tasks_file

	def _sanitize_fields(self,tasks):
		for name,data in tasks.items():
			self._debug("Sanitize %s %s"%(name,data))
			for serial in data.keys():
				if tasks[name][serial]['dow']!='*':
					tasks[name][serial]['dom']='*'
		return tasks

	def write_tasks(self,tasks,taskFilter):
		if taskFilter=='remote':
			self._write_server_tasks(tasks)
		else:
			self._write_local_tasks(tasks)
	#def write_tasks

	def _write_local_tasks(self,tasks):
		self._debug("Writing local task info")
		task_name=list(tasks.keys())[0]
		task_serial=list(tasks[task_name].keys())[0]
		self._debug(tasks)
		serialized_task={}
		sched_tasks={}
		if not os.path.isdir(self.localTasksDir):
			os.makedirs(self.localTasksDir)

		wrkfile=self.localTasksDir+'/'+task_name
		wrkfile=wrkfile.replace(' ','_')
		if os.path.isfile(wrkfile):
			sched_tasks=json.loads(open(wrkfile).read())
			serial=len(sched_tasks[task_name])
			if task_serial in sched_tasks[task_name].keys():
				self._debug("Modify item %s" % serial)
				sched_tasks[task_name][task_serial]=tasks[task_name][task_serial]
				#Modify
			else:
				#Add
				self._debug("Add item %s" % serial)
				serialized_data={}
				serialized_data[serial+1]=tasks[task_name][task_serial]
				sched_tasks[task_name].update(serialized_data)
		else:
			self._debug("Add new item 1 to %s"%wrkfile)
			tasks[task_name]={"1":tasks[task_name]["0"]}
			sched_tasks=tasks.copy()
		with open(wrkfile,'w') as json_data:
			json.dump(sched_tasks,json_data,indent=4)
		self._debug("%s updated" % task_name)

	def _write_server_tasks(self,tasks):
		self._debug("Sending task info to server")
		print(tasks)
		tasks=self.n4dclient.write_tasks("","ServerScheduler",tasks)
		return True

	def _format_value(self,value):
		if len(value)<2 and (value!='*' and value!=0):
			value='0'+value
		return value
	
	def _remove_task(self,task):
		self._debug("Removing task from system")
		for task_name in task.keys():
			try:
				os.remove(self.wrkdir+'/'+task_name)
			except exception as e:
				print("Error removing %s" % task_name)
		return True

	def _n4d_connect(self):
		#Setup SSL
		context=ssl._create_unverified_context()
		n4dclient = n4d.ServerProxy("https://server:9779",context=context)
		return(n4dclient)
	#def _n4d_connect
