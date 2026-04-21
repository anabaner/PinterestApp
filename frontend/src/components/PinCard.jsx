import { useState } from "react";

export default function PinCard({ pin, onClick, onDelete }) {
  const [hovered, setHovered] = useState(false);
  const imageUrl = `http://127.0.0.1:8000${pin.image_url}`;

  return (
    <div
      className="pin-card"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={() => onClick(pin)}
    >
      <img src={imageUrl} alt={pin.title} loading="lazy" />

      {hovered && (
        <div className="pin-overlay">
          <span className="pin-board">{pin.board}</span>
          <button
            className="pin-delete"
            onClick={(e) => {
              e.stopPropagation(); // don't open the drawer
              onDelete(pin.id);
            }}
          >
            Delete
          </button>
        </div>
      )}

      <div className="pin-info">
        <p className="pin-title">{pin.title}</p>
        <p className="pin-tags">{pin.tags}</p>
      </div>
    </div>
  );
}