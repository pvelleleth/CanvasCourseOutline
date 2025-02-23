from fastapi import FastAPI, HTTPException
from openai import OpenAI
import os
import dotenv
import requests
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json

dotenv.load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
) 

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
    Generate a course outline for a given course.
    Prompt chain:
    - Initial Analysis: Understand the course structure
    - Planning: Plan the course outline structure
    - Organization: Organize the course content into a structure
    """

    # Step 1: Initial Analysis and Understanding Course Structure
    analysis_prompt = {
        "role": "system",
        "content": """You are an expert in education and course design, with deep understanding of how instructors organize their course content.
Your task is to analyze Canvas LMS course data and understand how this specific instructor has structured their course to best serve their teaching goals.
CRITICAL REQUIREMENTS:
1. You MUST process and account for EVERY SINGLE file, assignment, quiz, and module provided in the input data
2. Create a comprehensive inventory of ALL resources - no file should be left out
3. If you receive lists or arrays of files/resources, you MUST process each item in those lists
4. Track and verify that every item from the input data is accounted for in your analysis
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
2. Course flow and progression:
   - How content builds upon itself
   - Key learning components
   - Core materials vs. supplementary resources
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
CRITICAL REQUIREMENTS:
1. Your plan MUST account for EVERY SINGLE file and resource from the analysis phase
2. Create explicit sections in your structure for ALL provided materials
3. Implement validation checks to ensure no files or resources are accidentally omitted
4. If dealing with lists of resources, verify that each item has a designated place in the structure
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
4. Group related materials based on how the instructor has organized them
5. Ensure all available resources are easily discoverable
6. Create clear sections for different types of content

Consider:
- How to work with the instructor's chosen organizational tools
- Ways to show relationships between materials within their system
- How to organize content topically based on their approach
- Making important information immediately visible
- Supporting different learning approaches within their framework

Return a JSON object describing your planned outline structure. Only include information that is explicitly available in the course data and only reference Canvas features that are actually being used.'''
    }
    
    messages = [planning_prompt, planning_generation]
    planning_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={ "type": "json_object" }
    )
    
    # Step 3: Creating the Final Course Outline
    organization_prompt = {
        "role": "system",
        "content": """You are an expert in creating clear, intuitive, and comprehensive course outlines.
Your task is to organize this course's content into a structure that will help students effectively navigate and understand their course.
CRITICAL REQUIREMENTS FOR COMPLETE RESOURCE INCLUSION:
1. You MUST include EVERY SINGLE file, assignment, quiz, and module in your output
2. Implement a systematic verification process:
   - Cross-reference all input files against your output structure
   - Verify that each resource from the input appears in your output
   - Double-check that no items are accidentally omitted
3. For any lists or arrays in the input:
   - Process each item individually
   - Track each item to ensure inclusion
   - Verify the count of items matches between input and output
4. If you detect any potential omissions, immediately flag them and ensure inclusion
The output MUST be a well-structured JSON object containing ALL course components that are explicitly available in the data.
CRITICAL: DO NOT make up, infer, or hallucinate any information that isn't directly present in the course data.
Adapt to the instructor's organizational choices - don't force a structure that doesn't match how they've set up their course."""
    }
    
    final_organization = {
        "role": "user",
        "content": f'''Using our planned structure: {planning_completion.choices[0].message.content}

Create a comprehensive course outline using EVERY PIECE of information present in:
Modules: {request.modules}
Assignments: {request.assignments}
Quizzes: {request.quizzes}
Files: {request.files}

VERIFICATION REQUIREMENTS:
1. Process each input list/array item by item
2. Keep a running count of processed items
3. Cross-reference your output against input to ensure nothing is missed
4. Verify that the number of resources in your output matches the input
5. Double-check that each file path, assignment, and quiz is included

Your JSON response should include these core components (ONLY if they are actually used and the information is explicitly available):
1. Course Information:
   - Course name (if provided)
   - Course code (if provided)
   - Instructor details (if provided)
2. Content Organization (based on how the instructor has structured it):
   - EVERY module (if modules are used)
   - EVERY assignment (if present)
   - EVERY quiz (if used)
   - ALL other organizational structures the instructor has chosen
3. Resources:
   - EVERY SINGLE downloadable resource with its link
   - ALL files categorized according to the instructor's organization
   - Verification that no files are omitted
4. Content Relationships (based on the instructor's organizational choices):
   - ALL dependencies between materials (if such relationships exist)
   - COMPLETE content groupings (as organized by the instructor)
   - ALL prerequisites (if explicitly specified)

Additional organization requirements:
1. Present a clear path through the course using whatever structure the instructor has chosen
2. Group related materials according to the instructor's organization
3. Show connections between content where they exist
4. Make ALL resources easily findable within their organizational context
5. Preserve the instructor's specific teaching approach
6. Support different learning styles within the given structure
7. Implement verification to ensure NO files are missed

The JSON structure should be:
- Complete in including EVERY resource
- Intuitive for navigation
- Adaptable to different teaching styles
- Comprehensive in covering what's actually present
- Organized according to the instructor's approach
- Easy to parse programmatically

IMPORTANT:
- Include ALL information that is explicitly present in the provided course data
- If certain features or information are not available, omit those fields entirely
- DO NOT create placeholder or example data
- DO NOT infer or guess at missing information
- DO NOT assume the use of any Canvas features that aren't actually being used
- Adapt to however the instructor has chosen to organize their course
- VERIFY that every single file and resource is included

Return a JSON object that satisfies these requirements while maintaining a student-friendly organization that matches the instructor's approach.'''
    }
    # Generate course outline
    messages = [organization_prompt, final_organization]
    final_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={ "type": "json_object" }
    )
    
    # Return JSON object
    try:
        return json.loads(final_completion.choices[0].message.content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse JSON response from AI")
