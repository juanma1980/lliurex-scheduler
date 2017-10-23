#! /usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
import json
import cairo
import os
import subprocess
import shutil
import threading
import platform
import subprocess
import sys
import time
#import commands
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, PangoCairo, Pango

from taskscheduler.taskscheduler import TaskScheduler as scheduler
from taskscheduler.cronParser import cronParser
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import gettext
gettext.textdomain('taskscheduler')
_ = gettext.gettext

BASE_DIR="/usr/share/taskscheduler/"
#BASE_DIR="../share/taskscheduler/"
GLADE_FILE=BASE_DIR+"rsrc/taskScheduler.ui"
REMOVE_ICON=BASE_DIR+"rsrc/trash.svg"
LOCK_PATH="/var/run/taskScheduler.lock"

class TaskDetails:
	
	def __init__(self,scheduler):
		self.scheduler=scheduler
		self.task_serial="0"
		self.task_type="remote"
		try:
			self.flavour=subprocess.getoutput("lliurex-version -f")
		except:
			self.flavour="client"

	def _format_widget_for_grid(self,widget):
		#common
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
		elif date==_("hour(s)"):
			total=24
		elif date==_("week(s)"):
			total=4
		elif date==_("month(s)"):
			total=12
		for i in range(total):
			self.cmb_interval.append_text(str(i+1))

		#Set sensitive status
		self._changed_interval()
		#If user changes selection try to activate same value on new interval data or max
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

	def _load_date_time_data(self,date_type):
		inc=0
		jump=0
		time_units=0
		if date_type=='hour':
			time_units=24
			widget=self.cmb_hours
		elif date_type=='minute':
			time_units=60
			jump=5
			widget=self.cmb_minutes
		elif date_type=='month':
			widget=self.cmb_months
			widget.append_text(_("Every month"))
			inc=1
			time_units=12
		elif date_type=='day':
			widget=self.cmb_days
			widget.append_text(_("Every day"))
			inc=1
			time_units=31

		for i in range(time_units):
			if jump:
				if (not i%jump):
					widget.append_text(str(i+inc))
			else:
				widget.append_text(str(i+inc))
		widget.set_active(0)

	def render_form(self,gtkGrid,btn_apply=True):
		self.chk_monday=Gtk.ToggleButton(_("Monday"))
		self.chk_thursday=Gtk.ToggleButton(_("Thursday"))
		self.chk_wednesday=Gtk.ToggleButton(_("Wednesday"))
		self.chk_tuesday=Gtk.ToggleButton(_("Tuesday"))
		self.chk_friday=Gtk.ToggleButton(_("Friday"))
		self.chk_saturday=Gtk.ToggleButton(_("Saturday"))
		self.chk_sunday=Gtk.ToggleButton(_("Sunday"))
		self.chk_daily=Gtk.CheckButton(_("Daily"))
		self.chk_hourly=Gtk.CheckButton(_("Hourly"))
		self.chk_weekly=Gtk.CheckButton(_("Weekly"))
		self.chk_interval=Gtk.CheckButton(_("Interval"))
		self.cmb_interval=Gtk.ComboBoxText()
		self.cmb_dates=Gtk.ComboBoxText()
		self._load_interval_data()
		self._load_date_data()
		self.chk_special_dates=Gtk.CheckButton(_("Special cases"))
		self.cmb_special_dates=Gtk.ComboBoxText()
		self._load_special_date_data()
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

		self.lbl_info=Gtk.Label("")
		self.lbl_info.set_margin_bottom(24)
		self.lbl_info.set_opacity(0.6)
		gtkGrid.attach(self.lbl_info,0,0,8,2)
		dow_frame=Gtk.Frame()
		dow_frame.set_shadow_type(Gtk.ShadowType.OUT)
		frame_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
		dow_frame.add(frame_box)
		label=Gtk.Label(_("Days of week"))
		frame_box.add(label)
		dow_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		frame_box.add(dow_box)
		gtkGrid.attach(dow_frame,1,1,1,15)
		work_days_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		dow_box.add(work_days_box)
		work_days_box.add(self.chk_monday)
		work_days_box.add(self.chk_tuesday)
		work_days_box.add(self.chk_wednesday)
		work_days_box.add(self.chk_thursday)
		work_days_box.add(self.chk_friday)
		work_days_box.set_focus_chain([self.chk_monday,self.chk_tuesday,self.chk_wednesday,self.chk_thursday,\
						self.chk_friday])
		weekend_days_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		dow_box.add(weekend_days_box)
		weekend_days_box.add(self.chk_saturday)
		weekend_days_box.add(self.chk_sunday)
		weekend_days_box.set_focus_chain([self.chk_saturday,self.chk_sunday])
		dow_box.set_focus_chain([work_days_box,weekend_days_box])
		label=Gtk.Label(_("Time & date"))
		label.set_margin_bottom(6)
		gtkGrid.attach(label,2,2,2,1)
		gtkGrid.attach_next_to(self.hour_box,label,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.minute_box,self.hour_box,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.month_box,self.minute_box,Gtk.PositionType.BOTTOM,1,1)
		gtkGrid.attach_next_to(self.day_box,self.month_box,Gtk.PositionType.BOTTOM,1,1)
		label=Gtk.Label(_("Time intervals"))
		label.set_margin_bottom(6)
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
			self.btn_apply.connect("clicked",self.update_task_details)
			if self.flavour!='server':
				self.btn_apply.set_sensitive(False)
		#Tab chain
		widget_array=[dow_frame,self.hour_box,self.minute_box,self.month_box,self.day_box,self.chk_interval,\
						self.interval_box,self.chk_special_dates,self.cmb_special_dates]
		if btn_apply:
			widget_array.append(self.btn_apply)

		gtkGrid.set_focus_chain(widget_array)
		#Add data to combos
		self._load_date_time_data('minute')
		self._load_date_time_data('hour')
		self._load_date_time_data('day')
		self._load_date_time_data('month')
		#Signals
		gtkGrid.connect("event",self._parse_scheduled)
		self.chk_monday.connect("toggled",self._enable_fixed_dates)
		self.chk_thursday.connect("toggled",self._enable_fixed_dates)
		self.chk_wednesday.connect("toggled",self._enable_fixed_dates)
		self.chk_tuesday.connect("toggled",self._enable_fixed_dates)
		self.chk_friday.connect("toggled",self._enable_fixed_dates)
		self.chk_saturday.connect("toggled",self._enable_fixed_dates)
		self.chk_sunday.connect("toggled",self._enable_fixed_dates)
		self.chk_interval.connect("toggled",self._chk_interval_status)
		self.chk_special_dates.connect("toggled",self._chk_special_dates_status)
		#handled signals
		self.cmb_dates.connect("changed",self._load_interval_data)

		#Initial control status
		self.interval_box.set_sensitive(False)
		self.cmb_special_dates.set_sensitive(False)
		return gtkGrid

	def load_task_details(self,task_name,task_serial,task_data,task_type):
		self.clear_screen()
		self.task_name=task_name
		self.task_serial=task_serial
		self.task_cmd=task_data['cmd']
		self.task_type=task_type
		self.lbl_info.set_text('')
		if task_data['m'].isdigit():
			cursor=0
			for minute in range(0,60,5):
				if minute>int(task_data['m']):
					break
				cursor+=1
			self.cmb_minutes.set_active(cursor-1)
		else:
			self.cmb_minutes.set_active(0)

		self._parse_date_details(task_data['h'],self.cmb_hours,'hour')
		self._parse_date_details(task_data['dom'],self.cmb_days,'dom')
		self._parse_date_details(task_data['mon'],self.cmb_months,'mon')
		widget_dict={'0':self.chk_sunday,'1':self.chk_monday,'2':self.chk_tuesday,\
					'3':self.chk_wednesday,'4':self.chk_thursday,'5':self.chk_friday,\
					'6':self.chk_saturday,'7':self.chk_sunday}
		self._parse_date_details(task_data['dow'],None,'dow',widget_dict)
	#def load_task_details

	def _parse_date_details(self,date,widget=None,date_type=None,widget_dict=None):
		if date.isdigit() and widget:
			widget.set_active(int(date))
		elif '/' in date:
			pos=date.split('/')
			self.chk_interval.set_active(True)
			self.cmb_interval.set_active(int(pos[1])-1)
			if date_type=='hour':
				self.cmb_dates.set_active(0)
				self.hour_box.set_sensitive(False)
			elif date_type=='dom':
				self.cmb_dates.set_active(1)
				self.day_box.set_sensitive(False)
				self.hour_box.set_sensitive(True)
			elif date_type=='mon':
				self.cmb_interval.set_active(int(pos[1])-1)
				self.cmb_dates.set_active(3)
				self.month_box.set_sensitive(False)
				self.hour_box.set_sensitive(True)
		elif widget_dict:
			array_date=[]
			if ',' in date:
				array_date=date.split(',')
			else:
				array_date.append(date)

			for selected_date in array_date:
				if selected_date.isdigit():
					widget_dict[selected_date].set_active(True)
	#def _parse_date_details

	def clear_screen(self):
		widgets=[self.chk_monday,self.chk_thursday,self.chk_wednesday,self.chk_tuesday,\
				self.chk_friday,self.chk_saturday,self.chk_sunday]
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
	
	def _set_sensitive_widget(self,widget_dic):
		for widget,status in widget_dic.items():
			widget.set_sensitive(status)
	
	def _changed_interval(self):
		if self.chk_interval.get_active():
			interval=self.cmb_dates.get_active_text()
			if interval==_('hour(s)'):
				self._set_sensitive_widget({self.day_box:not self._get_days_active(),\
						self.month_box:True,self.hour_box:False})
				self._set_days_sensitive(True)
			elif interval==_('day(s)') or interval==_('week(s)'):
				self._set_sensitive_widget({self.day_box:False,self.month_box:True,self.hour_box:True})
				self._set_days_sensitive(False)
			elif interval==_('month(s)'):
				self._set_sensitive_widget({self.day_box:not self._get_days_active(),\
						self.month_box:False,self.hour_box:True})
				self._set_days_sensitive(True)
	#def _changed_interval


	def _chk_interval_status(self,widget):
		if self.chk_interval.get_active():
			self._set_sensitive_widget({self.interval_box:True,self.cmb_special_dates:False,\
				self.hour_box:False,self.month_box:True,self.day_box:not self._get_days_active()})
			self._changed_interval()
		else:
			self._set_sensitive_widget({self.interval_box:False,self.cmb_special_dates:True,\
				self.hour_box:True,self.month_box:True,self.day_box:not self._get_days_active()})
			self._chk_special_dates_status()
	#def _chk_interval_status
			
	def _chk_special_dates_status(self,widget=None):
		if self.chk_special_dates.get_active():
			self._set_sensitive_widget({self.cmb_special_dates:True,self.day_box:False,\
				self.chk_interval:False})
			self._set_days_sensitive(False)
		else:
			self._set_sensitive_widget({self.cmb_special_dates:False,self.chk_interval:True,\
				self.day_box:not self._get_days_active()})
			self._set_days_sensitive(True)
	#def _chk_special_dates_status

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
	#def _get_days_active

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
				self.day_box.set_sensitive(True)
				self.month_box.set_sensitive(True)
	#def _enable_fixed_dates

	def _set_days_sensitive(self,state):
		widgets=[self.chk_monday,
				self.chk_thursday,
				self.chk_wednesday,
				self.chk_tuesday,
				self.chk_friday,
				self.chk_saturday,
				self.chk_sunday]
		for widget in widgets:
			widget.set_sensitive(state)
	#def _set_days_sensitive

	def _parse_screen(self):
		details={}
		dow=''
		widgets=[self.chk_monday,self.chk_thursday,	self.chk_wednesday,	self.chk_tuesday,\
				self.chk_friday,self.chk_saturday,self.chk_sunday]
		cont=1
		for widget in widgets:
			if widget.get_active():
				dow+=str(cont)+','
			cont+=1
		if dow!='':
			dow=dow.rstrip(',')
		else:
			dow='*'
		details['dow']=dow
		#Init date data
		for i in ["h","m","mon","dom"]:
			details[i]="*"
		#load data
		if self.cmb_hours.is_sensitive():
			details["h"]=self.cmb_hours.get_active_text()
		if self.cmb_minutes.is_sensitive():
			details["m"]=self.cmb_minutes.get_active_text()
		if self.cmb_months.is_sensitive():
			if self.cmb_months.get_active_text().isdigit():
				details["mon"]=self.cmb_months.get_active_text()
		if self.cmb_days.is_sensitive():
			if self.cmb_days.get_active_text().isdigit():
				details["dom"]=self.cmb_days.get_active_text()

		if self.cmb_dates.is_sensitive():
			if self.cmb_dates.get_active_text()==_('hour(s)'):
				details['h']="0/"+self.cmb_interval.get_active_text()
			if self.cmb_dates.get_active_text()==_('day(s)'):
				details['dom']="1/"+self.cmb_interval.get_active_text()
			if self.cmb_dates.get_active_text()==_('week(s)'):
				week=int(self.cmb_interval.get_active_text())*7
				details['dom']="1/"+str(week)
			if self.cmb_dates.get_active_text()==_('month(s)'):
				details['mon']="1/"+self.cmb_interval.get_active_text()
		details['hidden']=0
		return details
	#def _parse_screen

	def _parse_scheduled(self,container,widget=None):
		details=self._parse_screen()
		parser=cronParser()
		self.lbl_info.set_text("Task schedule: "+(parser.parse_taskData(details)))

	def update_task_details(self,widget=None):
		if self.task_name and self.task_serial:
			task_data=self.get_task_details()
			self.scheduler.write_tasks(task_data,self.task_type)
	#def update_task_details

	def get_task_details(self,widget=None,task_name=None,task_serial=None,task_cmd=None,task_type=None):
		if task_name:
			self.task_name=task_name
		if task_serial:
			self.task_serial=task_serial
		if task_cmd:
			self.task_cmd=task_cmd
		if task_type:
			self.task_type=task_type
		details=self._parse_screen()
		details['cmd']=self.task_cmd
		task={}
		task[self.task_name]={self.task_serial:details}
		return task

class TaskScheduler:

	def __init__(self):
		self.check_root()
		try:
			self.flavour=subprocess.getoutput("lliurex-version -f")
		except:
			self.flavour="client"
			
	#def __init__		

	def isscheduler_running(self):
		if os.path.exists(LOCK_PATH):
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Task Scheduler")
			dialog.format_secondary_text(_("There's another instance of Task Scheduler running."))
			dialog.run()
			sys.exit(1)

	def check_root(self):
		try:
			print ("  [taskScheduler]: Checking root")
			f=open("/etc/scheduler/scheduler.token","w")
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
		builder.set_translation_domain('taskscheduler')

		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

		glade_path=GLADE_FILE
		builder.add_from_file(glade_path)

		self.window=builder.get_object("main_window")
		self.main_box=builder.get_object("main_box")
		self.inf_info=Gtk.InfoBar()	
		self.inf_lbl=Gtk.Label("")
		self.inf_info.get_action_area().add(self.inf_lbl)
		self.inf_info.add_button(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL)
		self.inf_info.add_button(Gtk.STOCK_OK,Gtk.ResponseType.OK)
		self.inf_info.set_halign(Gtk.Align.CENTER)
		self.inf_info.set_valign(Gtk.Align.CENTER)
		self.main_box.pack_start(self.inf_info,False,False,0)
		self.view_tasks_button_box=builder.get_object("view_tasks_button_box")
		self.view_tasks_eb=builder.get_object("view_tasks_eventbox")
		self.btn_signal_id=None
		#Toolbar
		self.btn_add_task=builder.get_object("btn_add_task")
		self.btn_add_task.connect("button-release-event", self.add_task_clicked)

#		self.stackSwitcher=Gtk.StackSwitcher()
#		self.stackSwitcher.set_stack(self.stack)
		self.btn_remote_tasks=builder.get_object("btn_remote_tasks")

		self.btn_local_tasks=builder.get_object("btn_local_tasks")
		self.handler_remote=self.btn_remote_tasks.connect("clicked",self.view_tasks_clicked,'remote')
		self.handler_local=self.btn_local_tasks.connect("clicked",self.view_tasks_clicked,'local')
		#tasks list
		self.txt_search=builder.get_object("txt_search")
		self.txt_search.connect('changed',self.match_tasks)
		self._load_task_list_gui(builder)

		self.stack.add_titled(self.tasks_box, "tasks", "Tasks")
		self.stack.add_titled(self.add_task_box, "add", "Add Task")
		
		#Icons
		image=Gtk.Image()
		image.set_from_file(REMOVE_ICON)		
		self.remove_icon=image.get_pixbuf()

		#Signals

		#Packing
#		self.main_box.pack_start(self.stack,True,False,5)
#		separator=Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
#		self.main_box.pack_start(self.stackSwitcher,True,False,5)
#		self.main_box.pack_start(separator,True,True,0)
		self.main_box.pack_start(self.stack,True,False,5)
		self.window.show_all()
		self.inf_info.hide()
		self.window.connect("destroy",self.quit)
		self.set_css_info()
		self.task_list=[]

		GObject.threads_init()
		self.btn_remote_tasks.set_active(True)
		Gtk.main()

	#def start_gui

	def _load_task_list_gui(self,builder):
		self.tasks_box=builder.get_object("tasks_box")
		self.tasks_label=builder.get_object("tasks_label")
		self.tasks_tv=builder.get_object("tasks_treeview")
		self.task_details_grid=TaskDetails(self.scheduler_client)
		td_grid=self.task_details_grid.render_form(builder.get_object("task_details_grid"))
		self.tasks_store=Gtk.ListStore(str,str,str,GdkPixbuf.Pixbuf)
		self.tasks_store_filter=self.tasks_store.filter_new()
		self.tasks_store_filter.set_visible_func(self.filter_tasklist)
		self.tasks_tv.set_model(self.tasks_store_filter)
		self.tasks_tv.connect("button-release-event",self.task_clicked)
		self.tasks_tv.connect("cursor-changed",self.task_clicked)

		column=Gtk.TreeViewColumn(_("Task"))
		cell=Gtk.CellRendererText()
		column.pack_start(cell,True)
		column.add_attribute(cell,"markup",0)
		column.set_expand(True)
		self.tasks_tv.append_column(column)
		
		column=Gtk.TreeViewColumn(_("Serial"))
		cell=Gtk.CellRendererText()
		column.pack_start(cell,True)
		column.add_attribute(cell,"markup",1)
		column.set_expand(True)
		column.set_visible(False)
		self.tasks_tv.append_column(column)
		
		column=Gtk.TreeViewColumn(_("When"))
		cell=Gtk.CellRendererText()
		cell.set_property("alignment",Pango.Alignment.CENTER)
		column.pack_start(cell,False)
		column.add_attribute(cell,"markup",2)
		column.set_expand(True)
		self.tasks_tv.append_column(column)		

		column=Gtk.TreeViewColumn(_("Remove"))
		cell=Gtk.CellRendererPixbuf()
		cell.set_property('cell_background','red')
		column.pack_start(cell,True)
		column.add_attribute(cell,"pixbuf",3)
		self.col_remove=column
		self.tasks_tv.append_column(column)

		self.tasks_tv.set_search_column(2)
		self.tasks_tv.set_search_entry(self.txt_search)

		#Add tasks
		self.add_task_box=builder.get_object("add_task_box")
		self.add_task_grid=TaskDetails(self.scheduler_client)
		at_grid=self.add_task_grid.render_form(builder.get_object("add_task_grid"),False)
		self.cmb_task_names=builder.get_object("cmb_task_names")
		self.cmb_task_cmds=builder.get_object("cmb_task_cmds")
		builder.get_object("btn_cancel_add").connect("clicked", self.cancel_add_clicked)
		builder.get_object("btn_confirm_add").connect("clicked", self.save_task_details)
		self.chk_remote=builder.get_object("swt_remote")
		self.chk_local=builder.get_object("swt_local")

	def set_css_info(self):
	
		css = b"""
		#WHITE_BACKGROUND {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#ffffff),  to (#ffffff));;
		
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
		"""

		self.style_provider=Gtk.CssProvider()
		self.style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		
		self.window.set_name("WHITE_BACKGROUND")
		self.tasks_box.set_name("WHITE_BACKGROUND")
	#def set_css_info	

	def filter_tasklist(self,model,iterr,data):
		sw_match=True
		match=self.txt_search.get_text().lower()
		task_data=model.get_value(iterr,0).split('\n')
		task_sched_data=model.get_value(iterr,2).split('\n')
		task_cmd=task_data[0][task_data[0].find("<b>")+3:task_data[0].find("</b>")]
		task_name=task_data[1][task_data[1].find("<i>")+3:task_data[1].find("</i>")]
		task_sched=task_sched_data[0][task_sched_data[0].find("ll'>")+4:task_sched_data[0].find("</span>")]

		task_text=task_cmd+' '+task_name+' '+task_sched
		if match and match not in task_text.lower():
			sw_match=False
		return sw_match

	def match_tasks(self,widget):
		self.tasks_store_filter.refilter()
		GObject.timeout_add(100,self.tasks_tv.set_cursor,0)

	def populate_tasks_tv(self,parm):
		self.scheduled_tasks={}
		tasks=[]
		tasks=self.scheduler_client.get_scheduled_tasks(parm)
		self.tasks_store.clear()
		
		for task in tasks:
			for task_name,task_serialized in task.items():
				self.scheduled_tasks[task_name]=task_serialized
				for serial,task in task_serialized.items():
					parser=cronParser()
					parsed_calendar=''
					parsed_calendar=parser.parse_taskData(task)
					self.tasks_store.append(("<span font='Roboto'><b>"+task['cmd']+"</b></span>\n"+\
									"<span font='Roboto' size='small'><i>"+\
									task_name+"</i></span>",serial,"<span font='Roboto' size='small'>"+\
									parsed_calendar+"</span>",self.remove_icon))
	#def populate_tasks_tv

	def task_clicked(self,treeview,event=None):
		self.task_details_grid.clear_screen()
		sw_show=True
		if event!=None:
			row=self.tasks_tv.get_path_at_pos(int(event.x),int(event.y))
			col=row[1]
			if col==self.col_remove:
				sw_show=False
		selection=self.tasks_tv.get_selection()
		model,data=selection.get_selected()
		if not data:
			return
		task_data=model[data][0].split('\n')
		task_serial=model[data][1].split('\n')[0]
		task_cmd=task_data[0][task_data[0].find("<b>")+3:task_data[0].find("</b>")]
		task_name=task_data[1][task_data[1].find("<i>")+3:task_data[1].find("</i>")]
		task_serial=model[data][1]
		if self.btn_remote_tasks.get_active():
			task_type='remote'
		else:
			task_type='local'
		if sw_show:
			if task_name in self.scheduled_tasks.keys():
				if task_serial in self.scheduled_tasks[task_name].keys():
					task_data=self.scheduled_tasks[task_name][task_serial]
					print("Loading details of %s task %s of group %s"% (task_type,task_serial,task_name))
					self.task_details_grid.load_task_details(task_name,task_serial,task_data,task_type)
		else:
			self.inf_lbl.set_text(_("Are you sure to delete this task?"))
			self.inf_info.show_all()
			self.inf_info.connect('response',self.manage_remove_responses,model,task_name,task_serial,task_cmd,task_type)
	#def task_clicked			

	def save_task_details(self,widget):
		print("INVOKED BY %s"%widget)
		task_name=self.cmb_task_names.get_active_text()
		task_cmd=self.cmb_task_cmds.get_active_text()
		task_type='local'
		if self.btn_remote_tasks.get_active():
			task_type='remote'
		task=self.add_task_grid.get_task_details(None,task_name,None,task_cmd,task_type)

		taskFilter='local'
		print("Writing task info...")
		if self.chk_remote.get_active():
			self.scheduler_client.write_tasks(task,'remote')
		if self.chk_local.get_active():
			self.scheduler_client.write_tasks(task,'local')
#		self.view_tasks_clicked(None,taskFilter)
		return()
	#def save_task_details


	def view_tasks_clicked(self,widget,parm):
		if widget:
			if not widget.get_active():
				if parm=='remote':
					self._block_widget_state(True,widget,self.handler_remote)
				else:					
					self._block_widget_state(True,widget,self.handler_local)
#				widget.handler_unblock(handler)
				return True
		print("loading %s tasks" % parm)
		if parm=='remote':
			self.btn_local_tasks.set_active(False)
			self.btn_local_tasks.props.active=False
#			self.btn_remote_tasks.set_active(True)
#			self.btn_remote_tasks.set_sensitive(False)
		else:
			self.btn_remote_tasks.set_active(False)
			self.btn_remote_tasks.props.active=False
#			self.btn_local_tasks.set_active(True)
#			self.btn_remote_tasks.set_sensitive(True)
		self.populate_tasks_tv(parm)
		self.tasks_tv.set_model(self.tasks_store_filter)
		self.tasks_tv.set_cursor(0)
		self.cancel_add_clicked(widget,parm)
	#def view_tasks_clicked	

	def load_add_task_details(self):
		self._block_widget_state(False,self.btn_remote_tasks,self.handler_remote)
		self._block_widget_state(False,self.btn_local_tasks,self.handler_local)
		tasks=[]
		names=[]
		self.cmb_task_names.remove_all()
		tasks=self.scheduler_client.get_available_tasks()
		for task in tasks:
			for name in task.keys():
				if name not in names:
					names.append(name)
					self.cmb_task_names.append_text(name)
		
		self.cmb_task_names.connect('changed',self.load_add_task_details_cmds,tasks)
		self.cmb_task_names.set_active(0)

		if self.btn_remote_tasks.get_active():
			self.chk_remote.set_active(1)
			self.chk_local.set_active(0)
		else:
			self.chk_local.set_active(1)
			self.chk_remote.set_active(0)
		if self.flavour!='server':
			self.chk_remote.set_sensitive(False)
			self.chk_remote.set_active(0)
	#def load_add_task_details

	def load_add_task_details_cmds(self,widget,tasks):
		cmds=[]
		self.cmb_task_cmds.remove_all()
		task_name=self.cmb_task_names.get_active_text()
		if task_name:
			for task in tasks:
				for cmd in task[task_name]:
					if cmd not in cmds:
						cmds.append(cmd)
						self.cmb_task_cmds.append_text(cmd)
			self.cmb_task_cmds.set_active(0)
	#def load_add_task_details_cmds
	
	def add_task_clicked(self,widget,event):
		print("Loading new task form")
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack.set_visible_child_name("add")
		self.load_add_task_details()
	#def add_task_clicked	

	def cancel_add_clicked(self,widget,event):
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		self.stack.set_visible_child_name("tasks")	
	#def cancel_add_clicked

	def manage_remove_responses(self,widget,response,model,task_name,task_serial,task_cmd,task_type):
		if response==Gtk.ResponseType.OK:
			self.scheduler_client.remove_task(task_name,task_serial,task_cmd,task_type)
		#filter doesn't support remove so it's needed to get the filter iter and remove it on the parent model
			tasks_ts=self.tasks_tv.get_selection()
			(tm,path)=tasks_ts.get_selected_rows()
			child_path=model.convert_path_to_child_path(path[0])
			iterr=self.tasks_store.get_iter(child_path)
			self.tasks_store.remove(iterr)
		self.inf_info.hide()
	#def manage_remove_responses
	
	###
	#Changes the state of a widget blocking the signals
	###
	def _block_widget_state(self,state,widget,handler):
		widget.handler_block(handler)
		widget.set_active(state)
		GObject.timeout_add(100,widget.handler_unblock,handler)
	#def _block_widget_state

	def quit(self,widget,event=None):
		Gtk.main_quit()	

	#def quit	

#class TaskScheduler

tes=TaskScheduler()
tes.start_gui()		
