import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
    }
    return Promise.reject(error);
  }
);

export async function registerUser({ email, password, full_name }) {
  const { data } = await apiClient.post("/api/auth/register", {
    email,
    password,
    full_name: full_name || null,
  });
  return data;
}

export async function loginUser({ email, password }) {
  const { data } = await apiClient.post("/api/auth/login", { email, password });
  return data;
}

export async function getMe() {
  const { data } = await apiClient.get("/api/auth/me");
  return data;
}

export async function getHistoryList({ limit = 20, offset = 0 } = {}) {
  const { data } = await apiClient.get("/api/history", { params: { limit, offset } });
  return data;
}

export async function getHistoryItem(id) {
  const { data } = await apiClient.get(`/api/history/${id}`);
  return data;
}

export async function analyzeResume({ resumeFile, jobDescription }) {
  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("job_description", jobDescription);

  const { data } = await apiClient.post("/api/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}