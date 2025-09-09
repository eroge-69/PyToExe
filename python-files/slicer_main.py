"""
slicer_main.py

Copyright (C) 2025 Daniel Brogan

This file is part of the Fractal Cortex project.
Fractal Cortex is a Multidirectional 5-Axis FDM Slicer.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import pyglet
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key
import glooey
import trimesh
import numpy as np
from ctypes import (
    c_float,
    byref,
    create_string_buffer,
    cast,
    POINTER,
    pointer,
    c_char,
    c_uint,
    sizeof,
    c_double,
)
import math as m
from fractal_widgets import *
from widget_functions import *

"""
Contains all the logic and processes required to run the interactive graphics window.
"""

# Global variable
L_loadedIndices = []  # List of indices that have already been loaded

""" Camera Class """
class Camera:  # Sets initial camera instance variables
    def __init__(self):
        self.cameraDistance = 350.0
        self.cameraAngleX = 0.0
        self.cameraAngleY = -75.0
        self.lookPositionX = -60.0
        self.lookPositionY = -20.0
        self.rotateSensitivity = 0.4
        self.scrollSensitivity = 10.0
        self.panningSensitivity = 0.5

""" Calculation Worker Class """
class CalculationWorker: # Used for Multithreading
    def __init__(self):
        self.task_queue = queue.Queue()                         # Stores tasks to be processed
        self.result_queue = queue.Queue()                       # Stores completed results
        self.thread_pool = ThreadPoolExecutor(max_workers=4)    # Creates 4 worker threads
        self.running = True                                     # Controls worker lifecycle
        
    def start(self):
        # Launches daemon thread that processes queued tasks
        threading.Thread(target=self.process_queue, daemon=True).start()
        
    def process_queue(self):
        while self.running:
            try:
                # Get next task from queue
                task = self.task_queue.get(timeout=0.1)
                # Execute task in thread pool
                future = self.thread_pool.submit(task['function'], *task['args']) 
                # Store result and callback
                future.add_done_callback(lambda f, cb=task['callback'], 
                                              prog_cb=task.get('progress_callback'): 
                                              self.result_queue.put((cb, f, prog_cb)))
            except queue.Empty:
                continue
        # Clean shutdown
        self.thread_pool.shutdown(wait=False)
                
    def add_task(self, function, callback, *args, progress_callback=None):
        # Adds new task to queue with function to run, callback to handle result, and arguments
        self.task_queue.put({
            'function': function,
            'callback': callback,
            'progress_callback': progress_callback,
            'args': args
        })

    def stop(self):
        self.running = False


""" Graphics_Window Class """
class Graphics_Window(pyglet.window.Window):  # Custom pyglet window which contains everything (both the 3D interactive viewport and the widget foreground)
    # Initialize Class Variables:
    D_finalPositions = {}
    D_finalRotations = {}
    D_finalScales = {}

    L_actionHistory = [[]]
    L_translationHistory = [[]]
    L_rotationHistory = [[]]
    L_scalingHistory = [[]]

    D_stlSelectStates = {}

    D_previousPositions = {}
    D_previousRotations = {}
    D_previousScales = {}

    D_positionHistory = {}
    D_orientationHistory = {}
    D_sizeHistory = {}
    D_axisRotationHistory = {}

    selectedFileKey = None

    D_renderedToolpaths = {}

    D_slicePlaneValidity = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        glClearColor(240.0 / 255.0, 255.0 / 255.0, 255.0 / 255.0, 1.0)  # Azure

        self.Camera = Camera()                      # Create instance of Camera class
        self.Render_Model = Render_Model()          # Create instance of Render_Model class
        self.Render_Preview = Render_Preview()
        self.Render_SlicePlanes = Render_SlicePlanes()
        self.User_Interaction = User_Interaction()  # Create instance of User_Interaction class
        self.lastMousePosition = None
        self.translation = [0.0, 0.0, 0.0]
        self.dragging = False
        self.lastIntersectionPoint = None
        self.doneTranslating = True
        self.multipleSelected = False
        self.updateTranslateText = False
        self.windowHeight = 720
        self.windowWidth = 1080

        self.segments3D = []

        self.toolpathScene = trimesh.Scene()

        """ Add All Widgets: """
        self.gui = glooey.Gui(self)

        """ End of Widgets """
        self.projectionMatrix = (GLdouble * 16)()
        self.modelViewMatrix = (GLdouble * 16)()
        self.viewportMatrix = (GLint * 4)()

        # MULTITHREADING SETUP:
        self.worker = CalculationWorker()   # Creates instance of worker
        self.worker.start()                 # Begins the worker thread

        pyglet.clock.schedule_interval(self.check_calculation_results, 1/60.0) # Checks for completed results at 60Hz (Probably doesn't need to be this fast)

        self.calculation_in_progress = False

    def check_calculation_results(self, dt): # For Multithreading
        try:
            callback, future, progress_callback = self.worker.result_queue.get_nowait()
            if future.done():
                if callback:
                    try:
                        result = future.result()
                        callback(result)
                    except Exception as e:
                        print(f"Error processing result: {e}")
                self.calculation_in_progress = False
                        
        except queue.Empty: # If there is nothing in the queue, pass
            pass

    def queue_slicing_calculations(self, inputs):
        self.calculation_in_progress = True
        self.worker.add_task(self.slicing_calculations, self.TEST_slicing_callback, inputs, progress_callback=self.update_slicing_progress)

    def slicing_calculations(self, meshData):
        slice_function(meshData)
        result = 'test'
        return result

    def TEST_slicing_callback(self, result):
        """
        Handle the completed calculation results in the main thread.
        This will be called when calculations are done.
        """
        R_viewMode.set_disabled(False)
        R_printMode.set_disabled(False)
        sliceButtonDeck.set_state("B_saveGcodeAs")
        # Print a simple completion message
        print('Slicing Completed')
        
        # If you want to update the GUI, do it here
        # For example, you could update a label:
        # if hasattr(self, 'status_label'):
        #     self.status_label.text = "Calculations complete!"

    def update_slicing_progress(self, progress):
        # Update progress bar or other UI elements
        # self.progress_bar.value = progress * 100
        pass

    def on_close(self):
        # Make sure to clean up the worker when closing
        self.worker.stop()
        super().on_close()
        
    def on_resize(self, width, height):
        super().on_resize(width, height)
        glLoadIdentity()

    def on_show(self):
        ##        self.maximize()                               # Maximizes the screen
        self.set_minimum_size(
            width=self.windowWidth, height=self.windowHeight
        )                                                       # Sets the minimum size of the screen
        glEnable(
            GL_DEPTH_TEST
        )                                                       # Hides any pixels of models that are occluded by another model relative to the camera's perspective
        self.setup_lighting()                                   # Creates a light in the viewport and defines its properties
        glDepthFunc(
            GL_LEQUAL
        )                                                       # THIS SOLVES THE PROBLEM OF STACKED WIDGETS NOT RENDERING IN THE CORRECT ORDER

    @staticmethod
    def setup_lighting():
        glEnable(
            GL_LIGHTING
        )                   # Enables the ability to have the colors of polygons on models change by virtue of the presence of light
        glEnable(
            GL_LIGHT0
        )                   # Specifies that a single light source will be defined. For 2 light sources, use LIGHT1, for 3 use LIGHT2, etc. Up to 8 light sources can be supported

        # Define parameters of light source
        lightPosition = (
            0.0,
            350.0,
            0.0,
            0.5,
        )                   # Position and focus of light source (X, Y, Z, focus(0 = directional, 1 = diffuse)). This can be manipulated by the GL_MODELVIEW matrix, but just keep it where it is
        lightDiffuse = (
            1.0,
            1.0,
            1.0,
            1.0,
        )                   # RGB-Alpha settings for diffuse aspect of the lighting
        lightAmbient = (
            0.1,
            0.1,
            0.1,
            1.0,
        )                   # RGB-Alpha settings for ambient aspect of the lighting
        lightSpecular = (
            1.0,
            1.0,
            1.0,
            1.0,
        )                   # RBG-Alpha settings for specular aspect of the lighting

        # Apply parameters to light source
        glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(*lightPosition))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 4)(*lightDiffuse))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat * 4)(*lightAmbient))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (GLfloat * 4)(*lightSpecular))

    @staticmethod
    def reenable_lighting():
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

    @staticmethod
    def disable_lighting():
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)

    def on_draw(self):
        self.reenable_lighting()        # This in conjunction with disabling lighting at the end of this function solves the problem with incorrectly shading the widgets

        glLoadIdentity()                # Replaces the current matrix (the matrix on top of the stack) with the identity matrix

        # Apply camera rotation based on mouse input
        glTranslatef(self.Camera.lookPositionX, self.Camera.lookPositionY, -self.Camera.cameraDistance)     # Translate the camera
        glRotatef(self.Camera.cameraAngleY, 1, 0, 0)                                                        # Rotate the camera around the X axis
        glRotatef(self.Camera.cameraAngleX, 0, 0, 1)                                                        # Rotate the camera around the Y-axis

        # Enable blending for transparency
        glEnable(GL_BLEND)                                                      # Enable the ability to blend colors of different models together if transparent
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)                       # Defines which equations are used to blend pixel colors

        glViewport(0, 0, self.width, self.height)                               # Sets the bounds of where the viewport will be rendered
        glMatrixMode(GL_PROJECTION)                                             # Specifies matrix stack that will be used for subsequent matrix operations. GL_PROJECTION contains information about the viewing volume
        glLoadIdentity()                                                        # Replaces matrix on the top of the stack with the identity matrix
        gluPerspective(45.0, (self.width) / float(self.height), 0.1, 1000.0)    # Defines the parameters of the viewing volume
        glMatrixMode(GL_MODELVIEW)                                              # Specifies matrix stack that will be used for subsequent matrix operations. GL_MODELVIEW is responsible for transforming the camera and models relative to each other

        # Draw the circular disk (short cylinder)
        cylinderColor = (159.0 / 255.0,226.0 / 255.0,191.0 / 255.0,0.8)                     # Translucent Jade
        self.draw_cylinder(radius=150, height=3, slices=50, stacks=1, color=cylinderColor)  # Call the draw_cylinder method

        """ Update STL variables """
        if (B_selectFile.D_variables != {}):                                                        # If the user has selected to open any STL files
            for (k) in B_selectFile.D_variables:                                                    # For each STL file the user wants displayed
                if k not in L_loadedIndices:                                                        # If the STL file has not yet been loaded
                    self.Render_Model.load_stl(k, B_selectFile.D_variables[k])                      # Load the STL
                    self.__class__.D_finalPositions[k] = [0.0,0.0,0.0,]                             # Initialize the final position of the given STL as the origin
                    self.__class__.D_finalRotations[k] = np.eye(4)
                    self.__class__.D_finalScales[k] = [1.0, 1.0, 1.0]
                    self.__class__.L_translationHistory[0] = list(B_selectFile.D_variables.keys())  # Update the current movement history
                    self.__class__.L_rotationHistory[0] = list(B_selectFile.D_variables.keys())
                    self.__class__.L_scalingHistory[0] = list(B_selectFile.D_variables.keys())
                    self.__class__.L_actionHistory[0] = list(B_selectFile.D_variables.keys())
                    self.__class__.D_stlSelectStates[k] = (False)                                   # Add a new selected state as False, since it has just been loaded in
                    self.__class__.D_previousPositions[k] = [0.0,0.0,0.0]                           # Start the STL position at the origin
                    self.__class__.D_previousRotations[k] = np.eye(4)
                    self.__class__.D_previousScales[k] = [1.0, 1.0, 1.0]
                    self.__class__.D_positionHistory[k] = [[0.0, 0.0, 0.0]]                         # Record the position history of this STL
                    self.__class__.D_orientationHistory[k] = [np.eye(4)]
                    self.__class__.D_sizeHistory[k] = [[1.0, 1.0, 1.0]]
                    self.__class__.D_axisRotationHistory[k] = ("X")                                 # Initializing default value
                    self.__class__.D_renderedToolpaths[k] = False
                    L_loadedIndices.append(k)                                                       # Keep track of the fact that this STL has been loaded
            
        if L_loadedIndices != [] and self.calculation_in_progress == False:                         # If there is something to slice and a calculation isn't currently being done, consider enabling the slice button
            printMode = R_printMode.currentlyChecked
            if printMode == "3-Axis Mode" or (printMode == "5-Axis Mode" and B_numSlicingDirections.D_variables['applied'] == True):
                sliceButtonDeck.get_widget("B_slice").set_disabled(False)
                B_numSlicingDirections.set_disabled(False)
            elif printMode == "5-Axis Mode" and B_numSlicingDirections.D_variables['applied'] == False:
                sliceButtonDeck.get_widget("B_slice").set_disabled(True)
                B_numSlicingDirections.set_disabled(False)
                
        else:
            sliceButtonDeck.get_widget("B_slice").set_disabled(True)
            B_numSlicingDirections.set_disabled(True)

        if self.calculation_in_progress == True:
            disable_all_settings()                                          # Disable settings when a calculation is in progress
            R_printMode.set_disabled(True)
        else:
            enable_all_settings()

        meshData = [L_loadedIndices, Render_Model.D_stlMeshes]              # Contains transformed mesh data to be sent to slicing function

        sliceButtonDeck.get_widget("B_slice").argsList = [meshData]
        B_numSlicingDirections.D_variables['meshData'] = meshData
        sliceButtonDeck.get_widget("B_saveGcodeAs").argsList = [[B_selectFile.D_variables[fileKey] for fileKey in B_selectFile.D_variables if fileKey in L_loadedIndices]]

        if sliceButtonDeck.get_widget("B_slice").sliceFlag == True:         # Check if the slice button was pressed. If so, launch the calculation thread
            printMode = R_printMode.currentlyChecked
            if printMode == "3-Axis Mode":
                sliceButtonDeck.get_widget("B_slice").set_disabled(True)    # Disable the slice button so the user can't slice again while something is being sliced
                disable_all_settings()
                self.queue_slicing_calculations(meshData)                   # Perform Slicing Calculations in its own thread
                sliceButtonDeck.get_widget("B_slice").sliceFlag = False
                R_viewMode.D_variables["printMode"] = "3-Axis Mode"
            elif printMode == "5-Axis Mode":
                validityCheck = checkSlicePlaneValidity()
                D_slicePlaneValidity = validityCheck[1]
                if validityCheck[0] == True:
                    print('All slice planes are valid, begin slicing operations')
                    self.queue_slicing_calculations(meshData)
                else:
                    print('Not all slice planes are valid, do not begin slicing operations')
                sliceButtonDeck.get_widget("B_slice").sliceFlag = False
                R_viewMode.D_variables["printMode"] = "5-Axis Mode"
        

        currentViewMode = R_viewMode.currentlyChecked
        if currentViewMode == "Prepare":                    # Render STL models in Prepare mode
            R_geometryAction.set_disabled(False)            # Allow user to transform STLs while in Prepare Mode

            # Draw all loaded STL models
            for k in B_selectFile.D_variables:
                stlFilePath = B_selectFile.D_variables[k]
                self.Render_Model.draw_stl_model(k, stlFilePath)
                
        elif currentViewMode == "Preview":  # Render toolpaths in Preview mode
            # The first time after an STL is sliced, if the user selects Preview, prepare for plotting. Once the path3Ds are loaded once, the user can swap between Prepare and Preview without lag time.
            R_geometryAction.set_disabled(True)                         # Disable the user from transforming STLs while in Preview Mode
            if sliceButtonDeck.get_widget("B_slice").clearVBOs == True: # If VBOs need to be cleared (user just pressed the Slice Button)
                print('Clear VBOs')
                self.Render_Preview.clear_toolpath_vbos()
                sliceButtonDeck.get_widget("B_slice").clearVBOs = False
                self.__class__.D_renderedToolpaths[k] = False

            for k in B_selectFile.D_variables:

                if (self.__class__.D_renderedToolpaths[k] == False):    # If the toolpaths for this STL file haven't been rendered yet, render them once
                    print('This runs once')
                    adhesionPathsCombined = R_viewMode.D_variables["adhesionPathsCombined"]
                    shellPathsCombined = R_viewMode.D_variables["shellPathsCombined"]
                    internalInfillPathsCombined = R_viewMode.D_variables["internalInfillPathsCombined"]
                    solidInfillPathsCombined = R_viewMode.D_variables["solidInfillPathsCombined"]
    
                    adhesion_vbo_data = self.Render_Preview.create_vbo_for_segments(adhesionPathsCombined)
                    shell_vbo_data = self.Render_Preview.create_vbo_for_segments(shellPathsCombined)
                    infill_vbo_data = self.Render_Preview.create_vbo_for_segments(internalInfillPathsCombined)
                    solid_infill_vbo_data = self.Render_Preview.create_vbo_for_segments(solidInfillPathsCombined)
                    
                    self.__class__.D_renderedToolpaths[k] = (True, adhesion_vbo_data, shell_vbo_data, infill_vbo_data, solid_infill_vbo_data)
                    
                    R_viewMode.preRendered = True                       # In the future, make this reset to false when meshes are resliced

                elif self.__class__.D_renderedToolpaths[k][0] == True:
                    # Draw adhesion paths in one color
                    self.Render_Preview.draw_toolpaths_from_stored(self.__class__.D_renderedToolpaths[k][1], (1.0, 0.37, 0.08, 0.7))
                    # Draw shells in a different color
                    self.Render_Preview.draw_toolpaths_from_stored(self.__class__.D_renderedToolpaths[k][2], (0.0, 0.0, 0.0, 0.4))
                    # Draw infill in a different color
                    self.Render_Preview.draw_toolpaths_from_stored(self.__class__.D_renderedToolpaths[k][3], (0.2, 0.5, 0.8, 0.7))
                    # Draw solid infill a different color
                    self.Render_Preview.draw_toolpaths_from_stored(self.__class__.D_renderedToolpaths[k][4], (0.8, 0.2, 0.5, 0.7))
                    

        # DRAWING SLICE PLANES
        numSlicingDirections = int(R_optionMode.D_variables['numSlicingDirections'])
        D_slicePlaneValidity = R_optionMode.D_variables['D_slicePlaneValidity']

        if numSlicingDirections > 1:
            startingPositions = R_optionMode.D_variables['startingPositions']
            directions = R_optionMode.D_variables['directions']
            colors = self.Render_SlicePlanes.colors
            for k in range(numSlicingDirections):
                if k != 0:                                      # Skip the initial plane, since the initial slice direction is always normal to the build plate
                    isValid = D_slicePlaneValidity[str(k)]
                    startX = startingPositions[k][0]
                    startY = startingPositions[k][1]
                    startZ = startingPositions[k][2]
                    theta = directions[k][0]
                    phi = directions[k][1]
                    if isValid:                                 # If the current sliceplane is valid, color it blue
                        R = colors[k][0]/255.0
                        G = colors[k][1]/255.0
                        B = colors[k][2]/255.0
                        plane_vbo = self.Render_SlicePlanes.define_slicePlane(startX, startY, startZ, theta, phi, radius=50.0)
                        self.Render_SlicePlanes.draw_plane(plane_vbo, color=(R, G, B, 0.5))
                    else:                                       # If the current sliceplane is invalid, color it red
                        plane_vbo = self.Render_SlicePlanes.define_slicePlane(startX, startY, startZ, theta, phi, radius=50.0)
                        self.Render_SlicePlanes.draw_plane(plane_vbo, color=(255.0, 0.0, 0.0, 0.5))
        else:
            self.Render_SlicePlanes.cleanup_current_vbo()

        self.reset_widget_color()

        glGetDoublev(GL_PROJECTION_MATRIX, self.projectionMatrix)
        super().on_resize(self.width, self.height)
        glGetDoublev(GL_MODELVIEW_MATRIX, self.modelViewMatrix)
        glGetIntegerv(GL_VIEWPORT, self.viewportMatrix)         # Viewport is a list of pixel coordinates in the form: (0, 0, windowWidth, windowHeight)
        glLoadIdentity()

        self.disable_lighting()                                 # This in conjunction with reenabling lighting at the top of this function solves the problem with incorrectly shading the widgets

    def update_geometry_action_variables(self, fileKey):
        popUpBoxState = r0GeometryActionDeck.get_state()
        if popUpBoxState == "translate":
            r2c1GeometryActionDeck.get_widget("translate").entryBoxEditableLabel.set_text(str(round(self.__class__.D_finalPositions[fileKey][0], 2)))
            r3c1GeometryActionDeck.get_widget("translate").entryBoxEditableLabel.set_text(str(round(self.__class__.D_finalPositions[fileKey][1], 2)))
            r4c1GeometryActionDeck.get_widget("translate").entryBoxEditableLabel.set_text(str(round(self.__class__.D_finalPositions[fileKey][2], 2)))
        elif popUpBoxState == "rotate":
            print("Updating rotation variables")

    def translate_single_STL(self):
        """Define translation vector"""
        translateX = float(r2c1GeometryActionDeck.get_widget("translate").entryBoxEditableLabel.get_text())
        translateY = float(r3c1GeometryActionDeck.get_widget("translate").entryBoxEditableLabel.get_text())
        translateZ = float(r4c1GeometryActionDeck.get_widget("translate").entryBoxEditableLabel.get_text())
        translation = [translateX, translateY, translateZ]

        """ Update D_finalPositions """
        self.__class__.D_finalPositions[self.__class__.selectedFileKey] = translation

        """ Apply delta translation to Trimesh STL """
        originalPosition = self.__class__.D_previousPositions[self.__class__.selectedFileKey]
        newPosition = self.__class__.D_finalPositions[self.__class__.selectedFileKey]
        Render_Model.D_stlMeshes[self.__class__.selectedFileKey].apply_translation(np.subtract(newPosition, originalPosition))  # Translate the STL

        """ Keep track of translation history for CTRL+Z purposes """
        self.__class__.D_previousPositions[self.__class__.selectedFileKey] = np.array(translation)
        self.__class__.D_positionHistory[self.__class__.selectedFileKey].append(self.__class__.D_previousPositions[self.__class__.selectedFileKey])
        self.__class__.L_actionHistory.append("translation")                                                    # Keep track of which action just occured
        self.__class__.L_translationHistory.append([self.__class__.selectedFileKey])

    def rotate_single_STL(self):
        """Define delta rotation matrix"""
        currentRotationMode = (r2c1GeometryActionDeck.get_widget("rotate").currentlyChecked)                    # Gets the axis (X, Y, or Z) that the user has checked for this rotation
        rotateEntryBoxFloat = (r3c1GeometryActionDeck.get_widget("rotate").entryBoxEditableLabel.get_text())    # Gets the raw text from the rotate entry box
        if rotateEntryBoxFloat == "":                                                                           # If there is no text in the box, default to 0.0
            rotateEntryBoxFloat = 0.0
        else:                                                                                                   # Otherwise, convert the raw text into a float
            rotateEntryBoxFloat = float(rotateEntryBoxFloat)

        if currentRotationMode == "X":
            deltaThetaX = (np.pi / 180.0) * rotateEntryBoxFloat
            deltaThetaY = 0.0
            deltaThetaZ = 0.0
            deltaRotation = trimesh.transformations.rotation_matrix(deltaThetaX, [1, 0, 0])
        elif currentRotationMode == "Y":
            deltaThetaX = 0.0
            deltaThetaY = (np.pi / 180.0) * rotateEntryBoxFloat
            deltaThetaZ = 0.0
            deltaRotation = trimesh.transformations.rotation_matrix(deltaThetaY, [0, 1, 0])
        elif currentRotationMode == "Z":
            deltaThetaX = 0.0
            deltaThetaY = 0.0
            deltaThetaZ = (np.pi / 180.0) * rotateEntryBoxFloat
            deltaRotation = trimesh.transformations.rotation_matrix(deltaThetaZ, [0, 0, 1])

        """ Translate to origin, rotate, then translate back """
        currentPositionToOrigin = -np.array(self.__class__.D_finalPositions[self.__class__.selectedFileKey])
        originToCurrentPosition = np.array(self.__class__.D_finalPositions[self.__class__.selectedFileKey])
        Render_Model.D_stlMeshes[self.__class__.selectedFileKey].apply_translation(currentPositionToOrigin)     # First translate the Trimesh STL back to origin before the rotation
        Render_Model.D_stlMeshes[self.__class__.selectedFileKey].apply_transform(deltaRotation)                 # Perform Trimesh rotation
        Render_Model.D_stlMeshes[self.__class__.selectedFileKey].apply_translation(originToCurrentPosition)     # Lastly, translate the Trimesh STL back to where it originally was

        """ Vertically shift STL so it sits on build surface after rotating """
        boundingBox = Render_Model.D_stlMeshes[self.__class__.selectedFileKey].bounds
        verticalShift = np.array([0.0, 0.0, -boundingBox[0][2]])                                                # Vertical shift needed for bottom of STL to sit on build surface after rotation
        self.__class__.D_finalPositions[self.__class__.selectedFileKey] += (verticalShift)                      # Update this mainly for OpenGL
        Render_Model.D_stlMeshes[self.__class__.selectedFileKey].apply_translation(verticalShift)               # Translate the Trimesh STL
        finalPosition = [self.__class__.D_finalPositions[self.__class__.selectedFileKey][0],self.__class__.D_finalPositions[self.__class__.selectedFileKey][1],self.__class__.D_finalPositions[self.__class__.selectedFileKey][2]]  # Referencing each index is required, or else D_previousPositions will always update to equal D_finalPositions whenever D_finalPositions changes

        """ Update D_finalRotations and D_previousRotations """
        previousRotation = self.__class__.D_previousRotations[self.__class__.selectedFileKey]
        finalRotation = np.matmul(deltaRotation, previousRotation)
        self.__class__.D_finalRotations[self.__class__.selectedFileKey] = (finalRotation)                       # Update D_finalRotations
        self.__class__.D_previousRotations[self.__class__.selectedFileKey] = (finalRotation)                    # Update D_previousRotations

        """ Keep track of rotation history for CTRL+Z purposes """
        self.__class__.D_orientationHistory[self.__class__.selectedFileKey].append(self.__class__.D_previousRotations[self.__class__.selectedFileKey])
        self.__class__.L_actionHistory.append("rotation")                                                       # Keep track of which action just occured
        self.__class__.L_rotationHistory.append([self.__class__.selectedFileKey])

        """ Keep track of translation history for CTRL+Z purposes """
        self.__class__.D_previousPositions[self.__class__.selectedFileKey] = np.array(finalPosition)            # Update D_previousPositions

        self.__class__.D_positionHistory[self.__class__.selectedFileKey].append(np.array(finalPosition))

    def scale_single_STL(self):
        """Define final scale factor"""
        scaleFactor = r2c1GeometryActionDeck.get_widget("scale").entryBoxEditableLabel.get_text()
        if scaleFactor == "":
            scaleFactor = 1.0
        else:
            scaleFactor = float(scaleFactor) / 100.0
        previousScaleFactor = self.__class__.D_previousScales[
            self.__class__.selectedFileKey
        ][0]
        finalScaleFactor = scaleFactor / previousScaleFactor

        """ Translate to origin, scale, then translate back after scaling """
        currentPositionToOrigin = -np.array(
            self.__class__.D_finalPositions[self.__class__.selectedFileKey]
        )
        originToCurrentPosition = np.array(
            self.__class__.D_finalPositions[self.__class__.selectedFileKey]
        )
        Render_Model.D_stlMeshes[self.__class__.selectedFileKey].apply_translation(
            currentPositionToOrigin
        )
        Render_Model.D_stlMeshes[self.__class__.selectedFileKey].apply_scale(
            finalScaleFactor
        )
        Render_Model.D_stlMeshes[self.__class__.selectedFileKey].apply_translation(
            originToCurrentPosition
        )

        """ Vertically shift STL so it sits on build surface after scaling """
        boundingBox = Render_Model.D_stlMeshes[self.__class__.selectedFileKey].bounds
        verticalShift = np.array(
            [0.0, 0.0, -boundingBox[0][2]]
        )                       # Vertical shift needed for bottom of STL to sit on build surface after scaling
        self.__class__.D_finalPositions[self.__class__.selectedFileKey] += (
            verticalShift       # Update this mainly for OpenGL
        )
        Render_Model.D_stlMeshes[self.__class__.selectedFileKey].apply_translation(
            verticalShift
        )                       # Translate the Trimesh STL
        finalPosition = [
            self.__class__.D_finalPositions[self.__class__.selectedFileKey][0],
            self.__class__.D_finalPositions[self.__class__.selectedFileKey][1],
            self.__class__.D_finalPositions[self.__class__.selectedFileKey][2],
        ]                       # Referencing each index is required, or else D_previousPositions will always update to equal D_finalPositions whenever D_finalPositions changes

        """ Update D_finalScales and D_previousScales """
        self.__class__.D_finalScales[self.__class__.selectedFileKey] = [
            scaleFactor,
            scaleFactor,
            scaleFactor,
        ]
        self.__class__.D_previousScales[self.__class__.selectedFileKey] = [
            scaleFactor,
            scaleFactor,
            scaleFactor,
        ]

        """ Keep track of scaling history for CTRL+Z purposes """
        self.__class__.D_sizeHistory[self.__class__.selectedFileKey].append(
            self.__class__.D_previousScales[self.__class__.selectedFileKey]
        )
        self.__class__.L_actionHistory.append(
            "scaling"
        )                       # Keep track of which action just occurred
        self.__class__.L_scalingHistory.append([self.__class__.selectedFileKey])

        """ Keep track of translation history for CTRL+Z purposes """
        self.__class__.D_previousPositions[self.__class__.selectedFileKey] = np.array(
            finalPosition
        )                       # Update D_previousPositions

        self.__class__.D_positionHistory[self.__class__.selectedFileKey].append(
            np.array(finalPosition)
        )

    @staticmethod
    def reset_widget_color():
        widgetResetColor = (1.0, 1.0, 1.0, 1.0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glColor4f(*widgetResetColor)

    @staticmethod
    def draw_cylinder(radius, height, slices, stacks, color):
        # Set the color
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glColor4f(*color)
        # Color is set
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        glPushMatrix()
        glTranslatef(0, 0, -height)                         # Move the cylinder so its bottom is at z = -height
        gluCylinder(quadric, radius, radius, height, slices, stacks)
        gluDisk(quadric, 0, radius, slices, 1)              # Draw the top disk
        glTranslatef(0, 0, height)
        gluDisk(quadric, 0, radius, slices, 1)              # Draw the bottom disk
        glPopMatrix()
        gluDeleteQuadric(quadric)
        # Define material properties for the cylinder
        cylinderMaterialDiffuse = (
            0.8,
            0.8,
            0.8,
            0.5,
        )                                                   # Set alpha to 0.5 for transparency
        cylinderMaterialAmbient = (
            0.2,
            0.2,
            0.2,
            0.5,
        )                                                   # Set alpha to 0.5 for transparency
        cylinderMaterialSpecular = (0.2, 0.2, 0.2, 0.5)     # Decreased specular reflection
        cylinderMaterialShininess = 10.0                    # Decreased shininess

        # Set material properties for the cylinder
        glMaterialfv(
            GL_FRONT_AND_BACK, GL_DIFFUSE, (GLfloat * 4)(*cylinderMaterialDiffuse)
        )
        glMaterialfv(
            GL_FRONT_AND_BACK, GL_AMBIENT, (GLfloat * 4)(*cylinderMaterialAmbient)
        )
        glMaterialfv(
            GL_FRONT_AND_BACK, GL_SPECULAR, (GLfloat * 4)(*cylinderMaterialSpecular)
        )
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, cylinderMaterialShininess)

    @staticmethod
    def is_cursor_over_widget(widget, x, y):
        widgetRect = widget.rect
        if (
            widgetRect.left <= x <= widgetRect.right
            and widgetRect.bottom <= y <= widgetRect.top
        ):
            return True
        else:
            return False

    def is_cursor_over_widgets(self, widgetList, x, y):
        hitList = [self.is_cursor_over_widget(widget, x, y) for widget in widgetList]
        if any(hitList):
            return True
        else:
            return False

    def on_key_press(self, symbol, modifiers):
        if symbol == key.A:  # CTRL + A
            if modifiers & pyglet.window.key.MOD_CTRL:
                if len(L_loadedIndices) == 1:
                    self.__class__.selectedFileKey = L_loadedIndices[0]
                    self.__class__.D_stlSelectStates[L_loadedIndices[0]] = True
                    self.multipleSelected = False
                else:
                    self.multipleSelected = True
                    for i in L_loadedIndices:  # Select all STLs
                        self.__class__.D_stlSelectStates[i] = True

        if symbol == key.Z:  # CTRL + Z
            if modifiers & pyglet.window.key.MOD_CTRL:
                hide_geometry_action_pop_up_window()
                if len(self.__class__.L_actionHistory) > 1:
                    lastAction = self.__class__.L_actionHistory[
                        -1
                    ]  # The geometry action that was just performed (Either translation, rotation, or scaling)
                    if lastAction == "translation":
                        if len(self.__class__.L_translationHistory) > 1:
                            lastMovedStls = self.__class__.L_translationHistory[-1]
                            for stlIndex in lastMovedStls:
                                if stlIndex in L_loadedIndices:
                                    # TRANSLATION:
                                    currentPosition = self.__class__.D_positionHistory[
                                        stlIndex
                                    ][-1]               # Current position of model
                                    lastPosition = self.__class__.D_positionHistory[
                                        stlIndex
                                    ][-2]               # Previous position of model
                                    self.translation = np.subtract(
                                        lastPosition, currentPosition
                                    )                   # Translation needed to restore position to last position
                                    Render_Model.D_stlMeshes[
                                        stlIndex
                                    ].apply_translation(
                                        self.translation
                                    )                   # Apply translation to Trimesh STL
                                    self.__class__.D_finalPositions[stlIndex] += (
                                        self.translation
                                    )                   # Update finalPositions
                                    self.__class__.D_previousPositions[stlIndex] = (
                                        lastPosition    # Update the previousPosition of this STL as the restored position
                                    )
                                    self.__class__.D_positionHistory[stlIndex].pop(
                                        -1
                                    )                   # Remove the original position of the model from its position history
                            self.__class__.L_translationHistory.pop(-1)
                    elif lastAction == "rotation":
                        if len(self.__class__.L_rotationHistory) > 1:
                            lastRotatedStls = self.__class__.L_rotationHistory[
                                -1
                            ]                           # For now, the user can only rotate one STL at a time, but this is set up to allow undoing rotations of multiple STLs in the future
                            for stlIndex in lastRotatedStls:
                                if stlIndex in L_loadedIndices:
                                    # ROTATION

                                    """ Translate to origin, rotate, then translate back """
                                    currentPositionToOrigin = -np.array(
                                        self.__class__.D_finalPositions[stlIndex]
                                    )
                                    originToCurrentPosition = np.array(
                                        self.__class__.D_finalPositions[stlIndex]
                                    )
                                    Render_Model.D_stlMeshes[
                                        stlIndex
                                    ].apply_translation(
                                        currentPositionToOrigin
                                    )                   # First translate the Trimesh STL back to origin before the rotation
                                    currentOrientation = (
                                        self.__class__.D_orientationHistory[stlIndex][
                                            -1
                                        ]
                                    )                   # Current orientation of model
                                    lastOrientation = (
                                        self.__class__.D_orientationHistory[stlIndex][
                                            -2
                                        ]
                                    )                   # Previous orientation of model
                                    inverseDeltaRotation = np.linalg.inv(
                                        np.dot(
                                            currentOrientation,
                                            np.linalg.inv(lastOrientation),
                                        )
                                    )                   # Rotation needed to revert to last orientation
                                    Render_Model.D_stlMeshes[stlIndex].apply_transform(
                                        inverseDeltaRotation
                                    )                   # Apply rotation to Trimesh STL
                                    self.__class__.D_finalRotations[stlIndex] = (
                                        lastOrientation  # Update finalRotations
                                    )
                                    self.__class__.D_previousRotations[stlIndex] = (
                                        lastOrientation  # Update previousRotations
                                    )
                                    self.__class__.D_orientationHistory[stlIndex].pop(
                                        -1
                                    )                   # Remove original orientation from its history
                                    Render_Model.D_stlMeshes[
                                        stlIndex
                                    ].apply_translation(
                                        originToCurrentPosition
                                    )                   # Lastly, translate the Trimesh STL back to where it originally was

                                    """ Shift the STL back to original position before rotating """
                                    currentPosition = self.__class__.D_positionHistory[
                                        stlIndex
                                    ][-1]
                                    lastPosition = self.__class__.D_positionHistory[
                                        stlIndex
                                    ][-2]
                                    translation = np.subtract(
                                        lastPosition, currentPosition
                                    )                   # Translation needed to revert to previous position
                                    Render_Model.D_stlMeshes[
                                        stlIndex
                                    ].apply_translation(
                                        translation
                                    )                   # Apply translation to Trimesh STL
                                    self.__class__.D_finalPositions[stlIndex] += (
                                        translation     # Update finalPositions
                                    )
                                    self.__class__.D_previousPositions[stlIndex] = (
                                        lastPosition    # Update previousPositions
                                    )
                                    self.__class__.D_positionHistory[stlIndex].pop(
                                        -1
                                    )                   # Remove currentPosition from positionHistory

                            self.__class__.L_rotationHistory.pop(
                                -1
                            )                           # Remove the last rotation from rotationHistory
                    elif lastAction == "scaling":
                        if len(self.__class__.L_scalingHistory) > 1:
                            lastScaledStls = self.__class__.L_scalingHistory[-1]
                            for stlIndex in lastScaledStls:
                                if stlIndex in L_loadedIndices:
                                    # SCALING

                                    """ Translate to origin, scale, then translate back """
                                    currentPositionToOrigin = -np.array(
                                        self.__class__.D_finalPositions[stlIndex]
                                    )
                                    originToCurrentPosition = np.array(
                                        self.__class__.D_finalPositions[stlIndex]
                                    )
                                    Render_Model.D_stlMeshes[
                                        stlIndex
                                    ].apply_translation(
                                        currentPositionToOrigin
                                    )                   # First translate the Trimesh STL back to origin before the scaling
                                    currentSize = self.__class__.D_sizeHistory[
                                        stlIndex
                                    ][-1][0]
                                    lastSize = self.__class__.D_sizeHistory[stlIndex][
                                        -2
                                    ][0]
                                    scale = (
                                        lastSize / currentSize
                                    )                   # Scaling needed to return STL to its previous size
                                    Render_Model.D_stlMeshes[stlIndex].apply_scale(
                                        scale
                                    )                   # Apply scaling to Trimesh STL
                                    self.__class__.D_finalScales[stlIndex] = [
                                        lastSize,
                                        lastSize,
                                        lastSize,
                                    ]                   # Update finalScales
                                    self.__class__.D_previousScales[stlIndex] = [
                                        lastSize,
                                        lastSize,
                                        lastSize,
                                    ]                   # Update previousScales
                                    self.__class__.D_sizeHistory[stlIndex].pop(
                                        -1
                                    )                   # Remove the original size from its history
                                    Render_Model.D_stlMeshes[
                                        stlIndex
                                    ].apply_translation(
                                        originToCurrentPosition
                                    )                   # Lastly, translate the Trimesh STL back to its original position

                                    """ Shift the STL back to original position before scaling """
                                    currentPosition = self.__class__.D_positionHistory[
                                        stlIndex
                                    ][-1]
                                    lastPosition = self.__class__.D_positionHistory[
                                        stlIndex
                                    ][-2]
                                    translation = np.subtract(
                                        lastPosition, currentPosition
                                    )                   # Translation needed to revert to previous position
                                    Render_Model.D_stlMeshes[
                                        stlIndex
                                    ].apply_translation(
                                        translation
                                    )                   # Apply translation to Trimesh STL
                                    self.__class__.D_finalPositions[stlIndex] += (
                                        translation     # Update finalPositions
                                    )
                                    self.__class__.D_previousPositions[stlIndex] = (
                                        lastPosition    # Update previousPositions
                                    )
                                    self.__class__.D_positionHistory[stlIndex].pop(
                                        -1
                                    )                   # Remove currentPosition from positionHistory

                            self.__class__.L_scalingHistory.pop(-1)

                    self.__class__.L_actionHistory.pop(-1)

        if symbol == key.DELETE or symbol == key.BACKSPACE:
            loadedIndices = list(self.__class__.D_stlSelectStates.keys())
            for k in loadedIndices:                     # For each loaded STL object
                state = self.__class__.D_stlSelectStates[k]
                if (
                    state == True
                ):                                      # If the STL object is selected by the user, delete it from relevant variables
                    self.__class__.selectedFileKey = None
                    del B_selectFile.D_variables[k]
                    del self.Render_Model.D_stlVbos[k]
                    del self.Render_Model.D_stlDepths[k]
                    del self.Render_Model.D_stlMeshes[k]
                    L_loadedIndices.remove(k)
                    del self.__class__.D_finalPositions[k]
                    del self.__class__.D_finalRotations[k]
                    del self.__class__.D_finalScales[k]
                    self.__class__.L_translationHistory[0].remove(k)
                    self.__class__.L_rotationHistory[0].remove(k)
                    self.__class__.L_scalingHistory[0].remove(k)
                    self.__class__.L_actionHistory[0].remove(k)
                    del self.__class__.D_stlSelectStates[k]
                    del self.__class__.D_previousPositions[k]
                    del self.__class__.D_previousRotations[k]
                    del self.__class__.D_previousScales[k]

                    del self.__class__.D_positionHistory[k]
                    del self.__class__.D_orientationHistory[k]
                    del self.__class__.D_sizeHistory[k]
                    del self.__class__.D_axisRotationHistory[k]

                    del self.__class__.D_renderedToolpaths[k]

        if symbol == key.ESCAPE:
            self.multipleSelected = False
            for i in L_loadedIndices:               # Deselect all STLs
                self.__class__.D_stlSelectStates[i] = False
                self.__class__.selectedFileKey = None
                hide_geometry_action_pop_up_window()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.ENTER:
            if len(L_loadedIndices) >= 1 and self.__class__.selectedFileKey is not None:
                popUpBoxState = r0GeometryActionDeck.get_state()
                # Perform transformations
                if (
                    popUpBoxState == "translate"
                ):                                  # If the user is entering into the geometry action pop up box for translation and there are STLs loaded
                    self.translate_single_STL()
                elif popUpBoxState == "rotate":
                    self.rotate_single_STL()
                elif popUpBoxState == "scale":
                    self.scale_single_STL()

    def on_mouse_press(self, x, y, button, modifiers):
        currentViewMode = R_viewMode.currentlyChecked
        if currentViewMode == "Preview":            # Don't allow user to interact with STL's in Preview mode
            return
        if button == mouse.LEFT:                    # If left button is clicked
            rayOrigin, rayDirection = self.User_Interaction.get_ray_from_mouse(
                x, y, self.projectionMatrix, self.modelViewMatrix, self.viewportMatrix
            )                                       # Get the mouse ray
            ctrlPressed = modifiers & pyglet.window.key.MOD_CTRL
            self.anySelected = False
            closestMeshIndex = None
            closestDistance = float("inf")
            for k in L_loadedIndices:               # For each loaded STL mesh:
                clickResult, distance = self.User_Interaction.ray_intersects_mesh(
                    rayOrigin, rayDirection, Render_Model.D_stlMeshes[k]
                )                                   # See if the mouse ray intersects the mesh
                if (
                    clickResult > 0 and distance < closestDistance
                ):                                  # The user clicked on an STL and it's the closest one so far
                    self.anySelected = True
                    closestDistance = distance
                    closestMeshIndex = k

            if closestMeshIndex is not None:
                if (
                    self.multipleSelected and not ctrlPressed
                ):                                  # If (CTRL+A) was recently used to select all STLs and CTRL is not currently pressed
                    self.multipleSelected = False
                    self.__class__.D_stlSelectStates[closestMeshIndex] = True
                elif ctrlPressed:                   # If CTRL is pressed:
                    self.multipleSelected = True
                    self.__class__.D_stlSelectStates[
                        closestMeshIndex
                    ] = not self.__class__.D_stlSelectStates[
                        closestMeshIndex
                    ]                               # Toggle state of current STL

                else:                               # If CTRL is not pressed and (CTRL+A) was not recently used
                    for i in L_loadedIndices:       # Deselect all STLs
                        self.__class__.D_stlSelectStates[i] = False
                    self.__class__.D_stlSelectStates[closestMeshIndex] = (
                        True                        # Select only the current STL
                    )

                self.lastMousePosition = (x, y)
                intersectionHit, self.lastIntersectionPoint = (
                    self.User_Interaction.ray_intersects_xy_plane(
                        rayOrigin, rayDirection, planeZ=0
                    )
                )
                if (
                    intersectionHit and self.lastIntersectionPoint is not None
                ):                                  # If the mouse ray intersected the XY plane:
                    self.dragging = True
                else:
                    self.dragging = False

            if (
                not self.anySelected and not ctrlPressed
            ):                                      # If no STLs are selected and CTRL is not pressed:
                self.multipleSelected = False
                for i in L_loadedIndices:           # Deselect all STLs
                    self.__class__.D_stlSelectStates[i] = False

            if (self.is_cursor_over_widgets([R_geometryAction, geometryActionBackgroundDeck, settingsBoard], x, y) == False):
                self.__class__.selectedFileKey = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        global cameraAngleX, cameraAngleY, lookPositionX, lookPositionY
        if buttons & mouse.RIGHT:                   # Camera rotation
            self.Camera.cameraAngleX += dx * self.Camera.rotateSensitivity
            self.Camera.cameraAngleY -= dy * self.Camera.rotateSensitivity

        if buttons & mouse.MIDDLE:                  # Camera panning
            self.Camera.lookPositionX += dx * self.Camera.panningSensitivity
            self.Camera.lookPositionY += dy * self.Camera.panningSensitivity

        if buttons & mouse.LEFT:                    # Perform action (Like Translate)
            if self.dragging == True:
                rayOrigin, rayDirection = self.User_Interaction.get_ray_from_mouse(
                    x,
                    y,
                    self.projectionMatrix,
                    self.modelViewMatrix,
                    self.viewportMatrix,
                )                                   # Get the mouse ray
                intersectionHit, currentIntersectionPoint = (
                    self.User_Interaction.ray_intersects_xy_plane(
                        rayOrigin, rayDirection
                    )
                )                                   # See if ray intersects XY plane, and get intersection coords

                if (
                    intersectionHit and currentIntersectionPoint is not None
                ):                                  # If the mouse ray intersected the XY plane:
                    self.translation = (
                        currentIntersectionPoint - self.lastIntersectionPoint
                    )                               # The translation is the current intersection point minus the last one
                    self.lastIntersectionPoint = currentIntersectionPoint
                    self.lastMousePosition = (x, y)
                    self.doneTranslating = False
                    for k in L_loadedIndices:
                        if self.__class__.D_stlSelectStates[k] == True:
                            self.__class__.D_finalPositions[k] += (
                                self.translation
                            )                       # Accumulate the translations to get the final positions

    def on_mouse_release(self, x, y, button, modifiers):
        def updateSettings():
            if r5c1SettingsDeck.get_widget("movement").is_checked: # If retraction is enabled, make retraction options visible
                r6c0MovementDeck.set_state("enabled")
                r6c1MovementDeck.set_state("enabled")
                r7c0MovementDeck.set_state("enabled")
                r7c1MovementDeck.set_state("enabled")
            else:
                r6c0MovementDeck.set_state("disabled")
                r6c1MovementDeck.set_state("disabled")
                r7c0MovementDeck.set_state("disabled")
                r7c1MovementDeck.set_state("disabled")
                
        updateSettings()
        
        if button == mouse.LEFT:
            self.dragging = False
            self.lastMousePosition = None
            self.lastIntersectionPoint = None
            if self.doneTranslating == False:
                movedStls = []
                for selectedIndex in L_loadedIndices:
                    if self.__class__.D_stlSelectStates[selectedIndex] == True:
                        Render_Model.D_stlMeshes[selectedIndex].apply_translation(
                            np.subtract(
                                self.__class__.D_finalPositions[selectedIndex],
                                self.__class__.D_previousPositions[selectedIndex],
                            )
                        )                           # The trimesh STL values save their new positions, unlike OpenGL renderings

                        finalPosition = [
                            self.__class__.D_finalPositions[selectedIndex][0],
                            self.__class__.D_finalPositions[selectedIndex][1],
                            self.__class__.D_finalPositions[selectedIndex][2],
                        ]                           # Referencing each index is required, or else D_previousPositions will always update to equal D_finalPositions whenever D_finalPositions changes
                        self.__class__.D_previousPositions[selectedIndex] = (
                            finalPosition
                        )
                        self.__class__.D_positionHistory[selectedIndex].append(
                            self.__class__.D_previousPositions[selectedIndex]
                        )
                        movedStls.append(selectedIndex)
                self.__class__.L_actionHistory.append(
                    "translation"
                )                                   # Keep track of which geometry action just occured
                self.__class__.L_translationHistory.append(movedStls)
            self.doneTranslating = True

            self.manage_geometry_action_pop_up_accessibility()

            popUpBoxState = r0GeometryActionDeck.get_state()

            if popUpBoxState != "translate":
                self.updateTranslateText = True

            if (
                popUpBoxState == "translate"
                and self.__class__.selectedFileKey is not None
                and self.updateTranslateText == True
            ):                                      # If the user has selected an STL and the translate pop up box is open, update the textboxes
                self.update_geometry_action_variables(self.__class__.selectedFileKey)
                self.updateTranslateText = False

            if (
                popUpBoxState == "rotate"
                and self.is_cursor_over_widget(
                    r2c1GeometryActionDeck.get_widget("rotate"), x, y
                )
            ):                                      # If the user clicked on the rotate radio buttons, update the value of the rotation entry box
                currentRotationMode = r2c1GeometryActionDeck.get_widget(
                    "rotate"
                ).currentlyChecked
                previousRotationMode = self.__class__.D_axisRotationHistory[
                    self.__class__.selectedFileKey
                ]

                if currentRotationMode == previousRotationMode:
                    pass
                else:
                    r3c1GeometryActionDeck.get_widget(
                        "rotate"
                    ).entryBoxEditableLabel.set_text("0.0")

                self.__class__.D_axisRotationHistory[self.__class__.selectedFileKey] = (
                    currentRotationMode
                )

            if popUpBoxState == "rotate" and self.is_cursor_over_widget(
                r4c1GeometryActionDeck.get_widget("rotate"), x, y
            ):                                      # If the user clicked the apply rotation button, rotate the STL
                self.rotate_single_STL()

            if popUpBoxState == "scale" and self.is_cursor_over_widget(
                r3c1GeometryActionDeck.get_widget("scale"), x, y
            ):                                      # If the user clicked the apply scale button, scale the STL
                self.scale_single_STL()

    def manage_geometry_action_pop_up_accessibility(self):
        if len(L_loadedIndices) > 0:                # If there are any STLs loaded
            L_selectedStates = [
                self.__class__.D_stlSelectStates[key]
                for key in self.__class__.D_stlSelectStates
                if len(self.__class__.D_stlSelectStates) > 0
            ]                                       # List of selected states (Just used to see if any STLs are selected)
            if any(L_selectedStates) == True:       # If any STLs have been selected
                selectedFileKeys = [
                    key
                    for key in self.__class__.D_stlSelectStates
                    if self.__class__.D_stlSelectStates[key] == True
                ]
                if (
                    len(L_loadedIndices) == 1 or self.multipleSelected == False
                ):                                  # If only one STL is selected, populate the geometry action pop up box
                    self.__class__.selectedFileKey = selectedFileKeys[0]
                    self.__class__.D_stlSelectStates[self.__class__.selectedFileKey] = (
                        True
                    )
                    self.update_geometry_action_variables(
                        self.__class__.selectedFileKey
                    )
                elif (
                    self.multipleSelected == True
                ):                                  # If multiple STLs are selected, hide the geometry action pop up box
                    self.__class__.selectedFileKey = None
                    hide_geometry_action_pop_up_window()
            elif (
                all(L_selectedStates) == False
                and self.__class__.selectedFileKey == None
            ):                                      # If no STLs are selected, keep the geometry action pop up box hidden
                hide_geometry_action_pop_up_window()
                currentState = R_geometryAction.currentlyChecked
                if currentState == "Translate":
                    R_geometryAction.organizer.get_children()[0].toggle()
                elif currentState == "Rotate":
                    R_geometryAction.organizer.get_children()[1].toggle()
                elif currentState == "Scale":
                    R_geometryAction.organizer.get_children()[2].toggle()
                R_geometryAction.currentlyChecked = "deactivated"
        elif (
            len(L_loadedIndices) == 0
        ):                                          # If no STLs have been loaded in, don't allow the user to use R_geometryAction
            hide_geometry_action_pop_up_window()
            currentState = R_geometryAction.currentlyChecked
            if currentState == "Translate":
                R_geometryAction.organizer.get_children()[0].toggle()
            elif currentState == "Rotate":
                R_geometryAction.organizer.get_children()[1].toggle()
            elif currentState == "Scale":
                R_geometryAction.organizer.get_children()[2].toggle()
            R_geometryAction.currentlyChecked = "deactivated"

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):  # Camera zooming
        self.Camera.cameraDistance -= scroll_y * self.Camera.scrollSensitivity
        if self.Camera.cameraDistance > 950:
            self.Camera.cameraDistance = 950
        elif self.Camera.cameraDistance < 0:
            self.Camera.cameraDistance = 0


""" Render_Model Class """
class Render_Model:
    # Class variables:
    D_stlVbos = {}
    D_stlDepths = {}
    D_stlMeshes = {}

    def __init__(self):
        self.stlMesh = None
        self.alpha = 0.7
        self.beta = 1.0
        self.selectedColor = (64.0 / 255.0, 224.0 / 255.0, 208.0 / 255.0, self.alpha)
        self.unselectedColor = (0.0, 250.0 / 255.0, 154.0 / 255.0, self.beta)

    @staticmethod
    def numpy_to_ctypes(array, ctype):
        return (ctype * len(array))(*array.flatten())

    def load_stl(self, index, stlFilePath):
        vertexVbo = GLuint()
        normalVbo = GLuint()
        indexVbo = GLuint()
        self.stlMesh = trimesh.load_mesh(stlFilePath)
        self.__class__.D_stlMeshes[index] = self.stlMesh
        if not self.stlMesh.is_watertight:
            self.stlMesh.fix_normals()

        # Get the width of the STL:
        boundingBox = self.stlMesh.bounds
        spanX = boundingBox[1][0] - boundingBox[0][0]
        spanY = boundingBox[1][1] - boundingBox[0][1]
        self.__class__.D_stlDepths[index] = spanY

        # Center the STL on the origin and adjust altitude to sit on build plate before getting vertices
        centerShiftX = boundingBox[0][0] + (spanX / 2.0)
        centerShiftY = boundingBox[0][1] + (spanY / 2.0)
        bottomShiftZ = boundingBox[0][2]
        self.stlMesh.apply_translation([-centerShiftX, -centerShiftY, -bottomShiftZ])

        vertices = np.array(self.stlMesh.vertices, dtype="f").flatten()
        normals = np.array(self.stlMesh.vertex_normals, dtype="f").flatten()
        indices = np.array(self.stlMesh.faces.flatten(), dtype="uint32")

        # Convert numpy arrays to ctypes arrays
        verticesCtypes = self.numpy_to_ctypes(vertices, c_float)
        normalsCtypes = self.numpy_to_ctypes(normals, c_float)
        indicesCtypes = self.numpy_to_ctypes(indices, c_uint)
        # Generate and bind vertex VBO
        glGenBuffers(1, byref(vertexVbo))
        glBindBuffer(GL_ARRAY_BUFFER, vertexVbo)
        glBufferData(
            GL_ARRAY_BUFFER, len(verticesCtypes) * 4, verticesCtypes, GL_STATIC_DRAW
        )
        # Generate and bind normal VBO
        glGenBuffers(1, byref(normalVbo))
        glBindBuffer(GL_ARRAY_BUFFER, normalVbo)
        glBufferData(
            GL_ARRAY_BUFFER, len(normalsCtypes) * 4, normalsCtypes, GL_STATIC_DRAW
        )
        # Generate and bind index VBO
        glGenBuffers(1, byref(indexVbo))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexVbo)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            len(indicesCtypes) * 4,
            indicesCtypes,
            GL_STATIC_DRAW,
        )

        # Append the VBOs to the list
        self.__class__.D_stlVbos[index] = (
            vertexVbo,
            normalVbo,
            indexVbo,
            len(indicesCtypes),
        )

    @staticmethod
    def set_model_color(color):
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glColor4f(*color)

    def draw_stl_model(self, index, stlFilePath):
        stlVbo = self.__class__.D_stlVbos[index]
        vertexVbo = stlVbo[0]
        normalVbo = stlVbo[1]
        indexVbo = stlVbo[2]
        indexCount = stlVbo[3]

        # Enable vertex and normal arrays
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        # Bind vertex VBO
        glBindBuffer(GL_ARRAY_BUFFER, vertexVbo)            # Bind Vertices
        glVertexPointer(3, GL_FLOAT, 0, None)

        # Bind normal VBO
        glBindBuffer(GL_ARRAY_BUFFER, normalVbo)            # Bind Normals
        glNormalPointer(GL_FLOAT, 0, None)

        # Bind index VBO and draw
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexVbo)     # Bind Indices

        # Apply separate transformations for each model to avoid overlap
        glPushMatrix()

        glMultMatrixf((GLfloat * 16)(*Graphics_Window.D_finalRotations[index].T.flatten()))  # Rotation

        toFinalPosition = np.matmul(np.linalg.inv(Graphics_Window.D_finalRotations[index][:3, :3]), Graphics_Window.D_finalPositions[index])  # Translation
        glTranslatef(*toFinalPosition)

        glScalef(*Graphics_Window.D_finalScales[index])     # Scale

        # Set color and transparency based on selection state
        if (Graphics_Window.D_stlSelectStates[index] == True or index == Graphics_Window.selectedFileKey):
            colorTuple = self.selectedColor
        else:
            colorTuple = self.unselectedColor
        self.set_model_color(colorTuple)

        glDrawElements(GL_TRIANGLES, indexCount, GL_UNSIGNED_INT, None)
        glPopMatrix()

        # Disable vertex and normal arrays
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)


""" Render_Preview Class"""
class Render_Preview:
    def __init__(self):
        self.path_vbos = {}  # Dictionary to store VBOs for different paths

    def clear_toolpath_vbos(self):
        # Delete all stored VBOs
        for vbo_data in self.path_vbos.values():
            vbo, _ = vbo_data
            glDeleteBuffers(1, byref(vbo))
        
        # Clear the dictionary
        self.path_vbos.clear()


    def create_vbo_for_segments(self, segments):
        # Create VBO for vertices
        vbo = GLuint()
        glGenBuffers(1, byref(vbo))
        
        # Convert segments to flat array of vertices
        vertices = np.array(segments, dtype='float32').flatten()
        vertices_ctype = (GLfloat * len(vertices))(*vertices)
        
        # Bind and upload data to VBO
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, sizeof(vertices_ctype), vertices_ctype, GL_STATIC_DRAW)
        
        return vbo, len(vertices) // 3  # Number of vertices (2 per line segment)

    def draw_toolpaths(self, segments, color):
        # Create VBO if not already created for these segments
        segment_key = hash(str(segments))  # Create unique key for these segments
        if segment_key not in self.path_vbos:
            self.path_vbos[segment_key] = self.create_vbo_for_segments(segments)
            
        vbo, vertex_count = self.path_vbos[segment_key]
        
        # Set color
        glColor4f(*color)
        
        # Enable vertex arrays
        glEnableClientState(GL_VERTEX_ARRAY)
        
        # Bind VBO and set up vertex pointer
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        
        # Draw the lines
        glDrawArrays(GL_LINES, 0, vertex_count)
        
        # Clean up
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw_toolpaths_from_stored(self, vbo_data, color):
        vbo, vertex_count = vbo_data
        
        glColor4f(*color)
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawArrays(GL_LINES, 0, vertex_count)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

class Render_SlicePlanes:
    def __init__(self):
        self.current_vbo = None
        self.colors = self.generate_biv_gradient(20) # Create 20 separate RGB values

    def cleanup_current_vbo(self):
        if self.current_vbo is not None:
            vbo, _ = self.current_vbo
            glDeleteBuffers(1, byref(vbo))
            self.current_vbo = None

    def define_slicePlane(self, startX, startY, startZ, theta, phi, radius=50.0, segments=32):
        # Convert spherical coordinates (theta, phi) to Cartesian (normal vector)
        self.cleanup_current_vbo()

        theta = theta*(np.pi/180.0)
        phi = phi*(np.pi/180.0)
        
        nx = np.sin(theta) * np.cos(phi)
        ny = np.sin(theta) * np.sin(phi)
        nz = np.cos(theta)
        normal = np.array([nx, ny, nz])
        
        # Create basis vectors for the plane
        v1 = np.cross(normal, np.array([0, 0, 1]))
        if np.all(v1 == 0):
            v1 = np.array([1, 0, 0])
        v1 = v1 / np.linalg.norm(v1)
        v2 = np.cross(normal, v1)
        v2 = v2 / np.linalg.norm(v2)
        
        # Generate vertices for a circle
        vertices = []
        # Add center point
        vertices.extend([startX, startY, startZ])
        
        # Add vertices around the circle
        for i in range(segments + 1):
            angle = 2 * np.pi * i / segments
            x = startX + radius * (v1[0] * np.cos(angle) + v2[0] * np.sin(angle))
            y = startY + radius * (v1[1] * np.cos(angle) + v2[1] * np.sin(angle))
            z = startZ + radius * (v1[2] * np.cos(angle) + v2[2] * np.sin(angle))
            vertices.extend([x, y, z])
        
        # Create and setup VBO
        vbo = GLuint()
        glGenBuffers(1, byref(vbo))
        vertices_array = np.array(vertices, dtype='float32')
        vertices_ctype = (GLfloat * len(vertices))(*vertices)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, sizeof(vertices_ctype), vertices_ctype, GL_STATIC_DRAW)

        self.current_vbo = (vbo, len(vertices) // 3)
        return self.current_vbo

    def draw_plane(self, vbo_data, color=(0.5, 0.5, 0.8, 0.3)):
        # Save current OpenGL state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Draw the plane
        vbo, vertex_count = vbo_data
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*color)
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawArrays(GL_TRIANGLE_FAN, 0, vertex_count)
        
        # Restore previous OpenGL state
        glPopAttrib()
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableClientState(GL_VERTEX_ARRAY)

    def generate_biv_gradient(self, k):
        # Define RGB values for ROYGBIV colors
        biv = [
            [0, 0, 255],    # Blue
            [75, 0, 130],   # Indigo
            [148, 0, 211]   # Violet
        ]
        
        # Calculate the step size along the full spectrum
        n_colors = len(biv)
        total_segments = n_colors - 1
        
        # Generate k evenly spaced points
        result = []
        for i in range(1, k+1):
            # Position along the spectrum from 0 to 1
            pos = (i - 1) / (k - 1) if k > 1 else 0
            
            # Find which segment this position falls into
            segment_idx = min(int(pos * total_segments), total_segments - 1)
            
            # Calculate position within this segment (0 to 1)
            segment_pos = (pos * total_segments) - segment_idx
            
            # Get the two colors to interpolate between
            color1 = biv[segment_idx]
            color2 = biv[segment_idx + 1]
            
            # Linear interpolation between the two colors
            r = int(color1[0] + segment_pos * (color2[0] - color1[0]))
            g = int(color1[1] + segment_pos * (color2[1] - color1[1]))
            b = int(color1[2] + segment_pos * (color2[2] - color1[2]))
            
            result.append([r, g, b])
        return result

""" User_Interaction Class """
class User_Interaction:
    def __init__(self):
        pass

    @staticmethod
    def get_ray_from_mouse(x, y, projection, modelview, viewport):
        """Calculate the ray from the mouse position."""

        # Convert the mouse position to normalized device coordinates
        winX = c_double(float(x))
        winY = c_double(float(y))
        winZNear = c_double(0.0)
        winZFar = c_double(1.0)

        # Get the near and far points in world coordinates
        nearX = c_double(0.0)
        nearY = c_double(0.0)
        nearZ = c_double(0.0)

        farX = c_double(0.0)
        farY = c_double(0.0)
        farZ = c_double(0.0)

        gluUnProject(
            winX, winY, winZNear, modelview, projection, viewport, nearX, nearY, nearZ
        )
        gluUnProject(
            winX, winY, winZFar, modelview, projection, viewport, farX, farY, farZ
        )

        # Return the ray origin (camera position) and direction
        rayOrigin = np.array([nearX.value, nearY.value, nearZ.value])
        rayDirection = np.array([farX.value, farY.value, farZ.value]) - rayOrigin
        rayDirection /= np.linalg.norm(rayDirection)
        return rayOrigin, rayDirection

    @staticmethod
    def ray_intersects_mesh(rayOrigin, rayDirection, mesh):
        """Check if the ray intersects the mesh."""
        locations, indexRay, indexTri = mesh.ray.intersects_location(
            ray_origins=[rayOrigin], ray_directions=[rayDirection]
        )

        if len(locations) > 0:
            # Calculate the distances from the ray origin to the intersection points
            distances = np.linalg.norm(locations - rayOrigin, axis=1)
            closestDistance = np.min(distances)
            return len(locations), closestDistance

        return 0, float("inf")  # No intersection

    @staticmethod
    def ray_intersects_xy_plane(rayOrigin, rayDirection, planeZ=0):
        if rayDirection[2] == 0:  # If the ray doesn't intersect the XY plane
            return False, None
        t = (planeZ - rayOrigin[2]) / rayDirection[
            2
        ]  # Distance between camera and XY plane
        if t < 0:
            return False, None
        intersectionPoint = rayOrigin + t * rayDirection
        return True, intersectionPoint


# Main function
def main():
    win = Graphics_Window(width=1080, height=720, resizable=True, caption="3D STL Viewer")  # Instantiate the custom defined pyglet window class, Graphics_Window

    original_resize = win.on_resize

    def custom_resize(width, height):
        original_resize(width, height)
        cycle_decks(width, height)

    win.on_resize = custom_resize

    initialize_all_widgets(win.gui, win.windowHeight)  # Adds all default widgets to the screen

    pyglet.app.run()                                    # Run the pyglet main loop


if __name__ == "__main__":
    main()  # Call the main function
