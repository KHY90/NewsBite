import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    '환경변수가 설정되지 않았습니다. REACT_APP_SUPABASE_URL과 REACT_APP_SUPABASE_ANON_KEY를 확인해주세요.'
  )
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    flowType: 'pkce',
  },
})

// 데이터베이스 타입 정의
export interface User {
  id: string
  email: string
  name?: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface UserPreferences {
  user_id: string
  categories: string[]
  companies: string[]
  email_notifications: boolean
  created_at: string
  updated_at: string
}