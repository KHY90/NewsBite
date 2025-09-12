import axios from "axios";
import type {
  LoginResponse,
  User,
  UpdateProfileData,
  TokenValidationResponse,
} from "../types/auth";

const API_BASE_URL = import.meta.env.VITE_API_URL || "";

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 에러 시 자동 로그아웃
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰이 만료되었거나 유효하지 않은 경우
      localStorage.removeItem("accessToken");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  // 구글 로그인
  googleLogin: async (accessToken: string): Promise<LoginResponse> => {
    const response = await api.post("/auth/google-login", {
      access_token: accessToken,
    });
    return response.data;
  },

  // 로그아웃
  logout: async (): Promise<void> => {
    await api.post("/auth/logout");
  },

  // 현재 사용자 정보 조회
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get("/auth/me");
    return response.data;
  },

  // 토큰 검증
  validateToken: async (token: string): Promise<TokenValidationResponse> => {
    const response = await api.post("/auth/validate-token", {
      token,
    });
    return response.data;
  },
};

// 사용자 관련 API
export const userAPI = {
  // 프로필 조회
  getProfile: async (): Promise<User> => {
    const response = await api.get("/users/profile");
    return response.data;
  },

  // 프로필 업데이트
  updateProfile: async (data: UpdateProfileData): Promise<User> => {
    const response = await api.put("/users/profile", data);
    return response.data;
  },
};

export default api;
