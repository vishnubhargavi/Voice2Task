const API_URL = "http://127.0.0.1:8000";

const audioInput = document.getElementById("audioInput");
const uploadButton = document.getElementById("uploadButton");

const recordButton = document.getElementById("recordButton");
const stopButton = document.getElementById("stopButton");
const recordStatus = document.getElementById("recordStatus");
const recordingTimer = document.getElementById("recordingTimer");

const selectedAudio = document.getElementById("selectedAudio");
const selectedAudioName = document.getElementById("selectedAudioName");
const removeAudioButton = document.getElementById("removeAudioButton");

const audioPreview = document.getElementById("audioPreview");
const audioPlayer = document.getElementById("audioPlayer");

const processButton = document.getElementById("processButton");

const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");

const transcript = document.getElementById("transcript");
const summary = document.getElementById("summary");
const keyInfo = document.getElementById("keyInfo");
const detectedTasks = document.getElementById("detectedTasks");

const newMessageButton = document.getElementById("newMessageButton");

let selectedFile = null;

let mediaRecorder = null;
let audioChunks = [];
let stream = null;

let recordingStartTime = null;
let timerInterval = null;


// ============================================================
// UPLOAD
// ============================================================

uploadButton.addEventListener("click", () => {
    audioInput.click();
});

audioInput.addEventListener("change", () => {

    if (!audioInput.files || audioInput.files.length === 0) {
        return;
    }

    selectedFile = audioInput.files[0];

    showSelectedAudio(selectedFile);
});

function showSelectedAudio(file) {

    selectedAudio.classList.remove("hidden");

    selectedAudioName.textContent = file.name;

    const url = URL.createObjectURL(file);

    audioPlayer.src = url;

    audioPreview.classList.remove("hidden");

    processButton.disabled = false;
}


// ============================================================
// REMOVE AUDIO
// ============================================================

removeAudioButton.addEventListener("click", () => {

    selectedFile = null;

    audioInput.value = "";

    selectedAudio.classList.add("hidden");

    audioPreview.classList.add("hidden");

    audioPlayer.src = "";

    processButton.disabled = true;
});


// ============================================================
// START RECORDING
// ============================================================

recordButton.addEventListener("click", startRecording);

async function startRecording() {

    try {

        recordButton.disabled = true;

        recordStatus.textContent = "Starting microphone...";


        // ----------------------------------------------------
        // SIMPLE NATIVE BROWSER AUDIO PROCESSING
        // ----------------------------------------------------

        stream = await navigator.mediaDevices.getUserMedia({

            audio: {
                channelCount: 1,
                sampleRate: 48000,
                sampleSize: 16,

                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }

        });


        // ----------------------------------------------------
        // FIND BEST SUPPORTED OPUS FORMAT
        // ----------------------------------------------------

        let mimeType = "";

        const supportedTypes = [
            "audio/webm;codecs=opus",
            "audio/webm"
        ];

        for (const type of supportedTypes) {

            if (MediaRecorder.isTypeSupported(type)) {

                mimeType = type;

                break;
            }
        }


        // ----------------------------------------------------
        // MEDIA RECORDER
        // ----------------------------------------------------

        const options = {
            audioBitsPerSecond: 128000
        };

        if (mimeType) {
            options.mimeType = mimeType;
        }


        mediaRecorder =
            new MediaRecorder(
                stream,
                options
            );


        audioChunks = [];


        mediaRecorder.ondataavailable = (event) => {

            if (
                event.data &&
                event.data.size > 0
            ) {

                audioChunks.push(event.data);

            }

        };


        mediaRecorder.onstop = finishRecording;


        // ----------------------------------------------------
        // START RECORDING
        // ----------------------------------------------------

        mediaRecorder.start();


        recordingStartTime = Date.now();

        startTimer();


        recordStatus.textContent =
            "Recording... Speak naturally";


        recordButton.classList.add("hidden");

        stopButton.classList.remove("hidden");

        stopButton.disabled = false;


    } catch (error) {

        console.error(error);

        recordStatus.textContent =
            "Microphone permission was denied or unavailable.";

        recordButton.disabled = false;

        stopButton.disabled = true;

    }
}


// ============================================================
// STOP RECORDING
// ============================================================

stopButton.addEventListener("click", stopRecording);

function stopRecording() {

    if (!mediaRecorder) {
        return;
    }


    if (mediaRecorder.state === "recording") {

        mediaRecorder.stop();

    }


    stopTimer();


    recordStatus.textContent =
        "Preparing recording...";


    stopButton.classList.add("hidden");

    recordButton.classList.remove("hidden");

    recordButton.disabled = false;


    if (stream) {

        stream.getTracks().forEach(
            track => track.stop()
        );

    }
}


// ============================================================
// FINISH RECORDING
// ============================================================

function finishRecording() {

    const blob = new Blob(
        audioChunks,
        {
            type: mediaRecorder.mimeType ||
                "audio/webm"
        }
    );


    selectedFile = new File(
        [blob],
        "voice-message.webm",
        {
            type: blob.type
        }
    );


    showSelectedAudio(selectedFile);


    recordStatus.textContent =
        "Recording ready ✓";


    audioChunks = [];

    mediaRecorder = null;

}


// ============================================================
// TIMER
// ============================================================

function startTimer() {

    recordingTimer.textContent = "00:00";


    timerInterval = setInterval(() => {

        if (!recordingStartTime) {
            return;
        }


        const elapsed =
            Math.floor(
                (Date.now() - recordingStartTime) / 1000
            );


        const minutes =
            String(
                Math.floor(elapsed / 60)
            ).padStart(2, "0");


        const seconds =
            String(
                elapsed % 60
            ).padStart(2, "0");


        recordingTimer.textContent =
            `${minutes}:${seconds}`;

    }, 1000);

}


// ============================================================
// STOP TIMER
// ============================================================

function stopTimer() {

    clearInterval(timerInterval);

    timerInterval = null;

    recordingStartTime = null;

}


// ============================================================
// PROCESS AUDIO
// ============================================================

processButton.addEventListener(
    "click",
    processAudio
);

async function processAudio() {

    if (!selectedFile) {

        alert(
            "Please upload or record an audio message first."
        );

        return;
    }


    processButton.disabled = true;

    loadingSection.classList.remove("hidden");

    resultsSection.classList.add("hidden");


    const formData = new FormData();

    formData.append(
        "audio",
        selectedFile
    );


    try {

        const response =
            await fetch(
                `${API_URL}/process`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();

            throw new Error(
                errorText ||
                "Processing failed."
            );

        }


        const result =
            await response.json();


        displayResults(result);


    } catch (error) {

        console.error(error);

        alert(
            "Something went wrong while processing the audio.\n\n" +
            error.message
        );

    } finally {

        loadingSection.classList.add("hidden");

        processButton.disabled = false;

    }
}


// ============================================================
// DISPLAY RESULTS
// ============================================================

function displayResults(result) {

    transcript.textContent =
        result.transcript ||
        "No transcript available.";


    summary.textContent =
        result.summary ||
        "No summary available.";


    // --------------------------------------------------------
    // KEY INFORMATION
    // --------------------------------------------------------

    keyInfo.innerHTML = "";


    if (
        result.key_information &&
        result.key_information.length > 0
    ) {

        result.key_information.forEach(item => {

            const card =
                document.createElement("div");

            card.className =
                "key-info-item";


            card.innerHTML = `
                <div class="key-info-label">
                    ${escapeHtml(item.label)}
                </div>

                <div class="key-info-value">
                    ${escapeHtml(item.value)}
                </div>
            `;


            keyInfo.appendChild(card);

        });

    } else {

        keyInfo.innerHTML = `
            <div class="empty-state">
                No key information detected.
            </div>
        `;

    }


    // --------------------------------------------------------
    // TASKS
    // --------------------------------------------------------

    detectedTasks.innerHTML = "";


    if (
        result.tasks &&
        result.tasks.length > 0
    ) {

        result.tasks.forEach((task, index) => {

            const taskCard =
                document.createElement("div");

            taskCard.className =
                "task-item";


            taskCard.innerHTML = `
                <div class="task-number">
                    ${index + 1}
                </div>

                <div class="task-content">

                    <div class="task-title">
                        ${escapeHtml(task.title)}
                    </div>

                    <div class="task-deadline">
                        ${escapeHtml(task.deadline)}
                    </div>

                </div>
            `;


            detectedTasks.appendChild(taskCard);

        });

    } else {

        detectedTasks.innerHTML = `
            <div class="empty-state">
                No actionable tasks detected.
            </div>
        `;

    }


    resultsSection.classList.remove("hidden");


    resultsSection.scrollIntoView({
        behavior: "smooth"
    });

}


// ============================================================
// NEW MESSAGE
// ============================================================

newMessageButton.addEventListener(
    "click",
    () => {

        selectedFile = null;

        audioInput.value = "";

        selectedAudio.classList.add("hidden");

        audioPreview.classList.add("hidden");

        audioPlayer.src = "";

        resultsSection.classList.add("hidden");

        transcript.textContent = "";

        summary.textContent = "";

        keyInfo.innerHTML = "";

        detectedTasks.innerHTML = "";

        recordStatus.textContent =
            "Ready to record";

        recordingTimer.textContent =
            "00:00";

        processButton.disabled = true;


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }
);


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}