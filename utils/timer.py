import glfw
# TODO: Replace with Imgui
class Timer:
    """Simple timer for tracking frame times using GLFW."""
    
    def __init__(self):
        """Initialize timer with current GLFW time."""
        self.previous = glfw.get_time()
        self.current = glfw.get_time()
        self.dt = 0.0

    def update(self):
        """Update timer and calculate delta time between frames."""
        self.current = glfw.get_time()
        self.dt = self.current - self.previous
        self.previous = self.current
