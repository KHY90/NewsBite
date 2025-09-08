// 인증 컨텍스트

import React, { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { authAPI, userAPI } from '../lib/api'
import type { User, AuthContextType, UpdateProfileData } from '../types/auth'

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // 초기 인증 상태 확인
  useEffect(() => {
    checkAuthState()
  }, [])

  const checkAuthState = async () => {
    try {
      const token = localStorage.getItem('accessToken')
      const storedUser = localStorage.getItem('user')

      if (token && storedUser) {
        // 저장된 토큰과 사용자 정보가 있는 경우 검증
        const validationResult = await authAPI.validateToken(token)
        
        if (validationResult.valid && validationResult.user) {
          setUser(validationResult.user)
        } else {
          // 토큰이 유효하지 않은 경우 정리
          localStorage.removeItem('accessToken')
          localStorage.removeItem('user')
          setUser(null)
        }
      }
    } catch (error) {
      console.error('인증 상태 확인 중 오류:', error)
      // 오류 발생 시 로컬 저장소 정리
      localStorage.removeItem('accessToken')
      localStorage.removeItem('user')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const signInWithGoogle = async () => {
    try {
      setLoading(true)
      
      // Supabase Google OAuth 시작
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })

      if (error) {
        throw error
      }

      // OAuth 리다이렉트가 발생하므로 여기서는 추가 처리 불필요
      // callback에서 실제 로그인 처리가 이루어짐
      
    } catch (error) {
      console.error('구글 로그인 오류:', error)
      setLoading(false)
      throw error
    }
  }

  const signOut = async () => {
    try {
      // Supabase 로그아웃
      await supabase.auth.signOut()
      
      // 백엔드 로그아웃 (토큰이 있는 경우만)
      const token = localStorage.getItem('accessToken')
      if (token) {
        try {
          await authAPI.logout()
        } catch (error) {
          // 백엔드 로그아웃 실패해도 클라이언트는 로그아웃 진행
          console.warn('백엔드 로그아웃 실패:', error)
        }
      }

      // 로컬 상태 정리
      localStorage.removeItem('accessToken')
      localStorage.removeItem('user')
      setUser(null)
      
    } catch (error) {
      console.error('로그아웃 오류:', error)
      throw error
    }
  }

  const updateProfile = async (data: UpdateProfileData): Promise<User | null> => {
    try {
      if (!user) {
        throw new Error('로그인이 필요합니다')
      }

      const updatedUser = await userAPI.updateProfile(data)
      setUser(updatedUser)
      
      // 로컬 저장소 업데이트
      localStorage.setItem('user', JSON.stringify(updatedUser))
      
      return updatedUser
    } catch (error) {
      console.error('프로필 업데이트 오류:', error)
      throw error
    }
  }

  // Google OAuth 콜백 처리를 위한 함수
  const handleOAuthCallback = async (accessToken: string) => {
    try {
      setLoading(true)
      
      // 백엔드에 Google OAuth 토큰 전송하여 Supabase JWT 토큰 받기
      const loginResponse = await authAPI.googleLogin(accessToken)
      
      // 토큰과 사용자 정보 저장
      localStorage.setItem('accessToken', loginResponse.access_token)
      localStorage.setItem('user', JSON.stringify(loginResponse.user))
      
      setUser(loginResponse.user)
      
    } catch (error) {
      console.error('OAuth 콜백 처리 오류:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const value: AuthContextType = {
    user,
    loading,
    signInWithGoogle,
    signOut,
    updateProfile
  }

  // OAuth 콜백 처리를 위해 전역에 함수 등록
  ;(window as any).handleOAuthCallback = handleOAuthCallback

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}