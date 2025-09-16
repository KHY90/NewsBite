import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

const TodayBriefing: React.FC = () => {
  return (
    <Card className="mb-8 bg-blue-50 border-blue-200">
      <CardHeader>
        <CardTitle className="text-xl text-blue-800">오늘의 브리핑</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-gray-700 mb-4">
          주요 경제 지표와 AI 기술 동향을 중심으로 한 아침 뉴스 요약입니다. 시장의 흐름을 빠르게 파악하고 중요한 기회를 놓치지 마세요.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="bg-white p-3 rounded-lg">
            <h4 className="font-semibold text-sm">NVIDIA, 시총 3조 달러 돌파</h4>
            <p className="text-xs text-gray-600">AI 칩 수요가 폭발하며 새로운 마일스톤을 달성했습니다.</p>
          </div>
          <div className="bg-white p-3 rounded-lg">
            <h4 className="font-semibold text-sm">한국은행, 기준금리 동결 전망</h4>
            <p className="text-xs text-gray-600">물가와 성장 사이의 균형점을 찾고 있습니다.</p>
          </div>
        </div>
        <Button variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-100 hover:text-blue-700">
          전체 브리핑 보기 <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  );
};

export default TodayBriefing;
