#!/usr/bin/env python
receiver="ProcessViewer"

from gi.repository import Gtk, Gdk, Pango
import heapq

from Tools.output import *
from Tools.simplemath import *
from multiprocessing.pool import ThreadPool
import psutil

from Tools.hardware import percentToNiceString, dataToNiceString

class Widget():
	def __init__(self, name, parentName, parent):
		self.parent=parent
		self.hMid=False
		self.vMid=False
		self.name=parentName+name

		self.labels = []
		#by default 3 columns, 5 rows
		self.rows=5
		self.columns=3
		self.rowSpacing=30
		self.columnSpacing=30

		self.availableColumnTypes = { "name":"name", "username":"username", "pid":"pid",
									  "cpuPercent":"get_cpu_percent", "ram":"get_memory_info",
									  "ramPercent":"get_memory_percent", "status":"status" }
		self.columnTypes={}
		self.psutilInfo = []

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		self.cssClear = [ self.name ]

		self.fixed=Gtk.Fixed()

		self.frame=Gtk.Frame()
		self.frame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
		self.frame.add(self.fixed)

		self.frame.connect('destroy', self.destroyed)
		self.frame.connect('size-allocate', self.getSize)

		self.readyShow=False
		self.sortFunction = None
		self.niceFunction = None
		self.pool = ThreadPool(processes=1)
		self.cssApplied=False
		self.processData=None
		self.labelSize=None
		self.trimN=100
		self.percentDecimals=0
		self.counter=10

	def destroyWidget(self, widget):
		widget.hide()
		widget.destroy()
		widget=0

	def constructPsUtilInfo(self):
		if(len(self.columnTypes)!=self.columns):
			stderr("Not all column types have been declared for "+receiver+"!")
			self.sortFunction=None
			return
		for key in self.columnTypes:
			self.psutilInfo.append(self.availableColumnTypes[self.columnTypes[key]])
		if(self.sortFunction==self.cpuSort):
			if "get_cpu_percent" not in self.psutilInfo:
				self.psutilInfo.append("get_cpu_percent")
		elif(self.sortFunction==self.memorySort):
			if "get_memory_percent" not in self.psutilInfo:
				self.psutilInfo.append("get_memory_percent")

	def updateLabelArray(self):
		self.fixed.forall(self.destroyWidget)
		self.labels = []
		counter=0
		for i in range(self.rows):
			rowArray = []
			for j in range(self.columns):
				label = Gtk.Label("L1")
				label.set_name(self.name+"l"+str(i)+"-"+str(j))
				frame = Gtk.Frame()
				frame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
				frame.set_label_widget(label)
				self.fixed.put(frame, j*self.columnSpacing, i*self.rowSpacing)
				rowArray.append(frame)
				counter+=1
			self.labels.append(rowArray)

	def getSize(self, widget, allocation):
		if not self.cssApplied:
			return
		self.width=allocation.width
		self.height=allocation.height
		if(self.hMid):
			self.x=(self.parent.width - self.width)/2.0
		if(self.vMid):
			self.y=(self.parent.height - self.height)/2.0
		if(self.hMid or self.vMid):
			self.parent.fixed.move(self.frame, self.x, self.y)
		widget.disconnect_by_func(self.getSize)

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def largerThanAll(self, value, array):
		for i in array:
			if value < i:
				return False
		return True

	def replaceMinWith(self, value, array):
		if(len(array)==0):
			return [value]
		counter=0
		minimum=array[0]
		index=0
		for i in array:
			if i < minimum:
				minimum=i
				index=counter
			counter+=1
		array[index]=value
		return index, array

	def memorySort(self):
		procs=[]
		for p in psutil.process_iter():
			try:
				pdict=p.as_dict(self.psutilInfo)
				if(len(procs)<self.rows):
					procs.append(pdict)
				elif pdict['memory_percent']!=0:
					procs.append(pdict)
			except psutil.NoSuchProcess:
				pass

		# return processes sorted by RAM percent usage
		# processes = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)
		processes=heapq.nlargest(self.rows, procs, key=lambda p: p['memory_percent'])
		if(self.rows > len(processes)):
			return processes
		else:
			return processes[:self.rows]

	def cpuSort(self):
		procs=[]
		for p in psutil.process_iter():
			try:
				pdict=p.as_dict(self.psutilInfo)
				if(len(procs)<self.rows):
					procs.append(pdict)
				elif pdict['cpu_percent']!=0:
					procs.append(pdict)
			except psutil.NoSuchProcess:
				pass

		# return processes sorted by CPU percent usage
		# processes = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)
		processes=heapq.nlargest(self.rows, procs, key=lambda p: p['cpu_percent'])
		if(self.rows > len(processes)):
			return processes
		else:
			return processes[:self.rows]

	def trim(self, text):
		text=str(text)
		return text[:self.trimN]

	def percentToNice(self, percent):
		return percentToNiceString(percent, self.percentDecimals, True)

	def dataToNice(self, data):
		return dataToNiceString(data, 0)

	def update(self):
		if(self.sortFunction==None):
			stderr("No sort function has been declared! The "+receiver+" cannot show results!")
			return

		self.counter+=1
		if(self.counter<5):
			return

		if(self.processData==None):
			self.processData=self.pool.apply_async(self.sortFunction)
		elif(self.processData.ready()):
			self.counter=0
			self.readyShow=True
			sortedProcs=self.processData.get()
			for i in range(self.columns):
				columnKey=self.columnTypes[i]
				accessFirst=False
				if columnKey=='cpuPercent':
					columnKey='cpu_percent'
				elif columnKey=='ramPercent':
					columnKey='memory_percent'
				elif columnKey=='ram':
					columnKey='memory_info'
					accessFirst=True
				for j in range(self.rows):
					if accessFirst:
						if(sortedProcs[j][columnKey]!=self.labels[j][i].get_label_widget().get_text()):
							self.niceFunction=0
							if('percent' in columnKey):
								self.niceFunction=self.percentToNice
							elif('info' in columnKey):
								self.niceFunction=self.dataToNice
							else:
								self.niceFunction=self.trim
							self.labels[j][i].get_label_widget().set_text(str(self.niceFunction(sortedProcs[j][columnKey][0])))
					else:
						if(sortedProcs[j][columnKey]!=self.labels[j][i].get_label_widget().get_text()):
							self.niceFunction=0
							if('percent' in columnKey):
								self.niceFunction=self.percentToNice
							elif('info' in columnKey):
								self.niceFunction=self.dataToNice
							else:
								self.niceFunction=self.trim
							self.labels[j][i].get_label_widget().set_text(str(self.niceFunction(sortedProcs[j][columnKey])))
			self.processData=self.pool.apply_async(self.sortFunction)

	def runCommand(self, key, value, lineCount, configurationFile):
		if(key=="size"):
			size=value.split(",")
			self.frame.set_size_request(int(size[0]),int(size[1]))
		elif(key=="label-size"):
			self.labelSize=value.split(",")
			if(self.labelSize!=2 or not representsInt(self.labelSize[0]) or not representsInt(self.labelSize[1])):
				self.labelSize[0]=int(self.labelSize[0])
				self.labelSize[1]=int(self.labelSize[1])
		elif(key=="font"):
			#todo apply same font to all
			for i in range(self.rows):
				for j in range(self.columns):
					self.updateCss("font", value, self.name+"l"+str(i)+"-"+str(j))
		elif(key=="color"):
			#todo apply same color to all
			self.updateCss("color", value)
		elif(key=="border"):
			self.updateCss("border", value)
		elif(key=="border-top"):
			self.updateCss("border-top", value)
		elif(key=="border-right"):
			self.updateCss("border-right", value)
		elif(key=="border-bottom"):
			self.updateCss("border-bottom", value)
		elif(key=="border-left"):
			self.updateCss("border-left", value)
		elif(key=="sort"):
			if(value=="ram"):
				self.sortFunction=self.memorySort
			elif(value=="cpu"):
				self.sortFunction=self.cpuSort
			else:
				stderr("Unknown sort function "+value)
		elif(key=="cr"):
			size=value.split(",")
			self.columns=int(size[0])
			self.rows=int(size[1])
			self.updateLabelArray()
		elif(',' in key and key.startswith("l") and len(key)>1 and representsInt(key[1])):
			#specific label
			indexParts=key.split(",")
			if(len(indexParts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'l': Format: lx,y-property = value.\nSkipping...")
				return
			indexParts[0]=indexParts[0][1:]
			finalIndex=0
			for i in range(len(indexParts[1])):
				if(not representsInt(indexParts[1][i])):
					finalIndex=i
					break

			try:
				secondaryKey=indexParts[1][i+2:]
				indexParts[1]=indexParts[1][:i]
			except:
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'l': Format: lx,y-property = value.\nSkipping...")
				return

			if not representsInt(indexParts[0]) or not representsInt(indexParts[1]):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'l': Format: lx,y-property = value.\nSkipping...")
				return
			indexParts[0]=int(indexParts[0]); indexParts[1]=int(indexParts[1])
			
			if(secondaryKey=="font"):
				self.updateCss("font", value, self.name+"l"+str(indexParts[0])+"-"+str(indexParts[1]))
			elif(secondaryKey=="color"):
				self.updateCss("color", value, self.name+"l"+str(indexParts[0])+"-"+str(indexParts[1]))
			else:
				stderr(configurationFile+", line "+str(lineCount)+": Unknown property for command 'l': Available properties: font, color.\nSkipping...")
				return
		elif(key.startswith("c") and len(key) > 1 and representsInt(key[1])):
			#specific column
			columnNumber=key[1:]
			finalIndex=0
			for i in range(1, len(key)):
				if not representsInt(key[i]):
					finalIndex=i
					break
			columnNumber=key[1:i]
			if not representsInt(columnNumber):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'c': Format: cn-property.\nSkipping...")
				return
			# 2 because of the dash and the 'c'
			secondaryKey=key[2+len(columnNumber):]
			columnNumber=int(columnNumber)
			if(columnNumber >= self.columns):
				stderr(configurationFile+", line "+str(lineCount)+": Too high index for command 'c': Max Index: length of columns - 1.\nSkipping...")
				return
			if(secondaryKey=="type"):
				if(value in self.availableColumnTypes):
					self.columnTypes[columnNumber]=value;
				else:
					stderr(configurationFile+", line "+str(lineCount)+": Unknown type '"+value+"'.\nSkipping...")
					return
			elif(secondaryKey=="pos"):
				coords=value.split(",")
				if(len(coords)!=2):
					stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'c': Format: cn-pos = x,y.\nSkipping...")
					return
				for i in range(self.rows):
					self.fixed.move(self.labels[i][columnNumber], int(coords[0]), int(coords[1])+i*self.rowSpacing)
			elif(secondaryKey=="font"):
				for i in range(self.rows):
					self.updateCss("font", value, self.name+"l"+str(i)+"-"+str(columnNumber))
			elif(secondaryKey=="color"):
				for i in range(self.rows):
					self.updateCss("color", value, self.name+"l"+str(i)+"-"+str(columnNumber))
			elif(secondaryKey=="align"):
				if value == 'left':
					for i in range(self.rows):
						self.labels[i][columnNumber].set_label_align(0, 0.5)
				elif value == 'right':
					for i in range(self.rows):
						self.labels[i][columnNumber].set_label_align(1, 0.5)
				else:
					stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'align': Format: align = left/right.\nSkipping...")
					return
		elif(key.startswith("r") and len(key) > 1 and representsInt(key[1])):
			#specific row
			rowNumber=key[1:]
			finalIndex=0
			for i in range(1, len(key)):
				if not representsInt(key[i]):
					finalIndex=i
					break
			rowNumber=key[1:i]
			if not representsInt(rowNumber):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'r': Format: rn-property.\nSkipping...")
				return
			# 2 because of the dash and the 'r'
			secondaryKey=key[2+len(rowNumber):]
			rowNumber=int(rowNumber)
			if(rowNumber >= len(self.labels[0])):
				stderr(configurationFile+", line "+str(lineCount)+": Too high index for command 'r': Max Index: length of rows - 1.\nSkipping...")
				return
			if(secondaryKey=="pos"):
				coords=value.split(",")
				if(len(coords)!=2):
					stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'r': Format: rn-pos = x,y.\nSkipping...")
					return
				for i in range(self.columns):
					self.fixed.move(self.labels[rowNumber][i], int(coords[0])+i*self.columnSpacing, int(coords[1]))
			elif(secondaryKey=="font"):
				for i in range(self.columns):
					self.updateCss("font", value, self.name+"l"+str(rowNumber)+"-"+str(i))
			elif(secondaryKey=="color"):
				for i in range(self.columns):
					self.updateCss("color", value, self.name+"l"+str(rowNumber)+"-"+str(i))
		elif(key=="crspacing"):
			size=value.split(",")
			self.columnSpacing=int(size[0])
			self.rowSpacing=int(size[1])
		elif(key=="percent-decimals"):
			self.percentDecimals=int(value)
		elif(key=="trim"):
			self.trimN=int(value)
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command.")

	def updateCss(self, key, value, name=None):
		if(name is None):
			name=self.name
		if name not in self.currentCss:
			self.currentCss[name]={}
		key=key.rstrip(); key=key.lstrip()
		value=value.rstrip(); value=value.lstrip()

		if key not in self.currentCss[name]:
			self.currentCss[name][key]={}

		self.currentCss[name][key]["value"]=value

	def applyCss(self):
		finalString=''
		for name in self.currentCss:
			if(len(self.currentCss[name])>0):
				finalString+="#"+name+" { "
				for key in self.currentCss[name]:
					finalString+=key+" : "+self.currentCss[name][key]["value"]+"; "
				finalString+="} "

		if(finalString!=''):
			self.styleProvider.load_from_data(finalString.encode())

	def changeLabelSize(self):
		for i in range(self.rows):
			for j in range(self.columns):
				self.labels[i][j].set_size_request(self.labelSize[0], self.labelSize[1])

	def initial(self):
		if(len(self.labels)==0):
			self.updateLabelArray()
		self.constructPsUtilInfo()
		if(self.labelSize!=None):
			self.changeLabelSize()
		self.applyCss()
		self.cssApplied=True

	def widget(self):
		return self.frame