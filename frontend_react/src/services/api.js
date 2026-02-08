import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api/",
});

// Set token dynamically
export const setAuthToken = (token) => {
  if (token) {
    API.defaults.headers.common["Authorization"] = `Token ${token}`;
  } else {
    delete API.defaults.headers.common["Authorization"];
  }
};

export default API;
