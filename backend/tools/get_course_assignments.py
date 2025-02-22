from canvas.canvas import CanvasAPI
from config import Config
import json

def get_course_assignments(course_id: int):
    """
    Retrieve the assignments for a specific course.
    """
    canvas = CanvasAPI(Config.get_token())
    assignments = canvas.get_course_assignments(course_id)
    return json.dumps(assignments)