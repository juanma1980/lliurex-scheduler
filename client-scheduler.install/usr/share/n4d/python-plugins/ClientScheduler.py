#!/usr/bin/env python
###
#
###

import os
import xmlrpclib

crondir='/etc/cron.d'
task_prefix='sched-' #Temp workaround->Must be declared on a n4d var
n4d=xmlrpclib.ServerProxy("https://server:9779")
tasks=n4d.get_tasks("","ServerScheduler",'remote')
task_files=[]
for task in tasks:
	for task_name,task_data in task.items():
		fname=crondir+'/'+task_prefix+'/'+task_name.replace(' ','_')
		task_files.append(fname)
		cron_array=[]
		for task_serial,task_info in task_data.items():
			cron_task=("%s %s %s %s %s %s"%(task_info['m'],task_info['h'],task_info['dom'],task_info['mon'],\
							task_info['dow'],task_info['cmd']))

			cron_array.append(cron_task)
		for cron_line in cron_array:
			with open(fname,'w') as data:
				data.write(cron_line)


