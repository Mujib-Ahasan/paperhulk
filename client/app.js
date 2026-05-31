const form = document.getElementById("summary-form");
const fileInput = document.getElementById("pdf-file");
const modeInput = document.getElementById("mode");

const statusText = document.getElementById("status");

const resultCard = document.getElementById("result-card");
const metadata = document.getElementById("metadata");
const summaryOutput = document.getElementById("summary-output");

const selectedFile = document.getElementById("selected-file");
const summaryOptions = document.getElementById("summary-options");

const modeCards = document.querySelectorAll(".mode-card");

const providerInput = document.getElementById("provider");
const providerOptions = document.getElementById("provider-options");
const providerCards = document.querySelectorAll(".provider-card");

const progressWrapper = document.getElementById("progress-wrapper");
const progressText = document.getElementById("progress-text");
const progressBar = document.getElementById("progress-bar");

const cancelButton = document.getElementById("cancel-button");
const summarizeButton = document.querySelector(".summarize-btn");

let activeJobId = null;
let activeSocket = null;

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    selectedFile.textContent = fileInput.files[0].name;
    summaryOptions.classList.remove("hidden");
    summaryOptions.classList.add("slide-up");
    statusText.textContent = "";
  }
});

modeCards.forEach((card) => {
  card.addEventListener("click", () => {
    modeCards.forEach((item) => item.classList.remove("active"));

    card.classList.add("active");
    modeInput.value = card.dataset.mode;

    providerOptions.classList.remove("hidden");
    providerOptions.classList.add("slide-up");
  });
});

providerCards.forEach((card) => {
  card.addEventListener("click", () => {
    providerCards.forEach((item) => item.classList.remove("active"));

    card.classList.add("active");
    providerInput.value = card.dataset.provider;
  });
});

cancelButton.addEventListener("click", async () => {
  if (!activeJobId) return;

  statusText.textContent = "Cancelling summarization...";
  cancelButton.disabled = true;

  try {
    await fetch(`http://localhost:8000/summarize/jobs/${activeJobId}/cancel`, {
      method: "POST",
    });
  } catch (error) {
    statusText.textContent = "Failed to cancel summarization.";
    cancelButton.disabled = false;
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = fileInput.files[0];

  if (!file) {
    statusText.textContent = "Please upload a PDF file.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("mode", modeInput.value);
  formData.append("provider", providerInput.value);

  resultCard.classList.add("hidden");
  summaryOutput.textContent = "";
  metadata.innerHTML = "";

  progressWrapper.classList.remove("hidden");
  progressBar.style.width = "0%";
  progressText.textContent = "Starting summarization...";

  summarizeButton.classList.add("hidden");
  cancelButton.classList.remove("hidden");
  cancelButton.disabled = false;

  statusText.textContent = `Starting summarization using ${providerInput.value}...`;

  try {
    const response = await fetch("http://localhost:8000/summarize/start", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to start summarization");
    }

    activeJobId = data.job_id;

    const socket = new WebSocket(
      `ws://localhost:8000/ws/progress/${activeJobId}`
    );

    activeSocket = socket;

    socket.onmessage = (event) => {
      const progress = JSON.parse(event.data);

      const completed = progress.completed || 0;
      const total = progress.total || 1;
      const percent = Math.round((completed / total) * 100);

      progressBar.style.width = `${percent}%`;
      progressText.textContent = `${completed}/${total} steps completed`;

      statusText.textContent =
        `Summarizing paper... ${completed}/${total} steps completed (${percent}%)`;

      if (progress.status === "done") {
        progressBar.style.width = "100%";
        progressText.textContent = "Summary completed.";
        statusText.textContent = "Summary generated successfully.";

        metadata.innerHTML = `
          <div class="stats">
            <div class="stat-card">
              <p>Total Words: ${progress.word_count}</p>
            </div>
            <div class="stat-card">
              <p>Total Chunks: ${progress.chunk_count}</p>
            </div>
            <div class="stat-card">
              <p>Summary Mode: ${progress.mode}</p>
            </div>
            <div class="stat-card">
              <p>Time: ${progress.timestamp}</p>
            </div>
            <div class="stat-card">
              <p>AI Provider: ${progress.provider}</p>
            </div>
          </div>
        `;

        summaryOutput.textContent = progress.summary;
        resultCard.classList.remove("hidden");

        cancelButton.classList.add("hidden");
        summarizeButton.classList.remove("hidden");

        activeJobId = null;
        activeSocket = null;

        socket.close();
      }

      if (progress.status === "failed") {
        statusText.textContent = progress.error || "Summarization failed.";

        cancelButton.classList.add("hidden");
        summarizeButton.classList.remove("hidden");

        activeJobId = null;
        activeSocket = null;

        socket.close();
      }

      if (progress.status === "cancelled") {
        progressText.textContent = "Summarization cancelled.";
        statusText.textContent = "Summarization cancelled.";
        progressBar.style.width = "0%";

        cancelButton.classList.add("hidden");
        summarizeButton.classList.remove("hidden");

        activeJobId = null;
        activeSocket = null;

        socket.close();
      }
    };

    socket.onerror = () => {
      statusText.textContent = "WebSocket connection failed.";

      cancelButton.classList.add("hidden");
      summarizeButton.classList.remove("hidden");

      activeJobId = null;
      activeSocket = null;
    };

  } catch (error) {
    statusText.textContent = error.message;

    cancelButton.classList.add("hidden");
    summarizeButton.classList.remove("hidden");

    activeJobId = null;
    activeSocket = null;
  }
});