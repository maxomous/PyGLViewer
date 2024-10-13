class Color:
    BLACK = (0.0, 0.0, 0.0)
    WHITE = (1.0, 1.0, 1.0)
    RED = (1.0, 0.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE = (0.0, 0.0, 1.0)
    YELLOW = (1.0, 1.0, 0.0)
    CYAN = (0.0, 1.0, 1.0)
    MAGENTA = (1.0, 0.0, 1.0)
    GRAY = (0.5, 0.5, 0.5)
    ORANGE = (1.0, 0.5, 0.0)
    PURPLE = (0.5, 0.0, 0.5)
    BROWN = (0.6, 0.3, 0.0)
    PINK = (1.0, 0.75, 0.8)

    @staticmethod
    def rgb(r, g, b):
        return (r / 255.0, g / 255.0, b / 255.0)

    @staticmethod
    def rgba(r, g, b, a):
        return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)
