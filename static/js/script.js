function getSuggestions() {
    const query = document.getElementById("test_name").value;

    fetch(`/suggest-tests?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const suggestionsBox = document.getElementById("suggestions");
            suggestionsBox.innerHTML = "";

            if (query.trim() === "" || data.length === 0) {
                return;
            }

            data.forEach(test => {
                const item = document.createElement("div");
                item.className = "suggestion-item";
                item.innerText = test;
                item.onclick = function () {
                    document.getElementById("test_name").value = test;
                    suggestionsBox.innerHTML = "";
                };
                suggestionsBox.appendChild(item);
            });
        });
}

function searchTests() {
    const testName = document.getElementById("test_name").value;
    const city = document.getElementById("city").value;
    const area = document.getElementById("area").value;

    const formData = new FormData();
    formData.append("test_name", testName);
    formData.append("city", city);
    formData.append("area", area);

    fetch("/search", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = "";

            if (data.length === 0) {
                resultsDiv.innerHTML = `<p class="no-results">No matching tests found.</p>`;
                return;
            }

            data.forEach(item => {
                const card = document.createElement("div");
                card.className = "result-card";

                card.innerHTML = `
                <h3>${item.Lab_Name}</h3>
                <p><strong>Test:</strong> ${item.Test_Name}</p>
                <p><strong>City:</strong> ${item.City}</p>
                <p><strong>Area:</strong> ${item.Area}</p>
                <p class="price">₹ ${item.Price}</p>
                <button class="nav-btn" onclick="navigateToLab('${item.Latitude}', '${item.Longitude}')">Navigate</button>
            `;

                resultsDiv.appendChild(card);
            });
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById("results").innerHTML = `<p class="no-results">Something went wrong.</p>`;
        });
}

function uploadPrescription() {
    const fileInput = document.getElementById("prescription");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select an image.");
        return;
    }

    const formData = new FormData();
    formData.append("prescription", file);

    fetch("/upload-prescription", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            const ocrDiv = document.getElementById("ocr-result");

            if (data.error) {
                ocrDiv.innerHTML = `<p class="no-results">${data.error}</p>`;
                return;
            }

            let html = `<h3>Detected Tests</h3>`;

            if (data.matched_tests.length === 0) {
                html += `<p>No matching tests detected.</p>`;
            } else {
                html += `<ul>`;
                data.matched_tests.forEach(test => {
                    html += `<li onclick="selectDetectedTest('${test}')" class="detected-test">${test}</li>`;
                });
                html += `</ul>`;
            }

            ocrDiv.innerHTML = html;
        })
        .catch(error => {
            console.error("Upload error:", error);
            document.getElementById("ocr-result").innerHTML = `<p class="no-results">Upload failed.</p>`;
        });
}

function selectDetectedTest(test) {
    document.getElementById("test_name").value = test;
    searchTests();
}

function navigateToLab(lat, lon) {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {
            const userLat = position.coords.latitude;
            const userLon = position.coords.longitude;
            const url = `https://www.google.com/maps/dir/${userLat},${userLon}/${lat},${lon}`;
            window.open(url, "_blank");
        },
        function (error) {
            alert("Could not get current location.");
            console.error(error);
        }
    );
}