# PyGLViewer

A Python-based 3D Viewer & GUI.

## Overview
PyGLViewer handles the boilerplate code of OpenGL, GLFW, and ImGui, to allow you to quickly build 3D applications.
It includes:
- OpenGL 3.3+ context creation and management
- GLFW window setup and event handling
- ImGui setup and rendering pipeline
- Camera system (orbit, pan, zoom) implementation
- Pre-configured shader system with lighting

## Controls
- Left/middle click + drag: Rotate camera
- Ctrl + left/middle click + drag: Pan camera
- Scroll wheel: Zoom in/out
- WASD: Move camera
- ESC: Exit application

## Installation Instructions

### 1. Install Visual C++ Build Tools
- Download from: [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Select "Desktop development with C++" 

### 2. Install Required Packages
   pip install PyOpenGL
   pip install PyOpenGL_accelerate  # optional
   pip install glfw
   pip install imgui[glfw]

### 3. For ImGui Docking Branch (Alternative)
   git clone --recurse-submodules https://github.com/pyimgui/pyimgui.git
   cd pyimgui
   git checkout docking
   pip install .[glfw]

### 4. ImGui Intellisense (Optional)
   - Download from: https://github.com/masc-it/pyimgui-interface-generator/blob/master/imgui.pyi
   - Save to: AppData\Roaming\Python\Python312\site-packages\imgui\__init__.pyi 
