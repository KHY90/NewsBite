import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import Spinner from "../components/Spinner";

// 임시 뉴스 데이터
const mockNews = [
  {
    id: 1,
    category: "IT/과학",
    title: "차세대 AI 모델, 인간과 유사한 수준의 추론 능력 선보여",
    summary:
      "A사의 새로운 AI 모델이 복잡한 다단계 추론 테스트에서 인간과 대등한 성능을 기록하며 기술계에 큰 충격을 주었습니다. 이는 AI가 단순 정보 검색을 넘어 창의적 문제 해결의 영역으로 진입하고 있음을 시사합니다.",
    source: "NewsBite AI Times",
    timestamp: "2시간 전",
  },
  {
    id: 2,
    category: "경제",
    title: "연준, 금리 동결 시사하며 시장 안도 랠리",
    summary:
      "미국 연방준비제도 의장이 인플레이션 둔화 신호를 긍정적으로 평가하며 당분간 금리를 동결할 것임을 시사했습니다. 이 발언으로 뉴욕 증시는 일제히 상승 마감했습니다.",
    source: "머니투데이",
    timestamp: "4시간 전",
  },
  {
    id: 3,
    category: "사회",
    title: "정부, 저출산 대책으로 파격적인 주거 지원 정책 발표",
    summary:
      "정부가 심각한 저출산 문제 해결을 위해 신혼부부 및 출산 가구에 대한 주택 공급 확대와 대출 지원을 포함한 파격적인 주거 안정 대책을 발표했습니다.",
    source: "연합뉴스",
    timestamp: "1시간 전",
  },
  {
    id: 4,
    category: "문화/연예",
    title: "영화 '서울의 봄', 천만 관객 돌파하며 흥행 신기록",
    summary:
      "12.12 군사반란을 다룬 영화 '서울의 봄'이 개봉 한 달 만에 천만 관객을 돌파하며 올해 최고 흥행작으로 등극했습니다. 작품성과 대중성을 모두 잡았다는 평가입니다.",
    source: "씨네21",
    timestamp: "8시간 전",
  },
];

const NewsCard = ({ newsItem }: { newsItem: (typeof mockNews)[0] }) => (
  <div className="card flex flex-col p-6 hover:shadow-lg transition-shadow duration-300">
    <div className="flex-grow">
      <span className="inline-block bg-brand-primarySoft text-brand-primary text-xs font-semibold px-2.5 py-1 rounded-full mb-2">
        {newsItem.category}
      </span>
      <h3 className="text-lg font-bold text-gray-900 mb-2 leading-snug">
        {newsItem.title}
      </h3>
      <p className="text-gray-600 text-sm leading-relaxed">
        {newsItem.summary}
      </p>
    </div>
    <div className="mt-4 pt-4 border-t border-line-soft text-xs text-gray-500 flex justify-between items-center">
      <span>{newsItem.source}</span>
      <span>{newsItem.timestamp}</span>
    </div>
  </div>
);

const DashboardPage: React.FC = () => {
  const { user, loading } = useAuth();

  if (!user && !loading) {
    return <Navigate to="/login" replace />;
  }

  if (loading) {
    return (
      <div className="w-full h-96 flex items-center justify-center">
        <Spinner size="xl" />
      </div>
    );
  }

  return (
    <div className="container py-12">
      <div className="mb-10">
        <h1 className="text-h2 font-bold text-gray-900">오늘의 뉴스 브리핑</h1>
        <p className="mt-2 text-md text-gray-600">
          {user?.email}님을 위해 AI가 선별한 주요 뉴스입니다.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {mockNews.map((news) => (
          <NewsCard key={news.id} newsItem={news} />
        ))}
      </div>
    </div>
  );
};

export default DashboardPage;
