import os, gettext, Queue, re
if os.path.exists('/usr/share/pronterface/locale'):
    gettext.install('probez', '/usr/share/pronterface/locale', unicode=1)
else: 
    gettext.install('probez', './locale', unicode=1)
from numpy import *
import wx, pronsole, time
import wx.aui
import sys
import fileinput
import threading      

set_printoptions(linewidth=80)

## known bug - after closing the probze gui and reopening the mayavi thing dont work seems to be related to how the gui is killed but couldnt figure it out.

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
 
class GuiWin(wx.Frame): #class for gui + general functions
    def __init__(self, size=(0, 0), parent=None):
        self.parent = parent
        self.O3D = Offset3D() 
        self.OPCG = OffsetPCBGOCDE(parent=self)
        self.PROBZ = ProbeZ(parent=self)         
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
        self.pz = wx.Button(self.panel, label=_("Probe Z!"), pos=(5, 150))
        self.lf = wx.Button(self.panel, label=_("Load File"), pos=(5, 200))
        self.of = wx.Button(self.panel, label=_("Offset!"), pos=(90, 200))
        self.ca = wx.Button(self.panel, label=_("Cancel"), pos=(90, 150))
        self.td = wx.Button(self.panel, label=_("Test Data"), pos=(5, 250))
        self.pd = wx.Button(self.panel, label=_("Show Data"), pos=(90, 250))
        self.gauge = wx.Gauge(self.panel, range=100000, pos=(5, 300), size=(160, 15))
        self.ca.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
        self.pz.Bind(wx.EVT_BUTTON, self.ProbeZ)
        self.lf.Bind(wx.EVT_BUTTON, self.Load)
        self.td.Bind(wx.EVT_BUTTON, self.TestData)
        self.pd.Bind(wx.EVT_BUTTON, self.PrintData)
        self.of.Bind(wx.EVT_BUTTON, self.OffsetG)
        self.basedir = "."
        self.filename = ""        
        self.of.Disable()
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainsizer.Add(self.panel,9, wx.EXPAND)
        self.mainsizer.Add(self.notebook,32, wx.EXPAND)
        self.SetSizer(self.mainsizer)
        #self.mainsizer.Fit(self)
        self.Layout()
    
    def ProbeZ(self, event): #this function is the probing rutine
        child = threading.Thread(target=self.PROBZ.ProbeZ)
        child.setDaemon(True)
        child.start()
                
    def TestData(self, event): #this function will go 0.2mm over each 4 of the end points of data and see there is no endstop hit then go down by 0.1 and get an enstop hit.        
        child = threading.Thread(target=self.PROBZ.TestData)
        child.setDaemon(True)
        child.start()
                 
    def PrintData(self, event): #this function will simply print the data
        OffsetData = load('{}.npz'.format('offset'))
        print OffsetData['OffsetData']
        print 'Min Z = {}'.format(OffsetData['OffsetData'].min())
        print 'Max Z = {}'.format(OffsetData['OffsetData'].max())
        print 'Start X = {}'.format(OffsetData['ProbData'][0])
        print 'Start Y = {}'.format(OffsetData['ProbData'][1])
        print 'End X = {}'.format(OffsetData['ProbData'][2])
        print 'End Y = {}'.format(OffsetData['ProbData'][3])
        print 'Step = {}'.format(OffsetData['ProbData'][4])        

        self.xstart.SetValue(str(OffsetData['ProbData'][0]))
        self.ystart.SetValue(str(OffsetData['ProbData'][1]))
        self.xend.SetValue(str(OffsetData['ProbData'][2]))
        self.yend.SetValue(str(OffsetData['ProbData'][3]))
        self.step.SetValue(str(OffsetData['ProbData'][4]))
        
        #self.OPCG.TestFunction()
                 
        OffsetData = load('{}.npz'.format('offset'))        
        self.mayavi_view = MayaviView()
        self.control = self.mayavi_view.edit_traits(parent=self,kind='subpanel').control
        self.notebook.AddPage(page=self.control, caption='3D Display')
        set_printoptions(threshold='nan')
        
    def Load(self,  event, filename=None):
        basedir=self.parent.settings.last_file_path
        if not os.path.exists(basedir):
            basedir = "."
            try:
                basedir=os.path.split(self.filename)[0]
            except:
                pass
        dlg=wx.FileDialog(self,_("Open file to offset"),basedir,style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        dlg.SetWildcard(_("Tap, NC, and GCODE files (;*.gcode;*.gco;*.g;*.nc;*.tap;)"))
        if(filename is not None or dlg.ShowModal() == wx.ID_OK):
            if filename is not None:
                name=filename
            else:
                name=dlg.GetPath()
            if not(os.path.exists(name)):
                self.parent.status.SetStatusText(_("File not found!"))
                return
            path = os.path.split(name)[0]
            if path != self.parent.settings.last_file_path:
                self.parent.set("last_file_path",path)
            else:
                self.filename=name
                self.of.Enable()
                try: 
                    _Changed = self.OPCG.PrepareGcode(self.filename)
                    if (_Changed > 0): print 'File Offseted Into The Probed Area!'
                    print 'File Loaded Correctly!'
                except: 
                    print 'Insufficent Probing Data, Probe larger or Load Smaller Gcode'
                    return
      
    def OffsetG(self, event):
        child = threading.Thread(target=self.OPCG.PcbOffset, args=[self.filename])
        child.setDaemon(True)
        child.start()
        #self.OPCG.PcbOffset(self.filename)

class ProbeZ(object):
    def __init__(self, parent=None):        
        self.parent = parent
        self.OC = OffsetCalc()    
        self.OffsetData = load('{}.npz'.format('offset')) # load the Offset data and initailze it 
        self.X_Start    = self.OffsetData['ProbData'][0]
        self.Y_Start    = self.OffsetData['ProbData'][1] 
        self.X_End      = self.OffsetData['ProbData'][2]
        self.Y_End      = self.OffsetData['ProbData'][3]
        try:
            self.z_max = self.OffsetData['OffsetData'].max()
        except:
            self.z_max = 6
        
    def SamplePoint(self): #this function will execute a single prob, TODO : make elevation reletive to last point not, absulute.
        _LastLine = _CurrentLastLine = _TimeOutCounter = _DeltaFloat = 0
        _LastLine = self.parent.parent.p.log[-1]
        #self.parent.parent.p.send_now("G92 Z4")
        self.parent.parent.p.send_now("G1 Z-8 F60")
        self.parent.parent.p.clear = True
        while(True):
            _CurrentLastLine = self.parent.parent.p.log[-1]
            if(_CurrentLastLine is not _LastLine and not _CurrentLastLine.startswith('ok')):
                break
        _CurrentLastLine = _CurrentLastLine.replace("echo:endstops","").replace("hit:","").replace("Z:","").replace(" ","").replace("\n","")
        self.parent.parent.p.send_now('G92 Z{}'.format(float(_CurrentLastLine)))
        self.parent.parent.p.send_now('G1 Z{} F200'.format(1+float(_CurrentLastLine)))
        return _CurrentLastLine
    
    def TestData(self): #this function will go 0.2mm over each 4 of the end points of data and see there is no endstop hit then go down by 0.1 and get an enstop hit.        
        _A = _B = _Index = _Good_Flag = _Z = 0
        _LastLine = ''

        result = wx.MessageBox(_('Start? This Will Home First, Make Sure The Prob Is Connected'), _('Testing Data'),
            wx.YES_NO | wx.ICON_QUESTION)
        if (result == 2):
            if self.parent.parent.p.online:                 
                self.SafeHome(0)
                self.parent.parent.p.send_now('G1 Z{}'.format(self.z_max+2)) #go up 1mm above z max so we dont run into the plate
                _A , _B = self.TestPoint(self.X_Start, self.Y_Start)
                if (_A == -1):print 'Point 1 Too low ' 
                elif (_A == 1): print 'Point 1 Too high'
                else: print 'Point 1 (Z={0} Hit = {1}) is Good'.format(_A, _B)
                
                self.parent.parent.p.send_now('G1 Z{}'.format(self.z_max+2))                
                
                _A , _B = self.TestPoint(self.X_Start, self.Y_End-1)
                if (_A == -1):print 'Point 2 Too low ' 
                elif (_A == 1): print 'Point 2 Too high'
                else: print 'Point 2 (Z={0} Hit = {1}) is Good'.format(_A, _B)
                
                self.parent.parent.p.send_now('G1 Z{}'.format(self.z_max+2))                
                
                _A , _B = self.TestPoint(self.X_End-1, self.Y_End-1)
                if (_A == -1):print 'Point 3 Too low ' 
                elif (_A == 1): print 'Point 3 Too high'
                else: print 'Point 3 (Z={0} Hit = {1}) is Good'.format(_A, _B)
                
                self.parent.parent.p.send_now('G1 Z{}'.format(self.z_max+2))                
                
                _A , _B = self.TestPoint(self.X_End-1, self.Y_Start)
                if (_A == -1):print 'Point 4 Too low ' 
                elif (_A == 1): print 'Point 4 Too high'
                else: print 'Point 4 (Z={0} Hit = {1}) is Good'.format(_A, _B)
                                      
            else:print _("Printer is not online.") 
            
    def TestPoint(self, X, Y): # If using this USE SAFE HOME FIRST!!
        _tX = _tY = _Index = _Good_Flag = 0
        _LastLine = ''
             
        if (self.X_Start <= X <= self.X_End and self.Y_Start <= Y <= self.Y_End):  
                self.parent.parent.p.send_now('G1 X{0} Y{1}'.format(X, Y)) #go to z 0.1 @ Xstart Ystart
                _Z = self.OC.GetZforXY(X, Y)
                self.parent.parent.p.send_now('G1 Z{}'.format(_Z+0.2))
                _LastLine = self.parent.parent.p.log[-1]
                while(True):
                    _Index += 1
                    if(_Index > 2000):
                        print 'TimedOut!'
                        break
                    self.parent.parent.p.send_now('M114')
                    _CurrentLastLine = self.parent.parent.p.log[-1]
                    time.sleep(0.01)
                    if(_CurrentLastLine.startswith('ok')):
                        _CurrentLastLine = self.parent.parent.p.log[-2]
                    if(_CurrentLastLine.startswith('X:') is True):
                        left, delimiter, right = _CurrentLastLine.partition('Count ')
                        left, delimiter, right = right.partition('Y:')
                        _tX = floor(float(left.replace("X:","")))
                        left, delimiter, right = right.partition('Z:')
                        _tY = floor(float(left.replace("Y:","")))                   
                        if(_tX == X and _tY == Y and float(right) == (_Z+0.2)):
                            _Good_Flag = 1                            
                            break                                           
                if (_Good_Flag is 1):                     
                    for i in range(1, 10):
                        _LastLine = self.parent.parent.p.log[i*-1]   
                        if(_LastLine.startswith('echo:endstops') is False):                                                                                                 
                            self.parent.parent.p.send_now('G1 Z{}'.format(_Z+0.1))
                            time.sleep(0.1)
                            _Good_Flag = 0
                            break
                    if(_Good_Flag is 1):
                        return (-1,-1) #Point Too low 
                    else:
                        for i in range(1, 10):
                            _LastLine = self.parent.parent.p.log[i*-1]
                            if(_LastLine.startswith('echo:endstops') is True):
                                _LastLine = _LastLine.replace("echo:endstops","").replace("hit:","").replace("Z:","").replace(" ","").replace("\n","")
                                return (_Z, _LastLine)#Point is Good 
                                _Good_Flag = 1
                                break
                        if(_Good_Flag is 0):
                            return (1,1) #Point Too high
        else:
            raise NameError('X or Y out of range')
       
    def SafeHome(self, endUp): #end up or down = 1 finsihes the move without homeing the z
        self.parent.parent.p.send_now('G92 Z0')
        self.parent.parent.p.send_now('G1 Z{}'.format(self.z_max+2)) #go up 1mm above z max so we dont run into the plate    
        self.parent.parent.p.send_now('G28 X0 Y0')
        if(endUp != 1):self.parent.parent.p.send_now('G28 Z0') #home z
 
    def ProbeZ(self): #this function is the probing rutine
        _firstSample = file_out = Step = X_Start = Y_Start = X_End = Y_End = Step = LoopCountX = LoopCountY = _LastLine = _CurrentLastLine = _DeltaFloat = _DeltaStr = _TimeOutCounter = _ProbYPos = _ProbXPos = _InvertDirS = _InvertDirE = _3D_out_String = 0
        result = wx.MessageBox(_('Are you sure you want to probe the grid? this may take a while'), _('Probe the grid?'),
            wx.YES_NO | wx.ICON_QUESTION)
        if (result == 2):
            X_Start     = int(self.parent.xstart.GetValue())
            Y_Start     = int(self.parent.ystart.GetValue())
            X_End       = int(self.parent.xend.GetValue())
            Y_End       = int(self.parent.yend.GetValue())
            Step        = int(self.parent.step.GetValue())
            file_out    = 'offset'
            LoopCountX  = int(floor((X_End - X_Start) / Step))
            LoopCountY  = int(floor((Y_End - Y_Start) / Step))
            _OffsetData = zeros( (LoopCountX+1,LoopCountY+1), dtype=float )
            _ProbData   = ([X_Start,Y_Start,X_End,Y_End,Step])
            z_max = 1                  
            if self.parent.parent.p.online:            
                self.SafeHome(0)
                self.parent.parent.p.send_now('G1 Z{}'.format(z_max)) #go up 1mm above z max so we dont run into the plate    
                self.parent.parent.p.send_now('G1 X{0} Y{1}'.format(X_Start, Y_Start))
                self.parent.parent.p.send_now('G92 X0 Y0')
                _firstSample = self.SamplePoint()
                for _ProbYPos in range(0, LoopCountY+1):
                    self.parent.parent.p.send_now('G1 Y' + str(_ProbYPos*Step) + ' F10000')
                    if _ProbYPos%2==0:
                      _InvertDirS = 0
                      _InvertDirE = LoopCountX + 1
                      LoopStep = 1
                    else:
                      _InvertDirS = LoopCountX
                      _InvertDirE = -1
                      LoopStep = -1
                    for _ProbXPos in range(_InvertDirS, _InvertDirE, LoopStep):
                      self.parent.parent.p.send_now('G1 X' + str(_ProbXPos*Step) + ' F10000')
                      _CurrentLastLine = self.SamplePoint()
                      _OffsetData[_ProbXPos,_ProbYPos] = float(_CurrentLastLine)-float(_firstSample)                    
                savez(file_out, OffsetData=_OffsetData, ProbData=_ProbData)
            else:
                print _("Printer is not online.")
            self.parent.Refresh()
                    
class OffsetCalc(object):
    def __init__(self, parent=None):        
        self.ReloadData()
        
    def ReloadData(self):
        self.OffsetData = load('{}.npz'.format('offset')) # load the Offset data and initailze it 
        self.X_Start    = self.OffsetData['ProbData'][0]
        self.Y_Start    = self.OffsetData['ProbData'][1] 
        self.X_End      = self.OffsetData['ProbData'][2]
        self.Y_End      = self.OffsetData['ProbData'][3]
        self.R          = self.OffsetData['ProbData'][4] # R - the Resolution of the test
        self.Nx    = int(floor((self.X_End - self.X_Start) / self.R))
        self.Ny    = int(floor((self.Y_End - self.Y_Start) / self.R))
        self.MyOffsetData = self.OffsetData['OffsetData']        
        self.Zmax = self.OffsetData['OffsetData'].max()
         
    def DisCalc(self, X1, Y1, X2, Y2):
        result = float(sqrt(power(X1-X2,2) + power(Y1-Y2,2)))
        result = format(result, ".4f")
        return float(result)

    def GetZforXY(self, X, Y):  #this function makes a simple bilinar interploation to retrive Z hight for a given X&Y            
        Xclose = Yclose = XcloseRatio = YcloseRatio = r1 = r2 = result = 0
  
        if( X >= self.X_Start and Y >= self.Y_Start and X<self.X_Start + self.R*(self.Nx) and Y< self.Y_Start + self.R*(self.Ny) ):
            Xclose = int(floor((X-self.X_Start)/self.R))
            Yclose = int(floor((Y-self.Y_Start)/self.R))    
            XcloseRatio = float(self.X_Start + self.R*Xclose)      
            YcloseRatio = float(self.Y_Start + self.R*Yclose)
            r1 = (XcloseRatio+self.R-X)*self.MyOffsetData[Xclose][Yclose]/self.R + (X-XcloseRatio)*self.MyOffsetData[Xclose+1][Yclose]/self.R
            r2 = (XcloseRatio+self.R-X)*self.MyOffsetData[Xclose][Yclose+1]/self.R + (X-XcloseRatio)*self.MyOffsetData[Xclose+1][Yclose+1]/self.R
            result = (YcloseRatio+self.R-Y)*r1/self.R + (Y-YcloseRatio)*r2/self.R 
            result = format(result, ".4f")
            return float(result)
        else:
            print X, self.X_Start, Y, self.Y_Start, (self.X_Start + self.R*(self.Nx-1)), (self.Y_Start + self.R*(self.Ny-1))
            print 'Data Out Of Range' 
    
class OffsetPCBGOCDE(object): #class for pcb gcode offset calculations
    
    def __init__(self, parent=None):        
        self.parent = parent        
        self.OC = OffsetCalc()
    
    def PrepareGcode(self, filename): #this function offsets the x axis to be in the positive side, and validates that all x and y locations have probing data.
        _MaxX = _MaxY =  _MinX = _MinY = _Y  = _X = _OffsetX = _OffsetY = _Changed = first_time = skip = 0
        _target_file = []
        str = str2 = ''
        self.OC.ReloadData()
        X_Data_Length = int(self.OC.X_End - self.OC.X_Start) #calcultae how much data we have in length for each axis
        Y_Data_Length = int(self.OC.Y_End - self.OC.Y_Start)  
            
        GcodeFile = open(filename, 'r') #this gets us the max and min location for x and y        
        for line in GcodeFile:
            if (line.find('G00 X0.0000 Y0.0000') is not -1):
                continue              
            if (line.find('G00 X') is not -1 or line.find('G01 X') is not -1): # this simply saves the last X Y location of the last line
                left, delimiter, right = line.partition('X')
                left, delimiter, right = right.partition(' Y')  
                _X = float(left)
                if(right.find(' F200.00') is not -1): #in case theres F200 in the end
                    right = right.replace(" F200.00","")
                right = right.replace("\n","")
                _Y = float(right)
                if (first_time == 0):
                    first_time = 1
                    _MinX = _X
                    _MinY = _Y
                    _MaxX = _X
                    _MaxY = _Y
                                    
                if (_X < _MinX): _MinX = _X
                if (_Y < _MinY): _MinY = _Y
                if (_X > _MaxX): _MaxX = _X
                if (_Y > _MaxY): _MaxY = _Y
        
        if (ceil(abs(_MaxX -_MinX)) > X_Data_Length or ceil(abs(_MaxY -_MinY)) > Y_Data_Length): # first validate  gcode isnt larger then probing data area    
            print ceil(abs(_MaxX -_MinX)), X_Data_Length, ceil(abs(_MaxY -_MinY)), Y_Data_Length
            raise NameError('Insufficent Probing Data, Probe larger or Load Smaller Gcode')
        if (_MinX < self.OC.X_Start):
            _OffsetX = ceil(self.OC.X_Start-_MinX)
        elif(_MaxX > self.OC.X_End):
            _OffsetX = ceil(_MaxX-self.OC.X_End)*-1
        if (_MinY < self.OC.Y_Start):
            _OffsetY = ceil(self.OC.Y_Start-_MinY)
        elif (_MaxY > self.OC.Y_End):
            _OffsetY = ceil(_MaxY-self.OC.Y_End)*-1
        
        if (_OffsetX > 0 or _OffsetX < 0 or _OffsetY > 0 or _OffsetY < 0):
            print 'Offset X by:{0} Offset Y by:{1}'.format(_OffsetX,_OffsetY)
            _Changed = 1
            GcodeFile = open(filename, 'r') #open the gcode file        
            for line in GcodeFile:
                if (line.find('M05') is not -1):
                    skip = 6
                    continue
                if (skip > 0):
                    skip -= 1
                    continue      
                if (line.find('(') is not -1): #this will remove all the text at start of the pcb gcode
                    continue
                if (line.find('G00 X0.0000 Y0.0000') is not -1): #this will skip that line
                    _target_file.append(line)
                    continue 
                if (line.find('G00 X') is not -1 or line.find('G01 X') is not -1): # this simply saves the last X Y location of the last line
                    if (line.find('G00 X') is not -1):
                        str2 = '00'
                    else: str2 = '01'
                    left, delimiter, right = line.partition('X')
                    left, delimiter, right = right.partition(' Y')  
                    _X = float(left)
                    if(right.find(' F200.00') is not -1): #in case theres F200 in the end
                        right = right.replace(" F200.00","")
                        str = 'F200.00'
                    else:
                        str = ''
                    right = right.replace("\n","")
                    _Y = float(right)                    
                    line = 'G{0} X{1} Y{2} {3} \n'.format(str2,_X+_OffsetX, _Y+_OffsetY, str)
                _target_file.append(line)
        
            GcodeFile.close()        
            GcodeFile = open(filename, 'w')        
            for line in _target_file:GcodeFile.write(line)
            GcodeFile.close()
        return _Changed
                                 
    def GetDrillDepth(self, filename):
        GcodeFile = open(filename, 'r') #open the gcode file
        for line in GcodeFile:
            if (line.find('Z-') is not -1): ##if its going down then set edit ON, offset current Z and save x,y as refernce for testing is next point is utleast 2mm apart
                left, delimiter, right = line.partition('Z-')
                left, delimiter, right = right.partition(' ')
                print 'Drill Depth Found : {}'.format(left)
                return left
        raise NameError('Invalide PCB-Gcode File (No Drill Depth Found)')
        
    def PcbOffset(self, filename): #non genric function (gcode specific - slic3r in this case)
        _index_counter = _editOn = _clear = _drill_depth= _X = _Y = _LastX = _LastY = _Z = _refx = _tempx = _tempy = _refy = _cur_dis = _min_dis = _leftover = 0 
        _target_file = ['M120 \n']        
        self.OC.ReloadData()                 
        GcodeFile = open(filename, 'r') #open the gcode file
        _Num_Lines = sum(1 for line in GcodeFile)
        _stepsize  = int(round(100000/float(_Num_Lines), 0))*100
        
        try: _drill_depth = float(self.GetDrillDepth(filename))
        except: 
            print 'Invalide PCB-Gcode File (No Drill Depth Found)'
            return
        self.parent.gauge.SetValue(pos=0)
        GcodeFile = open(filename, 'r') #open the gcode file
        for line in GcodeFile: # this is the where the offseting is done
            _index_counter += 1  #keep index
            if (_index_counter % 100 == 0):
                self.parent.gauge.SetValue(pos=self.parent.gauge.GetValue() + _stepsize)
            #if (line.find('G01 Z') is not -1 or line.find('G00 Z') is not -1): ## if we have a line that starts with G01/G00 Z determine if its the going up or down
            if (line.find('Z-') is not -1): ##if its going down then set edit ON, offset current Z and save x,y as refernce for testing is next point is utleast 2mm apart
                _editOn = 1
                _Z = self.OC.GetZforXY( _X, _Y)
                _refx = _X
                _refy = _Y
                if (_Z is None): print 'No Z data for Point X{} Y{}'.format(_X , _Y)
                line = 'G01 Z{0} F200.00 \n'.format(_Z - _drill_depth)
                _target_file.append(line)
                continue
            elif (line.find('Z') is not -1): # otherwise it must be going up so just turn editOff
                _editOn = 0
                line = 'G01 Z{0} F2000 \n'.format(self.OC.Zmax + 1)
                _target_file.append(line)
                continue
                               
            if (line.find('G00 X') is not -1 or line.find('G01 X') is not -1): # this simply saves the last X Y location of the last line
                left, delimiter, right = line.partition('X')
                left, delimiter, right = right.partition(' Y')  
                _X = float(left)
                if(right.find(' F200.00') is not -1): #in case theres F200 in the end
                    right = right.replace(" F200.00","")
                right = right.replace("\n","")
                _Y = float(right)
                
                if (_editOn is 1):   # if editOn is on this means that this line needs to be offseted 
                    
                    _min_dis = self.OC.DisCalc(_X,_Y,_refx,_refy) # calculate the distance reletive to refrence point (e.g. last point offseted)
                    _cur_dis = self.OC.DisCalc(_X,_Y,_LastX,_LastY)
                    
                    if (_min_dis < 0.3):   # if the point were testing is less than 2mm away from the refrence point just pass.
                        pass                    
                    if (_min_dis > 0.3 and _cur_dis < self.OC.R ): #if the distance to refrence point is more than 2 but less then R offset it like it is
                        _Z = self.OC.GetZforXY(_X, _Y)
                        _refx = _X
                        _refy = _Y
                        line = 'G01 X{0} Y{1} Z{2} \n'.format(_X, _Y, (_Z - _drill_depth))
                    
                    elif (_cur_dis > self.OC.R):    #if the distance from the last point to currnet point is more than R we need to split the data by the reminder of the dis/R                     
                        _leftover = int(floor(_cur_dis / self.OC.R))
                        line = ''
                        for i in range(1, _leftover + 2): # this splits the line to points that are less the R away from each other and offsets them
                            _tempx = (((_X - _LastX) / (_leftover + 1))* i) + _LastX # 
                            _tempy = (((_Y - _LastY) / (_leftover + 1))* i) + _LastY #
                            _tempx = float(format(_tempx, ".4f"))
                            _tempy = float(format(_tempy, ".4f"))                            
                            _Z = self.OC.GetZforXY(_tempx, _tempy)
                    
                            line += 'G01 X{0} Y{1} Z{2} \n'.format(_tempx, _tempy, _Z - _drill_depth)
                       
                        _refx = _X
                        _refy = _Y
                       
                _LastX = _X
                _LastY = _Y            
    
            _target_file.append(line)
        _target_file.append('M120')    
        GcodeFile.close()
        filename, fileExtension = os.path.splitext(filename)
        filename+='_offset'+fileExtension       
        GcodeFile = open(filename, 'w')        
        for line in _target_file:GcodeFile.write(line)
        GcodeFile.close()

    def TestFunction(self):              
        _MyOffsetData = zeros((Nx,Ny),dtype=float)        
        for i in range(self.OC.X_Start, self.OC.X_End+1):            
            for j in range(self.OC.Y_Start, self.OCY_End+1): 
                _Z = self.OC.GetZforXY(i, j)
                _MyOffsetData[i-x0,j-y0] = _Z
                print i,j                   
        savez('test', OffsetData=_MyOffsetData)        
                
class Offset3D(object): #class for 3d printing offset calculations
    
    def GetLayer(self, filename, layer_number): #this function return a single layer of gcode as a list of lines
        _target_layer = []
        x = 0
        _start_layer_index, _end_layer_index = self.GetSlic3rIndexLayer(filename,layer_number)
        GcodeFile = open(filename, 'r') #open the gcode file
        for line in GcodeFile:
            x += 1
            if x in range(_start_layer_index, _end_layer_index):_target_layer.append(line)
        GcodeFile.close()
        return _target_layer 
                        
    def GetSlic3rIndexLayer(self, filename, layer_number): #non genric function (gcode specific - slic3r in this case)
        _start_layer_index = 0
        _end_layer_index = 0
        _index_counter = 0
        _clear = 0
        _layer_counter = 0
        _findme = 'str'
        _layer_height = 0
        _firstLayer_height = 0
        GcodeFile = open(filename, 'r') #open the gcode file
        for line in GcodeFile:
            _index_counter += 1
            if (_layer_counter == 20 and _clear == 0): #in case not found in first 20 lines
                print 'Bad File! Not a Slic3r format?'
                break
            elif (line.find('; layer_height = ') is not -1 and _clear == 0): #look for the layer hight Slic3r format only
                _layer_height = float(line.replace("; layer_height = ","").replace("\n",""))
                _clear = 1
            if (line.find('G1 Z') is not -1 and _clear is not 2 and _clear is not 3):  #look for the the *first layer hight* might be diffrent from others
                left, delimiter, right = line.partition(' F')
                _firstLayer_height = float(left.replace("G1 Z",""))
                _start_layer_index = _index_counter
                _findme = 'G1 Z' + str(_firstLayer_height+_layer_height) # calc the next layer hight
                _clear = 2
            if (line.find(_findme) is not -1): #find the next layer
                _end_layer_index = _index_counter #save it, might be the result
                _clear = 3
                continue
            if (_clear == 3):
                if (line.find('G92 E0') is not -1): #this means its a z lift not next layer   
                    _clear = 2
                else:
                    _layer_counter += 1
                    if (_layer_counter == layer_number):
                        GcodeFile.close()
                        return (_start_layer_index, _end_layer_index) #stop and return the indexs
                    else:
                        _start_layer_index = _index_counter #clear saved and continue
                        _findme = 'G1 Z' + str(_firstLayer_height+_layer_height+(_layer_height*currentLayer))
                        _clear = 2 
    
    def ReplaceLayer(self, filename, layer_number, target_layer):
        x = 0
        _target_file = []
        _start_layer_index, _end_layer_index = self.GetSlic3rIndexLayer(filename,layer_number)
        GcodeFile = open(filename, 'r') #open the gcode file
        for line in GcodeFile:
            _target_file.append(line)
        #print _start_layer_index, _end_layer_index
        for x in range(_start_layer_index, _end_layer_index):
            _target_file.pop(_start_layer_index-1)
        GcodeFile.close()
        GcodeFile = open('test.gcode', 'w')
        for line in target_layer:
            _target_file.insert(_start_layer_index-1, line)
            _start_layer_index += 1
        for line in _target_file:GcodeFile.write(line)
        GcodeFile.close()
        return 
    
    def SplitLines(self, layer):
        counter, index
        for line in layer:
            if (line.find('G1 X') is not -1 and line.find('E') is not -1):               
             counter += 1               
    
    def PlaceZ(self, line, ):  
        pass

    def FixData(self, Layer):
        pass 