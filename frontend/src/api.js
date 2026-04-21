import axios from "axios";

const BASE = "http://127.0.0.1:8000";

export const api = {
  // Fetch all pins
  getAllPins: () =>
    axios.get(`${BASE}/pins`).then((r) => r.data),

  // Upload image (multipart form)
  uploadPin: (file, board = "General") => {
    const form = new FormData();
    form.append("file", file);
    form.append("board", board);
    return axios.post(`${BASE}/pins/upload`, form).then((r) => r.data);
  },

  // Get similar pins
  getSimilarPins: (pinId) =>
    axios.get(`${BASE}/pins/${pinId}/similar`).then((r) => r.data),

  // Delete a pin
  deletePin: (pinId) =>
    axios.delete(`${BASE}/pins/${pinId}`),
};