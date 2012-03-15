
from numpy import *


def Unit_set():
    global file_out,Step,X_Start,Y_Start,X_End,Y_End,Step,file_out,LoopCountX,LoopCountY,_LastLine,_CurrentLastLine,_DeltaFloat,_DeltaStr,_TimeOutCounter,_ProbYPos,_ProbXPos,_InvertDirS,_InvertDirE,_3D_out_String
    X_Start           =  0
    Y_Start           =  0
    X_End             =  190
    Y_End             =  190
    Step              =  10
    file_out          =  "Offset1"
    Ent_Start_X.delete(0, END)
    Ent_Start_Y.delete(0, END)
    Ent_End_X.delete(0, END)
    Ent_End_Y.delete(0, END)
    Ent_step.delete(0, END)   
    Ent_Start_X.insert(0, X_Start)
    Ent_Start_Y.insert(0, Y_Start)
    Ent_End_X.insert(0, X_End)
    Ent_End_Y.insert(0, Y_End)
    Ent_step.insert(0, Step)
    Ent_fileout.insert(0, file_out)
def OK() :
    global OK, file_out
    if file_out == "": OK = False
    else: OK = True
    top.destroy()
def Cancel() :
    global OK    
    OK = False
    top.destroy()   
# Entry validation functions
def IntCheck(new_string) :
    if new_string == "": new_string = "0"
    try:
        v = int(new_string)
        if v > 1000 or v < 0: return False
        if len(new_string) > 4 : return False
        return True
            # True tells Tkinter to accept the new string
    except ValueError:
        return False
def FileNameCheck(new_string) :
    if new_string == "": new_string = "0"
    try:
        if not new_string.isalnum(): return False
        if len(new_string) > 9 : return False
        return True
            # True tells Tkinter to accept the new string
    except ValueError:
        return False
def StepCheck(new_string) :
    if new_string == "": new_string = "0"
    try:
        v = int(new_string)
        if v > 100 or v < 0: return False
        if len(new_string) > 3 : return False
        return True
            # True tells Tkinter to accept the new string
    except ValueError:
        return False
def test_X(X_min, X_max):
    if X_dest < X_min : X_min = X_dest
    elif X_dest > X_max : X_max = X_dest
    return X_min, X_max
def test_Y(Y_min, Y_max):
    if Y_dest < Y_min : Y_min = Y_dest
    elif Y_dest > Y_max : Y_max = Y_dest
    return Y_min, Y_max           
# Fire up the Tkinter GUI

from Tkinter import *
top = Tk()
top.title("Etch_Z_adjust setup")

# Define the Tkinter variables
get_X_Start     = IntVar()
get_Y_Start     = IntVar()
get_X_End       = IntVar()
get_Y_End       = IntVar()
get_step        = IntVar()
get_file_out    = StringVar()

# define the label, checkbutton, radiobutton, button and entry widgets:
# Label widgets:
L_blank1        = Label(top, text="")
L_blank2        = Label(top, text="")
L_blank3        = Label(top, text="")                       
L_blank4        = Label(top, text="")
L_blank5        = Label(top, text="")
L_blank6        = Label(top, text="")  
L_units         = Label(top, text="Units to use:")
L_grid_def      = Label(top, text="Sample Resolution(mm):")
L_X_Start_eq    = Label(top, text="Start X:")
L_Y_Start_eq    = Label(top, text="Start Y:")
L_X_End_eq      = Label(top, text="End X:")
L_Y_End_eq      = Label(top, text="End Y:")
L_File_out      = Label(top, text="Offset File Name:")
# Checkbutton

# Button widgets:
B_cancel        = Button(top, text ="CANCEL",    command = Cancel)
B_OK            = Button(top, text ="OK",        command = OK)

# Define validation function numbers for validatecommand to call 
val_int  = top.register(IntCheck)
val_FileNameCheck = top.register(FileNameCheck)
val_step = top.register(StepCheck)

# Entry widget definitions:
Ent_Start_X     = Entry(master=top, width = 3,  textvariable = get_X_Start,
                        validate = "key", validatecommand = val_int + ' %P')
Ent_Start_Y     = Entry(master=top, width = 3,  textvariable = get_Y_Start,
                        validate = "key", validatecommand = val_int + ' %P')
Ent_End_X       = Entry(master=top, width = 3,  textvariable = get_X_End,
                        validate = "key", validatecommand = val_int + ' %P')
Ent_End_Y       = Entry(master=top, width = 3,  textvariable = get_Y_End,
                        validate = "key", validatecommand = val_int + ' %P')
Ent_step        = Entry(master=top, width = 6,  textvariable = get_step,
                        validate = "key", validatecommand = val_step + ' %P')
Ent_fileout     = Entry(master=top, width = 6,  textvariable = get_file_out,
                        validate = "key", validatecommand = val_FileNameCheck + ' %P ')

# lay out the widgets:
L_blank1.grid       (row=0, column=0)
Ent_step.grid       (row=1, column=2, sticky=W, ipadx = 10)
L_grid_def.grid     (row=1, column=1, sticky=W)
L_blank3.grid       (row=1, column=3)
Ent_Start_X .grid   (row=1, column=5, columnspan=2, sticky=W, ipadx = 8)
Ent_Start_Y.grid    (row=2, column=5, sticky=W, ipadx = 8)
L_X_Start_eq.grid   (row=1, column=4, sticky=W)
L_Y_Start_eq.grid   (row=2, column=4, sticky=W)
L_X_End_eq.grid     (row=1, column=6, sticky=W)
L_Y_End_eq.grid     (row=2, column=6, sticky=W)
Ent_End_X .grid     (row=1, column=7, sticky=W, ipadx = 8)
Ent_End_Y.grid      (row=2, column=7, sticky=W, ipadx = 8)
L_blank4.grid       (row=2, column=3)
L_File_out.grid     (row=2, column=1, sticky=W)
Ent_fileout.grid    (row=2, column=2, sticky=W, ipadx = 10)
L_blank5.grid       (row=8, column=0)
B_OK.grid           (row=9, column=4, sticky=W)
B_cancel.grid       (row=9, column=2, sticky=W)
L_blank6.grid       (row=10, column=0)

def GetZforXY(X, Y, OffsetData):
    # x - the x axis of the point
    # y - the y axis of the point
    # x0 - the x axis of the first point
    # y0 - the y axis of the first point
    # R - the Resioltion of the test
    # Nx - the number of test in the x axis
    # Ny - the number of test in the y axis
    # Rconst = sqrt(R*R/2)
    global x0,y0,X_End,Y_End,R,Nx,Ny,Rconst,Xclose,Yclose,XcloseRatio,YcloseRatio,Dis1,Dis2,Dis3,Dis4,total,mag1,mag2,mag2,mag4,result
    x0    = OffsetData['ProbData'][0]
    y0    = OffsetData['ProbData'][1]
    X_End = OffsetData['ProbData'][2]
    Y_End = OffsetData['ProbData'][3]
    R     = OffsetData['ProbData'][4]
    Nx    = int(round((X_End - x0) / Step, 0))
    Ny    = int(round((Y_End - y0) / Step, 0))
    Rconst = sqrt(R*R*2)
    
    if( X >= x0 and Y >= y0 and X<x0 + R*(Nx-1) and Y< y0 + R*(Ny-1) ):
        Xclose = int(round((X-x0)/R, 0))
        Yclose = int(round((Y-y0)/R, 0))      
        XcloseRatio = float(x0 + R*Xclose)      
        YcloseRatio = float(y0 + R*Yclose)
        Dis1 = float(sqrt(power(X-XcloseRatio,2) + power(Y-YcloseRatio,2)))
        Dis2 = float(sqrt(power(X-XcloseRatio - R,2) + power(Y-YcloseRatio,2)))
        Dis3 = float(sqrt(power(X-XcloseRatio - R,2) + power(Y-YcloseRatio - R,2)))
        Dis4 = float(sqrt(power(X-XcloseRatio,2) + power(Y-YcloseRatio - R,2)))
        total = float(4 * Rconst - (Dis1 + Dis2 + Dis3 + Dis4))
        mag1 = float(Rconst-Dis1)
        mag2 = float(Rconst-Dis2)
        mag3 = float(Rconst-Dis3)
        mag4 = float(Rconst-Dis4)
        result = ( (OffsetData['OffsetData'][Xclose][Yclose]*mag1) + (OffsetData['OffsetData'][Xclose+1][Yclose]*mag2) + (OffsetData['OffsetData'][Xclose+1][Yclose+1]*mag3) + (OffsetData['OffsetData'][Xclose][Yclose+1]*mag4) )
        return result / total


## End Tkinter defaults
Unit_set()
# Now let's get the Tkinter loop twirling
top.mainloop()
# After exiting the Tkinter loop, process the data
if OK == True:
    OffsetData = load('{}.npz'.format('offset'))
    GetZforXY(30,30, OffsetData)