from fastapi import FastAPI, HTTPException
from openai import OpenAI
import os
import dotenv
import requests
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from canvas.canvas import CanvasAPI
from toolbox.toolbox import ToolBox
from config import Config
from tools.tools_definition import tools
import json
from tools.get_course_modules import get_course_modules
from tools.get_course_assignments import get_course_assignments
from tools.get_course_quizzes import get_course_quizzes
from tools.get_course_files import get_course_files
from tools.get_courses import get_courses
from tools.analyze_course_structure import analyze_course_structure
import time
dotenv.load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create an assistant once during startup


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class TokenRequest(BaseModel):
    token: str

@app.post("/set-token")
async def set_token(request: TokenRequest):
    """Set the global Canvas API token"""
    Config.set_token(request.token)
    return {"message": "Token set successfully"}
    

@app.get("/")
def read_root():
    return {"Hello": "World"}

class CourseOutlineRequest(BaseModel):
    course_id: int
    modules: str
    assignments: str
    quizzes: str
    files: str

@app.post("/generate-course-outline")
async def generate_course_outline(request: CourseOutlineRequest):
    """
    Generate a course outline for a given course ID using OpenAI Assistants API.
    First analyzes the course structure, then generates a dynamic schema.
    """
    functions_map = {
        "get_course_modules": get_course_modules,
        "get_course_assignments": get_course_assignments,
        "get_course_quizzes": get_course_quizzes,
        "get_course_files": get_course_files
    }

    # Step 1: Initial Analysis - Understanding Course Structure
    analysis_prompt = {
        "role": "system",
        "content": """You are an expert in education and course design, with deep understanding of how instructors organize their course content.
Your task is to analyze Canvas LMS course data and understand how this specific instructor has structured their course to best serve their teaching goals.
IMPORTANT: Only use information that is explicitly present in the provided course data. DO NOT make up or infer any information that isn't directly available.
Be aware that instructors may not use all Canvas features - some might not use modules, quizzes, or other components. Analyze only what's actually being used."""
    }
    
    initial_analysis = {
        "role": "user",
        "content": f'''Analyze this Canvas course (ID: {request.course_id}) to understand how the instructor has organized their teaching materials.
ONLY use information that is explicitly present in the provided course data.

First, identify which Canvas features this instructor actually uses in their course organization.
Then focus on understanding:
1. The instructor's teaching approach (based ONLY on visible patterns in the data):
   - How they sequence and present content
   - Their preferred teaching methods (lectures, assignments, discussions, etc.)
   - Which Canvas features they rely on most
   - Any unique teaching patterns or strategies
2. Course flow and progression (using whatever organizational tools the instructor has chosen):
   - How content builds upon itself
   - Key learning milestones
   - Time-sensitive vs. reference materials
3. Content organization (based on the features actually in use):
   - How materials are grouped and related
   - Important dependencies between content
   - Resource organization and accessibility

Course Data:
Modules: {request.modules}
Assignments: {request.assignments}
Quizzes: {request.quizzes}
Files: {request.files}

Provide your analysis as a JSON object that captures these insights. If any information is not explicitly available in the data or if certain features aren't being used, omit them rather than making assumptions.'''
    }

    messages = [analysis_prompt, initial_analysis]
    
    analysis_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={ "type": "json_object" }
    )
    
    # Step 2: Planning the Course Outline Structure
    planning_prompt = {
        "role": "system",
        "content": """You are an expert in creating intuitive and useful course outlines that help students navigate and understand their course materials effectively.
Your task is to plan how to best present this course's content in a way that maintains the instructor's intent while making it highly accessible to students.
IMPORTANT: Only work with information that is explicitly available in the course data. DO NOT create, infer, or make up any additional information.
Adapt your approach based on which Canvas features the instructor actually uses - don't assume a module-based structure if the instructor organizes differently."""
    }
    
    planning_generation = {
        "role": "user",
        "content": f'''Based on our analysis: {analysis_completion.choices[0].message.content}

Plan a course outline structure that adapts to how this specific instructor has chosen to organize their course.
The structure should:
1. Make the course easy to navigate and understand
2. Preserve the instructor's chosen organizational approach
3. Highlight the course components and relationships that are actually in use
4. Make important deadlines and milestones clear
5. Group related materials based on how the instructor has organized them
6. Ensure all available resources are easily discoverable

Consider:
- How to work with the instructor's chosen organizational tools
- Ways to show relationships between materials within their system
- How to balance chronological vs. topical organization based on their approach
- Making important information immediately visible
- Supporting different learning approaches within their framework

Return a JSON object describing your planned outline structure. Only include information that is explicitly available in the course data and only reference Canvas features that are actually being used.'''
    }
    
    messages = [planning_prompt, planning_generation]
    planning_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={ "type": "json_object" }
    )
    
    # Step 3: Creating the Final Course Outline
    organization_prompt = {
        "role": "system",
        "content": """You are an expert in creating clear, intuitive, and comprehensive course outlines.
Your task is to organize this course's content into a structure that will help students effectively navigate and understand their course.
The output MUST be a well-structured JSON object containing all required course components that are explicitly available in the data.
CRITICAL: DO NOT make up, infer, or hallucinate any information that isn't directly present in the course data.
Adapt to the instructor's organizational choices - don't force a structure that doesn't match how they've set up their course."""
    }
    
    final_organization = {
        "role": "user",
        "content": f'''Using our planned structure: {planning_completion.choices[0].message.content}

Create a comprehensive course outline using ONLY the information present in:
Modules: {request.modules}
Assignments: {request.assignments}
Quizzes: {request.quizzes}
Files: {request.files}

Your JSON response should include these core components (ONLY if they are actually used and the information is explicitly available):
1. Course Information:
   - Course name (if provided)
   - Course code (if provided)
   - Instructor details (if provided)
2. Content Organization (based on how the instructor has structured it):
   - Modules (if used)
   - Assignments (if present)
   - Quizzes (if used)
   - Other organizational structures the instructor has chosen
3. Resources:
   - All available downloadable resources with their links
   - Files categorized according to the instructor's organization
4. Dates and Timelines (for whatever components are actually used):
   - Assignment deadlines (if assignments are used)
   - Quiz dates (if quizzes are present)
   - Other important course milestones
5. Relationships (based on the instructor's organizational choices):
   - Dependencies between materials (if such relationships exist)
   - Content groupings (as organized by the instructor)
   - Prerequisites (if explicitly specified)

Additional organization requirements:
1. Present a clear path through the course using whatever structure the instructor has chosen
2. Make important dates and deadlines obvious
3. Group related materials according to the instructor's organization
4. Show connections between content where they exist
5. Make all resources easily findable within their organizational context
6. Preserve the instructor's specific teaching approach
7. Support different learning styles within the given structure

The JSON structure should be:
- Intuitive for navigation
- Adaptable to different teaching styles
- Comprehensive in covering what's actually present
- Organized according to the instructor's approach
- Easy to parse programmatically

IMPORTANT:
- Only include information that is explicitly present in the provided course data
- If certain features or information are not available, omit those fields entirely
- DO NOT create placeholder or example data
- DO NOT infer or guess at missing information
- DO NOT assume the use of any Canvas features that aren't actually being used
- Adapt to however the instructor has chosen to organize their course

Return a JSON object that satisfies these requirements while maintaining a student-friendly organization that matches the instructor's approach.'''
    }
    
    messages = [organization_prompt, final_organization]
    final_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={ "type": "json_object" }
    )
    
    # Parse the response as JSON and return it as a proper JSON object
    try:
        return json.loads(final_completion.choices[0].message.content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse JSON response from AI")
