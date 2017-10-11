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
		self.remote_tasks_dir=self.schedTasksDir+"/remote"
		self.crondir="/etc/cron.d"
		self.cronPrefix="scheduler-"
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
		if not os.path.isdir(self.remote_tasks_dir):
			os.makedirs(self.remote_tasks_dir)

		wrkfiles=[]
		for f in os.listdir(wrkdir):
			wrkfiles.append(self.remote_tasks_dir+'/'+wrkdir)
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

	def write_tasks(self,tasks):
		self._debug("Writing remote task info")
		task_name=list(tasks.keys())[0]
		task_serial=list(tasks[task_name].keys())[0]
		self._debug(tasks)
		serialized_task={}
		sched_tasks={}
		if not os.path.isdir(self.remote_tasks_dir):
			os.makedirs(self.remote_tasks_dir)

		wrkfile=self.remote_tasks_dir+'/'+task_name
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

		try:
			with open(wrkfile,'w') as json_data:
				json.dump(sched_tasks,json_data,indent=4)
		except Exception as e:
			print('*****')
			print('*****')
			print(e)
			print('*****')
			print('*****')
		self._debug("22222222222222222222")
		self._debug("%s updated" % task_name)
	#def write_tasks

