#!/usr/bin/env python
###
#
###

import os
import threading
import time
import xmlrpclib as xmlrpc

class SchedulerClient():
	def __init__(self):
		self.cron_dir='/etc/cron.d'
		self.task_prefix='remote-' #Temp workaround->Must be declared on a n4d var
		self.cron_dir='/etc/cron.d'
		self.count=0
		self.dbg=0

	def startup(self,options):
		t=threading.Thread(target=self._main_thread)
		t.daemon=True
		t.start()

	def _debug(self,msg):
		if self.dbg:
			print(str(msg))

	def _main_thread(self):
		objects["VariablesManager"].register_trigger("SCHEDULED_TASKS","SchedulerClient",self.process_tasks)
		tries=10
		for x in range (0,tries):
			self.scheduler_var=objects["VariablesManager"].get_variable("SCHEDULED_TASKS")
			if self.scheduler_var!=self.count:
				self.count=self.scheduler_var
				self.process_tasks()
				break
			else:
				time.sleep(1)

	def process_tasks(self,data=None):
		self._debug("Scheduling tasks")
		prefixes=['remote','local']
		for prefix in prefixes:
			if prefix=='remote':
				n4d=xmlrpc.ServerProxy("https://server:9779")
			else:
				n4d=xmlrpc.ServerProxy("https://localhost:9779")
			tasks=n4d.get_tasks("","ServerScheduler",prefix)
			#Create the cron files
			task_names={}
			for task in tasks:
				for name in task.keys():
					self._debug("Scheduling %s"%name)
					fname=name.replace(' ','_')
					task_names[fname]=task
					self._write_crontab_for_task(task_names[fname],prefix)

			#If a file is not in tasks delete it
			for f in os.listdir(self.cron_dir):
				if f.startswith(prefix):
					fname=f.replace(prefix,'')
					if fname not in task_names.keys():
						os.remove(cron_dir+'/'+f)
	#def process_tasks

	def _write_crontab_for_task(self,ftask,prefix):
		task=list(ftask.keys())[0]
		for task_name,task_data in ftask.items():
			fname=self.cron_dir+'/'+prefix+task_name.replace(' ','_')
			cron_array=[]
			for task_serial,task_info in task_data.items():
				cron_task=("%s %s %s %s %s %s"%(task_info['m'],task_info['h'],task_info['dom'],\
								task_info['mon'],task_info['dow'],task_info['cmd']))
				cron_array.append(cron_task)
			if task_data:
				with open(fname,'w') as data:
					for cron_line in cron_array:
						data.write(cron_line+"\n")
	#def _write_crontab_for_task

