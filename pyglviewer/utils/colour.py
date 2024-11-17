class Colour:
    """Common color constants."""
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
        """Convert 8-bit RGB values to normalized floats.
        
        Args:
            r (int): Red value (0-255)
            g (int): Green value (0-255)
            b (int): Blue value (0-255)
        
        Returns:
            tuple: Normalized RGB values (0.0-1.0)
        """
        return (r / 255.0, g / 255.0, b / 255.0)

    @staticmethod
    def rgba(r, g, b, a):
        """Convert 8-bit RGBA values to normalized floats.
        
        Args:
            r (int): Red value (0-255)
            g (int): Green value (0-255)
            b (int): Blue value (0-255)
            a (int): Alpha value (0-255)
        
        Returns:
            tuple: Normalized RGBA values (0.0-1.0)
        """
        return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)

    @staticmethod
    def interpolate(color_1, color_2, t):
        """Linearly interpolate between two colors.
        
        Args:
            color_1 (tuple): First color (r,g,b) or (r,g,b,a)
            color_2 (tuple): Second color (r,g,b) or (r,g,b,a)
            t (float): Interpolation factor (0.0-1.0)
                      0.0 returns color_1
                      1.0 returns color_2
        
        Returns:
            tuple: Interpolated color with same dimensions as inputs
        """
        # Ensure t is clamped between 0 and 1
        t = max(0.0, min(1.0, t))
        
        # Handle both RGB and RGBA colors   
        return tuple(c1 + (c2 - c1) * t for c1, c2 in zip(color_1, color_2))
