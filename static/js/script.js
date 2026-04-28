window.onload = async function () {
    await loadFilters();

    const userMessage = document.getElementById("userMessage");
    userMessage.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            askAI();
        }
    });
};

async function loadFilters() {
    try {
        const response = await fetch("/get-filters");
        const data = await response.json();

        const citySelect = document.getElementById("citySelect");
        const areaSelect = document.getElementById("areaSelect");
        const testList = document.getElementById("testList");

        citySelect.innerHTML = `<option value="">Select City</option>`;
        areaSelect.innerHTML = `<option value="">Select Area</option>`;
        testList.innerHTML = "";

        data.cities.forEach(city => {
            citySelect.innerHTML += `<option value="${city}">${city}</option>`;
        });

        data.areas.forEach(area => {
            areaSelect.innerHTML += `<option value="${area}">${area}</option>`;
        });

        data.tests.forEach(test => {
            testList.innerHTML += `<option value="${test}">`;
        });

    } catch (error) {
        console.error("Error loading filters:", error);
    }
}

async function searchTests() {
    const test = document.getElementById("testInput").value.trim();
    const city = document.getElementById("citySelect").value;
    const area = document.getElementById("areaSelect").value;
    const resultSection = document.getElementById("resultSection");

    resultSection.innerHTML = "<p class='loading'>Searching...</p>";

    try {
        const response = await fetch("/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ test, city, area })
        });

        const data = await response.json();

        if (data.status === "error") {
            resultSection.innerHTML = `<p class="error">${data.message}</p>`;
            return;
        }

        let html = `
            <div class="best-card">
                <h2>Best Cheapest Option</h2>
                <p><b>Lab:</b> ${data.cheapest.Lab_Name}</p>
                <p><b>Test:</b> ${data.cheapest.Test_Name}</p>
                <p><b>Price:</b> ₹${data.cheapest.Price}</p>
                <p><b>Area:</b> ${data.cheapest.Area}</p>
                <p><b>City:</b> ${data.cheapest.City}</p>
                <button class="map-btn" onclick="openCurrentLocationMap(${data.cheapest.Latitude}, ${data.cheapest.Longitude})">
                    Navigate to Best Lab
                </button>
            </div>

            <h2 class="table-title">Available Lab Options</h2>
            <table>
                <thead>
                    <tr>
                        <th>Lab Name</th>
                        <th>Test Name</th>
                        <th>Price</th>
                        <th>City</th>
                        <th>Area</th>
                        <th>Navigation</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.results.forEach(item => {
            html += `
                <tr>
                    <td>${item.Lab_Name}</td>
                    <td>${item.Test_Name}</td>
                    <td>₹${item.Price}</td>
                    <td>${item.City}</td>
                    <td>${item.Area}</td>
                    <td>
                        <button class="table-map-btn" onclick="openCurrentLocationMap(${item.Latitude}, ${item.Longitude})">
                            Navigate
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        resultSection.innerHTML = html;

    } catch (error) {
        resultSection.innerHTML = `<p class="error">Something went wrong. Please try again.</p>`;
        console.error(error);
    }
}

function toggleChat() {
    const chatBox = document.getElementById("chatBox");
    chatBox.style.display = chatBox.style.display === "block" ? "none" : "block";
}

async function askAI() {
    const messageInput = document.getElementById("userMessage");
    const message = messageInput.value.trim();
    const chatMessages = document.getElementById("chatMessages");

    if (message === "") {
        alert("Please type a question");
        return;
    }

    chatMessages.innerHTML += `<p class="user">${message}</p>`;
    messageInput.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch("/ai-assistant", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        chatMessages.innerHTML += `<p class="bot">${data.reply}</p>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        chatMessages.innerHTML += `<p class="bot">Sorry, something went wrong.</p>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
        console.error(error);
    }
}

function startVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Speech recognition is not supported in this browser. Use Chrome or Edge.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("userMessage").value = transcript;
        askAI();
    };

    recognition.onerror = function (event) {
        alert("Microphone error: " + event.error);
    };
}

function openCurrentLocationMap(destinationLat, destinationLng) {
    if (!navigator.geolocation) {
        alert("Location is not supported in this browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {
            const currentLat = position.coords.latitude;
            const currentLng = position.coords.longitude;

            const mapsUrl =
                `https://www.google.com/maps/dir/?api=1&origin=${currentLat},${currentLng}&destination=${destinationLat},${destinationLng}&travelmode=driving`;

            window.open(mapsUrl, "_blank");
        },
        function () {
            const mapsUrl =
                `https://www.google.com/maps/dir/?api=1&destination=${destinationLat},${destinationLng}&travelmode=driving`;

            window.open(mapsUrl, "_blank");
        }
    );
}

function uploadPrescription() {
    alert("Prescription upload is added as future scope. Next version can use OCR to read test names.");
}