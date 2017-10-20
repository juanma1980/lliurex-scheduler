#!/usr/bin/env python
###
#
###

import os
import threading
import time

class SchedulerClient():
	def __init__(self):
		self.cron_dir='/etc/cron.d'
		self.task_prefix='remote-' #Temp workaround->Must be declared on a n4d var
		self.cron_dir='/etc/cron.d'
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
			if self.scheduler_var!=None:
				self.process_tasks()
				break
			else:
				time.sleep(1)

	def process_tasks(self):
		tasks=objects["ServerScheduler"].get_tasks("")
		self._debug("Scheduling tasks")
		#Create the cron files
		task_names={}
		for task in tasks:
			for name in task.keys():
				self._debug("Scheduling %s"%name)
				fname=name.replace(' ','_')
				task_names[fname]=task
				_write_crontab_for_task(task_names[fname])

		#If a file is not in tasks delete it
		for f in os.listdir(self.cron_dir):
			if f.startswith(self.task_prefix):
				fname=f.replace(self.task_prefix,'')
				if fname not in task_names.keys():
					os.remove(cron_dir+'/'+f)
	#def process_tasks

	def _write_crontab_for_task(ftask):
		task=list(ftask.keys())[0]
		for task_name,task_data in ftask.items():
			fname=self.cron_dir+'/'+self.task_prefix+task_name.replace(' ','_')
			cron_array=[]
			for task_serial,task_info in task_data.items():
				cron_task=("%s %s %s %s %s %s"%(task_info['m'],task_info['h'],task_info['dom'],\
								task_info['mon'],task_info['dow'],task_info['cmd']))
				cron_array.append(cron_task)
			with open(fname,'w') as data:
				for cron_line in cron_array:
					data.write(cron_line+"\n")
	#def _write_crontab_for_task

