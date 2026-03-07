import axios from "axios";

// 1. Create a base Axios instance
const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    headers: {
        "Content-Type": "application/json",
    },
});

// 2. Add an Interceptor to automatically attach the JWT token to every request
api.interceptors.request.use((config) => {
    // Check if we are in the browser environment
    if (typeof window !== "undefined") {
        const token = localStorage.getItem("access_token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// 3. Define and export all API functions
export const loginUser = async (email, password) => {
    // FastAPI uses form-data for OAuth2 login
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const response = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "multipart/form-data" }
    });
    return response.data;
};

export const registerUser = async (name, email, phone, password) => {
    const response = await api.post("/auth/register", {
        name, email, phone, password, role: "patient"
    });
    return response.data;
};

export const getProfile = async () => {
    const response = await api.get("/auth/profile");
    return response.data;
};

export const sendChatMessage = async (message) => {
    const response = await api.post("/chat/message", { message });
    return response.data;
};

export const getAppointments = async () => {
    const response = await api.get("/appointments/my-appointments");
    return response.data;
};

export const getReports = async () => {
    const response = await api.get("/records/reports");
    return response.data;
};

export const getPrescriptions = async () => {
    const response = await api.get("/records/prescriptions");
    return response.data;
};

export const getBills = async () => {
    const response = await api.get("/records/bills");
    return response.data;
};

export const getPendingBills = async () => {
    const response = await api.get("/records/bills/pending");
    return response.data;
};

export const bookAppointment = async (doctor_id, appointment_date, appointment_time) => {
    const response = await api.post("/appointments/book", {
        doctor_id,
        appointment_date,
        appointment_time
    });
    return response.data;
};

export const getDoctors = async () => {
    const response = await api.get("/doctors/");
    return response.data;
};

export default api;