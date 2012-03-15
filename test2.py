import numpy 
from traits.api import HasTraits, Instance
from traitsui.api import View, Item
from mayavi.core.ui.api import SceneEditor, MlabSceneModel
from tvtk.pyface.api import Scene


class MayaviView(HasTraits):

    scene = Instance(MlabSceneModel, ())
    # The layout of the panel created by Traits
    view = View(Item('scene', editor=SceneEditor(scene_class=Scene), resizable=True,show_label=False),resizable=True)

    def __init__(self):
        HasTraits.__init__(self)
        # Create some data, and plot it using the embedded scene's engine
        OffsetData = numpy.load('{}.npz'.format('offset'))
        self.scene.mlab.surf(OffsetData['OffsetData'], warp_scale='auto')        


#-----------------------------------------------------------------------------
# Wx Code
import wx

class MainWindow(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Mayavi in Wx')
        self.notebook = wx.aui.AuiNotebook(self, id=-1, style=wx.aui.AUI_NB_TAB_SPLIT | wx.aui.AUI_NB_CLOSE_ON_ALL_TABS | wx.aui.AUI_NB_LEFT)
        self.panel  = wx.Panel(self, -1, size=(800, 800), pos=(0, 0))
        self.mayavi_view = MayaviView()
        # Use traits to create a panel, and use it as the content of this
        # wx frame.
        self.control = self.mayavi_view.edit_traits(parent=self,kind='subpanel').control
        self.panel.add
        self.Show(True)

app = wx.PySimpleApp()
frame = MainWindow(None, wx.ID_ANY)
app.MainLoop()