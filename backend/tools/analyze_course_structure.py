from canvas.canvas import CanvasAPI
from config import Config
import cohere
import os
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def analyze_course_structure(course_id: int):
    """
    Analyze the course structure and generate a schema using AI.
    """
    canvas = CanvasAPI(Config.get_token())
    course_data = canvas.get_course_structure(course_id)
    
    prompt = f"""
    Analyze this Canvas LMS course structure and create a schema that captures its organization:
    
    Course: {course_data['course_information']}
    
    Number of Modules: {len(course_data['modules'])}
    Number of Assignments: {len(course_data['assignments'])}
    Number of Quizzes: {len(course_data['quizzes'])}
    Number of Resources: {len(course_data['resources'])}
    
    Please identify patterns in how the content is organized and suggest a schema that would best represent this structure.
    """
    
    response = co.generate(
        prompt=prompt,
        max_tokens=500,
        temperature=0.7,
        model='command'
    )
    
    return response.generations[0].text 