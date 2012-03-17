import os, gettext, Queue, re
if os.path.exists('/usr/share/pronterface/locale'):
    gettext.install('probez', '/usr/share/pronterface/locale', unicode=1)
else: 
    gettext.install('probez', './locale', unicode=1)
from numpy import *
import wx, pronsole, time
import wx.aui
## known bug - after closing the probze gui and reopening the mayavi thing dont work
'''
from traits.api import HasTraits, Instance
from traitsui.api import View, Item
from mayavi.core.ui.api import SceneEditor, MlabSceneModel
from tvtk.pyface.api import Scene

class MayaviView(HasTraits): #class for mayavi view
    scene = Instance(MlabSceneModel, ())
    # The layout of the panel created by Traits
    view = View(Item('scene', editor=SceneEditor(scene_class=Scene), resizable=True,show_label=False),resizable=True)

    def __init__(self):
        HasTraits.__init__(self)
        # Create some data, and plot it using the embedded scene's engine
        OffsetData = load('{}.npz'.format('offset'))
        self.scene.mlab.surf(OffsetData['OffsetData'], warp_scale='auto')
'''        
class guiwin(wx.Frame): #class for gui + probing functions
    def __init__(self, size=(1000, 500), parent=None):
        self.parent = parent
        self.O3D = Offset3D()           
        wx.Frame.__init__(self, parent, title=_("Probe Z"), size=size)
        self.notebook = wx.aui.AuiNotebook(self, id=-1, style=wx.aui.AUI_NB_TAB_SPLIT | wx.aui.AUI_NB_CLOSE_ON_ALL_TABS | wx.aui.AUI_NB_LEFT)
        self.SetIcon(wx.Icon("P-face.ico", wx.BITMAP_TYPE_ICO))
        self.panel  = wx.Panel(self, -1, size=(170, 500), pos=(0, 0))
        self.step   = wx.TextCtrl(self.panel, size=(50, 21), value="10", pos=(100, 10))
        self.xstart = wx.TextCtrl(self.panel, size=(50, 21), value="30", pos=(100, 35))
        self.ystart = wx.TextCtrl(self.panel, size=(50, 21), value="30", pos=(100, 60))
        self.xend   = wx.TextCtrl(self.panel, size=(50, 21), value="190", pos=(100, 85))
        self.yend   = wx.TextCtrl(self.panel, size=(50, 21), value="190", pos=(100, 110))
        self.lstep   = wx.StaticText(self.panel,label="Step: ", pos=(10, 13))
        self.lxstart = wx.StaticText(self.panel,label="X Start: ", pos=(10, 38))
        self.lystart = wx.StaticText(self.panel,label="Y Start: ", pos=(10, 63))
        self.lxend   = wx.StaticText(self.panel,label="X End: ", pos=(10, 88))
        self.lyend   = wx.StaticText(self.panel,label="Y End: ", pos=(10, 113))
        self.cl = wx.Button(self.panel, label=_("Probe Z!"), pos=(5, 150))
        self.ld = wx.Button(self.panel, label=_("Load File"), pos=(5, 200))
        self.sv = wx.Button(self.panel, label=_("Offset Gcode"), pos=(90, 200))
        self.eb = wx.Button(self.panel, label=_("Cancel"), pos=(90, 150))
        self.eb.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
        self.cl.Bind(wx.EVT_BUTTON, self.ProbeZ)
        self.ld.Bind(wx.EVT_BUTTON, self.Load)
        self.sv.Bind(wx.EVT_BUTTON, self.OffsetG)
        self.basedir = "."
        #self.mainsizer.AddSpacer(10)
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainsizer.Add(self.panel,9, wx.EXPAND)
        self.mainsizer.Add(self.notebook,32, wx.EXPAND)
        self.SetSizer(self.mainsizer)
        #self.mainsizer.Fit(self)
        self.Layout()
    
    def SamplePoint(self): #this function will execute a sapmle
        _LastLine,_CurrentLastLine,_TimeOutCounter,_DeltaFloat
        _LastLine = self.parent.p.log[-1]
        self.parent.p.send_now("G92 Z5")
        self.parent.p.send_now("G1 Z0 F800")
        self.parent.p.clear = True
        while(True):
            _CurrentLastLine = self.parent.p.log[-1]
            if(_CurrentLastLine is not _LastLine and not _CurrentLastLine.startswith('ok')):
                break
        _CurrentLastLine = _CurrentLastLine.replace("echo:endstops","").replace("hit:","").replace("Z:","").replace(" ","").replace("\n","")
        _DeltaFloat = 5-float(_CurrentLastLine)
        self.parent.p.send_now('G1 Z' + str(_DeltaFloat))
        return _CurrentLastLine
    
    def ProbeZ(self, event):
        result = wx.MessageBox(_('Are you sure you want to probe the grid? this may take a while'), _('Probe the grid?'),
            wx.YES_NO | wx.ICON_QUESTION)
        if (result == 2):
            _firstSample,file_out,Step,X_Start,Y_Start,X_End,Y_End,Step,LoopCountX,LoopCountY,_LastLine,_CurrentLastLine,_DeltaFloat,_DeltaStr,_TimeOutCounter,_ProbYPos,_ProbXPos,_InvertDirS,_InvertDirE,_3D_out_String
            X_Start     = int(self.xstart.GetValue())
            Y_Start     = int(self.ystart.GetValue())
            X_End       = int(self.xend.GetValue())
            Y_End       = int(self.yend.GetValue())
            Step        = int(self.step.GetValue())
            file_out    = 'offset'
            LoopCountX  = int(round((X_End - X_Start) / Step, 0))
            LoopCountY  = int(round((Y_End - Y_Start) / Step, 0))
            _OffsetData = zeros( ((X_End-X_Start)/Step,(Y_End-Y_Start)/Step), dtype=float )
            _ProbData   = ([X_Start,Y_Start,X_End,Y_End,Step])
            _3D_out_String = "ListPlot3D[{" 
            if self.parent.p.online:            
                print Step
                print LoopCountY
                self.parent.p.send_now('G92 Z0')
                self.parent.p.send_now('G1 Z1')
                self.parent.p.send_now('G28 X0 Y0')
                self.parent.p.send_now('G28 Z0')
                self.parent.p.send_now('G1 Z1')
                self.parent.p.send_now('G1 X{0} Y{1}'.format(X_Start, Y_Start))
                self.parent.p.send_now('G92 X0 Y0')
                _firstSample = self.SamplePoint()
                for _ProbYPos in range(0, LoopCountY):
                    self.parent.p.send_now('G1 Y' + str(_ProbYPos*Step) + ' F10000')
                    if _ProbYPos%2==0:
                      _InvertDirS = 0
                      _InvertDirE = LoopCountX
                      LoopStep = 1
                    else:
                      _InvertDirS = LoopCountX-1
                      _InvertDirE = -1
                      LoopStep = -1
                    for _ProbXPos in range(_InvertDirS, _InvertDirE, LoopStep):
                      self.parent.p.send_now('G1 X' + str(_ProbXPos*Step) + ' F10000')
                      _CurrentLastLine = self.SamplePoint()
                      _OffsetData[_ProbXPos,_ProbYPos] = float(_CurrentLastLine)-float(_firstSample)
                      _3D_out_String += '{' + str(_ProbXPos) + "," + str(_ProbYPos) + "," + str(_CurrentLastLine) + "}" + ","
                savez(file_out, OffsetData=_OffsetData, ProbData=_ProbData)
            else:
                print _("Printer is not online.")
            self.Refresh()
            
    def Load(self, event):
        OffsetData = load('{}.npz'.format('offset'))
        #print OffsetData
        '''self.mayavi_view = MayaviView()
        self.control = self.mayavi_view.edit_traits(parent=self,kind='subpanel').control
        self.notebook.AddPage(page=self.control, caption='3D Display')
        set_printoptions(threshold='nan')           
        print OffsetData['OffsetData']
        print OffsetData['OffsetData'].min()
        print OffsetData['OffsetData'].max()'''
          
    def OffsetG(self, event):
        first_layer_Gcode = self.O3D.GetLayer('1.gcode', 1)
        for line in first_layer_Gcode:
            print line,
        '''OffsetData = load('{}.npz'.format('offset'))
        for line in first_layer_Gcode:
            if (line.find('G1 X') is not -1):
                left, delimiter, right = line.partition(' X')
                X, delimiter2, Yt = right.partition(' Y')
                Y, delimiter2, junk = Yt.partition(' ')
                Z = self.GetZforXY(float(X),float(Y),OffsetData)              
                line = line.replace('\n',' Z{}\n'.format(Z))
                print line,
        '''
    #    if Dis1 = float(sqwrt(power(X-XcloseRatio,2) + power(Y-YcloseRatio,2)))          
class Offset3D(object): #class for 3d printing offset calculations
    def DisCalc(self, X1, Y1, X2, Y2):
        return float(sqrt(power(X1-X2,2) + power(Y1-Y2,2)))
    
    def GetZforXY(self, X, Y, OffsetData):  #this function makes a simple linar interploation to retrive Z hight for a given X&Y
        # x - the x axis of the point
        # y - the y axis of the point
        # x0 - the x axis of the first point
        # y0 - the y axis of the first point
        # R - the Resioltion of the test
        # Nx - the number of test in the x axis
        # Ny - the number of test in the y axis
        # Rconst = sqrt(R*R/2)
        Xclose,Yclose,XcloseRatio,YcloseRatio,Dis1,Dis2,Dis3,Dis4,total,mag1,mag2,mag2,mag4,result
        x0    = OffsetData['ProbData'][0]
        y0    = OffsetData['ProbData'][1]
        X_End = OffsetData['ProbData'][2]
        Y_End = OffsetData['ProbData'][3]
        R     = OffsetData['ProbData'][4]
        Nx    = int(round((X_End - x0) / R, 0))
        Ny    = int(round((Y_End - y0) / R, 0))
        Rconst = sqrt(R*R*2)
        
        if( X >= x0 and Y >= y0 and X<x0 + R*(Nx-1) and Y< y0 + R*(Ny-1) ):
            Xclose = int(round((X-x0)/R, 0))
            Yclose = int(round((Y-y0)/R, 0))      
            XcloseRatio = float(x0 + R*Xclose)      
            YcloseRatio = float(y0 + R*Yclose)
            Dis1 = self.DisCalc(X,Y,XcloseRatio,YcloseRatio)
            Dis2 = self.DisCalc(X,Y,XcloseRatio+R,YcloseRatio)
            Dis3 = self.DisCalc(X,Y,XcloseRatio+R,YcloseRatio+R)
            Dis4 = self.DisCalc(X,Y,XcloseRatio,YcloseRatio+R)
            total = float(4 * Rconst - (Dis1 + Dis2 + Dis3 + Dis4))
            mag1 = float(Rconst-Dis1)
            mag2 = float(Rconst-Dis2)
            mag3 = float(Rconst-Dis3)
            mag4 = float(Rconst-Dis4)
            result = ( (OffsetData['OffsetData'][Xclose][Yclose]*mag1) + (OffsetData['OffsetData'][Xclose+1][Yclose]*mag2) + (OffsetData['OffsetData'][Xclose+1][Yclose+1]*mag3) + (OffsetData['OffsetData'][Xclose][Yclose+1]*mag4) )
            return result / total

    def GetLayer(self, Filename, LayerNumber): #this function return a single layer of gcode as a list of lines
        _layerGcode = []
        _TemplayerGcode = []
        counter = 0
        clear = 0
        currentLayer = 0
        findme = 'str'
        _layer_height = 0
        _firstLayer_height = 0
        fg = open(Filename, 'r') #open the gcode file
        for line in fg:
            counter += 1
            _TemplayerGcode.append(line)
            if (counter == 20 and clear == 0): #in case not found in first 20 lines
                break
            elif (line.find('; layer_height = ') is not -1 and clear == 0): #look for the layer hight Slic3r format only
                _layer_height = float(line.replace("; layer_height = ","").replace("\n",""))
                clear = 1
            if (line.find('G1 Z') is not -1 and clear is not 2 and clear is not 3):  #look for the the *first layer hight* might be diffrent from others
                left, delimiter, right = line.partition(' F')
                _firstLayer_height = float(left.replace("G1 Z",""))
                del _TemplayerGcode[:] #clear saved and continue
                _TemplayerGcode.append(line)
                findme = 'G1 Z' + str(_firstLayer_height+_layer_height) # calc the next layer hight
                clear = 2
            if (line.find(findme) is not -1): #find the next layer
                _layerGcode = _TemplayerGcode #save it, might be the result
                clear = 3
                continue
            if (clear == 3):
                if (line.find('G92 E0') is not -1):    
                    clear = 2
                else:
                    currentLayer += 1
                    if (currentLayer == LayerNumber):
                        fg.close()
                        _layerGcode.pop()
                        _layerGcode.pop()
                        return _layerGcode #stop and return the gcode
                    else:
                        del _TemplayerGcode[:] #clear saved and continue
                        _TemplayerGcode.append(line)
                        findme = 'G1 Z' + str(_firstLayer_height+_layer_height+(_layer_height*currentLayer))
                        clear = 2 

    def ReplaceLayer(self, Filename, LayerNumber, TargetLayer):
        pass
    def SplitLongs(self, Layer):
        pass
    def MarkTargets(self, Layer):
        pass
    
class OffsetPCBGOCDE(object): #class for pcb gcode offset calculations
    pass

class PreformenceTest(object): #class for testing gcode preformence
    pass    