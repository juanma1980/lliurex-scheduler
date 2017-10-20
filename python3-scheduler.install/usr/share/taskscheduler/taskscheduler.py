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
		self.dbg=1
		self.sw_n4d=1
		if hasattr(sys,'last_value'):
		#If there's any error at this point it only could be an ImportError caused by xmlrpc
			self.sw_n4d=0
		else:
			self.n4dclient=self._n4d_connect()
		self.tasks_dir="/etc/scheduler/tasks.d"
		self.sched_tasks_dir=self.tasks_dir+"/scheduled"
		self.local_tasks_dir=self.sched_tasks_dir+"/local"
		self.cron_dir="/etc/cron.d"
		self.task_prefix="local-" #If n4d it's available then prefix must be the one defined in n4d
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
				tasks=self._get_remote_tasks()
		else:
			tasks=self._get_local_tasks()
		return tasks

	def _get_remote_tasks(self):
		tasks=[]
		self._debug("Retrieving task list")
		tasks=self.n4dclient.get_tasks("","ServerScheduler")
		self._debug(str(tasks))
		return tasks
	#def _get_remote_tasks

	def _get_local_tasks(self):
		tasks=[]
		wrkfiles=self._get_wrkfiles()
		for wrkfile in wrkfiles:
			task=self._sanitize_fields(self._read_tasks_file(wrkfile))
			if task:
				tasks.append(task)
		return tasks
	#def _get_local_tasks

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
		sched_tasks={}
		if not os.path.isdir(self.local_tasks_dir):
			os.makedirs(self.local_tasks_dir)

		wrkfile=self.local_tasks_dir+'/'+task_name
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
				self._debug("Data item %s" % serialized_data)
				self._debug("%s" % sched_tasks)
				sched_tasks[task_name].update(serialized_data)
				self._debug("%s" % sched_tasks)
		else:
			self._debug("Add new item 1 to %s"%wrkfile)
			tasks[task_name]={"1":tasks[task_name]["0"]}
			sched_tasks=tasks.copy()
		if sched_tasks:
			with open(wrkfile,'w') as json_data:
				json.dump(sched_tasks,json_data,indent=4)
		else:
			if os.isfile(wrkfile):
				os.remove(wrkfile)
		self._debug("%s updated" % task_name)
		self._debug("%s" % sched_tasks)
		self._send_tasks_to_crontab()

	def _write_server_tasks(self,tasks):
		self._debug("Sending task info to server")
		tasks=self.n4dclient.write_tasks("","ServerScheduler",tasks)
		return True

	def remove_task(self,task_name,task_serial,task_cmd,filter_tasks):
		if filter_tasks=='remote':
			self._remove_remote_task(task_name,task_serial,task_cmd)
		else:
			self._remove_local_task(task_name,task_serial,task_cmd)

	def _remove_local_task(self,task_name,task_serial,task_cmd):
		self._debug("Removing task from system")
		sw_del=False
		wrkfile=self.local_tasks_dir+'/'+task_name
		wrkfile=wrkfile.replace(' ','_')
		task=self._read_tasks_file(wrkfile)
		if task_name in task.keys():
			if task_serial in task[task_name].keys():
				del task[task_name][task_serial]
				sw_del=True

		if sw_del:
			task=self._serialize_task(task)
			if task:
				with open(wrkfile,'w') as json_data:
					json.dump(task,json_data,indent=4)
			else:
				if os.isfile(wrkfile):
					os.remove(wrkfile)
			self._send_tasks_to_crontab()
		return True

	def _serialize_task(self,task):
		serial_task={}
		for name,task_data in task.items():
			print("PROCESSING %s"%name)
			cont=0
			serial_task[name]={}
			for serial,data in task_data.items():
				print("SERIAL: %s"%serial)
				serial_task[name].update({cont+1:data})
				cont+=1
		return(serial_task)

	def _remove_remote_task(self,task_name,task_serial,task_cmd):
		self._debug("Removing task from server")
		tasks=self.n4dclient.remove_task("","ServerScheduler",task_name,task_serial,task_cmd)
#		self._debug("TASKS REMOVED")
		print(tasks)
	#def _remove_remote_task

	def _send_tasks_to_crontab(self):
		self._debug("Scheduling tasks")
		#Get scheduled tasks
		tasks=self._get_local_tasks()
		#Create a dict with the task names
		task_names={}
		for task in tasks:
			for name in task.keys():
				self._debug("Scheduling %s"%name)
				self._debug("%s"%task)
				fname=name.replace(' ','_')
				task_names[fname]=task
				self._debug("%s"%task_names)
				self._write_crontab_for_task(task_names[fname])

		for f in os.listdir(self.cron_dir):
			if f.startswith(self.task_prefix):
				fname=f.replace(self.task_prefix,'')
				if fname not in task_names.keys():
					self._debug("Removing %s"%f)
					self._debug("%s"%task_names)
					#Task is not scheduled, delete it
					os.remove(self.cron_dir+'/'+f)

	#def _send_tasks_to_crontab

	def _write_crontab_for_task(self,ftask):
		task=list(ftask.keys())[0]
		for task_name,task_data in ftask.items():
			fname=self.cron_dir+'/'+self.task_prefix+task_name.replace(' ','_')
			cron_array=[]
			self._debug("Sending %s" %task_name)
			self._debug("Data %s"%task_data)
			for task_serial,task_info in task_data.items():
				cron_task=("%s %s %s %s %s %s"%(task_info['m'],task_info['h'],task_info['dom'],task_info['mon'],\
							task_info['dow'],task_info['cmd']))

				cron_array.append(cron_task)
			with open(fname,'w') as data:
				for cron_line in cron_array:
					data.write(cron_line+"\n")

	def _n4d_connect(self):
		#Setup SSL
		context=ssl._create_unverified_context()
		n4dclient = n4d.ServerProxy("https://server:9779",context=context,allow_none=True)
		return(n4dclient)
	#def _n4d_connect
