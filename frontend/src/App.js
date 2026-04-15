import { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [docId, setDocId] = useState("");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const BASE_URL = "http://13.127.159.78:8000";

  // 🔥 Upload PDF
  const uploadFile = async () => {
    if (!file) {
      alert("Select a PDF first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const res = await axios.post(`${BASE_URL}/upload`, formData);
      setDocId(res.data.doc_id);
      alert("Upload successful. Doc ID set automatically.");
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }

    setLoading(false);
  };

  // 🔥 Ask question
  const askQuestion = async () => {
    if (!query || !docId) {
      alert("Upload file and enter query");
      return;
    }

    setLoading(true);
    setAnswer("");

    try {
      const res = await axios.post(`${BASE_URL}/query`, {
        query: query,
        doc_id: docId
      });

      setAnswer(res.data.answer);
    } catch (err) {
      console.error(err);
      setAnswer("Error occurred");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: 30 }}>
      <h2>Vectorless RAG System</h2>

      {/* Upload */}
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={uploadFile}>
        {loading ? "Uploading..." : "Upload PDF"}
      </button>

      <p><b>Doc ID:</b> {docId}</p>

      <hr />

      {/* Query */}
      <textarea
        rows={5}
        cols={60}
        placeholder="Ask your question..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <br /><br />

      <button onClick={askQuestion}>
        {loading ? "Processing..." : "Ask"}
      </button>

      <h3>Answer:</h3>
      <div style={{ whiteSpace: "pre-wrap" }}>{answer}</div>
    </div>
  );
}

export default App;