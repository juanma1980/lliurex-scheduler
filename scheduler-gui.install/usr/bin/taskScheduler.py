#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
import json
import cairo
import os
import shutil
import threading
import platform
import subprocess
import sys
import time
#import commands
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, PangoCairo, Pango

from clientScheduler import clientScheduler as scheduler

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import gettext
gettext.textdomain('lliurex-up')
_ = gettext.gettext



#BASE_DIR="/usr/share/taskScheduler/"
BASE_DIR="../share/taskScheduler/"
GLADE_FILE=BASE_DIR+"rsrc/taskScheduler.ui"
REMOVE_ICON=BASE_DIR+"rsrc/trash.svg"
LOCK_PATH="/var/run/taskScheduler.lock"

class TaskDetails:
	
	def __init__(self):
		up=True

	def _format_widget_for_grid(self,widget):
		#common
		print(str(type(widget)))
		widget.set_hexpand(False)
		widget.set_halign(Gtk.Align.CENTER)
		widget.set_valign(Gtk.Align.CENTER)
		if 'Gtk.Button' in str(type(widget)):
			pass
		elif 'Gtk.Entry' in str(type(widget)):
			widget.set_alignment(xalign=0.5)
			widget.set_max_length(2)
			widget.set_width_chars(2)
			widget.set_max_width_chars(3)

	def render(self,gtkGrid,btn_apply=True):
		self.chk_monday=Gtk.ToggleButton(_("Monday"))
		self.chk_thursday=Gtk.ToggleButton(_("Thursday"))
		self.chk_wednesday=Gtk.ToggleButton(_("Wednesday"))
		self.chk_tuesday=Gtk.ToggleButton(_("Tuesday"))
		self.chk_friday=Gtk.ToggleButton(_("Friday"))
		self.chk_saturday=Gtk.ToggleButton(_("Saturday"))
		self.chk_sunday=Gtk.ToggleButton(_("Sunday"))
		self.btn_monthUp=Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_GO_UP))
		self._format_widget_for_grid(self.btn_monthUp)
		self.txt_month=Gtk.Entry()
		self._format_widget_for_grid(self.txt_month)
		self.chk_monthly=Gtk.CheckButton("Monthly")
		self._format_widget_for_grid(self.chk_monthly)
		self.btn_monthDown=Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_GO_DOWN))
		self._format_widget_for_grid(self.btn_monthDown)
		self.btn_dayUp=Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_GO_UP))
		self._format_widget_for_grid(self.btn_dayUp)
		self.txt_day=Gtk.Entry()
		self._format_widget_for_grid(self.txt_day)
		self.btn_dayDown=Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_GO_DOWN))
		self._format_widget_for_grid(self.btn_dayDown)
		self.chk_daily=Gtk.CheckButton("Daily")
		self._format_widget_for_grid(self.chk_daily)
		self.chk_weekly=Gtk.CheckButton("Weekly")
		self._format_widget_for_grid(self.chk_weekly)
		self.btn_hourUp=Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_GO_UP))
		self._format_widget_for_grid(self.btn_hourUp)
		self.txt_hour=Gtk.Entry()
		self._format_widget_for_grid(self.txt_hour)
		self.btn_hourDown=Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_GO_DOWN))
		self._format_widget_for_grid(self.btn_hourDown)
		self.chk_hourly=Gtk.CheckButton("Hourly")
		self._format_widget_for_grid(self.chk_hourly)
		self.btn_minUp=Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_GO_UP))
		self._format_widget_for_grid(self.btn_minUp)
		self.txt_min=Gtk.Entry()
		self._format_widget_for_grid(self.txt_min)
		self.btn_minDown=Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_GO_DOWN))
		self._format_widget_for_grid(self.btn_minDown)
		self.btn_apply=Gtk.Button(stock=Gtk.STOCK_APPLY)
		label=Gtk.Label(_("Month"))
		gtkGrid.add(label)
		gtkGrid.attach_next_to(self.btn_monthUp,label,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.txt_month,self.btn_monthUp,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.btn_monthDown,self.txt_month,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_monthly,self.btn_monthDown,Gtk.PositionType.BOTTOM,1,1)
		label=Gtk.Label(("Day of month"))
		gtkGrid.add(label)
		gtkGrid.attach_next_to(self.btn_dayUp,label,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.txt_day,self.btn_dayUp,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.btn_dayDown,self.txt_day,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_daily,self.btn_dayDown,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(Gtk.Label(("Day of week")),label,Gtk.PositionType.RIGHT,2,1)
		gtkGrid.attach_next_to(self.chk_monday,self.btn_dayUp,Gtk.PositionType.RIGHT,1,1)
		gtkGrid.attach_next_to(self.chk_tuesday,self.chk_monday,Gtk.PositionType.RIGHT,1,1)
		gtkGrid.attach_next_to(self.chk_wednesday,self.chk_monday,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_thursday,self.chk_wednesday,Gtk.PositionType.RIGHT,1,1)
		gtkGrid.attach_next_to(self.chk_friday,self.chk_wednesday,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_saturday,self.chk_friday,Gtk.PositionType.RIGHT,1,1)
		gtkGrid.attach_next_to(self.chk_sunday,self.chk_friday,Gtk.PositionType.BOTTOM,1,1)
		label=Gtk.Label(_("Hour"))
		gtkGrid.add(label)
		gtkGrid.attach_next_to(self.btn_hourUp,label,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.txt_hour,self.btn_hourUp,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.btn_hourDown,self.txt_hour,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_hourly,self.btn_hourDown,Gtk.PositionType.BOTTOM,1,1)
		label=Gtk.Label(_("Minute"))
		gtkGrid.add(label)
		gtkGrid.attach_next_to(self.btn_minUp,label,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.txt_min,self.btn_minUp,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.btn_minDown,self.txt_min,Gtk.PositionType.BOTTOM,1,1)
		if btn_apply:
			gtkGrid.attach(self.btn_apply,5,14,1,1)
		return(gtkGrid)

	def load_task_details(self,task_data):
		self.txt_min.set_text('0')
		self.txt_hour.set_text('0')
		self.chk_hourly.set_active(False)
		self.txt_day.set_text('0')
		self.chk_daily.set_active(False)
		self.txt_month.set_text('0')
		self.chk_monthly.set_active(False)
		self.chk_weekly.set_active(False)

		if task_data['m'].isdigit():
			self.txt_min.set_text(task_data['m'])
		else:
			self.txt_min.set_text('0')

		if task_data['h'].isdigit():
			self.txt_hour.set_text(task_data['h'])
		elif task_data['h']=='*':
			self.chk_hourly.set_active(True)
		else:
			self.txt_hour.set_text('0')


		if task_data['dom'].isdigit():
			self.txt_day.set_text(task_data['dom'])
		else:
			self.txt_day.set_text('0')
			self.chk_daily.set_active(True)

		if task_data['mon'].isdigit():
			self.txt_month.set_text(task_data['mon'])
		else:
			self.txt_month.set_text('0')
			self.chk_monthly.set_active(True)

		if task_data['dow'].isdigit():
			self.chk_weekly.set_active(True)
	#def load_task_details
	
	def put_task_details(self,widget,task_name,task_cmd,taskFilter):
		m=self.txt_min.get_text()
		h=self.txt_hour.get_text()
		dom=self.txt_day.get_text()
		mon=self.txt_month.get_text()
		dow='*'
		hidden=0
		details={}
		details={'m':m,'h':h,'dom':dom,'mon':mon,'dow':dow,'hidden':hidden}
		self.tasks={}
		print(details)
#		with open('/home/lliurex/borrar/tasks.json') as json_data:
#			tasks=json.load(json_data)
		if task_name in self.tasks:
			self.tasks[task_name][task_cmd]=details
		else: 
			self.tasks[task_name]={task_cmd:details}

#		with open('/home/lliurex/borrar/tasks.json','w') as json_data:
#			json.dump(tasks,json_data)

	def get_task_details(self):
		return self.tasks

class TaskScheduler:

	def __init__(self):
		self.check_root()
			
	#def __init__		

	def isscheduler_running(self):

		if os.path.exists(LOCK_PATH):
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Lliurex UP")
			dialog.format_secondary_text(_("Lliurex Up is now running."))
			dialog.run()
			sys.exit(1)

	def check_root(self):
		
		try:
			print ("  [taskScheduler]: Checking root")
			f=open("/etc/lliurex-up.token","w")
			f.close()
		except:
			print ("  [taskScheduler]: No administration privileges")
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "taskScheduler")
			dialog.format_secondary_text(_("You need administration privileges to run this application."))
			dialog.run()
			sys.exit(1)
		
	#def check_root

	def start_gui(self):
		self.scheduler_client=scheduler()
		builder=Gtk.Builder()
		builder.set_translation_domain('taskScheduler')

		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

		glade_path=GLADE_FILE
		builder.add_from_file(glade_path)

		self.window=builder.get_object("main_window")
		self.main_box=builder.get_object("main_box")
	
		self.scheduler_box=builder.get_object("scheduler_box")
		self.view_tasks_button_box=builder.get_object("view_tasks_button_box")
		self.view_tasks_eb=builder.get_object("view_tasks_eventbox")
		self.btn_signal_id=None
		#Toolbar
		btn_add_task=builder.get_object("btn_add_task")
		btn_add_task.connect("button-release-event", self.add_task_clicked)
		self.btn_remote_tasks=builder.get_object("btn_remote_tasks")
		self.btn_local_tasks=builder.get_object("btn_local_tasks")
		self.btn_remote_tasks.connect("clicked",self.view_tasks_clicked,'remote')
		self.btn_local_tasks.connect("clicked",self.view_tasks_clicked,'local')
		#tasks list
		self.tasks_box=builder.get_object("tasks_box")
		self.tasks_label=builder.get_object("tasks_label")
		self.tasks_tv=builder.get_object("tasks_treeview")
		self.task_details_grid=TaskDetails()
		td_grid=self.task_details_grid.render(builder.get_object("task_details_grid"))
		self.tasks_store=Gtk.ListStore(str,str,GdkPixbuf.Pixbuf)
		self.tasks_tv.set_model(self.tasks_store)

		column=Gtk.TreeViewColumn(_("Task"))
		cell=Gtk.CellRendererText()
		column.pack_start(cell,True)
		column.add_attribute(cell,"markup",0)
		column.set_expand(True)
		self.tasks_tv.append_column(column)
		self.tasks_tv.connect("button-release-event",self.task_clicked)
		self.tasks_tv.connect("cursor-changed",self.task_clicked)
		
		column=Gtk.TreeViewColumn(_("When"))
		cell=Gtk.CellRendererText()
		cell.set_property("alignment",Pango.Alignment.CENTER)
		column.pack_start(cell,False)
		column.add_attribute(cell,"markup",1)
		column.set_expand(True)
		self.tasks_tv.append_column(column)		

		column=Gtk.TreeViewColumn(_("Remove"))
		cell=Gtk.CellRendererPixbuf()
		column.pack_start(cell,True)
		column.add_attribute(cell,"pixbuf",2)
		self.col_remove=column
		self.tasks_tv.append_column(column)

		#Add tasks
		self.add_task_box=builder.get_object("add_task_box")
		self.add_task_grid=TaskDetails()
		at_grid=self.add_task_grid.render(builder.get_object("add_task_grid"),False)
		builder.get_object("btn_cancel_add").connect("button-release-event", self.cancel_add_clicked)
		self.cmb_task_names=builder.get_object("cmb_task_names")
		self.cmb_task_cmds=builder.get_object("cmb_task_cmds")
		self.swt_remote=builder.get_object("swt_remote")
		self.swt_local=builder.get_object("swt_local")

		self.stack.add_titled(self.tasks_box, "tasks", "Tasks")
		self.stack.add_titled(self.add_task_box, "add", "Add Task")
		
		#Icons
		image=Gtk.Image()
		image.set_from_file(REMOVE_ICON)		
		self.remove_icon=image.get_pixbuf()

		self.main_box.pack_start(self.stack,True,False,5)

		self.window.show_all()
		
		self.window.connect("destroy",self.quit)
		
		self.set_css_info()
		
		self.task_list=[]

		GObject.threads_init()
		self.btn_remote_tasks.set_active(True)
		Gtk.main()

	#def start_gui
	
	def set_css_info(self):
	
		css = b"""


		#WHITE_BACKGROUND {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#ffffff),  to (#ffffff));;
		
		}

		#BUTTON_LABEL{
			color:white;
			font: Roboto 10;
		}

		#DISABLED_BUTTON_OVER{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#888888),  to (#888888));;
		}
		
		#DISABLED_BUTTON{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#666666),  to (#666666));;
		}
		
		#CANCEL_BUTTON{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#D32F2F),  to (#D32F2F));;
		}
		
		#CANCEL_BUTTON_OVER{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#F44336),  to (#F44336));;
		}

		#BUTTON_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#448AFF),  to (#448AFF));;
		
		}
		
		#BUTTON_OVER_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#449fff),  to (#449fff));;
			
		
		}

		#LOCAL_BUTTON_LABEL{
			color:white;
			font: Roboto 11;
		}
		
		#UPDATE_CORRECT_BUTTON_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#43A047),  to (#43A047));;
		
		}

		#UPDATE_OVER_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#53b757),  to (#53b757));;
		
		}


		#UPDATE_ERROR_BUTTON_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#D32F2F),  to (#D32F2F));;
		
		}

		#UPDATE_LAUNCHED_OVER_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#F44336),  to (#F44336));;
		
		}

		#LOCAL_BUTTON_LAUNCHED_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#bdbdbd), to (#bdbdbd));;

		}
				
		#GATHER_ICON_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#b0bec5),  to (#b0bec5));;
		
		}
		
		
		#BLUE_FONT {
			color: #3366cc;
			font: Roboto Bold 11;
			
		}	
		

		#TASKGRID_FONT {
			color: #3366cc;
			font: Roboto 11;
			
		}

		#LABEL_OPTION{
		
			color: #808080;
			font: Roboto 11;
		}

		#ERROR_FONT {
			color: #CC0000;
			font: Roboto Bold 11; 
		}
		
		#DISABLED_BUTTON{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#666666),  to (#666666));;
		}
		"""

		self.style_provider=Gtk.CssProvider()
		self.style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		
		self.window.set_name("WHITE_BACKGROUND")
		self.scheduler_box.set_name("WHITE_BACKGROUND")
		self.tasks_box.set_name("WHITE_BACKGROUND")
#		self.task_details_grid.set_name("TASKGRID_FONT")
	#def set_css_info	
	
	def populate_tasks_tv(self,parm):
		self.scheduled_tasks={}
		tasks=[]
		tasks=self.scheduler_client.get_tasks(parm)
		self.tasks_store.clear()
		
		for task in tasks:
			for taskDesc,taskData in task.items():
				self.scheduled_tasks[taskDesc]=taskData
				print("Adding %s" % taskDesc)
				for cmd,calendar in taskData.items():
					print("Parsing "+str(calendar))
					parsed_calendar=self.parse_taskData(calendar)
					self.tasks_store.append(("<span font='Roboto'><b>"+cmd+"</b></span>\n"+"<span font='Roboto' size='small'><i>"+taskDesc+"</i></span>","<span font='Roboto' size='small'>"+parsed_calendar+"</span>",self.remove_icon))
	#def populate_tasks_tv

	###
	#Input: dict
	###
	def parse_taskData(self,taskData):
		parsed_data=[]
		parsed_calendar=''
		expr={}
		day_dict={'1':'Mo','2':'Tu','3':'We','4':'Th','5':'Fr','6':'Sa','7':'Su','*':'every'}
		mon_dict={'1':'Jan','2':'Feb','3':'Mar','4':'Apr','5':'May','6':'Jun','7':'Jul','8':'Aug','9':'Sep','10':'Oct','11':'Nov','12':'Dec','*':'every'}
		mon_expr=self.parse_cron_expression(taskData['mon'],mon_dict)
		dow_expr=self.parse_cron_expression(taskData['dow'],day_dict)
		dom_expr=self.parse_cron_expression(taskData['dom'])
		min_expr=self.parse_cron_expression(taskData['m'])
		hou_expr=self.parse_cron_expression(taskData['h'])
		time_expr=self.parse_time_expr(hou_expr,min_expr)
		date_expr=self.parse_date_expr(mon_expr,dow_expr,dom_expr)
		parsed_data=" ".join([time_expr,date_expr])
		if parsed_data[0].isdigit():	
			parsed_calendar="At " + parsed_data
		else:
			parsed_calendar=parsed_data
		return parsed_calendar.capitalize()
	#def parse_taskData(self,taskData):

	def parse_time_expr(self,hour,minute):
		sw_err=False
		try:
			int(hour)
			int(minute)
		except:
			sw_err=True
		if not sw_err:
			time_expr=hour+':'+minute
		else:
			if minute!='every':
				minute=minute+' '+_("minutes")
			else:
				minute='each minute'
			if hour!='every':
				hour=hour+' '+_("o'clock")
				time_expr=_("%s %s" % (hour,minute))
			else:
				hour=hour+' '+_("hour")
				time_expr=_("%s of %s" % (minute,hour))
		return time_expr
	#def parse_time_expr

	def parse_date_expr(self,mon,dow,dom):
		sw_err=False
		time_expr=''
		try:
			int(dom)
			int(mon)
		except:
			sw_err=True
		time_expr=_("%s %s" % (dom,mon))
		if sw_err:
			if dom=='every':
				dom=_("everyday")
			elif mon=='every' in mon:
				dom=_(("day %s") % dom)
			elif ',' in dom:
				dom=_(("days %s") % dom)
			elif 'from' in dom:
				dom=_(("days %s") % dom)
			if mon=='every':
				mon=_('every month')
			time_expr="%s %s" % (dom,mon)

		if dow!='every':
			time_expr=_("on %s, %s" % (dow,time_expr))
		else:
			time_expr=_("on %s" % time_expr)

		return time_expr
	#def parse_time_expr

	def parse_cron_expression(self,data,description_dict={}):
		(each,at_values,range_values,extra_range,values)=('','','','','')
#	*/2 -> Each two time units
#	1-2 -> Range between 1 and 2
#	1,2 -> At 1 and 2
#	1 -> direct value
		if data in description_dict.keys():
			values=description_dict[data]
		else:
			if '/' in data:
				expr=data.split('/')
				each=expr[-1]
				data=expr[0]
			if ',' in data:
				at_values=data.split(',')
				value_desc=[]
				for value in at_values:
					if '-' in value:
						extra_range=value
					else:
						if value in description_dict.keys():
							value_desc.append(description_dict[value])
				at_values=value_desc
			if '-' in data or extra_range:
				if extra_range:
					data=extra_range
				range_values=data.split('-')
				value_desc=[]
				for value in range_values:
					if value in description_dict.keys():
						value_desc.append(description_dict[value])
				if value_desc:
					range_values=value_desc
		(str_range,str_each,str_at)=('','','')
		if range_values:
			str_range=(_("from %s to %s ") % (range_values[0],range_values[1]))
		if each:
			str_each=(_("each %s ") % each)
		if at_values:
			if range_values:
				str_at=(_("and %s and %s") % (','.join(at_values[:-1]),at_values[-1]))
			else:
				str_at=(_("at %s and %s") % (','.join(at_values[:-1]),at_values[-1]))

		retval=str_range+str_at+str_each+values
		if retval=='':
			if len(data)<2 and data!='*':
				data='0'+data
			elif data=='*':
				data='every'
			retval=data
		return (retval.rstrip('\n'))
	#def parse_cron_expression

	def task_clicked(self,treeview,event=None):
		sw_show=True
		if event!=None:
			row=self.tasks_tv.get_path_at_pos(int(event.x),int(event.y))
			col=row[1]
			if col==self.col_remove:
				sw_show=False
		selection=self.tasks_tv.get_selection()
		model,data=selection.get_selected()
		if sw_show:
			if self.btn_remote_tasks.get_active():
				taskFilter='remote'
			else:
				taskFilter='local'
			task_id=model[data][0].split('\n')
			task_cmd=task_id[0][task_id[0].find("<b>")+3:task_id[0].find("</b>")]
			task_name=task_id[1][task_id[1].find("<i>")+3:task_id[1].find("</i>")]
			if task_name in self.scheduled_tasks.keys():
				if task_cmd in self.scheduled_tasks[task_name].keys():
					task_data=self.scheduled_tasks[task_name][task_cmd]
					print("Loading details of task %s of group %s"% (task_cmd,task_name))
#			self.load_task_details(task_data)
					self.task_details_grid.load_task_details(task_data)
			if self.btn_signal_id:
				self.task_details_grid.btn_apply.disconnect(self.btn_signal_id)
			self.btn_signal_id=self.task_details_grid.btn_apply.connect("clicked",self.task_details_grid.put_task_details,task_name,task_cmd,taskFilter)

#			if taskFilter=='remote':
#				self.btn_remote_tasks.set_active(False)
#				self.btn_remote_tasks.set_active(True)
#			else:
#				self.btn_local_task.set_active(False)
#				self.btn_local_task.set_active(True)
		else:
			model.remove(data)
	#def task_clicked			

	def save_task_details(self,widget,task_name,task_cmd):
		taskFilter='local'
		if self.btn_remote_tasks.get_active():
			taskFilter='remote'
		m=self.txt_min.get_text()
		h=self.txt_hour.get_text()
		dom=self.txt_day.get_text()
		mon=self.txt_month.get_text()
		dow='*'
		hidden=0
		details={}
		details={'m':m,'h':h,'dom':dom,'mon':mon,'dow':dow,'hidden':hidden}
		with open('/home/lliurex/borrar/tasks.json') as json_data:
			tasks=json.load(json_data)
		if task_name in tasks:
			tasks[task_name][task_cmd]=details
		else: 
			tasks[task_name]={task_cmd:details}

		with open('/home/lliurex/borrar/tasks.json','w') as json_data:
			json.dump(tasks,json_data)

		if taskFilter=='remote':
			self.btn_remote_tasks.set_active(False)
			self.btn_remote_tasks.set_active(True)
		else:
			self.btn_local_task.set_active(False)
			self.btn_local_task.set_active(True)

		return True

	def view_tasks_clicked(self,widget,parm):
		if not widget.get_active():
			return True
		print("loading %s tasks" % parm)
		if parm=='remote':
			self.btn_local_tasks.set_active(False)
		else:
			self.btn_remote_tasks.set_active(False)
		self.populate_tasks_tv(parm)
		self.tasks_tv.set_model(self.tasks_store)
		self.tasks_tv.set_cursor(0)
		self.cancel_add_clicked(widget,parm)
	#def view_tasks_clicked	

	def load_add_task_details(self):
		tasks=[]
		names=[]
		self.cmb_task_names.remove_all()
		tasks=self.scheduler_client.get_tasks('local')
		tasks.extend(self.scheduler_client.get_tasks('remote'))
		for task in tasks:
			for name in task.keys():
				if name not in names:
					names.append(name)
					self.cmb_task_names.append_text(name)

		self.cmb_task_names.connect('changed',self.load_add_task_details_cmds,tasks)
		self.cmb_task_names.set_active(0)
		if self.btn_remote_tasks.get_active():
			self.swt_remote.set_active(1)
			self.swt_local.set_active(0)
		else:
			self.swt_local.set_active(1)
			self.swt_remote.set_active(0)

	def load_add_task_details_cmds(self,widget,tasks):
		cmds=[]
		self.cmb_task_cmds.remove_all()
		task_name=self.cmb_task_names.get_active_text()
		for task in tasks:
			for cmd in task[task_name].keys():
				if cmd not in cmds:
					cmds.append(cmd)
					self.cmb_task_cmds.append_text(cmd)
		self.cmb_task_cmds.set_active(0)
	
	def add_task_clicked(self,widget,event):
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack.set_visible_child_name("add")
		self.load_add_task_details()
	#def view_packages_clicked	

	def cancel_add_clicked(self,widget,event):
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		self.stack.set_visible_child_name("tasks")	
		
	#def arrow_clicked

	def quit(self,widget,event=None):
		Gtk.main_quit()	

	#def quit	

#class TaskScheduler

tes=TaskScheduler()
tes.start_gui()		
