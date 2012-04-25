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
class guiwin(wx.Frame): #class for gui + general functions
    def __init__(self, size=(0, 0), parent=None):
        self.parent = parent
        self.O3D = Offset3D() 
        self.OPCG = OffsetPCBGOCDE(parent=self)           
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
        self.sv = wx.Button(self.panel, label=_("Offset!"), pos=(90, 200))
        self.eb = wx.Button(self.panel, label=_("Cancel"), pos=(90, 150))
        self.ts = wx.Button(self.panel, label=_("Test Data"), pos=(5, 250))
        self.pr = wx.Button(self.panel, label=_("Print Data"), pos=(90, 250))
        self.gauge = wx.Gauge(self.panel, range=100000, pos=(5, 300), size=(160, 15))
        self.eb.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
        self.cl.Bind(wx.EVT_BUTTON, self.ProbeZ)
        self.ld.Bind(wx.EVT_BUTTON, self.Load)
        self.ts.Bind(wx.EVT_BUTTON, self.TestData)
        self.pr.Bind(wx.EVT_BUTTON, self.PrintData)
        self.sv.Bind(wx.EVT_BUTTON, self.OffsetG)
        self.basedir = "."
        #self.mainsizer.AddSpacer(10)
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainsizer.Add(self.panel,9, wx.EXPAND)
        self.mainsizer.Add(self.notebook,32, wx.EXPAND)
        self.SetSizer(self.mainsizer)
        #self.mainsizer.Fit(self)
        self.Layout()
    
    def SamplePoint(self): #this function will execute a single prob, TODO : make elevation reletive to last point not, absulute.
        _LastLine = _CurrentLastLine = _TimeOutCounter = _DeltaFloat = 0
        _LastLine = self.parent.p.log[-1]
        self.parent.p.send_now("G92 Z8")
        self.parent.p.send_now("G1 Z0 F800")
        self.parent.p.clear = True
        while(True):
            _CurrentLastLine = self.parent.p.log[-1]
            if(_CurrentLastLine is not _LastLine and not _CurrentLastLine.startswith('ok')):
                break
        _CurrentLastLine = _CurrentLastLine.replace("echo:endstops","").replace("hit:","").replace("Z:","").replace(" ","").replace("\n","")
        _DeltaFloat = 8-float(_CurrentLastLine)
        self.parent.p.send_now('G1 Z' + str(_DeltaFloat))
        return _CurrentLastLine
    
    def ProbeZ(self, event): #this function is the probing rutine
        _firstSample = file_out = Step = X_Start = Y_Start = X_End = Y_End = Step = LoopCountX = LoopCountY = _LastLine = _CurrentLastLine = _DeltaFloat = _DeltaStr = _TimeOutCounter = _ProbYPos = _ProbXPos = _InvertDirS = _InvertDirE = _3D_out_String = 0
        result = wx.MessageBox(_('Are you sure you want to probe the grid? this may take a while'), _('Probe the grid?'),
            wx.YES_NO | wx.ICON_QUESTION)
        if (result == 2):
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
            if self.parent.p.online:            
                print Step
                print LoopCountY
                self.parent.p.send_now('G92 Z0')
                self.parent.p.send_now('G1 Z1')
                self.parent.p.send_now('G28 X0 Y0')
                self.parent.p.send_now('G28 Z0')
                self.parent.p.send_now('G1 Z8')
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
                savez(file_out, OffsetData=_OffsetData, ProbData=_ProbData)
            else:
                print _("Printer is not online.")
            self.Refresh()
    
    def TestData(self, event): #this function will go 0.2mm over each 4 of the end points of data and see there is no endstop hit then go down by 0.1 and get an enstop hit.        

        OffsetData = load('{}.npz'.format('offset'))
        z_max = OffsetData['OffsetData'].max()
        z_min = OffsetData['OffsetData'].min()
        X_Start    = OffsetData['ProbData'][0]
        y0    = OffsetData['ProbData'][1]
        X_End = OffsetData['ProbData'][2]
        Y_End = OffsetData['ProbData'][3]
        R     = OffsetData['ProbData'][4]
        Nx    = int(round((X_End - X_Start) / R, 0))
        Ny    = int(round((Y_End - y0) / R, 0))
        print Nx, Ny
        result = wx.MessageBox(_('Start? This Will Home First, Make Sure The Prob Is Connected'), _('Testing Data'),
            wx.YES_NO | wx.ICON_QUESTION)
        if (result == 2):
            self.parent.p.send_now('G92 Z0') 
            self.parent.p.send_now('G1 Z1')
            self.parent.p.send_now('G28 X0 Y0')
            self.parent.p.send_now('G28 Z0') #home all axis so we start from same ref.
            self.parent.p.send_now('G1 Z{}'.format(z_max+3)) #go up 1mm above z max so we dont run into the plate
            self.parent.p.send_now('G1 X{0} Y{1}'.format(X_Start, y0)) #go to z 0.1 @ Xstart Ystart
            self.parent.p.send_now('G1 Z{}'.format(OffsetData['OffsetData'][0][0]+0.2))
            print 'point 1 Z{}'.format(OffsetData['OffsetData'][0][0]+0.2)
        else: return
        
        result = wx.MessageBox(_('Next Point?'), _('Testing Data'),
            wx.YES_NO | wx.ICON_QUESTION)
        if (result == 2):
            self.parent.p.send_now('G1 Z{}'.format(z_max+3)) #go up 1mm above z max so we dont run into the plate
            self.parent.p.send_now('G1 X{0} Y{1}'.format(X_Start, Y_End)) #go to z 0.1 @ Xstart Ystart
            self.parent.p.send_now('G1 Z{}'.format(OffsetData['OffsetData'][0][Ny-1]+0.2))
            print 'point 2 Z{}'.format(OffsetData['OffsetData'][0][Ny-1]+0.2)
        else: return        
        
        result = wx.MessageBox(_('Next Point?'), _('Testing Data'),
            wx.YES_NO | wx.ICON_QUESTION)
        if (result == 2):
            self.parent.p.send_now('G1 Z{}'.format(z_max+3)) #go up 1mm above z max so we dont run into the plate
            self.parent.p.send_now('G1 X{0} Y{1}'.format(X_End, Y_End)) #go to z 0.1 @ Xstart Ystart
            self.parent.p.send_now('G1 Z{}'.format(OffsetData['OffsetData'][Nx-1][Ny-1]+0.2))
            print 'point 3 Z{}'.format(OffsetData['OffsetData'][Nx-1][Ny-1]+0.2)
        else: return 
        
        result = wx.MessageBox(_('Next Point?'), _('Testing Data'),
            wx.YES_NO | wx.ICON_QUESTION)
        if (result == 2):
            self.parent.p.send_now('G1 Z{}'.format(z_max+3)) #go up 1mm above z max so we dont run into the plate
            self.parent.p.send_now('G1 X{0} Y{1}'.format(X_End, y0)) #go to z 0.1 @ Xstart Ystart
            self.parent.p.send_now('G1 Z{}'.format(OffsetData['OffsetData'][Nx-1][0]+0.2))
            print 'point 4 Z{}'.format(OffsetData['OffsetData'][Nx-1][0]+0.2)
        else: return
                 
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
                 
    def Load(self, event):
        #OffsetData = load('{}.npz'.format('offset'))        
        #self.mayavi_view = MayaviView()
        #self.control = self.mayavi_view.edit_traits(parent=self,kind='subpanel').control
        #self.notebook.AddPage(page=self.control, caption='3D Display')
        #set_printoptions(threshold='nan')
        pass
      
    def OffsetG(self, event):
        #try: 
        self.OPCG.PrepareGcode('pcbtest.gcode')
        #except: 
        #    print 'Insufficent Probing Data, Probe larger or Load Smaller Gcode'
        #    return
        child = threading.Thread(target=self.OPCG.PcbOffset, args=['pcbtest.gcode'])
        child.setDaemon(True)
        child.start()
        
class OffsetCalc(object):
    def DisCalc(self, X1, Y1, X2, Y2):
        result = float(sqrt(power(X1-X2,2) + power(Y1-Y2,2)))
        result = format(result, ".4f")
        return float(result)

    def GetZforXY(self, X, Y, OffsetData):  #this function makes a simple bilinar interploation to retrive Z hight for a given X&Y            
        Xclose = Yclose = XcloseRatio = YcloseRatio = r1 = r2 = result = 0
        X_Start    = OffsetData['ProbData'][0]
        Y_Start    = OffsetData['ProbData'][1] 
        X_End      = OffsetData['ProbData'][2]
        Y_End      = OffsetData['ProbData'][3]
        R          = OffsetData['ProbData'][4] # R - the Resolution of the test
        Nx    = int(floor((X_End - X_Start) / R))
        Ny    = int(floor((Y_End - Y_Start) / R))
        
        if( X >= X_Start and Y >= X_Start and X<X_Start + R*(Nx-1) and Y< X_Start + R*(Ny-1) ):
            Xclose = int(round((X-X_Start)/R, 0))
            Yclose = int(round((Y-Y_Start)/R, 0))      
            XcloseRatio = float(X_Start + R*Xclose)      
            YcloseRatio = float(Y_Start + R*Yclose)
            r1 = (XcloseRatio+R-X)*OffsetData['OffsetData'][Xclose][Yclose]/R + (X-XcloseRatio)*OffsetData['OffsetData'][Xclose+1][Yclose]/R
            r2 = (XcloseRatio+R-X)*OffsetData['OffsetData'][Xclose][Yclose+1]/R + (X-XcloseRatio)*OffsetData['OffsetData'][Xclose+1][Yclose+1]/R
            result = (YcloseRatio+R-Y)*r1/R + (Y-YcloseRatio)*r2/R 
            result = format(result, ".4f")
            return float(result)  
    
class OffsetPCBGOCDE(object): #class for pcb gcode offset calculations
    
    def __init__(self, parent=None):        
        self.parent = parent
        self.OC = OffsetCalc()
        
    def PrepareGcode(self, filename): #this function offsets the x axis to be in the positive side, and validates that all x and y locations have probing data.
        _MaxX = _MaxY = _MinX = _MinY = _X = _Y = _OffsetX = _OffsetY = 0
        _target_file = []
        str = str2 = ''
        OffsetData = load('{}.npz'.format('offset')) # load the Offset data and initailze it
        X_Start    = OffsetData['ProbData'][0]
        Y_Start    = OffsetData['ProbData'][1]
        X_End      = OffsetData['ProbData'][2]
        Y_End      = OffsetData['ProbData'][3]
        X_Data_Length = int(X_End - X_Start) #calcultae how much data we have in length for each axis
        Y_Data_Length = int(Y_End - Y_Start)  
            
        GcodeFile = open(filename, 'r') #this gets us the max and min location for x and y        
        for line in GcodeFile:      
            if (line.find('G00 X') is not -1 or line.find('G01 X') is not -1): # this simply saves the last X Y location of the last line
                left, delimiter, right = line.partition('X')
                left, delimiter, right = right.partition(' Y')  
                _X = float(left)
                if(right.find(' F200.00') is not -1): #in case theres F200 in the end
                    right = right.replace(" F200.00","")
                right = right.replace("\n","")
                _Y = float(right)
                                
            if (_X < _MinX): _MinX = _X
            if (_Y < _MinY): _MinY = _Y
            if (_X > _MaxX): _MaxX = _X
            if (_Y > _MaxY): _MaxY = _Y
        
        if (ceil(abs(_MaxX -_MinX)) > X_Data_Length or ceil(abs(_MaxY -_MinY)) > Y_Data_Length): # first validate  gcode isnt larger then probing data area    
            raise NameError('Insufficent Probing Data, Probe larger or Load Smaller Gcode')
        if (_MinX < X_Start):
            _OffsetX = ceil(abs(_MinX))+1
        elif(_MaxX > X_End):
            _OffsetX = ((_MaxX-X_End)*-1)-1
        if (_MinY < Y_Start):
            _OffsetY = ceil(abs(_MinY))+1
        elif (_MaxY > Y_End):
            _OffsetY = ((_MaxY-Y_End)*-1)-1
        
        if (_OffsetX != 0 or _OffsetY != 0):
            GcodeFile = open(filename, 'r') #open the gcode file        
            for line in GcodeFile:      
                if (line.find('(') is not -1): #this will remove all the text at start of the pcb gcode
                    continue
                if (line.find('G00 X0.0000 Y0.0000') is not -1): #this will remove all the text at start of the pcb gcode
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
        return
                                 
    def GetDrillDepth(self, filename):
        GcodeFile = open(filename, 'r') #open the gcode file
        for line in GcodeFile:
            if (line.find('Z-') is not -1 or line.find('Z-') is not -1): ##if its going down then set edit ON, offset current Z and save x,y as refernce for testing is next point is utleast 2mm apart
                left, delimiter, right = line.partition('Z-')
                left, delimiter, right = right.partition(' ')
                return left
        raise NameError('Invalide PCB-Gcode File (No Drill Depth Found)')
        
    def PcbOffset(self, filename): #non genric function (gcode specific - slic3r in this case)
        _index_counter = _editOn = _clear = _drill_depth= _X = _Y = _LastX = _LastY = _Z = _refx = _tempx = _tempy = _refy = _cur_dis = _min_dis = _leftover = 0 
        _target_file = []
        OffsetData = load('{}.npz'.format('offset')) # load the Offset data and initailze it
        z_max = OffsetData['OffsetData'].max()
        z_min = OffsetData['OffsetData'].min()
        x0    = OffsetData['ProbData'][0]
        y0    = OffsetData['ProbData'][1]
        X_End = OffsetData['ProbData'][2]
        Y_End = OffsetData['ProbData'][3]
        R     = OffsetData['ProbData'][4]
        Nx    = int(round((X_End - x0) / R, 0))
        Ny    = int(round((Y_End - y0) / R, 0))        
        
        GcodeFile = open(filename, 'r') #open the gcode file
        _Num_Lines = sum(1 for line in GcodeFile)
        _stepsize  = int(round(100000/float(_Num_Lines), 0))
        print _stepsize
        try: _drill_depth = float(self.GetDrillDepth(filename))
        except: 
            print 'Invalide PCB-Gcode File (No Drill Depth Found)'
            return
        self.parent.gauge.SetValue(pos=0)
        GcodeFile = open(filename, 'r') #open the gcode file
        for line in GcodeFile: # this is the where the offseting is done
            _index_counter += 1  #keep index
            self.parent.gauge.SetValue(pos=self.parent.gauge.GetValue() + _stepsize)
            if (line.find('G01 Z') is not -1 or line.find('G00 Z') is not -1): ## if we have a line that starts with G01/G00 Z determine if its the going up or down
                if (line.find('Z-') is not -1): ##if its going down then set edit ON, offset current Z and save x,y as refernce for testing is next point is utleast 2mm apart
                    _editOn = 1
                    _Z = self.OC.GetZforXY( _X, _Y, OffsetData)
                    _refx = _X
                    _refy = _Y    
                    line = 'G01 Z{0} F200.00 \n'.format(_Z - _drill_depth)
                    _target_file.append(line)
                    continue
                else: # otherwise it must be going up so just turn editOff
                    _editOn = 0
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
                    if (_min_dis > 0.3 and _cur_dis < R ): #if the distance to refrence point is more than 2 but less then R offset it like it is
                        _Z = self.OC.GetZforXY(_X, _Y, OffsetData)
                        _refx = _X
                        _refy = _Y
                        line = 'G01 X{0} Y{1} Z{2} \n'.format(_X, _Y, (_Z - _drill_depth))
                    
                    elif (_cur_dis > R):    #if the distance from the last point to currnet point is more than R we need to split the data by the reminder of the dis/R                     
                        _leftover = int(floor(_cur_dis / R))
                        line = ''
                        for i in range(1, _leftover + 2): # this splits the line to points that are less the R away from each other and offsets them
                            _tempx = (((_X - _LastX) / (_leftover + 1))* i) + _LastX # 
                            _tempy = (((_Y - _LastY) / (_leftover + 1))* i) + _LastY #
                            _tempx = float(format(_tempx, ".4f"))
                            _tempy = float(format(_tempy, ".4f"))                            
                            _Z = self.OC.GetZforXY(_tempx, _tempy, OffsetData)
                    
                            line += 'G01 X{0} Y{1} Z{2} \n '.format(_tempx, _tempy, _Z - _drill_depth)
                       
                        _refx = _X
                        _refy = _Y
                       
                _LastX = _X
                _LastY = _Y            

    
            _target_file.append(line)
            
        GcodeFile.close()        
        GcodeFile = open('test2.gcode', 'w')        
        for line in _target_file:GcodeFile.write(line)
        GcodeFile.close()
        
             
 
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