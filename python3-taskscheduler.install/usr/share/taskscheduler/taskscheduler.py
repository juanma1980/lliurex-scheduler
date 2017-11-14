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
		self.n4dserver=self._n4d_connect()
		self.n4dclient=self._n4d_connect('localhost')
		self.tasks_dir="/etc/scheduler/conf.d"
		self.custom_tasks=self.tasks_dir+"/custom.json"
		self.commands_file=self.tasks_dir+'/commands.json'
		self.sched_dir="/etc/scheduler/tasks.d"
		self.local_tasks_dir=self.sched_dir+"/local"
		self.credentials=["",""]
	#def __init__

	def _debug(self,msg):
		if (self.dbg):
			print("Scheduler Client: %s" % msg)
	#def _debug
	
	def set_credentials(self,credentials):
		self.credentials=credentials

	def get_available_tasks(self):
#		tasks=[]
		tasks={}
		wrkfiles=self._get_wrkfiles('available')
		for wrkfile in wrkfiles:
			task=self._read_tasks_file(wrkfile)
			if task:
#				tasks.append(task)
				tasks.update(task)
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

	def get_task_description(self,task_cmd):
		desc=task_cmd
		sw_found=False
		self._debug("Getting desc for %s"%task_cmd)
		tasks=self.get_available_tasks()
		for task_desc,task_data in tasks.items():
			for action,cmd in task_data.items():
				if cmd==task_cmd:
					desc=action
					sw_found=True
					break
			if sw_found:
				break
		return desc
	#def get_task_description

	def get_task_command(self,task_description):
		cmd=task_description
		sw_found=False
		self._debug("Getting cmd for %s"%task_description)
		tasks=self.get_available_tasks()
		for task_desc,task_data in tasks.items():
			if task_description in task_data.keys():
				cmd=task_data[task_description]
				sw_found=True
				break
		return cmd
	#def get_task_command

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

	def get_commands(self):
		cmds={}
		if os.path.isfile(self.commands_file):
			try:
				cmds=json.loads(open(self.commands_file).read())
			except Exception as e:
				print(e)
				self.errormsg=(("unable to open %s") % self.commands_file)
				self.status=1
				self._debug(self.errormsg)
		return(cmds)

	def get_command_cmd(self,cmd_desc):
		commands=self.get_commands()
		cmd=cmd_desc
		if cmd_desc in commands.keys():
			cmd=commands[cmd_desc]
		return cmd

	def write_custom_task(self,cmd_name,cmd,parms):
		n4d_server=self.n4dserver
		tasks=n4d_server.write_custom_task(self.credentials,"SchedulerServer",cmd_name,cmd,parms)

	def _read_tasks_file(self,wrkfile):
		self._debug("Opening %s" % wrkfile)
		tasks=None
		if os.path.isfile(wrkfile) and wrkfile!=self.commands_file:
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
