from canvas.canvas import CanvasAPI
from config import Config
import json

def get_courses():
    """
    Retrieve all courses for the authenticated user.
    """
    canvas = CanvasAPI(Config.get_token())
    courses = canvas.get_courses()
    return [{"data": json.dumps(courses)}]
