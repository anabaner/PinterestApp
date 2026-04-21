import { useState } from "react";
import { api } from "../api";

const BOARDS = ["General", "Travel", "Food", "Fashion", "Art", "Technology", "Nature"];

export default function UploadModal({ onClose, onUploaded }) {
  const [file, setFile]       = useState(null);
  const [board, setBoard]     = useState("General");
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  function handleFileChange(e) {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected)); // show preview instantly
  }

  async function handleSubmit() {
    if (!file) { setError("Please select an image."); return; }
    setLoading(true);
    setError("");
    try {
      const newPin = await api.uploadPin(file, board);
      onUploaded(newPin); // tell parent to add pin to grid
      onClose();
    } catch (err) {
      setError("Upload failed. Make sure your backend is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Upload a Pin</h2>

        <div className="upload-area" onClick={() => document.getElementById("file-input").click()}>
          {preview
            ? <img src={preview} alt="preview" style={{ width: "100%", borderRadius: 8 }} />
            : <p>Click to choose an image</p>
          }
        </div>
        <input
          id="file-input"
          type="file"
          accept="image/*"
          style={{ display: "none" }}
          onChange={handleFileChange}
        />

        <select value={board} onChange={(e) => setBoard(e.target.value)} className="board-select">
          {BOARDS.map((b) => <option key={b}>{b}</option>)}
        </select>

        {error && <p className="error-text">{error}</p>}

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? "Uploading + AI tagging..." : "Upload"}
          </button>
        </div>
      </div>
    </div>
  );
}