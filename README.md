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
- Left click: Select object (2D mode only)
- ESC: Exit application

## Installation Instructions

### 1. Install Visual C++ Build Tools
- Download from: [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Select "Desktop development with C++" 

### 2. Install PyGLViewer
```bash
pip install git+https://github.com/maxomous/pyglviewer.git
```

#### Note: It installs the following packages:
```bash
- numpy
- PyOpenGL
- PyOpenGL_accelerate  # optional 
- glfw
- imgui[glfw]
```

### 3. For ImGui Docking Branch (Alternative)
```bash
git clone --recurse-submodules https://github.com/pyimgui/pyimgui.git
cd pyimgui
git checkout docking
pip install .[glfw]
```

### 4. ImGui Intellisense (Optional)
ImGui documentation: https://pyimgui.readthedocs.io/en/latest/reference/imgui.core.html
Intellisense is not included in the current version of the 'imgui' due to it being a port from C++, you can manually add it by:
- Copy file: imgui_descriptions\__init__.pyi (Or download from: https://github.com/masc-it/pyimgui-interface-generator/blob/master/imgui.pyi)
- Save to: AppData\Roaming\Python\Python312\site-packages\imgui\__init__.pyi 

## Usage
See the [examples](examples) folder for usage examples.
- `example_2d.py` gives a simple example of how to use the library in 2D.
- `example_3d.py` gives a more complete example of how to use the library in both 2D and 3D.
