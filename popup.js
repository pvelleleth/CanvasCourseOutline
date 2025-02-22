document.addEventListener("DOMContentLoaded", function () {
    const fetchButton = document.getElementById("generate-outline");
    const buttonText = document.getElementById("button-text");
    const loadingSpinner = document.getElementById("loading-spinner");

    // Get the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];
        
        if (activeTab && activeTab.url.includes("instructure.com")) {
            fetchButton.disabled = false; // Enable button if on Canvas
        } else {
            fetchButton.disabled = true; // Keep button disabled
        }
    });

    // Function to set loading state
    function setLoading(isLoading) {
        if (isLoading) {
            fetchButton.classList.add('loading');
            buttonText.textContent = 'Generating...';
            loadingSpinner.style.display = 'inline-block';
            fetchButton.disabled = true;
        } else {
            fetchButton.classList.remove('loading');
            buttonText.textContent = 'Generate Outline';
            loadingSpinner.style.display = 'none';
            fetchButton.disabled = false;
        }
    }

    // Inject content.js when button is clicked
    fetchButton.addEventListener("click", function () {
        setLoading(true);
        
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.scripting.executeScript({
                target: { tabId: tabs[0].id },
                files: ["content.js"]
            }).then(() => {
                setLoading(false);
            }).catch((error) => {
                console.error('Error:', error);
                setLoading(false);
            });
        });
    });
});

