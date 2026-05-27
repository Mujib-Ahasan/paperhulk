const form = document.getElementById("summary-form");
const fileInput = document.getElementById("pdf-file");
const modeInput = document.getElementById("mode");

const statusText = document.getElementById("status");

const resultCard = document.getElementById("result-card");
const metadata = document.getElementById("metadata");
const summaryOutput = document.getElementById("summary-output");

const selectedFile = document.getElementById("selected-file");
const summaryOptions = document.getElementById("summary-options");

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    selectedFile.textContent = fileInput.files[0].name;
    summaryOptions.classList.remove("hidden");
    statusText.textContent = "";
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

  statusText.textContent = "Summarizing paper locally...";

  resultCard.classList.add("hidden");
  summaryOutput.textContent = "";

  try {
    const response = await fetch("http://localhost:8000/summarize", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to summarize PDF");
    }

    statusText.textContent = "Summary generated successfully.";

    metadata.innerHTML = `
      <div class="stats">
        <div class="stat-card">
          <p>Total Words: ${data.word_count}</p>
        </div>
        <div class="stat-card">
          <p>Total Chunks: ${data.chunk_count}</p>
        </div>
        <div class="stat-card">
          <p>Summary Mode: ${data.mode}</p>
        </div>
      </div>
    `;
    summaryOutput.textContent = data.summary;
    resultCard.classList.remove("hidden");
  } catch (error) {
    statusText.textContent = error.message;
  }
});