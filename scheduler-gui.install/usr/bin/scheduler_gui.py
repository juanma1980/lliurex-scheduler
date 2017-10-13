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
from cronParser import cronParser
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

	def _load_interval_data(self,widget=None):
		position=self.cmb_interval.get_active()
		self.cmb_interval.remove_all()
		date=self.cmb_dates.get_active_text()
		total=24
		if date==_("day(s)"):
			total=7
			self.day_box.set_sensitive(False)
			self.month_box.set_sensitive(True)
			self.hour_box.set_sensitive(True)
			self._activate_days(False)
		elif date==_("hour(s)"):
			total=24
			self.day_box.set_sensitive(True)
			self.month_box.set_sensitive(True)
			self.hour_box.set_sensitive(False)
			self._activate_days(True)
		elif date==_("week(s)"):
			total=4
			self.day_box.set_sensitive(False)
			self.month_box.set_sensitive(True)
			self.hour_box.set_sensitive(True)
			self._activate_days(False)
		elif date==_("month(s)"):
			total=12
			self.day_box.set_sensitive(True)
			self.month_box.set_sensitive(False)
			self.hour_box.set_sensitive(True)
			self._activate_days(True)
		for i in range(total):
			self.cmb_interval.append_text(str(i+1))
		if position>=total:
			position=total-1
		elif position<0:
			position=0
		self.cmb_interval.set_active(position)

	def _load_date_data(self):
		date=[_("hour(s)"),_("day(s)"),_("week(s)"),_("month(s)")]
		for i in date:
			self.cmb_dates.append_text(i)
		self.cmb_dates.set_active(0)
	
	def _load_special_date_data(self):
		date=[_("Last month day"),_("First month day")]
		for i in date:
			self.cmb_special_dates.append_text(i)
		self.cmb_special_dates.set_active(0)

	def _load_hours_data(self):
		for i in range(24):
			self.cmb_hours.append_text(str(i))
		self.cmb_hours.set_active(0)

	def _load_minutes_data(self):
		for i in range(0,60,5):
			self.cmb_minutes.append_text(str(i))
		self.cmb_minutes.set_active(0)

	def _load_months_data(self):
		self.cmb_months.append_text("Every month")
		for i in range(12):
			self.cmb_months.append_text(str(i+1))
		self.cmb_months.set_active(0)
	
	def _load_days_data(self,max=31):
		self.cmb_days.append_text("Everyday")
		for i in range(max):
			self.cmb_days.append_text(str(i+1))
		self.cmb_days.set_active(0)

	def render_basic(self,gtkGrid,btn_apply=True):
		self.chk_monday=Gtk.ToggleButton(_("Monday"))
		self.chk_thursday=Gtk.ToggleButton(_("Thursday"))
		self.chk_wednesday=Gtk.ToggleButton(_("Wednesday"))
		self.chk_tuesday=Gtk.ToggleButton(_("Tuesday"))
		self.chk_friday=Gtk.ToggleButton(_("Friday"))
		self.chk_saturday=Gtk.ToggleButton(_("Saturday"))
		self.chk_sunday=Gtk.ToggleButton(_("Sunday"))
		self.chk_daily=Gtk.CheckButton("Daily")
		self.chk_hourly=Gtk.CheckButton("Hourly")
		self.chk_weekly=Gtk.CheckButton("Weekly")
		self.chk_interval=Gtk.CheckButton("Interval")
		self.cmb_interval=Gtk.ComboBoxText()
		self.cmb_dates=Gtk.ComboBoxText()
		self._load_interval_data()
		self._load_date_data()
		self.chk_special_dates=Gtk.CheckButton("Special cases")
		self.cmb_special_dates=Gtk.ComboBoxText()
		self._load_special_date_data()
		self.chk_fixed_date=Gtk.CheckButton("Fixed date")
		self.day_box=Gtk.Box()
		self.day_box.set_homogeneous(True)
		self.cmb_days=Gtk.ComboBoxText()
		self.day_box.add(Gtk.Label(_("Day")))
		self.day_box.add(self.cmb_days)
		self.month_box=Gtk.Box()
		self.month_box.set_homogeneous(True)
		self.cmb_months=Gtk.ComboBoxText()
		self.month_box.add(Gtk.Label(_("Month")))
		self.month_box.add(self.cmb_months)
		self.hour_box=Gtk.Box()
		self.hour_box.set_homogeneous(True)
		self.cmb_hours=Gtk.ComboBoxText()
		self.hour_box.add(Gtk.Label(_("Hour")))
		self.hour_box.add(self.cmb_hours)
		self.minute_box=Gtk.Box()
		self.minute_box.set_homogeneous(True)
		self.cmb_minutes=Gtk.ComboBoxText()
		self.minute_box.add(Gtk.Label(_("Minutes")))
		self.minute_box.add(self.cmb_minutes)
		self._load_minutes_data()
		self._load_hours_data()
		self._load_days_data()
		self._load_months_data()

		self.lbl_info=Gtk.Label("")
		self.lbl_info.set_margin_bottom(12)
		self.lbl_info.set_opacity(0.6)
		gtkGrid.attach(self.lbl_info,0,0,8,2)
		label=Gtk.Label(_("Days of week"))
		gtkGrid.attach(label,0,2,2,1)
		gtkGrid.attach_next_to(self.chk_monday,label,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_tuesday,self.chk_monday,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_wednesday,self.chk_tuesday,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_thursday,self.chk_wednesday,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_friday,self.chk_thursday,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_saturday,self.chk_monday,Gtk.PositionType.RIGHT,1,1)
		gtkGrid.attach_next_to(self.chk_sunday,self.chk_saturday,Gtk.PositionType.BOTTOM,1,1)
		label=Gtk.Label(_("Time & date"))
		gtkGrid.attach(label,2,2,2,1)
		gtkGrid.attach_next_to(self.hour_box,label,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.minute_box,self.hour_box,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_fixed_date,self.minute_box,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.month_box,self.chk_fixed_date,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.day_box,self.month_box,Gtk.PositionType.BOTTOM,1,1)
		label=Gtk.Label(_("Time intervals"))
		gtkGrid.attach(label,4,2,2,1)
		gtkGrid.attach_next_to(self.chk_interval,label,Gtk.PositionType.BOTTOM,1,1)
		self.interval_box=Gtk.Box()
		self.interval_box.add(Gtk.Label(_("Each")))
		self.interval_box.add(self.cmb_interval)
		self.interval_box.add(self.cmb_dates)
		gtkGrid.attach_next_to(self.interval_box,self.chk_interval,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.chk_special_dates,self.interval_box,Gtk.PositionType.BOTTOM,2,1)
		gtkGrid.attach_next_to(self.cmb_special_dates,self.chk_special_dates,Gtk.PositionType.BOTTOM,1,1)
		if btn_apply:
			self.btn_apply=Gtk.Button(stock=Gtk.STOCK_APPLY)
			gtkGrid.attach(self.btn_apply,5,15,1,1)
		#Signals
		gtkGrid.connect("event",self._parse_scheduled)
		self.chk_fixed_date.connect("toggled",self._chk_fixed_dates_status)
		self.chk_monday.connect("toggled",self._enable_fixed_dates)
		self.chk_thursday.connect("toggled",self._enable_fixed_dates)
		self.chk_wednesday.connect("toggled",self._enable_fixed_dates)
		self.chk_tuesday.connect("toggled",self._enable_fixed_dates)
		self.chk_friday.connect("toggled",self._enable_fixed_dates)
		self.chk_saturday.connect("toggled",self._enable_fixed_dates)
		self.chk_sunday.connect("toggled",self._enable_fixed_dates)
		self.chk_interval.connect("toggled",self._chk_interval_status)
		self.chk_special_dates.connect("toggled",self._chk_special_dates_status)
		self.cmb_dates.connect("changed",self._load_interval_data)
		self.cmb_minutes.connect("changed",self._parse_scheduled)
		self.cmb_hours.connect("changed",self._parse_scheduled)
		self.cmb_months.connect("changed",self._parse_scheduled)
		self.cmb_days.connect("changed",self._parse_scheduled)
		self.cmb_interval.connect("changed",self._parse_scheduled)
		#Initial control status
		self.interval_box.set_sensitive(False)
		self.cmb_special_dates.set_sensitive(False)
		self.day_box.set_sensitive(False)
		self.month_box.set_sensitive(False)
		return gtkGrid

	def _chk_interval_status(self,widget):
		if self.chk_interval.get_active():
			self.interval_box.set_sensitive(True)
			self.chk_special_dates.set_sensitive(True)
			self.hour_box.set_sensitive(False)
			self.month_box.set_sensitive(True)
			self.day_box.set_sensitive(not self._get_days_active())
		else:
			self.interval_box.set_sensitive(False)
			if not self.chk_fixed_date.get_active():
				self.month_box.set_sensitive(False)
				self.day_box.set_sensitive(False)
			self.hour_box.set_sensitive(True)
			self.minute_box.set_sensitive(True)
	#def _chk_interval_status
			
	def _chk_fixed_dates_status(self,widget):
		if self.chk_fixed_date.get_active():
			self.day_box.set_sensitive(not self._get_days_active())
			self.month_box.set_sensitive(True)
			self.chk_interval.set_active(False)
			self.chk_special_dates.set_active(False)
		else:
			self.day_box.set_sensitive(False)
			self.month_box.set_sensitive(False)
	#def _chk_interval_status

	def _chk_special_dates_status(self,widget):
		if self.chk_special_dates.get_active():
			self.cmb_special_dates.set_sensitive(True)
			self._activate_days(False)
		else:
			self.cmb_special_dates.set_sensitive(False)
			self._activate_days(True)
	#def _chk_interval_status

	def _get_days_active(self):
		sw_active=False
		widgets=[self.chk_monday,
				self.chk_thursday,
				self.chk_wednesday,
				self.chk_tuesday,
				self.chk_friday,
				self.chk_saturday,
				self.chk_sunday]
		for widget in widgets:
			if widget.get_active():
				sw_active=True
				break
		return sw_active

	def _enable_fixed_dates(self,widget):
		sw_enable=True
		sw_enable=self._get_days_active()
		if sw_enable:
			if self.chk_interval.get_active():
				self._load_interval_data(True)
				self.day_box.set_sensitive(False)
			else:
				self.month_box.set_sensitive(True)
				self.day_box.set_sensitive(False)
		else:
			if self.chk_interval.get_active():
				self._load_interval_data(True)
			else:
				self.day_box.set_sensitive(self.chk_fixed_date.get_active())
				self.month_box.set_sensitive(self.chk_fixed_date.get_active())

	def _activate_days(self,state):
		widgets=[self.chk_monday,
				self.chk_thursday,
				self.chk_wednesday,
				self.chk_tuesday,
				self.chk_friday,
				self.chk_saturday,
				self.chk_sunday]
		for widget in widgets:
			widget.set_sensitive(state)

	def _put_info(self):
			return True

	def _parse_scheduled(self,container,widget=None):
		task_details={}
		parser=cronParser()
		dow=''
		widgets=[self.chk_monday,
			self.chk_thursday,
			self.chk_wednesday,
			self.chk_tuesday,
			self.chk_friday,
			self.chk_saturday,
			self.chk_sunday]
		cont=1
		for day_widget in widgets:
			print(day_widget)
			if day_widget.get_active():
				print("Cont: "+str(cont))
				dow=dow+str(cont)+','
			cont+=1
		if dow:
			dow=dow.rstrip(',')
		else:
			dow='*'
		task_details['dow']=dow
		if self.cmb_months.is_sensitive():
			task_details['mon']=self.cmb_months.get_active_text()
		else:
			task_details['mon']='*'
		if self.cmb_days.is_sensitive():
			task_details['dom']=self.cmb_days.get_active_text()
		else:
			task_details['dom']='*'
		if self.cmb_hours.is_sensitive():
			task_details['h']=self.cmb_hours.get_active_text()
		else:
			task_details['h']='*'
		if self.cmb_minutes.is_sensitive():
			task_details['m']=self.cmb_minutes.get_active_text()
		else:
			task_details['m']='0'

		if self.chk_interval.get_active():
			interval=self.cmb_interval.get_active_text()
			if interval:
				units=self.cmb_dates.get_active_text()
				if units==_("hour(s)"):
					task_details['h']+="/"+interval
				if units==_("day(s)"):
					task_details['dom']="*/"+interval
				if units==_("month(s)"):
					task_details['mon']="*/"+interval
		task_details['hidden']=0
		parser.parse_taskData(task_details)
		self.lbl_info.set_text("Task schedule: "+(parser.parse_taskData(task_details)))

	def load_basic_task_details(self,task_data):
		self._clear_screen()
		if task_data['m'].isdigit():
			cursor=0
			for minute in range(0,60,5):
				if minute>int(task_data['m']):
					break
				cursor+=1
			self.cmb_minutes.set_active(cursor-1)
		else:
			self.cmb_minutes.set_active(0)

		if task_data['h'].isdigit():
			self.cmb_hours.set_active(int(task_data['h']))
		elif task_data['h']=='*':
			self.chk_interval.set_active(True)
			self.cmb_interval.set_active(0)
			self.cmb_dates.set_active(0)
		elif '/' in task_data['h']:
			self.chk_interval.set_active(True)
			interval=task_data['h'].split('/')[-1]
			self.cmb_interval.set_active(0)
			self.cmb_interval.set_active(int(interval)-1)
#			self.txt_hour.set_text('0')

		sw_fixed_mon=False
		sw_fixed_dom=False
		if task_data['dom'].isdigit():
			self.cmb_days.set_active(int(task_data['dom']))
			sw_fixed_dom=True
		else:
			if task_data['dom'].startswith('*'):
				self.chk_interval.set_active(True)
				if '/' in task_data['dom']:
					pos=task_data.split('/')
					self.cmb_interval.set_active(pos[1])
				else:
					self.cmb_interval.set_active(0)
				self.cmb_dates.set_active(1)
				self.day_box.set_sensitive(False)
				self.hour_box.set_sensitive(True)
#		else:
#			self.txt_day.set_text('0')
#			self.chk_daily.set_active(True)

		if task_data['mon'].isdigit():
			self.cmb_months.set_active(int(task_data['mon']))
			sw_fixed_mon=True
		else:
			if task_data['mon'].startswith('*'):
				self.chk_interval.set_active(True)
				if '/' in task_data['mon']:
					pos=task_data.split('/')
					self.cmb_interval.set_active(pos[1])
				else:
					self.cmb_interval.set_active(0)
				self.cmb_dates.set_active(3)
				self.month_box.set_sensitive(False)
				self.hour_box.set_sensitive(True)
#			self.txt_month.set_text('0')
#			self.chk_monthly.set_active(True)

		if sw_fixed_mon and sw_fixed_dom:
			self.chk_fixed_date.set_active(True)

		if task_data['dow'].isdigit():
			array_dow=[task_data['dow']]
		else:
			array_dow=task_data['dow'].split(',')
		for dow in array_dow:
			if dow=="1":
				self.chk_monday.set_active(True)
				continue
			if dow=="2":
				self.chk_tuesday.set_active(True)
				continue
			if dow=="3":
				self.chk_wednesday.set_active(True)
				continue
			if dow=="4":
				self.chk_thursday.set_active(True)
				continue
			if dow=="5":
				self.chk_friday.set_active(True)
				continue
			if dow=="6":
				self.chk_saturday.set_active(True)
				continue
			if dow=="7":
				self.chk_sunday.set_active(True)
				continue
#			self.chk_weekly.set_active(True)

	def _clear_screen(self):
		widgets=[self.chk_monday,
				self.chk_thursday,
				self.chk_wednesday,
				self.chk_tuesday,
				self.chk_friday,
				self.chk_saturday,
				self.chk_sunday]
		for widget in widgets:
			widget.set_active(False)
		self.cmb_hours.set_active(0)
		self.cmb_minutes.set_active(0)
		self.cmb_days.set_active(0)
		self.cmb_months.set_active(0)
		self.cmb_interval.set_active(0)
		self.cmb_dates.set_active(0)
		self.chk_special_dates.set_active(False)
		self.chk_interval.set_active(False)
		self.chk_fixed_date.set_active(False)
	
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
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Task Scheduler")
			dialog.format_secondary_text(_("Task scheduler is now running."))
			dialog.run()
			sys.exit(1)

	def check_root(self):
		
		try:
			print ("  [taskScheduler]: Checking root")
			f=open("/etc/task_sched.token","w")
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
#		td_grid=self.task_details_grid.render_detailed(builder.get_object("task_details_grid"))
		td_grid=self.task_details_grid.render_basic(builder.get_object("task_details_grid"))
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
		at_grid=self.add_task_grid.render_basic(builder.get_object("add_task_grid"),False)
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
					parser=cronParser()
					parsed_calendar=parser.parse_taskData(calendar)
					self.tasks_store.append(("<span font='Roboto'><b>"+cmd+"</b></span>\n"+"<span font='Roboto' size='small'><i>"+taskDesc+"</i></span>","<span font='Roboto' size='small'>"+parsed_calendar+"</span>",self.remove_icon))
	#def populate_tasks_tv

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
#					self.task_details_grid.load_task_details(task_data)
					self.task_details_grid.load_basic_task_details(task_data)
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
