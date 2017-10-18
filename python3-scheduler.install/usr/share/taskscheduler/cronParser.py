#!/usr/bin/env python3
import gettext
gettext.textdomain('lliurex-up')
_ = gettext.gettext

class cronParser():
	def __init__(self):
		self.parsedExpr=''
	
	###
	#Input: dict
	###
	def parse_taskData(self,taskData):
		print ("parsing: "+str(taskData))
		parsed_data=[]
		parsed_calendar=''
		expr={}
		day_dict={'1':'Mo','2':'Tu','3':'We','4':'Th','5':'Fr','6':'Sa','7':'Su','*':'every'}
		mon_dict={'1':'Jan','2':'Feb','3':'Mar','4':'Apr','5':'May','6':'Jun','7':'Jul','8':'Aug','9':'Sep','10':'Oct','11':'Nov','12':'Dec','*':'every'}
		mon_expr=self._parse_cron_expression(taskData['mon'],mon_dict)
		dow_expr=self._parse_cron_expression(taskData['dow'],day_dict)
		dom_expr=self._parse_cron_expression(taskData['dom'])
		min_expr=self._parse_cron_expression(taskData['m'])
		hou_expr=self._parse_cron_expression(taskData['h'])
		time_expr=self._parse_time_expr(hou_expr,min_expr)
		date_expr=self._parse_date_expr(mon_expr,dow_expr,dom_expr)
		parsed_data=" ".join([time_expr,date_expr])
		if parsed_data[0].isdigit():	
			parsed_calendar="At " + parsed_data
		else:
			parsed_calendar=parsed_data
		return parsed_calendar.capitalize()
	#def parse_taskData(self,taskData):

	def _parse_time_expr(self,hour,minute):
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
				if hour.startswith('each'):
					minute=_("at minute")+' '+minute
				else:
					minute=minute+' '+_("minutes")
			else:
				minute='each minute'
			if hour!='every':
				if hour.startswith('each'):
					if hour.endswith(' 1 '):
						hour=_("each hour")
					else:
						hour=hour+' '+_("hours")
				else:
					hour=hour+' '+_("o'clock")
				time_expr=_("%s %s" % (hour,minute))
			else:
				hour=hour+' '+_("hour")
				time_expr=_("%s of %s" % (minute,hour))
		return time_expr
	#def parse_time_expr

	def _parse_date_expr(self,mon,dow,dom):
		sw_dom_err=False
		sw_mon_err=False
		time_expr=''
		try:
			int(dom)
		except:
			sw_dom_err=True
		try:
			int(mon)
		except:
			sw_mon_err=True
		time_expr=_("%s %s" % (dom,mon))
		if sw_dom_err:
			if dom=='every' or dom=='*':
				dom=_("everyday")
			elif 'every' in mon or mon=='*':
				if dom.startswith('each'):
					if dom.endswith(' 1 '):
						dom=_("each day")
					else:
						dom=_(("%s days") % dom)
				else:
					dom=_(("day %s") % dom)
			elif ',' in dom:
				dom=_(("days %s") % dom)
			elif 'from' in dom:
				dom=_(("days %s") % dom)
			elif dom.startswith('each'):
					if dom.endswith(' 1 '):
						dom=_("each day")
					else:
						dom=_(("%s days") % dom)
		else:
			dom=_("day %s" % dom)
		if sw_mon_err:
			if mon=='every' or mon =='*':
				mon=_('every month')
			elif mon.startswith('each'):
				if mon.endswith(' 1 '):
					mon=_("each month")
				else:
					mon=_(("%s months") % mon)

		if dow!='every' and dow!='*':	
			time_expr=_("on %s %s" % (dow,mon))
		else:
			if dom.startswith('each'):
				time_expr=_("%s %s" % (dom,mon))
			else:
				time_expr=_("on %s %s" % (dom,mon))

		return time_expr
	#def parse_time_expr

	def _parse_cron_expression(self,data,description_dict={}):
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
