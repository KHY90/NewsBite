/**
 * 로그인 페이지
 * 구글 소셜 로그인 및 서비스 소개
 */
import React, { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const LoginPage: React.FC = () => {
  const { user, loading, signInWithGoogle } = useAuth()
  const [isLoggingIn, setIsLoggingIn] = useState(false)

  // 이미 로그인한 경우 메인 페이지로 리다이렉트
  if (user && !loading) {
    return <Navigate to="/dashboard" replace />
  }

  const handleGoogleLogin = async () => {
    try {
      setIsLoggingIn(true)
      await signInWithGoogle()
    } catch (error) {
      console.error('로그인 실패:', error)
      setIsLoggingIn(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            뉴스한입 📰
          </h1>
          <p className="text-xl text-gray-600">
            매일 저녁 7시, 개인 맞춤형 뉴스 요약을 받아보세요
          </p>
        </header>

        {/* 메인 컨텐츠 */}
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* 서비스 소개 */}
            <div className="space-y-6">
              <h2 className="text-3xl font-semibold text-gray-800 mb-6">
                똑똑한 뉴스 큐레이션
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">1</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">개인 맞춤 카테고리</h3>
                    <p className="text-gray-600">정치, 경제, 과학, 사회 등 관심 분야만 선택해서 받아보세요</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">2</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">AI 요약 & 감정분석</h3>
                    <p className="text-gray-600">핵심만 요약하고, 기업 관련 뉴스는 긍정/부정 분석까지</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">3</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">논쟁 이슈 찬반 정리</h3>
                    <p className="text-gray-600">복잡한 이슈를 중립적 관점에서 찬반 의견으로 정리</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-orange-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">4</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">정시 이메일 배송</h3>
                    <p className="text-gray-600">매일 저녁 7시, 이메일로 깔끔하게 정리된 뉴스를 받아보세요</p>
                  </div>
                </div>
              </div>
            </div>

            {/* 로그인 폼 */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-semibold text-gray-800 mb-2">
                  시작하기
                </h3>
                <p className="text-gray-600">
                  구글 계정으로 간편하게 로그인하세요
                </p>
              </div>

              <button
                onClick={handleGoogleLogin}
                disabled={isLoggingIn}
                className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoggingIn ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                    로그인 중...
                  </div>
                ) : (
                  <div className="flex items-center">
                    <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                      <path
                        fill="#4285f4"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="#34a853"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="#fbbc05"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="#ea4335"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    Google로 로그인
                  </div>
                )}
              </button>

              <div className="mt-6 text-xs text-gray-500 text-center">
                로그인하면{' '}
                <a href="/terms" className="text-blue-600 hover:underline">
                  이용약관
                </a>
                {' '}및{' '}
                <a href="/privacy" className="text-blue-600 hover:underline">
                  개인정보처리방침
                </a>
                에 동의한 것으로 간주됩니다.
              </div>
            </div>
          </div>
        </div>

        {/* 푸터 */}
        <footer className="mt-16 text-center text-gray-500">
          <p>&copy; 2024 뉴스한입. All rights reserved.</p>
        </footer>
      </div>
    </div>
  )
}

export default LoginPage