import requests
from bs4 import BeautifulSoup
import wx
import os
import re
from ebooklib import epub

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
        processButton = wx.Button(panel, id=wx.ID_ANY, label='Go', size=(70, 30))
        hboxButton.Add(processButton, flag=wx.RIGHT, border=5)
        vbox.Add(hboxButton, flag=wx.LEFT|wx.BOTTOM, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnProcess, id=processButton.GetId())

        #Textbox
        hboxText = wx.BoxSizer(wx.HORIZONTAL)
        self.statusTextBox = wx.StaticText(panel, label='Test', style=wx.ALIGN_LEFT)
        self.statusTextBox.SetFont(font)
        hboxText.Add(self.statusTextBox, flag=wx.ALL, border=10)
        vbox.Add(hboxText, flag=wx.ALL, border=5)

        panel.SetSizer(vbox)

    def OnProcess(self, event):
        #Get Page data
        url = self.textControlURL.GetValue()
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'lxml')
        self.statusTextBox.SetLabel("Finished Loading")

        #Generate ePub
        titleName = f"{soup.find('h4').get_text()} chapter {self.startChapter.GetValue()} - chapter {self.endChapter.GetValue()}"
        #Delete Old File If Exists
        desktop = os.path.expanduser("~/Desktop")
        #desktop + '/' + titleName
        if os.path.exists(f"{desktop}/{titleName}"):
            os.remove(f"{desktop}/{titleName}")
        #I/O
        #book = open(f"{desktop}/{titleName}", "xt", encoding="utf-8")
        book = epub.EpubBook()
        book.set_identifier(titleName)
        book.set_title(titleName)
        book.set_language('en')

        #Find start chapter
        links = soup.find(id='accordion')

        #Find first specified chapter link
        startLink = 'https://www.wuxiaworld.com'

        for link in links.find_all('a'):
            if re.search(f"chapter-{self.startChapter.GetValue()}$",link.get('href')):
                startLink += link.get('href')
        
        #Process first page of content
        page = requests.get(startLink)
        soup = soup = BeautifulSoup(page.content, 'lxml')
        pageText = soup.find('div', {'class' :'fr-view'})

        #Chapter Contents
        chapter = epub.EpubHtml(title='Chapter'+self.startChapter.GetValue(), file_name='Chapter'+self.startChapter.GetValue()+'.xhtml')
        chapter.set_content('<h1>About this book</h1><p>This is a book.</p>')
        book.add_item(chapter)
        #Add NCX and Navigation Title and then Write book to Desktop
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        epub.write_epub(f"{desktop}/{titleName}.epub", book)
        '''for p in pageText.find_all('p'):
            #Exclude uneeded lines
            if re.search('Previous Chapter', p.text):
                pass
            else:
                book.write(str(p)+'\n')'''

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