import glfw

class Timer:
    def __init__(self):
        self.previous_time = glfw.get_time()
        self.delta_time = 0.0

    def update(self):
        current_time = glfw.get_time()
        self.delta_time = current_time - self.previous_time
        self.previous_time = current_time

    def get_delta_time(self):
        return self.delta_time
