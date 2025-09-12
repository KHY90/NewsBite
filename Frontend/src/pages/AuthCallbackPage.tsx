/**
 * OAuth 콜백 페이지
 * 구글 로그인 후 리다이렉트되는 페이지
 */
import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import Spinner from "../components/Spinner";
import { useAuth } from "../contexts/AuthContext";

const AuthCallbackPage: React.FC = () => {
  const { user, loading } = useAuth();

  useEffect(() => {
    // 이 페이지는 Supabase 클라이언트가 URL에서 세션을 처리하고
    // AuthContext의 onAuthStateChange 리스너가 트리거될 때까지
    // 로딩 UI를 보여주는 역할만 합니다.
  }, []);

  // 이미 로그인되어 있고 로딩이 완료된 경우
  if (!loading && user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
        <Spinner size="lg" color="border-blue-600" className="mx-auto mb-6" />
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          로그인 처리 중...
        </h2>
        <p className="text-gray-600">
          잠시만 기다려주세요. 곧 대시보드로 이동합니다.
        </p>
      </div>
    </div>
  );
};

export default AuthCallbackPage;
