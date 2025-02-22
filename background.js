async function fetchCanvasCourses() {
    try {
        const response = await fetch("https://umd.instructure.com/api/v1/courses", {
            credentials: "include" // This ensures cookies (canvas_session) are sent with the request
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status} - ${response.statusText}`);
        }

        const courses = await response.json();
        console.log("Canvas Courses:", courses);
        return courses;
    } catch (error) {
        console.error("Failed to fetch Canvas courses:", error);
    }
}


// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "generateOutline") {
        fetch('http://localhost:8000/save-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({token: request.token})
        })
        // Make the API call
        fetch('http://localhost:8000/generate-course-outline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({courseId: request.courseId})
        })
        .then(response => response.json())
        .then(data => {
            // Convert JSON to blob
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            
            // Create download URL
            const url = URL.createObjectURL(blob);
            
            // Trigger download
            chrome.downloads.download({
                url: url,
                filename: `course-outline-${request.courseId}.json`,
                saveAs: true
            }, (downloadId) => {
                // Cleanup: revoke the blob URL after download starts
                URL.revokeObjectURL(url);
                sendResponse({success: true, downloadId: downloadId});
            });
        })
        .catch(error => {
            sendResponse({success: false, error: error.message});
        });

        // Return true to indicate we will send response asynchronously
        return true;
    }
    else if (request.action === "fetchCourses") {
        console.log("Background script received fetchCourses request");
        
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (!tabs[0]) {
                console.error("No active tab found");
                sendResponse({success: false, error: "No active tab found"});
                return;
            }
            
            const tabId = tabs[0].id;
            console.log("Sending message to tab:", tabId);
            
            // Wrap in a try-catch block
            try {
                chrome.tabs.sendMessage(tabId, {action: "fetchCourses"})
                    .then(response => {
                        console.log("Background received response:", response);
                        sendResponse(response);
                    })
                    .catch(error => {
                        console.error("Error in background script:", error);
                        sendResponse({
                            success: false,
                            error: error.message || "Failed to communicate with the page"
                        });
                    });
            } catch (error) {
                console.error("Error sending message:", error);
                sendResponse({success: false, error: error.toString()});
            }
        });
        
        return true; // Keep the message channel open
    }
});




// Fetch courses when the extension is installed

