import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_generate_course_outline():
    """
    Test the course outline generation endpoint
    """
    # Configuration
    BASE_URL = "http://localhost:8000"
    CANVAS_TOKEN = "1133~6GzN3MRU3f8a4umy9z3nnCA8WhGaNfDTcCDJyRNNBCArz2wFaGW6YuGU842VhXfN"
    TEST_COURSE_ID = 1378721  # Replace with an actual course ID you want to test with

    # First, set the Canvas token
    print("Setting Canvas token...")
    token_response = requests.post(
        f"{BASE_URL}/set-token",
        json={"token": CANVAS_TOKEN}
    )
    
    if token_response.status_code != 200:
        print(f"❌ Failed to set token: {token_response.text}")
        return
    print("✅ Token set successfully")

    # Generate course outline
    print("\nGenerating course outline...")
    try:
        outline_response = requests.post(
            f"{BASE_URL}/generate-course-outline",
            json={"course_id": TEST_COURSE_ID}
        )
        
        if outline_response.status_code != 200:
            print(f"❌ Failed to generate outline: {outline_response.text}")
            return

        # Parse and validate the response
        outline_data = outline_response.json()
        print("\n✅ Course outline generated successfully!")
        print("\nGenerated Outline:")
        print(json.dumps(outline_data, indent=4))

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return

if __name__ == "__main__":
    test_generate_course_outline() 