from canvas.canvas import CanvasAPI
from config import Config
import json

def get_course_files(course_id: int):
    """
    Retrieve the files and resources for a specific course.
    """
    canvas = CanvasAPI(Config.get_token())
    files = canvas.get_course_files(course_id)
    return json.dumps(files)