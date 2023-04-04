import adsk.core, adsk.fusion, adsk.cam
import traceback 
import math
import xml.etree.ElementTree as ET
import shutil
import os

"""

Hi, welcome to the source code for the custom thread generator.

Initial inputs are defined below.

Fusion defines threads by five key values:

1) Minor diameter.
2) Major diameter.
3) Pitch.
4) Pitch Diameter.
5) Thread Angle.

This app allows users to create custom thread profiles via input of the above values into a created UI.

The custom thread profile will appear in fusions thread menu under the chosen name upon completion.

DEBUG:

- CHECK FILE PATH IN "moveXML" FUNCTION IS CORRECT.

- Jake 

"""

#defines inital values.
defaultThreadName = 'Thread Zeppelin'
defaultID = 0.18 #minor diameter.
defaultOD = 0.2 #major diameter.
defaultPitch = 0.08
defaultPitchDiameter = (defaultOD - defaultID)/2 + defaultID
defaultAngle = 30.0 * math.pi/180

#stores command handlers.
handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface

class CommandExecuteHandler(adsk.core.CommandEventHandler):

    def __init__(self):
        super().__init__()

    def notify(self, args):
        global text
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs
            thread = Thread()
            for input in inputs:
                if input.id == 'thread_name':
                    thread.thread_name = input.value
                elif input.id == 'ID':
                    thread.ID = unitsMgr.evaluateExpression(input.expression, "mm")
                elif input.id == 'OD':
                    thread.OD = unitsMgr.evaluateExpression(input.expression, "mm")
                elif input.id == 'pitch':
                    thread.pitch = unitsMgr.evaluateExpression(input.expression, "mm")
                elif input.id == 'pitch_piamater':
                    thread.pitch_diameter = unitsMgr.evaluateExpression(input.expression, "mm")
                elif input.id == 'angle':
                    thread.angle = unitsMgr.evaluateExpression(input.expression, "deg") 
            text = [thread.thread_name, thread.ID, thread.OD, thread.pitch, thread. pitch_diameter, thread.angle]
            creatorXML()
            moveXML()      
        
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
class CommandDestroyHandler(adsk.core.CommandEventHandler):
    
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            adsk.terminate()
        
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    
    def __init__(self):
        super().__init__() 

    def notify(self, args):
        try:  
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = CommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            onDestroy = CommandDestroyHandler()
            cmd.destroy.add(onDestroy)

            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onDestroy)

            inputs = cmd.commandInputs
            inputs.addTextBoxCommandInput('readonly_textBox', 'Welcome, read me!', """This app generates custom thread profiles for Fusion. Once generated custom thread paths will become available, under the chosen name, in the threads tab within Fusion 360.""", 2, True)
            inputs.addStringValueInput('thread_name', 'Thread Name', defaultThreadName)
            initID = adsk.core.ValueInput.createByReal(defaultID)
            inputs.addValueInput('ID', 'Minor Diameter','mm',initID)
            initOD = adsk.core.ValueInput.createByReal(defaultOD)
            inputs.addValueInput('OD', 'Major Diameter', 'mm', initOD)
            initPitch = adsk.core.ValueInput.createByReal(defaultPitch)
            inputs.addValueInput('pitch', 'Pitch', 'mm', initPitch)
            initPitchDiameter = adsk.core.ValueInput.createByReal(defaultPitchDiameter)
            inputs.addValueInput('pitch_diameter', 'Pitch Diameter', 'mm', initPitchDiameter)
            initAngle = adsk.core.ValueInput.createByReal(defaultAngle)
            inputs.addValueInput('angle', 'Cut Angle', 'deg', initAngle)
        
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class Thread:
    
    def __init__(self):
        self._thread_name = defaultThreadName
        self._ID = defaultID
        self._OD = defaultOD
        self._pitch = defaultPitch
        self._pitch_diameter = defaultPitchDiameter
        self._angle = defaultAngle

    @property
    def thread_name(self):
        return self._thread_name
    @thread_name.setter
    def thread_name(self, value):
        self._thread_name = value

    @property
    def ID(self):
        return self._ID
    @ID.setter
    def ID(self, value):
        self._ID = value

    @property
    def OD(self):
        return self._OD
    @OD.setter
    def OD(self, value):
        self._OD = value 

    @property
    def pitch_diameter(self):
        return self._pitch_diameter
    @pitch_diameter.setter
    def pitch_diameter(self, value):
        self._pitch_diameter = value 

    @property
    def pitch(self):
        return self._pitch
    @pitch.setter
    def pitch(self, value):
        self._pitch= value   

    @property
    def angle(self):
        return self._angle
    @angle.setter
    def angle(self, value):
        self._angle = value  

#scripts, formats, generates and saves the thred xml file with user inputs. Do not edit formatting in this function.
def creatorXML():
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<ThreadType>
  <Name>""" + str(text[0]) + """</Name>
  <CustomName>""" + str(text[0])  + """</CustomName>
  <Unit>mm</Unit>
  <Angle>""" + str(round(text[5], 3) * 180/math.pi) + """</Angle>
  <SortOrder>4</SortOrder>
  <ThreadSize>
    <Size>""" + str(round(text[2], 3) * 10) + """</Size>
    <Designation>
      <ThreadDesignation>TR""" + str(round(text[2], 3) * 10) + """x""" + str(round(text[3], 3) * 10) + """</ThreadDesignation>
      <CTD>TR""" + str(round(text[2], 3) * 10) + """x""" + str(round(text[4], 3) * 10) + """</CTD>
      <Pitch>""" + str(round(text[3], 3) * 10) + """</Pitch>
      <Thread>
        <Gender>external</Gender>
        <Class>7e</Class>
        <MajorDia>""" + str(round(text[2], 3) * 10) + """</MajorDia>
        <PitchDia>""" + str(((round(text[2], 3) * 10)-(round(text[1], 3) * 10))/2 + round(text[1], 3) * 10) + """</PitchDia>
        <MinorDia>""" + str(round(text[1], 3) * 10) + """</MinorDia>
      </Thread>
      <Thread>
        <Gender>internal</Gender>
        <Class>7H</Class>
        <MajorDia>""" + str(round(text[1], 3) * 10) + """</MajorDia>
        <PitchDia>""" + str(((round(text[2], 3) * 10)-(round(text[1], 3) * 10))/2 + round(text[1], 3) * 10) + """</PitchDia>
        <MinorDia>""" + str(round(text[1], 3) * 10) + """</MinorDia>
        <TapDrill>""" + str(round(text[1], 3) * 10) + """</TapDrill>
      </Thread>
    </Designation>
  </ThreadSize>
</ThreadType>"""
    
    tree = ET.XML(xml_data)
    
    with open(text[0]+".xml", "wb") as f:
        f.write(ET.tostring(tree))

#moves the generated xml thread file to the thread directory.
def moveXML():
    global pth
    
    pth = str(os.getcwd())
    src_path = pth + r'\\' + text[0] + r".xml"
    drc_path = pth + r"\Fusion\Server\Fusion\Configuration\ThreadData" + "\\" + text[0] + r".xml"
    shutil.move(src_path, drc_path)

def run(context):
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        #main command line.
        cmdDef = _ui.commandDefinitions.itemById('cmdInputs')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('cmdInputs', "Threadzilla!", 'Command inputs')
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        cmdDef.execute()
        
        adsk.autoTerminate(False)     
    
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox("You have stopped Threadzilla.")
    
        cmdDef = ui.commandDefinitions.itemById('Thread')
        if cmdDef:
            cmdDef.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

