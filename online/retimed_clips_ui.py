#!/usr/bin/env python
import os
import wx
import wx.grid as gridlib

class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(1200,400))
		#wx.Frame.__init__(self, parent, title=title, si)

		panel = wx.Panel(self)
		
		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		#font.SetPointSize(9)
		
		main_sizer = wx.BoxSizer(wx.HORIZONTAL)

		grid_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.my_grid = gridlib.Grid(panel)
		self.my_grid.CreateGrid(0, 3)
		self.my_grid.SetColLabelValue(0, "Source XML")
		self.my_grid.SetColLabelValue(1, "New Timeline Name")
		self.my_grid.SetColLabelValue(2, "Save To")
		self.my_grid.SetDefaultColSize(300)
		self.my_grid.SetColMinimalAcceptableWidth(300)
		self.my_grid.AutoSizeColumns()
		grid_sizer.Add(self.my_grid, 1, wx.EXPAND|wx.ALL)
		main_sizer.Add(grid_sizer, 1, flag=wx.EXPAND|wx.ALL, border=1)
		
		button_sizer = wx.BoxSizer(wx.VERTICAL)
		load_button = wx.Button(panel, label='Add XML Files')
		load_button.SetFont(font)
		self.Bind(wx.EVT_BUTTON, self.add_row, load_button)
		button_sizer.Add(load_button, flag=wx.EXPAND|wx.ALL, border=3)

		save_button = wx.Button(panel, label='Generate New XML Files')
		save_button.SetFont(font)
		button_sizer.Add(save_button, flag=wx.EXPAND|wx.ALL, border=3)
		
		main_sizer.AddSpacer(10)

		main_sizer.Add(button_sizer, flag=wx.ALL|wx.EXPAND)

		panel.SetSizer(main_sizer)		
		
		self.Show(True)
		
	def add_row(self, event):
		dlg = wx.FileDialog(self, "Choose one or more FCP7 XML files", '', '', "*.xml", wx.FD_MULTIPLE)
		if dlg.ShowModal() == wx.ID_OK:
			for filename in dlg.GetFilenames():
				new_row_index = self.my_grid.GetNumberRows()
				self.my_grid.AppendRows(1)
				self.my_grid.SetCellValue(new_row_index, 0, os.path.join(dlg.GetDirectory(), filename))
				self.my_grid.SetCellValue(new_row_index, 2, os.path.join(dlg.GetDirectory(), "RETIMED-%s" % filename))
		
		dlg.Destroy()		
	
		print self.my_grid.GetSize()
		
		

app = wx.App(False)
frame = MainWindow(None, "Extract Retimed Clips")
app.MainLoop()