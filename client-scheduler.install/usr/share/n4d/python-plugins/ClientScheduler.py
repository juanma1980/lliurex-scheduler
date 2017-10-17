#!/usr/bin/env python
###
#
###

import os
import xmlrpclib

def _write_crontab_for_task(ftask):
	task=list(ftask.keys())[0]
	for task_name,task_data in ftask.items():
		fname=cron_dir+'/'+task_prefix+task_name.replace(' ','_')
		cron_array=[]
		for task_serial,task_info in task_data.items():
			cron_task=("%s %s %s %s %s %s"%(task_info['m'],task_info['h'],task_info['dom'],task_info['mon'],\
						task_info['dow'],task_info['cmd']))

			cron_array.append(cron_task)
		with open(fname,'w') as data:
			for cron_line in cron_array:
				data.write(cron_line+"\n")


cron_dir='/etc/cron.d'
task_prefix='remote-' #Temp workaround->Must be declared on a n4d var
n4d=xmlrpclib.ServerProxy("https://server:9779")
tasks=n4d.get_tasks("","ServerScheduler")

print("Scheduling tasks")
#Create a dict with the task names
task_names={}
for task in tasks:
	for name in task.keys():
		print("Scheduling %s"%name)
		fname=name.replace(' ','_')
		task_names[fname]=task
		_write_crontab_for_task(task_names[fname])

for f in os.listdir(cron_dir):
	if f.startswith(task_prefix):
		fname=f.replace(task_prefix,'')
		if fname not in task_names.keys():
#			self._debug("Removing %s"%f)
#			self._debug("%s"%task_names)
			#Task is not scheduled, delete it
			os.remove(cron_dir+'/'+f)

