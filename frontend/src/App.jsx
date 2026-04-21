import { useState, useEffect } from "react";
import { api } from "./api";
import PinGrid from "./components/PinGrid";
import UploadModal from "./components/UploadModal";
import "./App.css";

export default function App() {
  const [pins, setPins]               = useState([]);
  const [showUpload, setShowUpload]   = useState(false);
  const [selectedPin, setSelectedPin] = useState(null);
  const [similarPins, setSimilarPins] = useState([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);

  // Load all pins on startup
  useEffect(() => {
    api.getAllPins().then(setPins).catch(console.error);
  }, []);

  // When a pin is clicked, open the drawer and fetch similar pins
  async function handlePinClick(pin) {
    setSelectedPin(pin);
    setSimilarPins([]);
    setLoadingSimilar(true);
    try {
      const similar = await api.getSimilarPins(pin.id);
      setSimilarPins(similar);
    } catch (err) {
      console.error("Could not load similar pins", err);
    } finally {
      setLoadingSimilar(false);
    }
  }

  // Add newly uploaded pin to the top of the grid
  function handleUploaded(newPin) {
    setPins((prev) => [newPin, ...prev]);
  }

  // Remove deleted pin from the grid
  async function handleDelete(pinId) {
    await api.deletePin(pinId);
    setPins((prev) => prev.filter((p) => p.id !== pinId));
    if (selectedPin?.id === pinId) setSelectedPin(null);
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1 className="logo">PinBoard</h1>
        <button className="btn-primary" onClick={() => setShowUpload(true)}>
          + Upload
        </button>
      </header>

      {/* Main grid */}
      <main className="main">
        <PinGrid
          pins={pins}
          onPinClick={handlePinClick}
          onDelete={handleDelete}
        />
      </main>

      {/* Similar pins drawer */}
      {selectedPin && (
        <div className="drawer">
          <div className="drawer-header">
            <h3>{selectedPin.title}</h3>
            <button className="close-btn" onClick={() => setSelectedPin(null)}>×</button>
          </div>
          <p className="drawer-desc">{selectedPin.description}</p>
          <p className="drawer-tags">{selectedPin.tags}</p>

          <h4 style={{ margin: "16px 0 8px" }}>Similar pins</h4>
          {loadingSimilar && <p>Finding similar pins...</p>}
          {!loadingSimilar && similarPins.length === 0 && (
            <p style={{ color: "#999", fontSize: 13 }}>
              No similar pins found yet. Add more pins to the same board!
            </p>
          )}
          <div className="similar-grid">
            {similarPins.map((pin) => (
              <div key={pin.id} className="similar-card" onClick={() => handlePinClick(pin)}>
                <img src={`http://127.0.0.1:8000${pin.image_url}`} alt={pin.title} />
                <p>{pin.title}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload modal */}
      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUploaded={handleUploaded}
        />
      )}
    </div>
  );
}