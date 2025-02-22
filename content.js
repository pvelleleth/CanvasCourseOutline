(async () => {
    // Get the current URL
    const url = window.location.href;

    // Extract the course ID and institution domain using regex
    const courseIdMatch = url.match(/courses\/(\d+)/);
    const courseId = courseIdMatch ? courseIdMatch[1] : null;
    const institutionDomain = url.match(/^https?:\/\/([^\/]+)/i)?.[1];

    if (courseId && institutionDomain) {
        console.log("Course ID:", courseId);
        console.log("Institution Domain:", institutionDomain);
    } else {
        console.log("Could not extract required information from URL");
        return;
    }
    let modulesData, assignmentsData, quizzesData, filesData;

    try {
        const modules = await fetch(`https://${institutionDomain}/api/v1/courses/${courseId}/modules`, {
            method: "GET",
            credentials: "include"
        });
        if (!modules.ok) throw new Error("Modules not found");
        modulesData = await modules.json();
        modulesData = JSON.stringify(modulesData);
    } catch (error) {
        modulesData = "Modules do not exist for this course";
    }

    try {
        const assignments = await fetch(`https://${institutionDomain}/api/v1/courses/${courseId}/assignments`, {
            method: "GET",
            credentials: "include"
        });
        if (!assignments.ok) throw new Error("Assignments not found");
        assignmentsData = await assignments.json();
        assignmentsData = JSON.stringify(assignmentsData);
    } catch (error) {
        assignmentsData = "Assignments do not exist for this course";
    }

    try {
        const quizzes = await fetch(`https://${institutionDomain}/api/v1/courses/${courseId}/quizzes`, {
            method: "GET",
            credentials: "include"
        });
        if (!quizzes.ok) throw new Error("Quizzes not found");
        quizzesData = await quizzes.json();
        quizzesData = JSON.stringify(quizzesData);
    } catch (error) {
        quizzesData = "Quizzes do not exist for this course";
    }

    try {
        const files = await fetch(`https://${institutionDomain}/api/v1/courses/${courseId}/files`, {
            method: "GET",
            credentials: "include"
        });
        if (!files.ok) throw new Error("Files not found");
        filesData = await files.json();
        filesData = JSON.stringify(filesData);
    } catch (error) {
        filesData = "Files do not exist for this course";
    }

    const response = await fetch("http://localhost:8000/generate-course-outline", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            course_id: parseInt(courseId),
            modules: modulesData,
            assignments: assignmentsData,
            quizzes: quizzesData,
            files: filesData
        })
    });
    const data = await response.json();
    
    // Create a Blob with the JSON data
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    
    // Create a temporary URL for the Blob
    const downloadUrl = window.URL.createObjectURL(blob);
    
    // Create a temporary link element
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = 'course_outline.json';
    
    // Append link to body, click it, and remove it
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up the URL
    window.URL.revokeObjectURL(downloadUrl);
})();