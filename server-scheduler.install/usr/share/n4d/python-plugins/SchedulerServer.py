#!/usr/bin/env python
######
#Scheduler library for Lliurex
#Add to N4D the scheduled tasks
#This class reads the json file with the scheduled tasks and
#distributes the info among the clients

import os
import json

class SchedulerServer():
	def __init__(self):
		self.dbg=0
		self.taskDir="/etc/scheduler/tasks.d"
		self.schedTasksDir=self.taskDir+"/scheduled"
		self.available_tasks_dir="/etc/scheduler/conf.d/tasks"
		self.custom_tasks=self.available_tasks_dir+"/personal.json"
		self.remote_tasks_dir=self.taskDir+"/remote"
		self.local_tasks_dir=self.taskDir+"/local"
	#def __init__

	def _debug(self,msg):
		if (self.dbg):
			print("Scheduler: %s" % msg)
	#def _debug

	def get_tasks(self,task_type):
		result={}
		tasks=[]
		wrkfiles=self._get_wrkfiles(task_type)
		for wrkfile in wrkfiles:
			content=self._read_tasks_file(wrkfile)
			tasks.append(content)
		self._debug("Tasks loaded")
		self._debug(str(tasks))
		return({'status':True,'data':tasks})
	#def get_tasks

	def get_available_tasks(self):
		tasks={}
		wrkfiles=self._get_wrkfiles('available')
		self._debug(wrkfiles)
		for wrkfile in wrkfiles:
			task=self._read_tasks_file(wrkfile)
			if task:
				tasks.update(task)
		self._debug(str(tasks))
		return({'status':True,'data':tasks})

	def _get_wrkfiles(self,task_type):
		if task_type=='local':
			wrk_dir=self.local_tasks_dir
		elif task_type=='remote':
			wrk_dir=self.remote_tasks_dir
		elif task_type=='available':
			wrk_dir=self.available_tasks_dir
		if not os.path.isdir(wrk_dir):
			os.makedirs(wrk_dir)

		wrkfiles=[]
		for f in os.listdir(wrk_dir):
			wrkfiles.append(wrk_dir+'/'+f)
		return wrkfiles
	#def _get_wrkfiles

	def _read_tasks_file(self,wrkfile):
		self._debug("Opening %s" % wrkfile)
		tasks={}
		if os.path.isfile(wrkfile):
			try:
				tasks=json.loads(open(wrkfile).read())
			except :
				errormsg=(("unable to open %s") % wrkfile)
				self._debug(errormsg)
		return(tasks)
	#def _read_tasks_file
	
	def remove_task(self,task_type,task_name,task_serial,task_cmd):
		if task_type=='local':
			wrk_dir=self.local_tasks_dir
		else:
			wrk_dir=self.remote_tasks_dir
		self._debug("Removing task from system")
		sw_del=False
		msg=''
		wrkfile=wrk_dir+'/'+task_name
		wrkfile=wrkfile.replace(' ','_')
		task=self._read_tasks_file(wrkfile)
		if task_name in task.keys():
			if task_serial in task[task_name].keys():
				del task[task_name][task_serial]
				self._debug("Task deleted")
				sw_del=True

		if sw_del:
			task=self._serialize_task(task)
			with open(wrkfile,'w') as json_data:
				json.dump(task,json_data,indent=4)
			self._register_cron_update()
		return ({'status':sw_del,'data':msg})
	#def remove_task

	def _serialize_task(self,task):
		serial_task={}
		for name,task_data in task.items():
			cont=0
			serial_task[name]={}
			for serial,data in task_data.items():
				serial_task[name].update({cont+1:data})
				cont+=1
		return(serial_task)
	#def _serialize_task

	def write_tasks(self,task_type,tasks):
		if task_type=='local':
			wrk_dir=self.local_tasks_dir
		else:
			wrk_dir=self.remote_tasks_dir
		self._debug("Writing task info")
		msg=''
		status=True
		task_name=list(tasks.keys())[0]
		task_serial=list(tasks[task_name].keys())[0]
		self._debug(tasks)
		serialized_task={}
		sched_tasks={}
		if not os.path.isdir(wrk_dir):
			os.makedirs(wrk_dir)

		wrkfile=wrk_dir+'/'+task_name
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
			msg=e
			status=False
		self._register_cron_update()
		self._debug("%s updated" % task_name)
		return({'status':status,'data':msg})
	#def write_tasks

	def write_custom_task(self,cmd_name,cmd,parms):
		status=True
		msg=''
		tasks={}
		new_task={}
		if os.path.isfile(self.custom_tasks):
			tasks=json.loads(open(self.custom_tasks).read())
			if not 'Personal' in tasks.keys():
				tasks['Personal']={}
		else:
			tasks['Personal']={}
		if '%s' in cmd:
			cmd=cmd.replace('%s','')
			new_task[cmd_name]=cmd+' "'+parms+'"'
		else:
			new_task[cmd_name]=cmd+' '+parms
		tasks['Personal'].update(new_task)
		try:
			with open(self.custom_tasks,'w') as json_data:
				json.dump(tasks,json_data,indent=4)
		except Exception as e:
			status=False
			msg=e
		return({'status':status,'data':msg})
	#def write_custom_task

	def _register_cron_update(self):
		self._debug("Registering trigger var")
		val=0
		if not objects["VariablesManager"].get_variable("SCHEDULED_TASKS"):
			self._debug("Initializing trigger var")
			objects["VariablesManager"].add_variable("SCHEDULED_TASKS",{},"","Scheduled tasks trigger","n4d-scheduler-server",False,False)
		val=objects["VariablesManager"].get_variable("SCHEDULED_TASKS")
		if not val:
			val=0
		if val>=1000:
			val=0
		val+=1
		objects["VariablesManager"].set_variable("SCHEDULED_TASKS",val)
		self._debug("New value is %s"%val)
	#def _register_cron_update
