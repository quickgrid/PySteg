import wx
import StegAppFrameSplitter as st



if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()



    width, height = wx.GetDisplaySize()


    frm = st.StegAppFrameSplitter(None, title='File Splitter', pos=(width / 2 - width / 4, height / 2 - height / 4))
    frm.Show()
    frm.SetSize(width / 2, height / 2)




    app.MainLoop()

