from canvas.canvas import CanvasAPI
from config import Config
import json

def get_course_quizzes(course_id: int):
    """
    Retrieve the quizzes for a specific course.
    """
    try:
        canvas = CanvasAPI(Config.get_token())
        quizzes = canvas.get_course_quizzes(course_id)
        return [{"data": json.dumps(quizzes)}]
    except Exception as e:
        return json.dumps({"message": "No quizzes found in this course"})