#! /usr/bin/env python
#
"""XRD Main Window

We envision this as a notebook with tabs for each step in
the data processing procedure.
"""
import os, cPickle
from ConfigParser import SafeConfigParser as Parser

import wx
from wx.lib.wordwrap import wordwrap

import mdef

from XRD.Experiment import *

from guiConfig    import WindowParameters as WP
from guiUtilities import makeTitleBar
from xrdNoteBook  import xrdNoteBook
from canvasPanel  import CanvasPanel

from ListEditor      import ListEditDlg
from hydraInterface  import HydraControlFrame
from caking          import cakingDialog
#
# ---------------------------------------------------CLASS:  xrdMainFrame
#
class xrdMainFrame(wx.Frame):
    #
    def __init__(self, parent, id, title='LLNL XRD Analysis Tool'):
        #
        #  Pass option dictionary or string.
        #
        wx.Frame.__init__(self, parent, id, title)
        self.SetBackgroundColour(WP.BG_COLOR_FRAME)
	#
        #  Data
        #

        #
	#  Window Objects, menu bar and status bar.
	#
        self.__makeObjects()
	#
	#  Bindings.
	#
	self.__makeBindings()
	#
	#  Sizing.
	#
	self.__makeSizers()
	#
        self.__loadProject()
        #
	self.SetAutoLayout(True)
        self.SetSizerAndFit(self.sizer)
        #
        self.updateFromExp()
        #
        self.Show(True)

	return

    pass # class
    #
    # ============================== Internal Methods
    #
    def __makeObjects(self):
        """Add interactors"""
        #
        # NO TITLEBAR
        # self.tbarSizer = makeTitleBar(self, 'XRD Analysis')
        #
        #  Canvas panel will update on all pages.  Create this before
        #  creating the notebook.
        #
        self.canvasPanel = CanvasPanel(self, wx.NewId())
        #
        # Notebook
        #
        self.nBook = xrdNoteBook(self, wx.NewId())
	#
        # A Statusbar in the bottom of the window
        #
        self.CreateStatusBar()
        #
        # Creating the menubar.
        #
        menuBar = wx.MenuBar()

        self.__makeFileMenu()
        menuBar.Append(self.fileMenu,  "&File") 

        self.__makeMaterialMenu()
        menuBar.Append(self.materialMenu,  "&Materials") 
        
        self.__makeReaderMenu()
        menuBar.Append(self.readerMenu,  "Reader") 
        
        self.__makeDetectorMenu()
        menuBar.Append(self.detectorMenu,  "Detector") 
        
        self.__makeHelpMenu()
        menuBar.Append(self.helpMenu,  "Help") 
        
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        return

    def __makeFileMenu(self):
        """Construct file menu"""
        self.fileMenu = wx.Menu('File')
        #
        self.fileMenu.Append(wx.ID_NEW, "&New", "Create a new experiment")
        self.Bind(wx.EVT_MENU, self.OnFileNew, id=wx.ID_NEW)
        #
        self.fileMenu.Append(wx.ID_OPEN, "&Load", "Load a saved experiment")
        self.Bind(wx.EVT_MENU, self.OnFileLoad, id=wx.ID_OPEN)
        #
        self.fileMenu.Append(wx.ID_SAVE, "&Save As", "Save the experiment")
        self.Bind(wx.EVT_MENU, self.OnFileSave, id=wx.ID_SAVE)
        #
        self.fileMenu.Append(wx.ID_EXIT, "&Quit", "Quit the program")
        self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
        
        self.fileMenu.AppendSeparator()

        return

    def __makeMaterialMenu(self):
        """Construct calibrant menu"""
        self.materialMenu = wx.Menu('Materials')
        #
        #  Load, save and edit the material list
        #
        #  ===== Load List
        self.materialMenu.IDload = wx.NewId()
        self.materialMenu.Append(self.materialMenu.IDload, 
                             "Load material list", 
                             "Load a saved material list")
        self.Bind(wx.EVT_MENU, self.OnMaterialsLoad, id=self.materialMenu.IDload)
        #  ===== Edit List
        self.materialMenu.IDedit = wx.NewId()
        self.materialMenu.Append(self.materialMenu.IDedit, 
                                  "Edit material list", 
                                  "Rearrange/remove list items")
        self.Bind(wx.EVT_MENU, self.OnMaterialsEdit, id=self.materialMenu.IDedit)
        #  ===== Save List
        self.materialMenu.IDsave = wx.NewId()
	self.materialMenu.Append(self.materialMenu.IDsave, 
                           "Save material list", 
                           "Save the material list to a file.")
        self.Bind(wx.EVT_MENU, self.OnMaterialsSave, id=self.materialMenu.IDsave)

        return

    def __makeReaderMenu(self):
        """Menu for reader options"""
        self.readerMenu = wx.Menu('Readers')

        # ===== Load List
        self.readerMenu.IDloadl = wx.NewId()
	self.readerMenu.Append(self.readerMenu.IDloadl, 
                           "Load reader list", 
                           "Load the reader list to from a file")
        self.Bind(wx.EVT_MENU, self.OnReadersLoad, id=self.readerMenu.IDloadl)
        # ===== Edit
        self.readerMenu.IDedit = wx.NewId()
        self.readerMenu.Append(self.readerMenu.IDedit, 
                                  "Edit reader list", 
                                  "Rearrange/remove list items")
        self.Bind(wx.EVT_MENU, self.OnReadersEdit, id=self.readerMenu.IDedit)
        # ===== Save List
        self.readerMenu.IDsave = wx.NewId()
	self.readerMenu.Append(self.readerMenu.IDsave, 
                           "Save reader list", 
                           "Save the reader list to a file")
        self.Bind(wx.EVT_MENU, self.OnReadersSave, id=self.readerMenu.IDsave)
        #
        self.readerMenu.AppendSeparator()
        #
        # ===== Hydra
        #
        self.readerMenu.IDhydra = wx.NewId()
	self.readerMenu.Append(self.readerMenu.IDhydra,
                           "Hydra interface", 
                           "Open the hydra interface")
        self.Bind(wx.EVT_MENU, self.OnHydra, id=self.readerMenu.IDhydra)
        #

        return

    def __makeDetectorMenu(self):
        """Menu for detector options"""
        self.detectorMenu = wx.Menu('Detector')

        # ===== Load
        self.detectorMenu.IDload = wx.NewId()
	self.detectorMenu.Append(self.detectorMenu.IDload, 
                           "Load detector", 
                           "Load a saved detector from a file")
        self.Bind(wx.EVT_MENU, self.OnDetectorLoad, id=self.detectorMenu.IDload)
        # ===== Save
        self.detectorMenu.IDsave = wx.NewId()
	self.detectorMenu.Append(self.detectorMenu.IDsave, 
                           "Save detector", 
                           "Save the detector to a file")
        self.Bind(wx.EVT_MENU, self.OnDetectorSave, id=self.detectorMenu.IDsave)
        #
        self.detectorMenu.AppendSeparator()
        #
        #  Polar Rebin
        #
        # ===== Save
        self.detectorMenu.IDcake = wx.NewId()
	self.detectorMenu.Append(self.detectorMenu.IDcake, 
                           "Polar Rebinning", 
                           "Bring up a window for polar rebinning (caking)")
        self.Bind(wx.EVT_MENU, self.OnCaking, id=self.detectorMenu.IDcake)

        return

    def __makeHelpMenu(self):
        """Construct file menu"""
        self.helpMenu = wx.Menu('Help')
        #
        self.helpMenu.Append(wx.ID_ABOUT, "&About", "About heXRD")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)

        return


    def __makeBindings(self):
        """Bind interactors"""
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, 
                  self.OnPageChange, self.nBook)



        return

    def __makeSizers(self):
	"""Lay out the interactors"""
	
        self.hSizer = wx.BoxSizer(wx.HORIZONTAL)
	self.hSizer.Add(self.nBook,       1, 
                        wx.EXPAND|wx.ALIGN_CENTER|wx.RIGHT, 10)
	self.hSizer.Add(self.canvasPanel, 1,
                        wx.EXPAND|wx.ALIGN_CENTER|wx.TOP, 8)

	self.sizer = wx.BoxSizer(wx.VERTICAL)
	#self.sizer.Add(self.tbarSizer, 0, 
        #     wx.EXPAND|wx.ALIGN_CENTER|wx.BOTTOM, 10)
	self.sizer.Add(self.hSizer, 1, wx.EXPAND|wx.ALIGN_CENTER)

	return

    def __updateDetectorPage(self):
        """Update the detector page"""
        dPage = self.nBook.getPage_Detector()
        return

    def __loadProject(self):
        """Load any project data to initialize

        This should implemented and documented somewhere else,
        but for now, let's start it here.

        FILE FORMAT
        name:  experiment.cfg
        sections:
        [load]
        material-list = <filename>
        reader-list = <filename>
        [options] # options for this experiment
"""
        cfgFile = 'experiment.cfg'
        exp = wx.GetApp().ws
        #
        if os.path.exists(cfgFile):
            p = Parser()
            p.read(cfgFile)
            #
            #  Each section defines a material
            #
            sec = 'load'
            if p.has_section(sec):
                
                opt = 'material-list'
                try:
                    fname = p.get(sec, opt)
                    exp.loadMaterialList(fname)
                    print 'loaded materials list from "%s"\n' % fname
                except:
                    pass

                opt = 'reader-list'
                try:
                    fname = p.get(sec, opt)
                    exp.loadReaderList(fname)
                    print 'loaded readers list from "%s"\n' % fname
                except:
                    pass
                
                opt = 'detector'
                try:
                    fname = p.get(sec, opt)
                    exp.loadDetector(fname)
                    print 'loaded detector from "%s"\n' % fname
                except:
                    pass
                pass

            sec = 'options'
            if p.has_section(sec):
                opt = 'start-tab'
                try:
                    val = p.getint(sec, opt)
                    self.nBook.SetSelection(val)
                    print 'starting on tab number %d\n' % val
                except:
                    pass

            pass
        
        return
    #
    # ============================== API
    #
    #                     ========== *** Access Methods
    #
    def updateFromExp(self):
        """Update all subwindows"""
        self.nBook.updateFromExp()
        return
    #
    #                     ========== *** Event Callbacks
    #
    def OnPageChange(self, e):
        """Notebook page changed"""
        sel  = e.GetSelection()
        text = self.nBook.GetPageText(sel)
        #self.GetMenuBar().EnableTop(1, text == 'Reader')

        return
    #
    # ========== Detector Menu
    #
    def OnDetectorLoad(self, e):
        """Load detector"""
        app = wx.GetApp()
        exp = app.ws

        dlg = wx.FileDialog(self, 'Load Detector', 
                            style=wx.FD_OPEN | 
                                  wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            f = dlg.GetPath()
            try:
                exp.loadDetector(f)
            except:
                wx.MessageBox('failed to load file:  %s' % f)
                pass
            pass

        dlg.Destroy()

        self.updateFromExp()
        
        return

    def OnDetectorSave(self, e):
        """Save detector"""
        app = wx.GetApp()
        exp = app.ws

        dlg = wx.FileDialog(self, 'Save Detector', style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            f = dlg.GetPath()
            try:
                exp.saveDetector(f)
            except:
                wx.MessageBox('failed to save file:  %s' % f)
                pass
            pass

        dlg.Destroy()

        self.updateFromExp()
        return
    
    def OnCaking(self, e):
        """Raise the caking window"""
        app = wx.GetApp()
        exp = app.ws
        
        if exp.activeImage is None:
            wx.MessageBox('No Image is loaded')
            return

        dlg = cakingDialog(self, wx.NewId())
        dlg.ShowModal()

        app.getCanvas().update()
        
        return
    #
    # ========== Readers MENU
    #
    def OnReadersEdit(self, e):
        """Edit Reader list"""
        exp = wx.GetApp().ws

        dlg = ListEditDlg(self, wx.NewId(), exp.savedReaders)
        dlg.ShowModal()
        dlg.Destroy()

        self.updateFromExp()
        
        return

    def OnReadersSave(self, e):
        """Edit Reader list"""
        app = wx.GetApp()
        exp = app.ws

        dlg = wx.FileDialog(self, 'Save Readers', style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            f = dlg.GetPath()
            try:
                exp.saveReaderList(f)
            except:
                wx.MessageBox('failed to save file:  %s' % f)
                pass
            pass

        
        dlg.Destroy()

        self.updateFromExp()
        
        return

    def OnReadersLoad(self, e):
        """Edit Reader list"""
        app = wx.GetApp()
        exp = app.ws

        dlg = wx.FileDialog(self, 'Load Readers', 
                            style=wx.FD_OPEN | 
                                  wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            f = dlg.GetPath()
            try:
                exp.loadReaderList(f)
            except:
                wx.MessageBox('failed to load file:  %s' % f)
                pass
            pass

        dlg.Destroy()

        self.updateFromExp()
        
        return

    def OnHydra(self, e):
        """Raise hydra interface"""
        h = HydraControlFrame(self, wx.NewId())
        return
    #
    # ========== FILE MENU
    #
    def OnQuit(self, e):
        """Clean up and exit"""
        #
        #  Remember to check for any unsaved things.
        #
        #  check! print "callback from XRD main frame"
        self.Close(True)  

        return

    def OnFileNew(self, e):
        """Create a new experiment"""
        app = wx.GetApp()
        app.ws = loadExp('')
        #  NOW:  need to update workspace
        self.updateFromExp()

        return

    def OnFileLoad(self, e):
        """Load workspace"""
        #
        #  Get access to main app
        #
        app = wx.GetApp()

        dlg = wx.FileDialog(self, 'Load Experiment', 
                            style=wx.FD_OPEN | 
                                  wx.FD_FILE_MUST_EXIST |
                                  wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            f = dlg.GetPath()
            pass
        dlg.Destroy()

        try:
            app.ws = loadExp(f)
        except:
            wx.MessageBox('failed to load file')
            pass
        
        self.updateFromExp()

        return

    def OnFileSave(self, e):
        """Save workspace"""
        app = wx.GetApp()
        exp = app.ws
        dlg = wx.FileDialog(self, 'Save Experiment', style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            f = dlg.GetPath()
            pass
        dlg.Destroy()

        try:
            saveExp(exp, f)
        except:
            wx.MessageBox('failed to save file')
            pass

        return

    #
    # ========== MATERIALS MENU
    #
    def OnMaterialsSave(self, e):
        """Save the materials list to a file"""
        dlg = wx.FileDialog(self, 'Materials File', style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            exp = wx.GetApp().ws

            dir = dlg.GetDirectory()
            fil = dlg.GetFilename()
            if (fil):
                matFile = os.path.join(dir,fil)
                pass

            try:
                f = file(matFile, 'w')
                cPickle.dump(exp.matList, f)
                f.close()
            except Exception, exc:
                msg = 'Failed to save materials file: %s\n' % matFile
                msg += str(exc)
                wx.MessageBox(msg)
                pass

            pass

        dlg.Destroy()


        return

    def OnMaterialsLoad(self, e):
        """Load the materials list from a file"""
        dlg = wx.FileDialog(self, 'Load Materials File', style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            exp = wx.GetApp().ws

            dir = dlg.GetDirectory()
            fil = dlg.GetFilename()
            if (fil):
                matFile = os.path.join(dir,fil)
                pass

            try:
                f = file(matFile, 'r')
                matList = cPickle.load(f)
                f.close()
                exp.matList = matList
            except Exception, exc:
                msg = 'Failed to load materials file: %s\n' % matFile
                msg += str(exc)
                wx.MessageBox(msg)
                pass

            pass
        dlg.Destroy()

        self.updateFromExp()

        return

    def OnMaterialsEdit(self, e):
        """Edit the materials list"""
        exp = wx.GetApp().ws

        dlg = ListEditDlg(self, wx.NewId(), exp.matList)
        dlg.ShowModal()
        dlg.Destroy()

        self.updateFromExp()

        return

    def OnAbout(self, e):
        """About menu item"""

        aboutMsg = r"""heXRD Package for x-ray

========================================
%s
========================================
%s

"""
        ref_sglite = r"""sglite provided by Ralf W. Grosse-Kunstleve
(copyright included in source)        
"""
        aboutMsg = aboutMsg % (mdef.__doc__, ref_sglite)

        wx.MessageBox(aboutMsg)
        
        return

    pass # end class
#
# -----------------------------------------------END CLASS:  xrdMainFrame
#
