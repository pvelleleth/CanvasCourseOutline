import requests
from typing import List, Dict, Any

class CanvasAPI:
    def __init__(self, token: str):
        self.base_url = "https://umd.instructure.com/api/v1"
        self.headers = {"Authorization": f"Bearer {token}"}
        self.token = token
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request to Canvas API"""
        response = requests.get(f"{self.base_url}{endpoint}?access_token={self.token}")
        if response.status_code != 200:
            raise Exception(f"Canvas API Error: {response.status_code} - {response.text}")
        return response.json()

    def get_courses(self) -> List[Dict[str, Any]]:
        """Get list of courses for the authenticated user"""
        return self._make_request("/courses")

    def get_course_modules(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all modules for a specific course"""
        return self._make_request(f"/courses/{course_id}/modules")

    def get_course_assignments(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all assignments for a specific course"""
        return self._make_request(f"/courses/{course_id}/assignments")

    def get_course_quizzes(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all quizzes for a specific course"""
        try:
            return self._make_request(f"/courses/{course_id}/quizzes")
        except Exception:
            return [{"message": "No quizzes found in this course"}]

    def get_course_files(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all files/resources for a specific course"""
        return self._make_request(f"/courses/{course_id}/files")

    def get_course_structure(self, course_id: int) -> Dict[str, Any]:
        """Get complete course structure including modules, assignments, quizzes, and files"""
        modules = self.get_course_modules(course_id)
        assignments = self.get_course_assignments(course_id)
        quizzes = self.get_course_quizzes(course_id)
        files = self.get_course_files(course_id)
        course_info = self._make_request(f"/courses/{course_id}")

        return {
            "course_information": {
                "name": course_info.get("name"),
                "code": course_info.get("course_code"),
                "instructor": course_info.get("teacher"),
            },
            "modules": modules,
            "assignments": assignments,
            "quizzes": quizzes,
            "resources": files,
        }