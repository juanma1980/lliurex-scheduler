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

	def get_tasks(self,taskFilter):
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
		self._debug(str(tasks))
		return tasks
	#def _get_server_tasks

	def _get_local_tasks(self):
		tasks=[]
		wrkfiles=self._get_wrkfiles()
		for wrkfile in wrkfiles:
			tasks.append(self._read_tasks_file(wrkfile))
		return tasks
	#def _get_local_tasks

	def _get_wrkfiles(self):
		wrkfiles=[]
		if os.path.isdir(self.taskDir):
			wrkfiles=os.listdir(self.local_taskdir)
		else:
			wrkfiles.append(self.wrkfile)
		return wrkfiles
	
	def _read_tasks_file(self,wrkfile):
		self._debug("Opening %s" % wrkfile)
		tasks=None
		if os.path.isfile(wrkfile):
			try:
				tasks=json.loads(open(wrkfile).read())
			except :
				self.errormsg=(("unable to open %s") % wrkfile)
				self.status=1
				self._debug(self.errormsg)
		return(tasks)
	#def _read_tasks_file

	def write_tasks(self,tasks,taskFilter):
		if taskFilter=='remote':
			self._write_server_tasks(tasks)
		else:
			self._write_local_tasks(tasks)
	#def write_tasks

	def _write_local_tasks(self,tasks):
		self._debug("Writing local task info")
		if os.path.isdir(self.localTasksDir):
			wrkfile=self.localTasksDir+'/'+taskDesc
		else:
			wrkfile=self.wrkfile
		with open(wrkfile,'w') as json_data:
			json.dump(tasks,json_data)

	def _write_server_tasks(self,tasks):
		self._debug("Sending task info to server")
		tasks=self.n4dclient.write_tasks("","ServerScheduler",tasks)
		return True

	def _format_value(self,value):
		if len(value)<2 and (value!='*' and value!=0):
			value='0'+value
		return value
	
	def _remove_task(self,task):
		self._debug("Removing task from system")
		for taskDesc in task.keys():
			try:
				os.remove(self.wrkdir+'/'+taskDesc)
			except exception as e:
				print("Error removing %s" % taskDesc)
		return True

	def _n4d_connect(self):
		#Setup SSL
		context=ssl._create_unverified_context()
		n4dclient = n4d.ServerProxy("https://server:9779",context=context)
		return(n4dclient)
	#def _n4d_connect
