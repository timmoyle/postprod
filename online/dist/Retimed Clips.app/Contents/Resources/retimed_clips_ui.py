#!/usr/bin/env python
import os, sys, wx, retimed_clips
import wx.grid as gridlib

class FileDrop(wx.FileDropTarget):
	def __init__(self, window):
		wx.FileDropTarget.__init__(self)
		self.window = window

	def OnDropFiles(self, x, y, filenames):
		tried_non_xml = False
		for name in filenames:
			if (os.path.splitext(name)[1][1:].strip().lower()=='xml') and (retimed_clips.is_valid_xml(name) is True):
				self.window.add_filename(name)
			else:
				tried_non_xml = True
				
		if tried_non_xml is True:
			dlg = wx.MessageDialog(self.window, "This application can only process FCP7 XML files", style=wx.OK|wx.CENTRE|wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		
		
class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(800,400))
		
		self.my_filenames = []
		
		MenuBar = wx.MenuBar()
		filemenu = wx.Menu()

		# wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
		item  = filemenu.Append(wx.ID_EXIT, "E&xit")
		self.Bind(wx.EVT_MENU, self.OnQuit, item)
		
		MenuBar.Append(filemenu, "&File")
		self.SetMenuBar(MenuBar)

		panel = wx.Panel(self)
		
		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		
		lists_buttons_sizer = wx.FlexGridSizer(4, 2)
		
		lists_buttons_sizer.Add(wx.StaticText(panel, label="FCP7 XML Files To Process"))
		lists_buttons_sizer.Add(wx.StaticText(panel, label=""))

		self.file_listbox = wx.ListBox(panel, style=wx.LB_EXTENDED)
		lists_buttons_sizer.Add(self.file_listbox, 1, wx.EXPAND|wx.TOP, border=2)
		
		dt = FileDrop(self)
		self.file_listbox.SetDropTarget(dt)		
		
		button_sizer = wx.BoxSizer(wx.VERTICAL)
		load_button = wx.Button(panel, label='Add XML Files')
		load_button.SetFont(font)
		self.Bind(wx.EVT_BUTTON, self.add_row, load_button)
		button_sizer.Add(load_button, flag=wx.EXPAND|wx.ALL, border=3)

		remove_button = wx.Button(panel, label='Remove Selected XML Files')
		remove_button.SetFont(font)
		self.Bind(wx.EVT_BUTTON, self.remove_row, remove_button)
		button_sizer.Add(remove_button, flag=wx.EXPAND|wx.ALL, border=3)
		
		lists_buttons_sizer.Add(button_sizer, flag=wx.TOP|wx.EXPAND, border=2)

		lists_buttons_sizer.Add(wx.StaticText(panel, label="Save Processed XML Files To"), flag=wx.TOP, border=10)
		lists_buttons_sizer.Add(wx.StaticText(panel, label=""))
		
		self.save_dir = wx.TextCtrl(panel, style=wx.TE_READONLY)
		lists_buttons_sizer.Add(self.save_dir, 1, flag=wx.EXPAND)

		pick_saveto_button = wx.Button(panel, label='Change Save Folder')
		pick_saveto_button.SetFont(font)
		self.Bind(wx.EVT_BUTTON, self.change_directory, pick_saveto_button)
		lists_buttons_sizer.Add(pick_saveto_button, flag=wx.EXPAND|wx.ALL, border=3)
		
		lists_buttons_sizer.AddGrowableRow(1,1)
		lists_buttons_sizer.AddGrowableCol(0,1)

		main_sizer.Add(lists_buttons_sizer, 1, flag=wx.EXPAND|wx.ALL, border=10)
		
		process_button = wx.Button(panel, label='Process XML Files')
		self.Bind(wx.EVT_BUTTON, self.process_files, process_button)
		main_sizer.Add(process_button, 0, flag=wx.ALIGN_CENTER|wx.ALL, border=10)

		panel.SetSizer(main_sizer)		
		
		self.Show(True)
		
	def OnQuit(self,Event):
		self.Destroy()		
		
	def add_row(self, event):
		dlg = wx.FileDialog(self, "Choose one or more FCP7 XML files", '', '', "*.xml", wx.FD_MULTIPLE)
		if dlg.ShowModal() == wx.ID_OK:
			for filename in dlg.GetFilenames():
				self.add_filename(os.path.join(dlg.GetDirectory(), filename))
		
		dlg.Destroy()
		
	def remove_row(self, event):
		print self.file_listbox.GetCount()
	
		selections = self.file_listbox.GetSelections()
		if (self.file_listbox.IsEmpty()) or (len(selections)==0):
			dlg = wx.MessageDialog(self, "No XML Files selected", style=wx.OK|wx.CENTRE)
			dlg.ShowModal()
			dlg.Destroy()
			return
			
		selections = list(selections)
		selections.reverse()
		for index in selections: 
			self.file_listbox.Delete(index) 

	def change_directory(self, event):
		dlg = wx.DirDialog(self, "Choose a folder to save processed XML to", style=wx.DD_DEFAULT_STYLE)
		if dlg.ShowModal() == wx.ID_OK:
			#self.save_dir.Clear()
			self.save_dir.SetValue(dlg.GetPath())
		dlg.Destroy()
		
	def add_filename(self, filename):
		self.file_listbox.InsertItems([filename], self.file_listbox.GetCount())
	
	def process_files(self, event):
		files_to_process = self.file_listbox.GetStrings()
		save_to_dir = self.save_dir.GetValue()
	
		if len(files_to_process)==0:
			dlg = wx.MessageDialog(self, "Please add FCP7 XML files to process", style=wx.OK|wx.CENTRE|wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return

		if len(save_to_dir)==0:
			dlg = wx.MessageDialog(self, "Please select a folder to save processed XML files to", style=wx.OK|wx.CENTRE|wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return
			
		files_processed = 0
			
		for file in files_to_process:
			save_to_file = os.path.join(save_to_dir, "RETIMED-%s" % os.path.basename(file))

			response = wx.ID_YES
			response_msg = ''
			
			if os.path.isfile(save_to_file):
				dlg = wx.MessageDialog(self, 'A file named "%s" already exists in %s.  Overwrite the existing file?' % (os.path.basename(save_to_file), save_to_dir), style=wx.YES_NO|wx.CENTRE|wx.ICON_EXCLAMATION)
				response = dlg.ShowModal()
				response_msg = "The file %s will not be processed." % file
				dlg.Destroy()
			elif retimed_clips.is_valid_xml(file) is False:
				response = wx.ID_NO
				response_msg = '%s is not a valid FCP7 XML file and will not be processed.' % file

			if response==wx.ID_NO:
				fine = wx.MessageDialog(self, response_msg, style=wx.OK|wx.CENTRE|wx.ICON_INFORMATION)
				fine.ShowModal()
				fine.Destroy()
				continue
			else:
				try:
					retimed_clips.process_file(file, save_to_file)
					files_processed += 1
				except IndexError:
					fine = wx.MessageDialog(self, "There was an error processing %s" % file, style=wx.OK|wx.CENTRE|wx.ICON_EXCLAMATION)
					fine.ShowModal()
					fine.Destroy()
				

		if files_processed>0:
			dlg = wx.MessageDialog(self, "%s XML files processed and saved to %s" % (files_processed, save_to_dir), style=wx.OK|wx.CENTRE|wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()

class MyApp(wx.App):
	def OnInit(self):	
		self.SetAppName('Retimed Clips')
		self.frame = MainWindow(None, "Extract Retimed Clips")
		
		if len(sys.argv)>1:
			for filename in sys.argv[1:]:
				self.frame.add_filename(filename)
		return True

app = MyApp(False)
app.MainLoop()