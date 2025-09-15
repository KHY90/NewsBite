import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  ArrowRight,
  Mail,
  Brain,
  Clock,
  Star,
  TrendingUp,
  Shield,
  Zap,
  CheckCircle,
  Sparkles
} from 'lucide-react';

const MainPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="w-full bg-white font-sans">
      {/* Hero Section */}
      <section className="relative pt-16 pb-24 bg-white">
        <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-brand-accent text-brand-primary text-sm font-medium mb-8">
              <Sparkles className="w-4 h-4 mr-2" />
              매일 저녁 7시, 개인화된 뉴스 요약
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              스마트한 뉴스 생활의<br />
              <span className="text-brand-primary">새로운 시작</span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-12 leading-relaxed">
              AI가 200개 언론사에서 당신에게 꼭 필요한 뉴스만 선별하여<br />
              매일 저녁 이메일로 전달합니다
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
              <Button asChild size="lg" className="bg-brand-primary hover:bg-brand-primaryHover text-white px-8 py-4 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200">
                <Link to={user ? "/dashboard" : "/login"}>
                  무료로 시작하기
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="px-8 py-4 text-lg font-semibold border-2 border-gray-200 hover:border-brand-primary hover:text-brand-primary transition-all duration-200">
                서비스 둘러보기
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-8 text-gray-500">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-sm font-medium">완전 무료</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-5 h-5 text-blue-500" />
                <span className="text-sm font-medium">이메일 한 통으로 끝</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-purple-500" />
                <span className="text-sm font-medium">매일 정시 배송</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="container max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div className="space-y-2">
              <div className="text-3xl font-bold text-brand-primary">200+</div>
              <div className="text-sm text-gray-600">언론사</div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-brand-primary">10,000+</div>
              <div className="text-sm text-gray-600">활성 사용자</div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-brand-primary">99.9%</div>
              <div className="text-sm text-gray-600">배송 성공률</div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-brand-primary">4.9★</div>
              <div className="text-sm text-gray-600">사용자 만족도</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="container max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              왜 NewsBite인가요?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              매일 쏟아지는 뉴스 홍수 속에서 정말 중요한 정보만 골라드립니다
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto">
                <Brain className="w-8 h-8 text-brand-primary" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">AI 개인화</h3>
              <p className="text-gray-600 leading-relaxed">
                당신의 관심사와 읽기 패턴을 학습하여<br />
                꼭 필요한 뉴스만 선별합니다
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-green-50 rounded-2xl flex items-center justify-center mx-auto">
                <Clock className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">시간 절약</h3>
              <p className="text-gray-600 leading-relaxed">
                매일 30분씩 뉴스를 찾아볼 필요 없이<br />
                5분이면 하루 뉴스 완료
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-purple-50 rounded-2xl flex items-center justify-center mx-auto">
                <Mail className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">간편 배송</h3>
              <p className="text-gray-600 leading-relaxed">
                매일 저녁 7시 정시에<br />
                이메일로 깔끔하게 정리해 전달
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="container max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              간단한 3단계로 시작하세요
            </h2>
            <p className="text-xl text-gray-600">
              복잡한 설정 없이 바로 개인화된 뉴스를 받아보실 수 있습니다
            </p>
          </div>

          <div className="relative">
            {/* Connection Line */}
            <div className="hidden md:block absolute top-1/2 left-1/4 right-1/4 h-0.5 bg-gray-200 -translate-y-1/2"></div>

            <div className="grid md:grid-cols-3 gap-12 relative">
              <div className="text-center">
                <div className="w-20 h-20 bg-brand-primary rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <span className="text-2xl font-bold text-white">1</span>
                </div>
                <h3 className="text-xl font-semibold mb-4 text-gray-900">관심사 선택</h3>
                <p className="text-gray-600 leading-relaxed">
                  정치, 경제, 기술 등<br />
                  관심 있는 분야를 선택하세요
                </p>
              </div>

              <div className="text-center">
                <div className="w-20 h-20 bg-brand-primaryHover rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <span className="text-2xl font-bold text-white">2</span>
                </div>
                <h3 className="text-xl font-semibold mb-4 text-gray-900">AI 분석</h3>
                <p className="text-gray-600 leading-relaxed">
                  AI가 매일 200개 언론사에서<br />
                  당신만을 위한 뉴스를 선별
                </p>
              </div>

              <div className="text-center">
                <div className="w-20 h-20 bg-brand-primarySoft rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <span className="text-2xl font-bold text-white">3</span>
                </div>
                <h3 className="text-xl font-semibold mb-4 text-gray-900">이메일 수신</h3>
                <p className="text-gray-600 leading-relaxed">
                  매일 저녁 7시<br />
                  깔끔하게 정리된 뉴스 요약
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section id="pricing" className="py-20 text-center bg-brand-primary text-white">
        <div className="container max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-8">
            <h2 className="text-4xl sm:text-5xl font-bold">
              지금 바로 시작하세요
            </h2>
            <p className="text-xl opacity-90 max-w-2xl mx-auto">
              첫 번째 개인화된 뉴스 요약을 내일 저녁 받아보세요.<br />
              언제든 무료로 구독을 해지할 수 있습니다.
            </p>

            <div className="pt-4">
              <Button asChild size="lg" variant="secondary" className="bg-white text-brand-primary hover:bg-gray-50 px-8 py-4 text-lg font-semibold shadow-lg">
                <Link to={user ? "/dashboard" : "/login"}>
                  무료로 시작하기
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </Button>
            </div>

            <div className="pt-4 space-y-2 text-sm opacity-80">
              <p>✨ 완전 무료 서비스</p>
              <p>📧 매일 저녁 7시 정시 배송</p>
              <p>🚀 언제든 구독 해지 가능</p>
            </div>
          </div>
        </div>
      </section>

      <footer className="py-16 border-t bg-white">
        <div className="container max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-8">
            {/* Logo */}
            <div className="flex items-center justify-center space-x-2">
              <div className="w-8 h-8 bg-brand-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">NB</span>
              </div>
              <span className="text-2xl font-bold text-brand-primary">NewsBite</span>
            </div>

            {/* Description */}
            <p className="text-gray-600 max-w-md mx-auto">
              매일 저녁, 당신만을 위한 뉴스를 AI가 선별해서 전달하는<br />
              개인화된 뉴스 큐레이션 서비스
            </p>

            {/* Links */}
            <div className="flex flex-wrap justify-center gap-8 text-sm">
              <Link to="/login" className="text-gray-600 hover:text-brand-primary transition-colors">
                시작하기
              </Link>
              <a href="#features" className="text-gray-600 hover:text-brand-primary transition-colors">
                기능
              </a>
              <a href="#how-it-works" className="text-gray-600 hover:text-brand-primary transition-colors">
                사용법
              </a>
              <a href="#" className="text-gray-600 hover:text-brand-primary transition-colors">
                이용약관
              </a>
              <a href="#" className="text-gray-600 hover:text-brand-primary transition-colors">
                개인정보처리방침
              </a>
            </div>

            {/* Copyright */}
            <div className="pt-8 border-t border-gray-100 text-sm text-gray-500">
              &copy; {new Date().getFullYear()} NewsBite. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainPage;