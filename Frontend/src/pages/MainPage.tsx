import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Feature = ({ title, description }: { title: string, description: string }) => (
  <div className="bg-white p-6 rounded-lg shadow-sm">
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-gray-600">{description}</p>
  </div>
);

const MainPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="py-20 sm:py-32 bg-gradient-to-b from-white to-gray-50">
        <div className="container text-center">
          <h1 className="text-display font-bold tracking-tight text-gray-900">
            세상의 모든 뉴스, 나에게 맞게 한입에
          </h1>
          <p className="mt-6 text-lg text-gray-600 max-w-2xl mx-auto">
            매일 쏟아지는 정보의 홍수 속에서 길을 잃으셨나요? NewsBite가 AI 기술로 당신의 관심사에 꼭 맞는 뉴스만 요약하여 매일 저녁 이메일로 보내드립니다.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link to={user ? "/dashboard" : "/login"} className="btn btn-primary btn-lg">
              지금 시작하기
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="text-h2 font-bold text-gray-900">핵심 기능</h2>
            <p className="mt-4 text-md text-gray-600">NewsBite는 단순한 뉴스 요약을 넘어섭니다.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Feature 
              title="🤖 AI 자동 요약" 
              description="최신 AI가 뉴스의 핵심 내용만 정확하게 요약하여 시간을 절약해줍니다." 
            />
            <Feature 
              title="🎯 개인 맞춤 카테고리" 
              description="정치, 경제, IT, 과학 등 원하는 분야의 뉴스만 골라서 받아볼 수 있습니다." 
            />
            <Feature 
              title="🏢 기업 뉴스 분석" 
              description="관심 기업의 뉴스에 대한 긍정, 부정 감성 분석으로 시장 반응을 파악하세요." 
            />
            <Feature 
              title="⚖️ 논쟁 이슈 정리" 
              description="복잡한 사회적 논쟁에 대해 중립적인 시각에서 찬성과 반대 의견을 함께 제공합니다." 
            />
            <Feature 
              title="📧 매일 저녁 이메일 브리핑" 
              description="하루 동안의 중요 뉴스를 놓치지 않도록 매일 저녁 7시에 이메일로 보내드립니다." 
            />
            <Feature 
              title="🧩 뉴스 퀴즈" 
              description="읽은 뉴스를 바탕으로 생성된 퀴즈를 풀며 내용을 다시 한번 확인하고 지식을 쌓으세요." 
            />
          </div>
        </div>
      </section>
    </div>
  );
};

export default MainPage;