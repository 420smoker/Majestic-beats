import warnings
warnings.filterwarnings("ignore", message="Couldn't find ffmpeg")

from .pattern import Pattern
from .randomize import randomize
from .render import render

__version__ = "0.1.0"
__all__ = ["Pattern", "randomize", "render"]
