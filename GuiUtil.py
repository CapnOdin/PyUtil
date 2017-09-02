
try:
	from PyUtil import Util
except:
	import Util
	
import tkinter as tk
from tkinter import ttk, font

import base64

class TreeView(ttk.Treeview):
	"""
	dataCols is a dicitomary wherein keys sould corespond to column names as defined in the tuple colums,
	the value asusiated to the key sould be a dictionary with the foloing elements, here shown with their default values:
	{"text" : 'Default', "headanchor" : tk.CENTER, "stretch" : 0, "width" : width of "text", "colanchor" : tk.CENTER, "popup" : "entry", "choices" : a list, "editable" : True}

	"popup" can be one of these strings 'event', 'entry', 'combobox', 'menubutton' and 'listbox'.
	"choices" is only used if 'menubutton' is selected.

	entries in the dataCols are only needed if any non-default options are wanted
	"""
	
	def __init__(self, parent, frame, columns = {}, dataColumns = {}, editableParents = True, editableChildren = True, tooltips = True, **args):
		self.columns = list(columns)
		if("#0" in self.columns):
			columns = self.columns.copy()
			columns.remove("#0")
		
		s = ttk.Style()
		#s.configure('temp.Treeview', rowheight=40)
		
		super().__init__(frame, columns=tuple(columns), style = 'temp.Treeview', **args)
		self.ancestor = parent
		self.dataColumns = dataColumns
		
		self.ParentsAreEditable = editableParents
		self.ChildrenAreEditable = editableChildren
		self.tooltip = tooltips
		
		self.widgetPopup = None
		self.opened = False
		self.newestItem = -1
		self.newestChild = -1
		self.preLst = []
		self.posLst = []
		
		
		self.scollIcon = base64.decodebytes(	b'iVBORw0KGgoAAAANSUhEUgAAAAcAAAAHCAIAAABLMMCEAAAAAXNSR0IArs4c6QAA' +
												b'AARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYdEVYdFNvZnR3' +
												b'YXJlAHBhaW50Lm5ldCA0LjAuNWWFMmUAAACQSURBVBhXDY2hDoAgFADf35AtMIpF' +
												b'ghWGFuYsFh2JyIbFIPObHAn5FoPRYPTFuwsH7/ue57mu6zRN27Zd1/V9H6Ca51kp' +
												b'pbWWUjrnSingvUdANQxD3/eY930HhK7rjDHYhBB1XVtrIYTQtm3TNJxzQghj7DgO' +
												b'SCmN44hQVRWlFB85Z3ieBwPel2WJMaK67/sHFupE7DvaUi8AAAAASUVORK5CYII=')
		
		self.oldrowid = None
		self.oldcolumnid = None
		self.oldtooltip = None
		self.tipwindow = None
		
		self.bind("<Double-Button-1>"	, self._onDoubleClick, add = "+")
		self.bind("<B1-Motion>"		, self._resize, add = "+")
		self.bind("<ButtonRelease-1>"	, self._resize, add = "+")
		self.bind("<Configure>"		, self._resize, add = "+")
		self.bind("<MouseWheel>"		, lambda event: self._onTreeScrolly(*("scroll", 1 if event.delta < 0 else -1, "units")), add = "+")
		self.bind("<Button-2>"			, lambda event: self._middle_mouse_button(event, True), add = "+")
		self.bind("<ButtonRelease-2>"	, lambda event: self._middle_mouse_button(event, False), add = "+")
		self.bind("<Button-3>"			, self._onRightClick, add = "+")
		
		self.bind("<Control-z>", lambda event: self._undo(), add = "+")
		self.bind("<Control-y>", lambda event: self._redo(), add = "+")
		
		self.bind("<FocusIn>",  self._onKeyboardNavi, add = "+")
		
		self.bind("<<CharChange>>", lambda event: self._widgetPopup_save_destroy())
		
		if(self.tooltip):
			self.bind("<Motion>", self._administre_tooltips, add = "+")
			self.bind("<FocusOut>",  self._delete_tooltip, add = "+")
			self.bind("<Leave>",  self._delete_tooltip, add = "+")
		
		#setScrollBar(self, 1, 1)
		setScrollBar(self)
		
		self.style = self.cget("style")
		
		self.set_styles()
		
		if(self.style == ""):
			self.style = self.winfo_class()
		
		self.font = font.nametofont(ttk.Style().lookup(self.style, "font"))
		self.charwidth = self.font.measure("0")
		
		for column in self.columns:
			if(column not in self.dataColumns.keys()): self.dataColumns[column] = {}
			self.dataColumns[column]["text"]			= self.dataColumns[column]["text"]			if self.dataColumns[column].get("text")			!= None else column
			self.dataColumns[column]["headanchor"]	= self.dataColumns[column]["headanchor"]		if self.dataColumns[column].get("headanchor")	!= None else tk.CENTER
			self.dataColumns[column]["stretch"]		= self.dataColumns[column]["stretch"]			if self.dataColumns[column].get("stretch")		!= None else 0
			self.dataColumns[column]["width"]			= self.dataColumns[column]["width"]			if self.dataColumns[column].get("width")			!= None else self.font.measure(self.dataColumns[column]["text"] + "CC")
			self.dataColumns[column]["colanchor"]		= self.dataColumns[column]["colanchor"]		if self.dataColumns[column].get("colanchor")		!= None else tk.CENTER
			self.dataColumns[column]["editable"]		= self.dataColumns[column]["editable"]		if self.dataColumns[column].get("editable")		!= None else True
			
			self.heading(column, text = self.dataColumns[column]["text"], anchor = self.dataColumns[column]["headanchor"], command = lambda column = column: self.treeview_sort_column(column, False))
			self.column(column, stretch = self.dataColumns[column]["stretch"], width = self.dataColumns[column]["width"], anchor = self.dataColumns[column]["colanchor"])
	
	
	def treeview_sort_column(self, col, reverse):
		l = [(self.set(k, col), k) for k in self.get_children('')]
		l.sort(reverse=reverse)
		
		# rearrange items in sorted positions
		for index, (val, k) in enumerate(l):
			self.move(k, '', index)
		
		# reverse sort next time
		self.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))
		
	def set_styles(self):
		self.styles = ttk.Style(self.master)
		background = self.styles.lookup("Treeview", "background")
		self.styles.configure("popup.TMenubutton", background = background)
	
	def column(self, cid, option = None, **kw):
		if(cid):
			temp = super().column(cid, option, **kw)
		else:
			return None
		if(temp == "" and option == "id"):
			temp = "#0"
		return temp
		
		
	def next_row(self, iid):
		rowid = iid
		childen = self.get_children(iid)
		if(len(childen) > 0):
			iid = childen[0]
		else:
			iid = self.next(iid)
		
		if(iid == ""):
			iid = self.parent(rowid) if self.is_child(rowid) else rowid
			iid = self.next(iid) if self.next(iid) != "" else self.get_children()[0]
		return iid
	
	
	def prev_row(self, iid):
		rowid = iid
		iid = self.prev(iid)
		
		if(iid == ""):
			iid = self.prev(self.parent(rowid)) if self.is_child(rowid) else rowid
			if(iid == ""):
				children = self.get_children()
				iid = children[-1]
					
		if(self.have_children(iid)):
			children = self.get_children(iid)
			iid = children[-1]
		return iid
	
	def have_children(self, rowid):
		return len(self.get_children(rowid)) > 0
	
	def bind(self, sequence, func, add=None):
		def _substitute(*args):
			e = lambda: None #simplest object with __dict__
			e.data = eval(args[0])
			e.widget = self
			return (e,)
		
		if(sequence in ("<<Edited>>", "<<Selected>>")):
			funcid = self._register(func, _substitute, needcleanup=1)
			cmd = '{0}if {{"[{1} %d]" == "break"}} break\n'.format('+' if add else '', funcid)
			self.tk.call('bind', self._w, sequence, cmd)
		else:
			super().bind(sequence, func, add)
	
	def insert(self, parent, index, iid = None, **kw):
		self.newestItem = iid if iid != None else self.newestItem
		self.newestChild = iid if parent != "" else self.newestChild
		
		if("values" in kw):
			kw["values"] = self.handleNewLine("\n", "_._", kw["values"])
		
		result = super().insert(parent, index, iid, **kw)
		
		if("values" in result):
			result["values"] = self.handleNewLine("_._", "\n", result["values"])
		
		return result
	
	def handleNewLine(self, str1, str2, array):
		lst = []
		for val in array:
			if(isinstance(val, str) and str1 in val):
				val = val.replace(str1, str2)
			lst.append(val)
		return lst
	
	def set(self, iid, column=None, value=None):
		
		# handeling new line
		if(value and isinstance(value, str)):
			value = value.replace("\n", "_._")
		
		result = super().set(iid, column, value)
		
		# handeling new line
		if(column and not value and isinstance(result, str)):
			result = result.replace("_._", "\n")
			
		return result
	
	def set_options(self, editableTree = None, editableParents = None, editableChildren = None, tooltips = None):
		self.TreeIsEditable 		= editableTree 		if editableTree 		!= None else self.TreeIsEditable
		self.ParentsAreEditable 	= editableParents 		if editableParents 	!= None else self.ParentsAreEditable
		self.ChildrenAreEditable 	= editableChildren 	if editableChildren 	!= None else self.ChildrenAreEditable
		self.tooltip 				= tooltips 				if tooltips 			!= None else self.tooltip
		
		if(self.tooltip):
			self.bind("<Motion>", 		self._administre_tooltips, add = "+")		
			self.bind("<FocusOut>",  	self._delete_tooltip, add = "+")
			self.bind("<Leave>",  		self._delete_tooltip, add = "+")
		else:
			self.unbind("<Motion>")
			self.unbind("<FocusOut>")
			self.unbind("<Leave>")
		
	
	def open_close_all(self, Boolean, idds = None):
		if(idds != None):
			if(not isinstance(idds, tuple) and self.get_children(idds) != ()):
				return
			for idd in idds:
				self.open_close_all(Boolean, self.get_children(idd))
				if(Boolean):
					self.item(idd, open = True)
				else:
					self.item(idd, open = False)
		else:
			self.open_close_all(Boolean, self.get_children())
	
	def _administre_tooltips(self, event):
		try:
			if(self.identify_region(event.x, event.y) not in ("cell", "tree")):
				self._delete_tooltip()
				return
				
			if(self.tipwindow == None or not self.tipwindow.eval_mouse_pos()):
				rowid = self.identify_row(event.y)
				column = self.identify_column(event.x)
				parents = 0
				self._delete_tooltip()
					
				if(column == "#0"):
					text = self.item(rowid, "text")
					parents = self.parent(rowid)
					parents = len(parents) if not isinstance(parents, str) else 1
					parents = (parents + 1)*3*self.charwidth
				else:
					text = self.set(rowid, column)
					
				#if(self.tipwindow == None):
				if(self.font.measure(text) + parents > self.column(column, "width")):
					self.tipwindow = ToolTip(event, text)
		except:
			pass
			
		
	def _delete_tooltip(self, event = None):
		if(self.tipwindow != None and self.tipwindow.winfo_exists()):
			self.tipwindow.destroy()
			pass
		
	def _place_icon(self, x, y, address = None, data = None):
		if(address == None):
			photo = tk.PhotoImage(data=data)
		else:
			photo = tk.PhotoImage(file=address)
		self.icon = ttk.tkinter.Canvas(self, height = photo.height(), width = photo.width(), borderwidth=0, highlightthickness=0)
		self.icon.image = photo
		self.icon.create_image(0, 0, anchor=tk.NW, image=photo)
		self.icon.place(x = x, y = y, anchor = tk.CENTER)
	
	def _middle_mouse_button(self, event, Bool):
		self.dragScrollInProgress = Bool
		if(Bool):
			self.dragPos = event
			#self.place_icon(self.winfo_pointerx(), self.winfo_pointery(), self.scollIcon)
			self._place_icon(self.dragPos.x_root - self.winfo_rootx(), self.dragPos.y_root - self.winfo_rooty(), data = self.scollIcon)
			self._drag_scroll()
	
	def _drag_scroll(self):
		y = self.winfo_pointery() - self.dragPos.y_root
		x = self.winfo_pointerx() - self.dragPos.x_root
		self._onTreeScrolly(*("scroll", y // 30 if y >= 0 else (y // 30) + 1, "units"))
		self._onTreeScrollx(*("scroll", x // 10 if x >= 0 else (x // 10) + 1, "units"))
		#print(str(x) + " / " + str(y) + " / " + str(y / 30))
		if(self.dragScrollInProgress):
			self.after(20, self._drag_scroll)
		else:
			self.icon.place_forget()
	
	def _onTreeScrolly(self, *args):
		self.yview(*args)
		self._resize()
		return "break"

	def _onTreeScrollx(self, *args):
		self.xview(*args)
		self._resize()
		return "break"
	
	def cord_relative_to_tree(self):
		return (self.winfo_pointerx() - self.winfo_rootx(), self.winfo_pointery() - self.winfo_rooty())
	
	def item_delete(self, rowid):
		self._history(self.TreeUnReDo(self, "undead", rowid, parent = self.parent(rowid), index = self.index(rowid)))
		self.detach(rowid)
		self.item(rowid, tags = ("deleted"))
	
	def item_clear(self, rowid):
		self._history(self.TreeUnReDo(self, "cleared", rowid))
		self.item(rowid, value = ())
		
	def item_paste(self, rowid, value):
		self._history(self.TreeUnReDo(self, "pasted", rowid))
		self.item(rowid, value = value)
		self.event_generate("<<Edited>>", data = {"rowid": rowid, "column": None})
	
	def _history(self, unredo):
		self.posLst.clear()
		self.preLst.append(unredo)
		indexes = len(self.preLst) - 60
		if(indexes > 0):
			del self.preLst[0:indexes]
		
	def _undo(self):
		if(len(self.preLst) > 0):
			uredo = self.preLst.pop()
			self.posLst.append(uredo.creat_new_UnReDo())
			uredo.set_relevant_vars()
			self.event_generate("<<Edited>>", data = {"rowid": uredo.rowid, "column": uredo.column})
	
	def _redo(self):
		if(len(self.posLst) > 0):
			uredo = self.posLst.pop()
			self.preLst.append(uredo.creat_new_UnReDo())
			uredo.set_relevant_vars()
			self.event_generate("<<Edited>>", data = {"rowid": uredo.rowid, "column": uredo.column})
	
	
	def _onKeyboardNavi(self, event):
		if(self.selection() == ""):
			self.focus(self.get_children()[0])
	
	def _onRightClick(self, event):
		if(self.widgetPopup != None and self.widgetPopup.winfo_exists()):
			self.widgetPopup.check_focus("")
	
	def _onDoubleClick(self, event):
		rowid = self.identify_row(event.y)
		column = self.identify_column(event.x)
		
		self._widgetPopup_save_destroy()
		
		columnIndex = int(column[1:])
		
		if(not self._Check_for_Confligt(rowid, column, True)):		
			return
		
		if(rowid and columnIndex > -1):
			self._creat_next(rowid, column, columnIndex, "this")
	
	
	def _creat_next(self, rowid, column, columnIndex, variant = "next"):
		
		if(variant == "next"):
			rowid, column, nextcolmnid = self._find_next(rowid, columnIndex, 1, 0)
		elif(variant == "prev"):
			rowid, column, nextcolmnid = self._find_next(rowid, columnIndex, -1, 0)
		elif(variant == "above"):
			rowid, column, nextcolmnid = self._find_next(rowid, columnIndex, 0, -1)
		elif(variant == "below"):
			rowid, column, nextcolmnid = self._find_next(rowid, columnIndex, 0, 1)
		elif(variant == "this"):
			nextcolmnid = self.column("#" + str(columnIndex), "id")
		
		if(not self._Check_for_Confligt(rowid, column)):
			return
		
		popupType = self.dataColumns[nextcolmnid].get("popup")
		
		if(popupType == "event"):
			return
			
		elif(popupType == "tag"):
			tag = self.dataColumns[nextcolmnid].get("tag")
			if(self.tag_has(tag, rowid)):
				self.removeTag(rowid, tag)
			else:
				self.addTag(rowid, tag)
			
		elif(popupType == "combobox"):
			self.widgetPopup = self.ComboBoxPopup(self, rowid, column, justify = self.TranslateTkVals(self.dataColumns[nextcolmnid]["colanchor"], "1d"))
			
		elif(popupType == "listbox"):
			self.widgetPopup = self.ListBoxPopup(self, rowid, column)
			
		elif(popupType == "menubutton"):
			self.widgetPopup = self.MenuButtonPopup(self, rowid, column, choices = self.dataColumns[nextcolmnid].get("choices", "No choices in 'dataColumns'"))
			
		else:
			self.widgetPopup = self.EntryPopup(self, rowid, column, justify = self.TranslateTkVals(self.dataColumns[nextcolmnid]["colanchor"], "1d"))
	
	def addTag(self, rowid, tag):
		taglst = list(self.item(rowid, "tag")); taglst.append(tag)
		self.item(rowid, tag = taglst)
		
		
	def removeTag(self, rowid, tag):
		taglst = list(self.item(rowid, "tag")); taglst.remove(tag)
		self.item(rowid, tag = taglst)
		
	
	def TranslateTkVals(self, val, desired_type):
		if(desired_type == "2d"):
			if(val in (tk.NW, tk.N, tk.NE, tk.W, tk.CENTER, tk.E, tk.SW, tk.S, tk.SE, tk.NS, tk.EW, tk.NSEW)):
				return val
				
			return tk.W if val == tk.LEFT else tk.E if val == tk.RIGHT else tk.CENTER
		
		if(desired_type == "1d"):
			if(val in (tk.LEFT, tk.CENTER, tk.RIGHT)):
				return val
				
			return tk.LEFT if val == tk.W else tk.RIGHT if val == tk.E else tk.CENTER
		
	
	def _widgetPopup_save_destroy(self):
		if(self.widgetPopup != None and self.widgetPopup.winfo_exists()):
			self.widgetPopup.save_changes()
	
		
	def _resize(self, event = None):
		if(self.widgetPopup != None and self.widgetPopup.winfo_exists()):
			self.widgetPopup.resize()
		
		
	def _find_next(self, rowid, columnIndex, colchange, rowchange):
		
		rowid, column, columnIndex = self._Handle_Boundaries(rowid, columnIndex, colchange, rowchange)
		nextcolmnid = self.column(column, "id")
		#print(rowid + ", " + column)
		
		while(not self._Check_for_Confligt(rowid, column)):
			rowid, column, columnIndex = self._Handle_Boundaries(rowid, columnIndex, colchange, rowchange)
			#print(rowid + ", " + column)
		
		nextcolmnid = self.column(column, "id")
		
		return rowid, column, nextcolmnid
	
	
	def _Check_for_Confligt(self, rowid, column, boolean = False):
		
		if(not self.ParentsAreEditable and self.is_parent(rowid)):
			# do nothing if item is top-level
			return False
		
		if(not self.ChildrenAreEditable and self.is_child(rowid)):
			# do nothing if item is not top-level
			return False
		
		colmnid = self.column(column, "id")
		
		if(not self.dataColumns[colmnid].get("editable")):
			# do nothing if column dosen't allow editing
			if(boolean and self.dataColumns[colmnid].get("popup") == "event"):
				self.event_generate("<<Selected>>", data = {"rowid": rowid, "column": column})
			return False
		
		return True
	
	
	def is_parent(self, rowid):
		parent = self.parent(rowid)
		child = self.get_children(rowid)
		return parent == '' or child != ()
	
	def is_child(self, rowid):
		child = self.get_children(rowid)
		return child == ()
	
	
	def _Handle_Boundaries(self, rowid, columnIndex, colchange, rowchange = 0):
		#print(rowid + ", " + str(columnIndex) + ", " + str(colchange))
		if(colchange > 0):
			if(columnIndex + colchange >= len(self.dataColumns)):
				rowchange = 1
				columnIndex = 0
			else:
				columnIndex += colchange
		elif(colchange < 0):
			if(columnIndex + colchange < 0):
				rowchange = -1
				columnIndex = len(self.dataColumns)-1
			else:
				columnIndex += colchange
		
		if(rowchange > 0):
			if(self.is_parent(rowid)):
				rowid = self.get_children(rowid)[0]
			else:
				rowid = self.next_row(rowid)
		elif(rowchange < 0):
			if(self.is_parent(rowid)):
				children = self.get_children(rowid)
				rowid = children[len(children) - 1]
			else:
				rowid = self.prev_row(rowid)
				
		column = "#" + str(columnIndex)
		
		return rowid, column, columnIndex
		
	
	
	class TreeUnReDo:
		
		def __init__(self, tree, variant, rowid, column = None, value = None, parent = None, index = None):
			self.tree = tree
			self.variant = variant
			self.rowid = rowid
			self.column = column
			self.value = value if value != None else self.tree.set(self.rowid, self.column) if self.column != None else self.tree.item(self.rowid, "value")
			if(self.variant == "undead"):
				self.index = index if index != None else self.tree.index(self.rowid)
				self.parent = parent if parent != None else self.tree.parent(self.rowid)
			
		def set_relevant_vars(self):
			if(self.variant in ("cleared", "pasted")):
				self.tree.item(self.rowid, value = self.value)
				
			elif(self.variant == "undead"):
				self.handel_the_undead()
				
			elif(self.variant == "singel"):
				self.tree.set(self.rowid, self.column, self.value)
		
		def creat_new_UnReDo(self):
			if(self.variant == "cleared"):
				return self.tree.TreeUnReDo(self.tree, "cleared", self.rowid)
				
			elif(self.variant == "pasted"):
				return self.tree.TreeUnReDo(self.tree, "pasted", self.rowid)
				
			elif(self.variant == "undead"):
				return self.tree.TreeUnReDo(self.tree, "undead", self.rowid, parent = self.parent, index = self.index)
				
			elif(self.variant == "singel"):
				return self.tree.TreeUnReDo(self.tree, "singel", self.rowid, column = self.column)
	
		def handel_the_undead(self):
			if(self.tree.tag_has("deleted", self.rowid)):
				self.tree.move(self.rowid, self.parent, self.index)
				self.tree.item(self.rowid, tags = ("undead"))
			elif(self.tree.tag_has("undead", self.rowid)):
				self.tree.detach(self.rowid)
				self.tree.item(self.rowid, tags = ("deleted"))
	
	
	
#----------------------------------------------------------PopupWidget---------------------------------------------------------------
	
	class PopupWidget:
		
		def ini_PopupWidget(self, tree, rowid, column, forceheight):
			self.tree = tree
			self.tree.event_generate("<<TreeBusy>>")
			
			self.vcmd = (self.register(self.history), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
			self.vcmdTNI = (self.register(self.vcmdTwoNumInpout), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
			self.var = tk.StringVar()
			
			self.rowid = rowid
			self.column = column
			self.forceheight = forceheight
			self.preLst = []
			self.posLst = []
			
			self.columnindex = int(column[1:])
			
			self.entry_menu()
			self.binding()
			self.set_var()
			self.focus_force()
			self.draw()
			
		def binding(self):
			self.bind("<Control-a>", self.selectAll)
			self.bind("<Control-z>", lambda event: self.entry_undo())
			self.bind("<Control-y>", lambda event: self.entry_redo())
			self.bind("<Escape>", lambda *ignore: self.destroy())
			self.bind("<Return>", lambda event: self.save_changes())
			self.bind("<FocusOut>", lambda event: self.check_focus())
			self.bind("<Button-3>", lambda event, menu=self.dropdownmenu, widget=self: popupMenu(event, menu, widget))
			self.bind("<MouseWheel>", lambda event: self.tree._onTreeScrolly(*("scroll", 1 if event.delta < 0 else -1, "units")))
			self.bind("<Enter>", self.tree._delete_tooltip)
			
			self.bind("<Tab>", 		lambda event: self.nextFild("next"))
			self.bind("<Shift-Tab>", 	lambda event: self.nextFild("prev"))
			self.bind("<Up>", 			lambda event: self.nextFild("above"))
			self.bind("<Down>", 		lambda event: self.nextFild("below"))
			
			self.bind("<Destroy>", lambda event: self.Death(event))
		
		def Death(self, event):
			if(len(self.preLst) > 0):
				self.tree.event_generate("<<Edited>>", data = {"rowid": self.rowid, "column": self.column})
			self.tree.event_generate("<<TreeReady>>")
		
		def entry_menu(self):
			self.dropdownmenu = ttk.tkinter.Menu(tearoff=0)
			self.dropdownmenu.add_command(label="Cut", command = lambda: self.CutCopy("cut"))
			self.dropdownmenu.add_command(label="Copy", command = lambda: self.CutCopy("copy"))
			self.dropdownmenu.add_command(label="Paste", command = lambda: self.set_var(variant = "paste"))
			self.dropdownmenu.add_command(label="Delete", command = lambda: self.entry_delete())
		
		def draw(self):
			self.tree.see(self.rowid)
			try:
				x,y,width,height = self.tree.bbox(self.rowid, self.column)
				self.place_call(x = x, y = y, width = width, anchor = tk.CENTER, height = height)
			except:
				self.timer = self.after(100, self.draw)
			
		def place_call(self, x, y, width, anchor, height):
			pady = height / 2; temp = width // 2
			if(not self.forceheight):
				self.place(x = x + temp, y = y + pady, width = width, anchor = anchor)
			else:
				self.place(x = x + temp, y = y + pady, width = width, anchor = anchor, height = height)
		
		def resize(self):
			try:
				x,y,width,height = self.tree.bbox(self.rowid, self.column)
				self.place_call(x = x, y = y, width = width, anchor = tk.CENTER, height = height)
			except:
				self.place_forget()
		
		def check_focus(self, *args):
			focus = self.tree.identify_region(self.tree.winfo_pointerx() - self.tree.winfo_rootx(), self.tree.winfo_pointery() - self.tree.winfo_rooty())
			if(focus in ["heading", "separator"]):
				self.focus()
			else:
				self.save_changes()
		
		def nextFild(self, variant):
			self.save_changes(0)
			self.place_forget()
			self.tree._creat_next(self.rowid, self.column, self.columnindex, variant)
			self.destroy()
		
		def selectAll(self, *ignore):
			self.selection_range(0, tk.END)
			return 'break'
		
		def vcmdTwoNumInpout(self, d, i, P, s, S, v, V, W):
			truthVal = True
			if(d == "1"):
				if(len(P) > 2 or not self.isInt(P)):
					truthVal = False
			if(truthVal):
				self.history(d, i, P, s, S, v, V, W)
			return truthVal
		
		def CutCopy(self, variant):
			self.clipboard_clear()
			self.clipboard_append(self.get_var(variant))
			
		def entry_delete(self):
			if(self.select_present()):
				self.delete("sel.first", "sel.last")
			else:
				self.delete(0, tk.END)
		
		def set_tree_value(self, string):
			if(self.column == "#0"): # "#0"
				self.tree.item(self.rowid, text = string)
			else:
				self.tree._history(self.tree.TreeUnReDo(self.tree, "singel", self.rowid, self.column))
				self.tree.set(self.rowid, column = self.column, value = string)
		
		def get_tree_value(self):
			if(self.column == "#0"): # "#0"
				return self.tree.item(self.rowid, "text")
			else:
				return self.tree.set(self.rowid, column = self.column)
		
		def history(self, d, i, P, s, S, v, V, W):
			self.posLst.clear()
			self.preLst.append([int(d), int(i), S])
			return True
		
		def entry_undo(self):
			if(len(self.preLst) > 0):
				temp = self.preLst.pop()
				self.posLst.append(temp)
				tempstr = self.var.get()
				if(temp[0]):
					res = tempstr[0:temp[1]] + tempstr[temp[1] + len(temp[2]):]
				else:
					res = tempstr[0:temp[1]] + temp[2] + tempstr[temp[1]:]
				self.set_var(res)
		
		def entry_redo(self):
			if(len(self.posLst) > 0):
				temp = self.posLst.pop()
				self.preLst.append(temp)
				tempstr = self.var.get()
				if(not temp[0]):
					res = tempstr[0:temp[1]] + tempstr[temp[1] + len(temp[2]):]
				else:
					res = tempstr[0:temp[1]] + temp[2] + tempstr[temp[1]:]
				self.set_var(res)
	
#----------------------------------------------------------EntryPopup---------------------------------------------------------------
	
	class EntryPopup(ttk.Entry, PopupWidget):
		
		def __init__(self, tree, rowid, column, forceheight = 0, **kw):
			super().__init__(tree, style = "popup.TEntry", **kw)
			self.ini_PopupWidget(tree, rowid, column, forceheight)
			self.config(validate = "key", validatecommand = self.vcmd, textvariable = self.var)
			
		def get_var(self, variant = "normal"):
			if(variant == "normal"):
				return self.var.get()
			elif(variant in ("cut", "copy")):
				if(self.select_present()):
					substr = self.selection_get()
				else:
					substr = self.var.get()
				if(variant == "cut"):
					self.entry_delete()
				return substr
		
		def set_var(self, data = None, variant = "normal"):
			if(data == None and variant == "normal"):
				if(self.tree.widgetName == "ttk::treeview"):
					self.var.set(self.get_tree_value())
					self.selectAll()
				else:
					self.var.set(self.tree.get_var())
			elif(variant == "paste"):
				self.insert("insert", self.clipboard_get())
			else:
				self.var.set(data)
			
		def save_changes(self, Bool = 1):
			if(self.tree.widgetName == "ttk::treeview"):
				self.set_tree_value(self.get())
			else:
				self.tree.set_var(self.get())
			if(Bool):
				self.destroy()
				
			
			
#--------------------------------------------------------MenuButtonPopup-----------------------------------------------------------------	
	
	
	class MenuButtonPopup(ttk.Menubutton, PopupWidget):
		
		def __init__(self, tree, rowid, column, choices, forceheight = 0, **kw):
			self.choices = choices
			super().__init__(tree, style = "popup.TMenubutton", **kw)
			self.init_menu()
			self.ini_PopupWidget(tree, rowid, column, forceheight)
			self.config(textvariable = self.var, menu = self.menu)
			
			self.bind("<Button-3>", lambda event: None)
			
		def place_call(self, x, y, width, anchor, height):
			pady = height / 2
			if(not self.forceheight):
				self.place(x = x - 4, y = y + pady, width = width + 25, anchor = tk.W)
			else:
				self.place(x = x - 4, y = y + pady, width = width + 25, anchor = tk.W, height = height)
		
		def init_menu(self):
			self.menu = ttk.tkinter.Menu(self, tearoff=0)
			
			for choice in self.choices:
				self.menu.add_command(label=choice, command = lambda var = choice: self.set_var(var))
		
		def get_var(self):
			return self.var.get()
		
		def set_var(self, data = None):
			if(data == None):
				value = self.get_tree_value()
				if(value in self.choices):
					self.var.set(value)
			else:
				self.var.set(data)
			
		def save_changes(self, Bool = 1):
			self.set_tree_value(self.var.get())
			if(Bool):
				self.destroy()
	
			
#--------------------------------------------------------ComboBoxPopup-----------------------------------------------------------------
	
	
	class ComboListBox(ttk.Combobox):
		"""
		Grands access to the hidden listbox of the combobox
		"""
		def __init__(self, master, **kw):
			super().__init__(master, **kw)
			self.listbox = str(self.tk.call("ttk::combobox::PopdownWindow", self._w)) + ".f.l"
		
		def lbbox(self, index):
			"""Return a tuple of X1,Y1,X2,Y2 coordinates for a rectangle
			which encloses the item identified by the given index."""
			return self._getints(self.tk.call(self.listbox, 'bbox', index)) or None
		
		def lbind(self, sequence=None, func=None, add=None):
			return self._bind(('bind', self.listbox), sequence, func, add)
		
		def lcurselection(self):
			return self._getints(self.tk.call(self.listbox, 'curselection')) or ()
			
		def lget(self, first, last = None):
			if last is not None:
				return self.tk.splitlist(self.tk.call(self.listbox, 'get', first, last))
			else:
				return self.tk.call(self.listbox, 'get', first)
			
		def linsert(self, index, *elements):
			self.tk.call((self.listbox, 'insert', index) + elements)
			self.setList(self.lget(0, tk.END))
		
		def lsize(self):
			return tk.getint(self.tk.call(self.listbox, 'size'))
		
		def ldelete(self, first, last=None):
			self.tk.call(self.listbox, 'delete', first, last)
			self.setList(self.lget(0, tk.END))
		
		def lcget(self, key):
			"""Return the resource value for a KEY given as string."""
			return self.tk.call(self.listbox, 'cget', '-' + key)
		
		def lconfigure(self, cnf = None, **kw):
			return self._lconfigure("configure", cnf, **kw)
			
		def _lconfigure(self, cmd, cnf, **kw):
			"""Internal function."""
			if kw:
				cnf = tk._cnfmerge((cnf, kw))
			elif cnf:
				cnf = tk._cnfmerge(cnf)
			if cnf is None:
				return self._getconfigure(tk._flatten((self.listbox, cmd)))
			if isinstance(cnf, str):
				return self._getconfigure1(tk._flatten((self.listbox, cmd, '-'+cnf)))
			self.tk.call(tk._flatten((self.listbox, cmd)) + self._options(cnf))
		
		def litemcget(self, index, option):
			"""Return the resource value for an ITEM and an OPTION."""
			return self.tk.call((self.listbox, 'itemcget') + (index, '-'+option))
			
		def litemconfigure(self, index, cnf=None, **kw):
			"""Configure resources of an ITEM.

			The values for resources are specified as keyword arguments.
			To get an overview about the allowed keyword arguments
			call the method without arguments.
			Valid resource names: background, bg, foreground, fg,
			selectbackground, selectforeground."""
			return self._lconfigure(('itemconfigure', index), cnf, **kw)
		
		def getList(self):
			return self.cget("values")
		
		def setList(self, data):
			self.configure(values = data)
		
		def postList(self):
			self.tk.call("ttk::combobox::Post", self._w)
		
		def unpostList(self):
			self.tk.call("ttk::combobox::Unpost", self._w)
		
	
	class ComboBoxPopup(ComboListBox, ttk.Combobox, PopupWidget):
		
		def __init__(self, tree, rowid, column, forceheight = 0, **kw):
			super().__init__(tree, style = "popup.TCombobox", **kw)
			self.ini_PopupWidget(tree, rowid, column, forceheight)
			self.config(validate = "key", validatecommand = self.vcmd, textvariable = self.var)
			self.preModLst = []
			self.posModLst = []
			self.menu()
			
		def menu(self):
			self.modmenu = ttk.tkinter.Menu(tearoff=0)
			self.modmenu.add_command(label="Add", command = lambda event = None: self.addMod())
			self.modmenu.add_command(label="Delete", command = lambda event = False: self.removeMod(False))
			self.modmenu.add_command(label="Mod Undo", command = lambda event = None: self.undo())
			self.modmenu.add_command(label="Mod Redo", command = lambda event = None: self.redo())
			#self.modmenu.add_cascade(label="Text", menu=self.dropdownmenu)
			
			self.bind("<Return>", lambda event: self.addMod())
			self.bind("<Delete>", lambda event: self.removeMod(event))
			self.bind("<<ComboboxSelected>>", lambda event: self.set_edit())
			self.bind("<Control-z>", lambda event: self.check_unredo(self.preLst, self.undo, self.entry_undo))
			self.bind("<Control-y>", lambda event: self.check_unredo(self.posLst, self.redo, self.entry_redo))
			
			# binds to the hidden listbox of the combobox
			self.lbind("<Button-3>", lambda event, menu=self.modmenu: popupMenu(event, menu))
			self.lbind("<Delete>", lambda event = False: self.removeMod(False))
			self.lbind("<Control-z>", lambda event: self.undo())
			self.lbind("<Control-y>", lambda event: self.redo())
			self.lbind("<FocusOut>", lambda event: self.check_focus("popdown"))
			
		def check_focus(self, preState = "entry"):
			if(preState == "entry" and (Util.str_in_Error("popdown", KeyError, self.focus_get) or self.focus_get().winfo_name() == self.winfo_name())):
				return
			elif(preState == "popdown" and self.focus_get().winfo_name() == self.winfo_name()):
				return
			else:
				focus = self.tree.identify_region(self.tree.winfo_pointerx() - self.tree.winfo_rootx(), self.tree.winfo_pointery() - self.tree.winfo_rooty())
				if(focus in ["heading", "separator"]):
					self.focus()
				else:
					self.save_changes(0)
					self.destroy()
		
		def check_unredo(self, changes, unredoMod, unredoEntry):
			if(len(changes) == 0):
				unredoMod()
			else:
				unredoEntry()
		
		def set_edit(self, *args):
			self.edit = self.current()
		
		def get_var(self, variant = "normal"):
			if(variant == "normal"):
				return (self.get(),) + self.cget("values")
			elif(variant in ("cut", "copy")):
				if(self.select_present()):
					substr = self.selection_get()
				else:
					substr = self.get()
				if(variant == "cut"):
					self.entry_delete()
				return substr
		
		def set_var(self, data = None, variant = "normal"):
			if(data == None and variant == "normal"):
				self.setList(tuple(val for val in self.get_tree_value().split(" | ")))
			elif(variant == "paste"):
				self.insert("insert", self.clipboard_get())
			elif(isinstance(data, str)):
				self.var.set(data)
			self.edit = -1
		
		def save_changes(self, Bool = 1):
			modstr = ""
			for mod in self.getList():
				if(mod != ""):
					modstr += mod + " | "
			self.set_tree_value(modstr.rstrip(" | "))
			#if(not self.tree.str_in_Error("popdown", KeyError, self.focus_get) and not self.focus_get().winfo_name() == self.winfo_name()):
			if(Bool):
				self.destroy()
		
		def addMod(self):
			if(self.get() and self.get() not in self.getList()):
				self.preModLst.append(self.getList())
				self.posModLst.clear()
				if(self.edit != -1):
					temp = self.getList()
					pre = temp[0:self.edit]
					pos = temp[self.edit+1:]
					self.setList(pre + (self.get(),) + pos)
				else:
					self.setList(self.getList() + (self.get(),))
				self.set("")
				self.edit = -1
		
		def removeMod(self, Bool):
			oldmods = self.getList()
			self.preModLst.append(oldmods)
			index = self.lcurselection()
			if(Bool):
				index = (self.current(),)
				self.set("")
				self.edit = -1
			for i in index:
				self.ldelete(i)
			mods = self.lget(0, tk.END)
			self.setList(mods)
			self.postList()
			return "break"
			
		def undo(self):
			if(len(self.preModLst) > 0):
				res = self.preModLst.pop()
				self.posModLst.append(self.getList())
				self.setList(res)
				self.postList()

		def redo(self):
			if(len(self.posModLst) > 0):
				res = self.posModLst.pop()
				self.preModLst.append(self.getList())
				self.setList(res)
				self.postList()
		
		

#---------------------------------------------------------ListBoxPopup----------------------------------------------------------------
			
	class ListBoxPopup(ttk.tkinter.Listbox, PopupWidget):
		
		def __init__(self, tree, rowid, column, forceheight = 0, **kw):
			super().__init__(tree, **kw)
			self.ini_PopupWidget(tree, rowid, column, forceheight)
			self.config(selectmode = tk.EXTENDED)
			self.preModLst = []
			self.posModLst = []
			self.entry = None
			self.menu()
			
		def menu(self):
			self.modmenu = ttk.tkinter.Menu(tearoff=0)
			self.modmenu.add_command(label="New", command = lambda event = None: self.addMod())
			self.modmenu.add_command(label="Delete", command = lambda event = None: self.removeMod())
			self.modmenu.add_command(label="Undo", command = lambda event = None: self.undo())
			self.modmenu.add_command(label="Redo", command = lambda event = None: self.redo())
			
			self.bind("<Button-3>", lambda event, menu=self.modmenu, widget=self: self.popupMenu(event, menu, widget))
			self.bind("<Double-Button-1>", lambda event: self.editMod())
			self.bind("<Control-z>", lambda event: self.undo())
			self.bind("<Control-y>", lambda event: self.redo())
		
		def popupMenu(self, event, menu, Widget = None):
			#print(Widget.widgetName)
			if(Widget.widgetName == "listbox"):
				index = int(Widget.nearest(event.y))
				if(len(Widget.curselection()) < 2 or index not in Widget.curselection()):
					Widget.selection(index, 1)
			popupMenu(event, menu, Widget)
		
		def place_call(self, x, y, width, anchor, height, forceheight = 0):
			if(not forceheight):
				self.place(x = x, y = y, width = width, anchor = tk.NW)
			else:
				self.place(x = x, y = y, width = width, anchor = tk.NW, height = height)
		
		def resize(self):
			super().resize()
			try:
				self.entry.resize()
			except:
				pass
		
		def get_var(self):
			return self.get(tk.ACTIVE)
		
		def set_var(self, data = None):
			if(data == None):
				self.lst = self.tree.set(self.rowid, column = self.column).split(" | ")
				self.insert(0, *self.lst)
				self.config(height = len(self.lst))
			elif(isinstance(data, str)):
				self.insert(self.active, data)
				self.delete(self.active + 1)
				self.focus()
			elif(isinstance(data, tuple)):
				self.delete(0, tk.END)
				self.insert(0, *data)
				self.focus()
		
		def save_changes(self, Bool = 1):
			modstr = ""
			for mod in self.get(0, tk.END):
				if(mod != ""):
					modstr += mod + " | "
			self.tree.set(self.rowid, column = self.column, value = modstr.rstrip(" | "))
			if(Bool):
				self.destroy()
		
		def editMod(self):
			if(self.entry == None or not self.entry.winfo_exists()):
				self.active = self.index(tk.ACTIVE)
				self.entry = self.tree.EntryPopup(self, str(self.active), self.column)
		
		def selection(self, indexes, activate):
			self.select_clear(0, tk.END)
			if(isinstance(indexes, int)):
				indexes = [indexes]
			for i in indexes:
				self.select_set(i)
				self.activate(i)
		
		def addMod(self):
			self.preLst.append(self.get(0, tk.END))
			self.insert(0, "")
			self.config(height = self.size())
			self.selection(0, 1)
			self.editMod()
		
		def removeMod(self):
			self.preLst.append(self.get(0, tk.END))
			self.delete(tk.ACTIVE)
			self.config(height = self.size())
			
		def undo(self):
			if(len(self.preLst) > 0):
				if(isinstance(self.preLst[-1], tuple)):
					res = self.preLst.pop()
					self.posLst.append(self.get(0, tk.END))
					self.set_var(res)
					self.config(height = self.size())
				else:
					self.entry_undo()
		
		def redo(self):
			if(len(self.posLst) > 0):
				if(isinstance(self.posLst[-1], tuple)):
					res = self.posLst.pop()
					self.preLst.append(self.get(0, tk.END))
					self.set_var(res)
					self.config(height = self.size())
				else:
					self.entry_redo()

		def bbox(self, index, *args):
			x,y,width,height = super().bbox(index)
			return (-x, y, self.winfo_width(), height)
			
		def identify_region(self, x, y):
			return self.tree.identify_region(x, y)
		
		def winfo_rootx(self):
			return self.tree.winfo_rootx()
		
		def winfo_rooty(self):
			return self.tree.winfo_rooty()
		
		

#--------------------------------------------------Scrollbars-----------------------------------------------------------------------


class AutoScrollbar(ttk.Scrollbar):
	# a scrollbar that hides itself if it's not needed.  only
	# works if you use the grid geometry manager.
	def __init__(self, parent, **kw):
		super().__init__(parent, **kw)
		
	def set(self, lo, hi):
		if(float(lo) <= 0.0 and float(hi) >= 1.0):
			self.grid_remove()
		else:
			self.grid()
		ttk.Scrollbar.set(self, lo, hi)
		
		
def setScrollBar(widget, x = 0, y = 0):
	xscrollbar = AutoScrollbar(widget.master, orient=tk.HORIZONTAL)#ttk.Scrollbar(widget.master, orient=HORIZONTAL)
	yscrollbar = AutoScrollbar(widget.master)#ttk.Scrollbar(widget.master)
		
	if(x):
		widget.config(xscrollcommand = xscrollbar.set)
		if(widget.widgetName == "ttk::treeview"):
			xscrollbar.config(command = lambda *arg: widget._onTreeScrollx(*arg))
		else:
			xscrollbar.config(command = widget.xview)
			
	if(y):
		widget.config(yscrollcommand = yscrollbar.set)
		if(widget.widgetName == "ttk::treeview"):
			yscrollbar.config(command = lambda *arg: widget._onTreeScrolly(*arg))
		else:
			yscrollbar.config(command = widget.yview)
		
	widget.grid(row = 0, column = 0, sticky=tk.NSEW)
	if(x):
		xscrollbar.grid(row = 1, column = 0, sticky=tk.EW)
	if(y):
		yscrollbar.grid(row = 0, column = 1, sticky=tk.NS)
	widget.master.rowconfigure(0, weight=1)
	widget.master.columnconfigure(0, weight=1)


#--------------------------------------------------ToolTip-----------------------------------------------------------------------


class ToolTip(ttk.tkinter.Toplevel):
	
	def __init__(self, event, text = False):
		super().__init__()
		self.after(1000, self.init)
		self.x = None; self.y = None
		self.withdraw()
		self.event = event
		self.text = text
		self.dead = False
		self.get_coordinates()
		
	def init(self):
		if(not self.text):
			self.get_value()
			
		if(self.eval_mouse_pos()):
			self.show()
		
	def get_value(self):
		if(self.event.widget.widgetName == "ttk::treeview"):
			self.text = self.event.widget.set(self.rowid, self.column)
			
		elif(self.event.widget.widgetName in ("ttk::button", "ttk::menubutton", "ttk::label", "ttk::entry")):
			self.text = self.event.widget.configure("text")
			if(isinstance(self.text, tuple) and "textvariable" in self.text):
				self.text = self.getvar(self.event.widget.cget("textvariable"))
		
	def get_coordinates(self):
		if(self.event.widget.widgetName == "ttk::treeview"):
			self.column = self.event.widget.identify_column(self.event.x)
			self.rowid = self.event.widget.identify_row(self.event.y)
			self.x, self.y, self.width, self.height = self.event.widget.bbox(self.rowid, self.column)
		else:
			self.x, self.y, self.width, self.height = self.geometry()
		
	def show(self):
		x = self.x + (self.event.widget.winfo_rootx() if self.event.widget.master == None else self.event.widget.master.winfo_rootx())
		y = self.y + (self.event.widget.winfo_rooty() if self.event.widget.master == None else self.event.widget.master.winfo_rooty()) + self.height
		self.wm_overrideredirect(1)
		self.wm_geometry("+%d+%d" % (x, y))
		label = ttk.Label(self, text = self.text, justify = tk.LEFT)#, relief = tk.RAISED)#, font = font.nametofont("TkTooltipFont"))
		label.pack()
		self.deiconify()
		
	def eval_mouse_pos(self):
		x = self.event.widget.winfo_pointerx() - (self.event.widget.winfo_rootx() if self.event.widget.master == None else self.event.widget.master.winfo_rootx())
		y = self.event.widget.winfo_pointery() - (self.event.widget.winfo_rooty() if self.event.widget.master == None else self.event.widget.master.winfo_rooty())
		if(not self.dead and self.x != None and self.y != None):
			return x > self.x and x < self.x + self.width and y > self.y and y < self.y + self.height
		else:
			return False
		
	def geometry(self):
		string = self.event.widget.winfo_geometry()
		x = string.find("x")
		p1 = string.find("+")
		p2 = string.find("+", p1+1)
		return (int(string[p1+1:p2]), int(string[p2+1:]), int(string[0:x]), int(string[x+1:p1]))
		
	def geometry2(self):
		return (int(self.event.widget.winfo_x()), int(self.event.widget.winfo_y()), int(self.event.widget.winfo_width()), int(self.event.widget.winfo_height()))
		
	def destroy(self):
		super().destroy()
		self.dead = True

#--------------------------------------------------Menue-----------------------------------------------------------------------


def styleMenue(master, menubar):
	stylemenu = ttk.tkinter.Menu(menubar, tearoff = 0)
	menubar.add_cascade(label = "Style", menu = stylemenu)
	
	for style in sorted(ttk.Style(master).theme_names()):
		stylemenu.add_command(label = style.capitalize(), command = lambda style = style, master = master:ttk.Style(master).theme_use(style))
	

#--------------------------------------------------Misc-----------------------------------------------------------------------

def create_vcmd(master, conditions = False):
	return (master.register(_vcmd), master, conditions, '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

def create_invcmd(master, conditions = False):
	return (master.register(_invcmd), master, conditions, '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

def _vcmd(master, conditions, d, i, P, s, S, v, V, W):
	truthVal = True
	if(d == "1"):
		if(not Util.isInt(S)):
			truthVal = False
		
	return truthVal

def _invcmd(master, conditions, d, i, P, s, S, v, V, W):
	if(d):
		if(Util.isInt(P) and int(P) > int(conditions["maxval"])):
			temp = master.children
			j = 0
			lsttemp = W.split(".")
			for i in lsttemp:
				if(i and j != len(lsttemp)-1):
					temp = temp[i].children
				elif(i):
					temp = temp[i]
				j += 1
			
			master.setvar(temp.cget("textvariable"), conditions["maxval"])
			temp.icursor(len(conditions["maxval"]))
			temp.config(validate = "key")


def GridColRowConfig(frame, cells = tk.ALL, C_weight = 1, R_weight = 1):
	if(isinstance(cells, (list, tuple))):
		C_cells, R_cells = cells
	else:
		C_cells = R_cells = cells
	frame.grid_columnconfigure(C_cells, weight = C_weight)
	frame.grid_rowconfigure(R_cells, weight = R_weight)

def popupMenu(event, menu, Widget = None):
	menu.post(event.x_root, event.y_root)

def popupWindow(window):
	window.update()
	window.deiconify()