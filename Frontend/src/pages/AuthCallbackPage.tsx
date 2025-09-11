/**
 * OAuth 콜백 페이지
 * 구글 로그인 후 리다이렉트되는 페이지
 */
import React, { useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { supabase } from '../config/supabase'
import { useAuth } from '../contexts/AuthContext'

const AuthCallbackPage: React.FC = () => {
  const navigate = useNavigate()
  const { user, loading } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(true)

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // URL에서 인증 코드 처리
        const { data, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('인증 콜백 오류:', error)
          setError('로그인 처리 중 오류가 발생했습니다.')
          return
        }

        if (data.session) {
          console.log('로그인 성공:', data.session.user.email)
          // AuthContext에서 자동으로 사용자 상태가 업데이트됨
          // 잠시 기다린 후 대시보드로 이동
          setTimeout(() => {
            navigate('/dashboard', { replace: true })
          }, 1000)
        } else {
          // 세션이 없는 경우 로그인 페이지로 리다이렉트
          setError('로그인이 완료되지 않았습니다.')
          setTimeout(() => {
            navigate('/login', { replace: true })
          }, 2000)
        }
      } catch (error) {
        console.error('인증 처리 오류:', error)
        setError('로그인 처리 중 오류가 발생했습니다.')
      } finally {
        setIsProcessing(false)
      }
    }

    handleAuthCallback()
  }, [navigate])

  // 이미 로그인되어 있고 로딩이 완료된 경우
  if (user && !loading && !isProcessing) {
    return <Navigate to="/dashboard" replace />
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            로그인 오류
          </h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/login')}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            로그인 페이지로 돌아가기
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-6"></div>
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          로그인 처리 중...
        </h2>
        <p className="text-gray-600">
          잠시만 기다려주세요. 곧 대시보드로 이동합니다.
        </p>
      </div>
    </div>
  )
}

export default AuthCallbackPage