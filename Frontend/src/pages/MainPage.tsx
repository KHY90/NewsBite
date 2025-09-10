import React from 'react';
import { LoginButton } from '../components/auth/LoginButton';

const MainPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            뉴스한입 📰
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            매일 저녁 7시, 개인 맞춤형 뉴스 요약을 받아보세요
          </p>
        </div>

        <div className="space-y-4">
          <LoginButton size="lg" className="w-full" />
        </div>

        <div className="text-center text-sm text-gray-500">
          <p>✨ 개인 관심사별 맞춤 뉴스</p>
          <p>📊 기업별 뉴스 감정분석</p>
          <p>🎯 논쟁 이슈 찬반정리</p>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
