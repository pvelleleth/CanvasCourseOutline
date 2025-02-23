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
    /* Fill in the above variables with the data from the API
       Responses from Canvas are paginated so we loop through all pages and concatenate the results
    */
    try {
        let modulesAll = [];
        let apiUrl = `https://${institutionDomain}/api/v1/courses/${courseId}/modules?per_page=100`;
        while (apiUrl) {
            const modules = await fetch(apiUrl, {
                method: "GET",
                credentials: "include"
            });
            if (!modules.ok) throw new Error("Modules not found");
            modulesData = await modules.json();
            modulesAll = modulesAll.concat(modulesData);
            const nextPage = modules.headers.get("Link").match(/<([^>]+)>;\s*rel="next"/);
            apiUrl = nextPage ? nextPage[1] : null;
        }
        modulesData = JSON.stringify(modulesAll);
    } catch (error) {
        modulesData = "Modules do not exist for this course";
    }

    try {   
        let assignmentsAll = [];
        let apiUrl = `https://${institutionDomain}/api/v1/courses/${courseId}/assignments?per_page=100`;
        while (apiUrl) {
            const assignments = await fetch(apiUrl, {
                method: "GET",
                credentials: "include"
            });
            if (!assignments.ok) throw new Error("Assignments not found");
            assignmentsData = await assignments.json();
            assignmentsAll = assignmentsAll.concat(assignmentsData);
            const nextPage = assignments.headers.get("Link").match(/<([^>]+)>;\s*rel="next"/);
            apiUrl = nextPage ? nextPage[1] : null;
        }
        assignmentsData = JSON.stringify(assignmentsAll);
    } catch (error) {
        assignmentsData = "Assignments do not exist for this course";
    }

    try {   
        let quizzesAll = [];
        let apiUrl = `https://${institutionDomain}/api/v1/courses/${courseId}/quizzes?per_page=100`;
        while (apiUrl) {
            const quizzes = await fetch(apiUrl, {
                method: "GET",
                credentials: "include"
            });
            if (!quizzes.ok) throw new Error("Quizzes not found");
            quizzesData = await quizzes.json();
            quizzesAll = quizzesAll.concat(quizzesData);
            const nextPage = quizzes.headers.get("Link").match(/<([^>]+)>;\s*rel="next"/);
            apiUrl = nextPage ? nextPage[1] : null;
        }
        quizzesData = JSON.stringify(quizzesAll);
    } catch (error) {
        quizzesData = "Quizzes do not exist for this course";
    }

    try {   
        let filesAll = [];
        let apiUrl = `https://${institutionDomain}/api/v1/courses/${courseId}/files?per_page=100`;
        while (apiUrl) {
            const files = await fetch(apiUrl, {
                method: "GET",
                credentials: "include"
            });
            if (!files.ok) throw new Error("Files not found");
            filesData = await files.json();
            filesAll = filesAll.concat(filesData);
            const nextPage = files.headers.get("Link").match(/<([^>]+)>;\s*rel="next"/);
            apiUrl = nextPage ? nextPage[1] : null;
        }
        filesData = JSON.stringify(filesAll);
    } catch (error) {
        filesData = "Files do not exist for this course";
    }
    // Send the data to the backend to generate the course outline
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