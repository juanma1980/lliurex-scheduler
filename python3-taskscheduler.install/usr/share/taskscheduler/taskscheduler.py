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

class TaskScheduler():
	def __init__(self):
		self.dbg=0
		self.n4dserver=self._n4d_connect()
		self.n4dclient=self._n4d_connect('localhost')
		self.tasks_dir="/etc/scheduler/tasks.d"
		self.sched_tasks_dir=self.tasks_dir+"/scheduled"
		self.local_tasks_dir=self.sched_tasks_dir+"/local"
		self.credentials=["",""]
	#def __init__

	def _debug(self,msg):
		if (self.dbg):
			print("Scheduler Client: %s" % msg)
	#def _debug
	
	def set_credentials(self,credentials):
		self.credentials=credentials

	def get_available_tasks(self):
		tasks=[]
		wrkfiles=self._get_wrkfiles('available')
		for wrkfile in wrkfiles:
			task=self._read_tasks_file(wrkfile)
			if task:
				tasks.append(task)
		self._debug(str(tasks))
		return tasks

	def get_scheduled_tasks(self,task_type):
		tasks=[]
		self._debug("Retrieving %s task list"%task_type)
		if task_type=='remote':
			n4d_server=self.n4dserver
		else:
			n4d_server=self.n4dclient
		tasks=n4d_server.get_tasks("","SchedulerServer",task_type)
		self._debug(str(tasks))
		return tasks

	def _get_wrkfiles(self,task_type=None):
		if task_type=='available':
			wrkdir=self.tasks_dir
		else:
			wrkdir=self.local_tasks_dir
		wrkfiles=[]
		self._debug("Opening %s"%wrkdir)
		if os.path.isdir(wrkdir):
			for f in os.listdir(wrkdir):
				wrkfiles.append(wrkdir+'/'+f)
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

	def write_tasks(self,tasks,task_type):
		self._debug("Sending task info to %s server"%task_type)
		if task_type=='remote':
			n4d_server=self.n4dserver
		else:
			n4d_server=self.n4dclient
		tasks=n4d_server.write_tasks(self.credentials,"SchedulerServer",task_type,tasks)
		self._debug(tasks)
		return True
	#def write_tasks

	def remove_task(self,task_name,task_serial,task_cmd,task_type):
		self._debug("Removing task from %s server"%task_type)
		if task_type=='remote':
			n4d_server=self.n4dserver
		else:
			n4d_server=self.n4dclient
		tasks=n4d_server.remove_task(self.credentials,"SchedulerServer",task_type,task_name,task_serial,task_cmd)
		self._debug(tasks)

	def _n4d_connect(self,server='server'):
		#Setup SSL
		context=ssl._create_unverified_context()
		n4dclient = n4d.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		return(n4dclient)
	#def _n4d_connect
