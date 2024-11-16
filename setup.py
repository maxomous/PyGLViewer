from setuptools import setup, find_packages

setup(
    name="pyglviewer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pyopengl",
        "glfw",
        "glfw-accelerate",
        "imgui[glfw]",
    ],
    extras_require={
        'accelerated': [
            'glfw-accelerate',
        ],
    },
    author="Max Peglar-Willis",
    author_email="m.s.peglar@gmail.com",
    description="A 3D visualization framework using OpenGL and ImGui",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/maxomous/pyglviewer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 