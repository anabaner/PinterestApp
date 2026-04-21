import Masonry from "react-masonry-css";
import PinCard from "./PinCard";

const breakpoints = {
  default: 4,
  1100: 3,
  768: 2,
  500: 1,
};

export default function PinGrid({ pins, onPinClick, onDelete }) {
  if (pins.length === 0) {
    return (
      <div className="empty-state">
        <p>No pins yet. Upload your first image!</p>
      </div>
    );
  }

  return (
    <Masonry
      breakpointCols={breakpoints}
      className="masonry-grid"
      columnClassName="masonry-column"
    >
      {pins.map((pin) => (
        <PinCard
          key={pin.id}
          pin={pin}
          onClick={onPinClick}
          onDelete={onDelete}
        />
      ))}
    </Masonry>
  );
}