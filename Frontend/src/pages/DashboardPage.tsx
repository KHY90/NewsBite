import React from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DashboardPage: React.FC = () => {
  const { user, loading, signOut } = useAuth();

  // 로그인하지 않은 경우 로그인 페이지로 리다이렉트
  if (!user && !loading) {
    return <Navigate to="/login" replace />
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const handleLogout = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('로그아웃 실패:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-800">
                뉴스한입 📰
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {user?.user_metadata?.avatar_url && (
                  <img
                    src={user.user_metadata.avatar_url}
                    alt="프로필"
                    className="w-8 h-8 rounded-full"
                  />
                )}
                <span className="text-sm font-medium text-gray-700">
                  {user?.user_metadata?.name || user?.email}
                </span>
              </div>
              
              <button
                onClick={handleLogout}
                className="text-sm text-gray-600 hover:text-gray-800 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors"
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </header>
      <div className="py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            대시보드
          </h1>

          <div className="grid gap-6">
            {/* 환영 메시지 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                안녕하세요, {user?.email}님! 👋
              </h2>
              <p className="text-gray-600">
                뉴스한입에 오신 것을 환영합니다. 개인 맞춤형 뉴스 서비스가 곧 준비됩니다.
              </p>
            </div>

            {/* 빠른 액션 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                빠른 시작
              </h3>
              <div className="space-y-4">
                <Link
                  to="/preferences"
                  className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                >
                  <div className="flex items-center">
                    <span className="text-2xl mr-3">⚙️</span>
                    <div>
                      <h4 className="font-medium text-gray-900">관심사 설정</h4>
                      <p className="text-sm text-gray-600">
                        받고 싶은 뉴스 카테고리와 관심 기업을 선택하세요
                      </p>
                    </div>
                  </div>
                </Link>
              </div>
            </div>

            {/* 기능 소개 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                주요 기능
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="text-center p-4">
                  <span className="text-3xl block mb-2">📰</span>
                  <h4 className="font-medium text-gray-900">맞춤 뉴스</h4>
                  <p className="text-sm text-gray-600">개인 관심사별 뉴스 요약</p>
                </div>
                <div className="text-center p-4">
                  <span className="text-3xl block mb-2">📊</span>
                  <h4 className="font-medium text-gray-900">감정 분석</h4>
                  <p className="text-sm text-gray-600">기업별 뉴스 감정 추적</p>
                </div>
                <div className="text-center p-4">
                  <span className="text-3xl block mb-2">🎯</span>
                  <h4 className="font-medium text-gray-900">찬반 정리</h4>
                  <p className="text-sm text-gray-600">논쟁 이슈 중립적 분석</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
