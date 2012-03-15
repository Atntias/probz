# First thing, we need to make sure that we are importing a
# recent-enough version of wx
import wxversion
wxversion.ensureMinimal('2.8')

from numpy import ogrid, sin

from traits.api import HasTraits, Instance
from traitsui.api import View, Item

from mayavi.sources.api import ArraySource
from mayavi.modules.api import IsoSurface

from mayavi.core.ui.api import MlabSceneModel, SceneEditor

#-------------------------------------------------------------------------------
class MayaviView(HasTraits):

    scene = Instance(MlabSceneModel, ())

    # The layout of the panel created by traits.
    view = View(Item('scene', editor=SceneEditor(),
                    resizable=True,
                    show_label=False),
                resizable=True)

    def __init__(self):
        HasTraits.__init__(self)
        x, y, z = ogrid[-10:10:100j, -10:10:100j, -10:10:100j]
        scalars = sin(x*y*z)/(x*y*z)
        src = ArraySource(scalar_data=scalars)
        self.scene.mayavi_scene.add_child(src)
        src.add_module(IsoSurface())


#-------------------------------------------------------------------------------
# Wx Code
import wx

class MainWindow(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Mayavi in a Wx notebook')
        self.notebook = wx.aui.AuiNotebook(self, id=-1, style=wx.aui.AUI_NB_TAB_SPLIT | wx.aui.AUI_NB_CLOSE_ON_ALL_TABS | wx.aui.AUI_NB_LEFT)
        self.mayavi_view = MayaviView()
        self.panel  = wx.Panel(self, -1, size=(170, 500), pos=(0, 0))
        # The edit_traits method opens a first view of our 'MayaviView'
        self.control = self.mayavi_view.edit_traits(parent=self,kind='subpanel').control
        self.notebook.AddPage(page=self.control, caption='Display 1')

        sizer = wx.BoxSizer()
        sizer.Add(self.notebook,3, wx.EXPAND)
        sizer.Add(self.panel,1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Show(True)

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MainWindow(None, wx.ID_ANY)
    app.MainLoop()