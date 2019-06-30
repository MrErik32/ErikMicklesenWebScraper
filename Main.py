from bs4 import BeautifulSoup
import os
import re
import requests
from pubsub import pub
from threading import Thread
import time
import wx


#Menu ID's
APP_EXIT = 1

#global variables
url = ""
startingChapter = 1
endingChapter = 1

#Thread
class ProcessThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()

    def run(self):
        # This is the code executing in the new thread.
        pub.sendMessage('update', msg='Started')
        #Get Page data
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'lxml')

        #Generate ePub
        seriesName = soup.find('h4').get_text()
        fileName = f"{seriesName} chapter {startingChapter} - chapter {endingChapter}.doc"
        #Delete Old File If Exists
        desktop = os.path.expanduser("~/Desktop")
        #desktop + '/' + fileName
        if os.path.exists(f"{desktop}/{fileName}"):
            os.remove(f"{desktop}/{fileName}")
        #I/O
        book = open(f"{desktop}/{fileName}", "xt", encoding="utf-8")

        #Find start chapter
        links = soup.find(id='accordion')

        #Find first specified chapter link
        currentLink = 'https://www.wuxiaworld.com'

        for link in links.find_all('a'):
            if re.search(f"chapter-{startingChapter}$",link.get('href')):
                currentLink += link.get('href')
        
        #Begin looping through chapters to grab content
        for i in range(int(startingChapter), int(endingChapter)+1, 1):
            #Start timer before scraping
            t0 = time.time()
            page = requests.get(currentLink)
            soup = BeautifulSoup(page.content, 'lxml')
            pageText = soup.find("div", class_="fr-view")
            #Delay scaling on how long the server took to respond
            response_delay = time.time() - t0
            time.sleep(response_delay * 10)

            for p in pageText.find_all('p'):
                #Exclude uneeded lines
                if re.search('Previous Chapter', p.text):
                    pass
                else:
                    book.write(p.text+'\n')
            
            #Get next page link
            list = pageText.find_all("a")
            for link in list:
                if re.search("Next Chapter", link.string):
                    currentLink = 'https://www.wuxiaworld.com' + link.get('href')
            wx.CallAfter(self.postProgress, i, int(endingChapter))

        wx.CallAfter(pub.sendMessage, "update", msg='Finished!')

    def postProgress(self, currentChapter, endingChapter):
        """
        Send progress to GUI
        """
        prog = int((currentChapter/endingChapter)*100)
        pub.sendMessage("update", msg=f"In progress: {prog}%")

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
        hboxURL = wx.BoxSizer(wx.HORIZONTAL)
        staticTextURL = wx.StaticText(panel, label='URL:')
        staticTextURL.SetFont(font)
        hboxURL.Add(staticTextURL, flag=wx.RIGHT, border=8)
        self.textControlURL = wx.TextCtrl(panel)
        hboxURL.Add(self.textControlURL, proportion=1)
        vbox.Add(hboxURL, flag=wx.EXPAND|wx.ALL, border=10)

        #Chapter Selection
        hboxChapter = wx.BoxSizer(wx.HORIZONTAL)
        startText = wx.StaticText(panel, label='Start Chapter:')
        startText.SetFont(font)
        hboxChapter.Add(startText, flag=wx.RIGHT, border=8)
        self.startChapter = wx.TextCtrl(panel, size=(50,24))
        hboxChapter.Add(self.startChapter, proportion=0)
        endText = wx.StaticText(panel, label='Ending Chapter:')
        endText.SetFont(font)
        hboxChapter.Add(endText, flag=wx.RIGHT|wx.LEFT, border=8)
        self.endChapter = wx.TextCtrl(panel, size=(50,24))
        hboxChapter.Add(self.endChapter, proportion=0)
        vbox.Add(hboxChapter, flag=wx.EXPAND|wx.ALL, border=10)

        #Button
        hboxButton = wx.BoxSizer(wx.HORIZONTAL)
        self.processButton = processButton = wx.Button(panel, id=wx.ID_ANY, label='Go', size=(70, 30))
        hboxButton.Add(processButton, flag=wx.RIGHT, border=5)
        vbox.Add(hboxButton, flag=wx.LEFT|wx.BOTTOM, border=5)
        processButton.Bind(wx.EVT_BUTTON, self.onButton, id=processButton.GetId())

        #Textbox
        hboxText = wx.BoxSizer(wx.HORIZONTAL)
        self.statusTextBox = wx.StaticText(panel, label='', style=wx.ALIGN_LEFT)
        self.statusTextBox.SetFont(font)
        hboxText.Add(self.statusTextBox, flag=wx.ALL, border=10)
        vbox.Add(hboxText, flag=wx.ALL, border=5)

        panel.SetSizer(vbox)

        # create pub reciever
        pub.subscribe(self.updateDisplay, 'update')

    def onButton(self, event):
        global url
        global startingChapter
        global endingChapter

        url = self.textControlURL.GetValue()
        startingChapter = self.startChapter.GetValue()
        endingChapter = self.endChapter.GetValue()

        ProcessThread()
        self.buttonLock(True)

    def updateDisplay(self, msg):
        self.statusTextBox.SetLabel(msg)

    def buttonLock(self, lockStatus):
        if lockStatus is True:
            self.processButton.Disable()
        else:
            self.processButton.Enable()

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