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
		self.credentials=["",""]
		self.n4dserver=None
		self.n4dclient=self._n4d_connect('localhost')
		self.conf_dir="/etc/scheduler/conf.d/"
		self.tasks_dir=self.conf_dir+'/tasks'
		self.custom_tasks=self.tasks_dir+"/personal.json"
		self.commands_file=self.conf_dir+'/commands/commands.json'
		self.sched_dir="/etc/scheduler/tasks.d"
		self.local_tasks_dir=self.sched_dir+"/local"
	#def __init__

	def _debug(self,msg):
		if (self.dbg):
			print("Scheduler lib: %s" % msg)
	#def _debug
	
	def set_credentials(self,user,pwd,server):
		self.credentials=[user,pwd]
		self.n4dserver=self._n4d_connect(server)
	#def set_credentials

	def get_available_tasks(self):
		tasks={}
		if self.n4dserver:
			tasks=self.n4dserver.get_available_tasks("","SchedulerServer")['data'].copy()
		tasks.update(self.n4dclient.get_available_tasks("","SchedulerServer")['data'])
		return tasks
	#def get_available_tasks

	def get_scheduled_tasks(self,task_type):
		tasks=[]
		self._debug("Retrieving %s task list"%task_type)
		if task_type=='remote' and self.n4dserver:
			tasks=self.n4dserver.get_tasks("","SchedulerServer",task_type)['data']
		elif task_type=='local':
			tasks=self.n4dclient.get_tasks("","SchedulerServer",task_type)['data']
		return tasks
	#def get_scheduled_tasks

	def get_task_description(self,task_cmd):
		desc=task_cmd
		sw_found=False
		self._debug("Getting desc for %s"%task_cmd)
		tasks=self.get_available_tasks()
		try:
			for task_desc,task_data in tasks.items():
				for action,cmd in task_data.items():
					if cmd==task_cmd:
						desc=action
						sw_found=True
						break
				if sw_found:
					break
		except Exception as e:
			print(e)
			self._debug(("Error ocurred when looking for %s")%task_cmd)
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
	#def _get_wrkfiles

	def get_commands(self):
		cmds={}
		if os.path.isfile(self.commands_file):
			try:
				cmds=json.loads(open(self.commands_file).read())
			except Exception as e:
				print(e)
				self._debug(("unable to open %s") % self.commands_file)
		return(cmds)
	#def get_commands

	def get_command_cmd(self,cmd_desc):
		commands=self.get_commands()
		cmd=cmd_desc
		if cmd_desc in commands.keys():
			cmd=commands[cmd_desc]
		return cmd
	#def get_command_cmd

	def write_custom_task(self,cmd_name,cmd,parms):
		n4d_server=self.n4dserver
		result=n4d_server.write_custom_task(self.credentials,"SchedulerServer",cmd_name,cmd,parms)
		return (result['status'])
	#def write_custom_task

	def _read_tasks_file(self,wrkfile):
		self._debug("Opening %s" % wrkfile)
		tasks=None
		if os.path.isfile(wrkfile) and wrkfile!=self.commands_file:
			try:
				tasks=json.loads(open(wrkfile).read())
			except Exception as e:
				print(e)
				self._debug(("unable to open %s") % wrkfile)
		return(tasks)
	#def _read_tasks_file

	def write_tasks(self,tasks,task_type):
		self._debug("Sending task info to %s server"%task_type)
		if task_type=='remote':
			tasks=self.n4dserver.write_tasks(self.credentials,"SchedulerServer",task_type,tasks)
		else:
			tasks=self.n4dclient.write_tasks(self.credentials,"SchedulerServer",task_type,tasks)
		self._debug(tasks)
		return True
	#def write_tasks

	def remove_task(self,task_name,task_serial,task_cmd,task_type):
		self._debug("Removing task from %s server"%task_type)
		if task_type=='remote':
			tasks=self.n4dserver.remove_task(self.credentials,"SchedulerServer",task_type,task_name,task_serial,task_cmd)
		else:
			tasks=self.n4dclient.remove_task(self.credentials,"SchedulerServer",task_type,task_name,task_serial,task_cmd)
		self._debug(tasks)
	#def remove_task

	def _n4d_connect(self,server):
		#Setup SSL
		context=ssl._create_unverified_context()
		n4dclient = n4d.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		return(n4dclient)
	#def _n4d_connect
