import requests
from bs4 import BeautifulSoup
import wx

#Menu ID's
APP_EXIT = 1

#GUI Setup
class GUI(wx.Frame):

    def __init__(self, parent, title):
        
        super(GUI, self).__init__(parent, title=title)

        self.InitUI()
        self.Centre()

    def InitUI(self):
        
        #MenuBar
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileItem = wx.MenuItem(fileMenu, APP_EXIT, '&Quit\tCtrl+Q')
        fileMenu.Append(fileItem)

        self.Bind(wx.EVT_MENU, self.OnQuit, id=APP_EXIT)

        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        #GUI Panel
        panel = wx.Panel(self)
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        vbox = wx.BoxSizer(wx.VERTICAL)

        #URL Textbox
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='URL:')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.tc = wx.TextCtrl(panel)
        hbox1.Add(self.tc, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.ALL, border=10)

        #Button
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        processButton = wx.Button(panel, id=wx.ID_ANY, label='Go', size=(70, 30))
        hbox2.Add(processButton, flag=wx.RIGHT, border=5)
        vbox.Add(hbox2, flag=wx.LEFT|wx.BOTTOM, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnProcess, id=processButton.GetId())

        #Textbox
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.st2 = wx.StaticText(panel, label='Test', style=wx.ALIGN_LEFT)
        self.st2.SetFont(font)
        hbox3.Add(self.st2, flag=wx.ALL, border=10)
        vbox.Add(hbox3, flag=wx.ALL, border=5)

        panel.SetSizer(vbox)

    def OnProcess(self, event):
        
        #Get Page data
        page = requests.get(self.tc.GetValue())
        soup = BeautifulSoup(page.content, 'html.parser')
        self.st2.SetLabel(str(page.status_code))

    def OnQuit(self, e):
        
        self.Close()

def main():
    
    app = wx.App()
    frame = GUI(None, title="Wuxia Chapter Scraper")
    frame.Show()
    app.MainLoop()

#Checking if main program
if __name__ == '__main__':
    main()