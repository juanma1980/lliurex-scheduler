#!/usr/bin/env python
######
#Scheduler library for Lliurex
#Add to N4D the scheduled tasks
#This class reads the json file with the scheduled tasks and
#distributes the info among the clients

import os
import json

class ServerScheduler():
	def __init__(self):
		self.dbg=1
		self.taskDir="/etc/scheduler/tasks.d"
		self.schedTasksDir=self.taskDir+"/scheduled"
		self.remoteTasksDir=self.schedTasksDir+"/local"
		self.localTasksDir=self.schedTasksDir+"/remote"
		self.crondir="/etc/cron.d"
		self.cronPrefix="scheduler-"
		self.remote_wrkfile="/home/lliurex/borrar/rtasks.json"
		self.local_wrkfile="/home/lliurex/borrar/ltasks.json"
		self.status=0
		self.errormsg=''
	#def __init__

	def _debug(self,msg):
		if (self.dbg):
			print("Scheduler: %s" % msg)
	#def _debug

	def get_tasks(self,taskFilter):
		scheduled_tasks=[]
		wrkfiles=self._get_wrkfiles(taskFilter)
		for wrkfile in wrkfiles:
			scheduled_tasks.append(self._read_tasks_file(wrkfile))
		self._debug("Tasks loaded")
		self._debug(str(scheduled_tasks))
		return(scheduled_tasks)
	#def get_tasks

	def _get_wrkfiles(self,taskFilter):
		if taskFilter=='local':
			wrkdir=self.local_wrkfile
			wrkfile=self.local_wrkfile
		elif taskFilter=='remote':
			wrkdir=self.remote_wrkfile
			wrkfile=self.remote_wrkfile
		else:
			wrkdir=self.taskDir
			
		wrkfiles=[]
		if os.path.isdir(wrkdir):
			wrkfiles=os.listdir(wrkdir)
		else:
			wrkfiles.append(wrkfile)
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

	def _read_crontab(self):
		wrkfiles=os.listdir(self.crondir)
		cronfiles=[]
		crontasks=[]
		for wrkfile in wrkfiles:
			if wrkfile.startswith(self.cronPrefix):
				cronfiles.append(wrkfile)
		scheduled_tasks={}
		for cronfile in cronfiles:
			scheduled_tasks[cronfile]={}
			with open(self.crondir+'/'+cronfile) as f:
				for line in f:
					lstLine=line.split()
					m=lstLine[0]
					h=lstLine[1]
					mon=lstLine[2]
					dom=lstLine[3]
					dow=lstLine[4]
					user=lstLine[5]
					scheduled_tasks[cronfile][" ".join(lstLine[6:])]=" ".join(lstLine[:5])
		return scheduled_tasks
	#def _read_crontab	

	def write_tasks(self,tasksData,taskFilter):
		pass	
	#def write_tasks

