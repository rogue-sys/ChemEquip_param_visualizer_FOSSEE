import axios from "axios";

const API = axios.create({
  baseURL: "https://chemequip-param-visualizer-fossee.onrender.com/api/",
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
