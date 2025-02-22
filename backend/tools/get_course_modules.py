from canvas.canvas import CanvasAPI
from config import Config
import json

def get_course_modules(course_id: int):
    """
    Retrieve the modules for a specific course.
    """
    canvas = CanvasAPI(Config.get_token())
    modules = canvas.get_course_modules(course_id)
    return json.dumps(modules)
