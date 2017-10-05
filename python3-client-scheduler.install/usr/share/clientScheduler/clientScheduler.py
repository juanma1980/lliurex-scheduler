#!/usr/bin/env python3
###
#
###

import os
import json
import xmlrpc.client as n4d
import ssl

class clientScheduler():
	def __init__(self):
		self.dbg=1
		self.wrkdir='/tmp'
		self.fallback_taskDir="/etc/scheduler/tasks.d"
		self.fallback_schedTasksDir=self.fallback_taskDir+"/scheduled"
		self.fallback_remoteTasksDir=self.fallback_schedTasksDir+"/local"
		self.fallback_localTasksDir=self.fallback_schedTasksDir+"/remote"
	#def __init__

	def _debug(self,msg):
		if (self.dbg):
			print("Scheduler Client: %s" % msg)
	#def _debug

	def get_tasks(self,taskFilter):
		tasks=[]
		self._debug("Connecting to N4d")
		try:
			n4dclient=self._n4d_connect()
			self._debug("Retrieving task list")
			tasks=n4dclient.get_tasks("","ServerScheduler",taskFilter)
			self._debug(str(tasks))
		except:
			self._debug("Unable to connect")
			self._debug("Falling back to defaults")
		return(tasks)

	def _get_wrkfiles(self):
		wrkfiles=[]
		if os.path.isdir(self.wrkdir):
			wrkfiles=os.listdir(self.wrkdir)
		else:
			wrkfiles=self.wrkfile
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

	def write_tasks(self,tasks):
		for task in tasks:
			if task:
				self._process_task(task)
	#def write_tasks

	def _process_task(self,task):
		self._debug("Writing task info")
		for taskDesc,taskCmd in task.items():
			f=open(self.wrkdir+'/'+taskDesc,'w')
			for cmd,values in taskCmd.items():
				if values['enabled']=="1":
					values['m']=self._format_value(values['m'])
					values['h']=self._format_value(values['h'])
					values['dom']=self._format_value(values['dom'])
					values['mon']=self._format_value(values['mon'])
					line=(values['m']+' '+values['h']+' '+values['dom']+' '+values['mon']+' '+values['dow']+' '+cmd+'\n')
					f.write(line)
			f.close()

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
