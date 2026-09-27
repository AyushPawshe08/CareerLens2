import axios from "axios";

// Set VITE_API_BASE_URL in a .env file at the project root, e.g.:
//   VITE_API_BASE_URL=http://localhost:8000
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: BASE_URL,
});

// Attach the JWT (if we have one) to every outgoing request.
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If the backend ever returns 401 (expired/invalid token), clear the
// stored token so the app doesn't keep sending a dead one, and let the
// caller's own error handling take over (we don't force-redirect here —
// that's the AuthContext/route guard's job, not the HTTP client's).
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
    }
    return Promise.reject(error);
  }
);

// ---------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------

export async function registerUser({ email, password, full_name }) {
  const { data } = await apiClient.post("/api/auth/register", {
    email,
    password,
    full_name: full_name || null,
  });
  return data; // { access_token, token_type }
}

export async function loginUser({ email, password }) {
  const { data } = await apiClient.post("/api/auth/login", { email, password });
  return data; // { access_token, token_type }
}

export async function getMe() {
  const { data } = await apiClient.get("/api/auth/me");
  return data; // UserOut
}

// ---------------------------------------------------------------------
// History
// ---------------------------------------------------------------------

export async function getHistoryList({ limit = 20, offset = 0 } = {}) {
  const { data } = await apiClient.get("/api/history", { params: { limit, offset } });
  return data; // HistoryListItem[]
}

export async function getHistoryItem(id) {
  const { data } = await apiClient.get(`/api/history/${id}`);
  return data; // HistoryItem
}

// ---------------------------------------------------------------------
// Analyze
// ---------------------------------------------------------------------

export async function analyzeResume({ resumeFile, jobDescription }) {
  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("job_description", jobDescription);

  const { data } = await apiClient.post("/api/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data; // AnalyzeResponse shape from the backend
}