# 📄 PaperHulk

PaperHulk is a local-first research paper summarization system that processes scientific PDFs entirely on the user's machine. It performs structured PDF text extraction, content preprocessing, document validation, semantic chunking, and hierarchical summarization using locally hosted large language models through Ollama, eliminating the need to transmit research documents to external cloud services.

The application is designed for privacy-sensitive and air-gapped environments, providing an end-to-end offline summarization pipeline while supporting multiple summarization modes, real-time progress tracking, and exportable summaries. Since the inference server runs locally, the application can also be accessed from other devices (such as a mobile phone or tablet) connected to the same local network, enabling a lightweight self-hosted deployment without requiring internet connectivity.

## ✨ Features

- 📄 Upload research papers in PDF format
- 🤖 Local AI summarization using Ollama
- 🧠 Supports multiple summarization modes
     - Normal Summary
     - Explain Like I'm 10 (ELI10)
- 🔌 Multiple AI providers
    - Ollama (local)
    - Gemini (optional)
- 📊 Live progress tracking
- ❌ Cancel summarization at any time
- 💾 Export summaries
    - Markdown (.md)
    - Text (.txt)
    - PDF (.pdf)
- 🔒 Fully offline with local LLMs

## 🚀 Getting Started

**Clone the repository** 
```
git clone https:/github.com/Mujib-Ahasan/paperhulk.git
cd paperhulk
```

**Create a virtual environment**

```
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies**
```
pip install -r requirements.txt
```

**🤖 Install Ollama**

Install Ollama: ``` brew install ollama```


Pull the model: ```ollama pull qwen3:4b```

Start Ollama: ```ollama serve```

**🌐 Run the frontend**
cd client
```
python3 -m http.server 5500
```

Open: ```http://localhost:5500```

**📝 How it Works**
- Upload a research paper PDF.
- Choose the summarization mode.
- Select an AI provider.
- The backend:
    - extracts text
    - cleans noisy content
    - validates the document
    - splits it into chunks
    - summarizes each chunk
    - generates the final summary
- Save the generated summary locally.

**🎯 Motivation**

Research papers are often difficult to read while traveling or in environments with limited or no internet access.

PaperHulk was created to provide a fast, privacy-friendly, and completely local solution for summarizing technical research papers without sending sensitive documents to cloud-based AI services.

**🤝 Contributing**

Contributions are welcome!

If you'd like to improve PaperHulk, feel free to open an issue or submit a pull request.

**📄 License**

This project is licensed under the MIT License.
