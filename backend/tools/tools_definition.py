tools = [
    {
        "type": "function",
        "function": {
            "name": "get_course_modules",
            "description": "Retrieves all modules for a specific Canvas course",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "The ID of the course to get modules from"
                    }
                },
                "required": ["course_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_assignments",
            "description": "Retrieves all assignments for a specific Canvas course",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "The ID of the course to get assignments from"
                    }
                },
                "required": ["course_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_quizzes",
            "description": "Retrieves all quizzes for a specific Canvas course",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "The ID of the course to get quizzes from"
                    }
                },
                "required": ["course_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_files",
            "description": "Retrieves all files and resources for a specific Canvas course",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "The ID of the course to get files from"
                    }
                },
                "required": ["course_id"]
            }
        }
    }
] 