// 인증 관련 타입 정의
export interface User {
  id: string;
  supabase_id: string;
  email: string;
  display_name: string;
  avatar_url: string;
  is_active: boolean;
  email_notifications_enabled: boolean;
  email_send_time: string;
  created_at: string;
  last_login_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
  user: User;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signOut: () => void;
  updateProfile: (data: UpdateProfileData) => Promise<User | null>;
}

export interface UpdateProfileData {
  display_name?: string;
  email_notifications_enabled?: boolean;
  email_send_time?: string;
}

export interface TokenValidationResponse {
  valid: boolean;
  user?: User;
  message?: string;
}
