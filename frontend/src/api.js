import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000"
});

export const getMissionState = async () => {
    const response = await API.get("/mission");
    return response.data;
};

export const startMission = async () => {
    const response = await API.post("/mission/start");
    return response.data;
};

export const coordinateMission = async () => {
    const response = await API.post("/mission/coordinate");
    return response.data;
};

export const resetMission = async () => {
    const response = await API.post("/mission/reset");
    return response.data;
};

export default API;