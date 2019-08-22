import wx
import wx.adv
import StegAppFrameJoiner as safp
from threading import Thread
import ZipToImage3 as zti3
import os
import webbrowser

from concurrent import futures
import time




class StegAppFrameJoiner(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(StegAppFrameJoiner, self).__init__(*args, **kw)

        # create a panel in the frame
        self.pnl = wx.Panel(self)
        self.pnl.SetBackgroundColour("#ffffff")

        sizer = wx.GridBagSizer(4, 4)

        text = wx.StaticText(self.pnl, label="Information")
        sizer.Add(text, pos=(5, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        self.information_text = wx.StaticText(self.pnl, label="CHUNK COUNT: 0")
        sizer.Add(self.information_text, pos=(5, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        text = wx.StaticText(self.pnl, label="File Processing Percentage")
        sizer.Add(text, pos=(6, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        self.gauge = wx.Gauge(self.pnl, id=wx.ID_ANY, range=100, pos=(10, 190), size=wx.DefaultSize,
                              style=wx.GA_HORIZONTAL,
                              validator=wx.DefaultValidator)
        sizer.Add(self.gauge, pos=(6, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        """
        spinControl = wx.SpinCtrl(self.pnl, value="", pos=(10, 220),
         size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=0, max=100, initial=0,
         name="wxSpinCtrl")
        sizer.Add(spinControl, pos=(4, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        """

        text = wx.StaticText(self.pnl, label="Select file to split into Images")
        sizer.Add(text, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        self.file_picker = wx.DirPickerCtrl(self.pnl, message="Select Compressed Files Folder", size=wx.DefaultSize)
        font = self.file_picker.GetFont()
        font.PointSize += 10
        font = font.Bold()
        self.file_picker.SetFont(font)
        sizer.Add(self.file_picker, pos=(1, 0), span=(1, 5),
                  flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)



        buttonOk = wx.Button(self.pnl, label="Open Selected Folder", id=1)
        sizer.Add(buttonOk, pos=(6, 3))
        sizer.AddGrowableCol(2)
        sizer.AddGrowableRow(4)
        self.pnl.SetSizer(sizer)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar

    #        self.CreateStatusBar()
    #        self.SetStatusText("Welcome to wxPython!")

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        newItem = fileMenu.Append(-1, "&New\tCtrl+N", "Reset Program")
        openItem = fileMenu.Append(0, "&Open\tCtrl+O",
                                   "Load a new image")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT, '&Quit\tCtrl+Q')

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnNew, newItem)
        self.Bind(wx.EVT_MENU, self.OnOpen, openItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

        viewMenu = wx.Menu()
        menuBar.Append(viewMenu, "&View")
        self.shst = viewMenu.Append(wx.ID_ANY, 'Show statusbar',
                                    'Show Statusbar', kind=wx.ITEM_CHECK)
        self.shtl = viewMenu.Append(wx.ID_ANY, 'Show toolbar',
                                    'Show Toolbar', kind=wx.ITEM_CHECK)

        viewMenu.Check(self.shst.GetId(), True)
        viewMenu.Check(self.shtl.GetId(), True)
        self.Bind(wx.EVT_MENU, self.ToggleStatusBar, self.shst)
        self.Bind(wx.EVT_MENU, self.ToggleToolBar, self.shtl)

        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('Ready')

        self.Bind(wx.EVT_BUTTON, self.button_press)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        self.toolbar = self.CreateToolBar(style=wx.TB_TEXT)
        tool1 = self.toolbar.AddTool(1, 'Clear', wx.Bitmap('3d_img1.png'))
        tool2 = self.toolbar.AddTool(2, 'Info', wx.Bitmap('3d_img2.png'))
        tool3 = self.toolbar.AddTool(3, 'Join', wx.Bitmap('3d_img3.png'))
        tool4 = self.toolbar.AddTool(4, 'Hash', wx.Bitmap('3d_img4.png'))
        self.toolbar.Realize()
        self.Bind(wx.EVT_TOOL, self.OnClear, tool1)
        self.Bind(wx.EVT_TOOL, self.OnInfo, tool2)
        self.Bind(wx.EVT_TOOL, self.OnJoin, tool3)
        self.Bind(wx.EVT_TOOL, self.OnHash, tool4)


    def OnHash(self, event):
        val = zti3.ZipToImage3.calculateHash(self)

        if val == 0:
            wx.MessageBox("File matches with original", "Hash Success", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("File is corrupted", "Hash Failure", wx.OK | wx.ICON_INFORMATION)



    def OnJoin(self, event):
        zti_instance = zti3.ZipToImage3(self, self.file_picker.GetPath())
        self.setZtiInstance(zti_instance)

        thread_pool_executor1 = futures.ThreadPoolExecutor(max_workers=4)
        thread_pool_executor1.submit(self.blocking_code3, self.getZtiInstance())

    def blocking_code3(self, zti_instance):
        #zti_instance.convertToImage()
        wx.CallAfter(self.set_status_text, 'Running')
        val = zti_instance.assembleFile()
        print(val)
        if val == 0:
            print("SHUT DOWN")
        else:
            print("RETURN ERROR")
        wx.CallAfter(self.set_status_text, 'Ready')


    def OnInfo(self, event):
        description = """
        Use browse button to find file to split and convert to images.
        Then choose the resolution you want the output images to be.
        The number of image files are calculated based on formula: file size / (3 * width * height).
        If the files are already split then use joiner to get back original file.
        """

        info = wx.adv.AboutDialogInfo()

        info.SetIcon(wx.Icon('flash.png', wx.BITMAP_TYPE_PNG))
        info.SetName('PySteg')
        info.SetVersion('0.1')
        info.SetDescription(description)
        info.SetCopyright('(C) 2019 - Beyond Asif Ahmed')
        info.SetWebSite('http://quickgrid.blogspot.com')
        info.AddDeveloper('Asif Ahmed')

        wx.adv.AboutBox(info, parent=self.pnl)


    def setZtiInstance(self, inst):
        self.inst = inst

    def getZtiInstance(self):
        return self.inst


    def gauge_updater(self, value, piece_number):
        print("GAUGE VALUE " + str(value))
        self.gauge.SetValue(int(value))

        print(piece_number)

        if piece_number == -1:
            self.information_text.SetLabel("Processing")
        elif piece_number == -2:
            self.information_text.SetLabel("Almost Done")
        elif piece_number == -3:
            self.information_text.SetLabel("Operation Completed")
        else:
            self.information_text.SetLabel("CHUNK COUNT: " + str(piece_number))



    def set_status_text(self, text):
        self.statusbar.SetStatusText(text)

    def OnNew(self, event):
        """Close the frame, terminating the application."""
        # self.Close(True)
        self.OnClear(self)

    def OnClear(self, event):
        self.file_picker.SetPath("")
        self.gauge.SetValue(0)
        self.information_text.SetLabel("CHUNK COUNT: 0")

    def button_press(self, event):
        Id = event.GetId()
        print('Click Button', str(Id))
        if Id == 1:
            print("OPEN FOLDER PRESSED")
            path = self.file_picker.GetPath()
            limit_index = path.rindex('\\')
            path = path[:limit_index + 1]
            path = os.path.realpath(path)
            webbrowser.open(os.path.realpath(path))


    def on_key(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_DOWN or key == wx.WXK_UP:
            i = self.get_focus()
            if i == 1:
                self.btn1.SetDefault()
                self.btn1.SetFocus()
            else:
                self.btn2.SetDefault()
                self.btn2.SetFocus()
            print('Focus on', str(i))
        elif key == wx.WXK_RETURN:
            print('ENTER on Button', str(event.GetId()))
        else:
            event.Skip()

    def get_focus(self):
        focused = wx.Window.FindFocus()
        if focused == self.btn1:
            return 2
        elif focused == self.btn2:
            return 1

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnOpen(self, event):
        # Create open file dialog, gives file path
        openFileDialog = wx.FileDialog(self, "Open", "", "",
                                       "PySteg files (*.psteg)|*.psteg",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        print(openFileDialog.GetPath())
        openFileDialog.Destroy()

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("App Developed by ASIF AHMED", "About", wx.OK | wx.ICON_INFORMATION)

    def ToggleStatusBar(self, e):
        if self.shst.IsChecked():
            self.statusbar.Show()
        else:
            self.statusbar.Hide()

    def ToggleToolBar(self, e):

        if self.shtl.IsChecked():
            self.toolbar.Show()
        else:
            self.toolbar.Hide()
