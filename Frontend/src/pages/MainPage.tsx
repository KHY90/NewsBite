import React from 'react';
import Header from '@/components/Header';
import NewsCard from '@/components/NewsCard';
import TrendingKeywords from '@/components/TrendingKeywords';
import TodayBriefing from '@/components/TodayBriefing';

const sampleArticles = [
  {
    title: '애플, 새로운 AI 전략 발표: "Apple Intelligence"',
    source: '블룸버그',
    time: '30분 전',
    content: 'Apple이 WWDC 2024에서 온디바이스와 서버 기반을 결합한 새로운 AI 시스템 "Apple Intelligence"를 공개했습니다. 사용자 개인 정보 보호에 중점을 둔 기능이 특징입니다.',
    category: 'IT/테크',
    imageUrl: 'https://plus.unsplash.com/premium_photo-1683129624130-a62e675e5383?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
  },
  {
    title: 'NVIDIA, 시가총액 3조 달러 돌파',
    source: '로이터',
    time: '1시간 전',
    content: 'AI 칩 수요 폭증에 힘입어 NVIDIA의 시가총액이 3조 달러를 넘어서며 Apple을 제치고 세계 2위 기업으로 등극했습니다.',
    category: '증권',
    imageUrl: 'https://images.unsplash.com/photo-1718192329424-2085a12c7732?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
  },
  {
    title: '한국은행, 기준금리 동결 가능성 시사',
    source: '연합뉴스',
    time: '2시간 전',
    content: '물가 상승 압력이 여전히 높지만, 경기 둔화 우려로 인해 한국은행이 다음 금융통화위원회에서 기준금리를 동결할 것이라는 전망이 우세합니다.',
    category: '금융',
    imageUrl: 'https://images.unsplash.com/photo-1579621970795-87f91d908377?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
  },
];

const MainPage: React.FC = () => {
  return (
    <div className="bg-gray-50 min-h-screen font-sans">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          <main className="lg:col-span-2 xl:col-span-3">
            <TodayBriefing />
            <h2 className="text-2xl font-bold text-gray-800 mb-4">최신 뉴스</h2>
            {sampleArticles.map((article, index) => (
              <NewsCard key={index} article={article} />
            ))}
          </main>
          <aside className="lg:col-span-1 xl:col-span-1">
            <TrendingKeywords />
          </aside>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
