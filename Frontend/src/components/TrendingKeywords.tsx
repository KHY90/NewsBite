import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';

type Keyword = {
  rank: number;
  word: string;
  change: 'up' | 'down' | 'new';
};

const keywords: Keyword[] = [
    { rank: 1, word: '생성형 AI', change: 'up' },
    { rank: 2, word: '온디바이스', change: 'new' },
    { rank: 3, word: '공급망 재편', change: 'down' },
    { rank: 4, word: '디지털 자산', change: 'up' },
    { rank: 5, word: '유럽 시장', change: 'new' },
    { rank: 6, word: '반도체 수출', change: 'down' },
    { rank: 7, word: '전기차 보조금', change: 'up' },
];

const TrendIcon = ({ change }: { change: Keyword['change'] }) => {
  switch (change) {
    case 'up':
      return <ArrowUp className="h-4 w-4 text-red-500" />;
    case 'down':
      return <ArrowDown className="h-4 w-4 text-blue-500" />;
    case 'new':
      return <Minus className="h-4 w-4 text-gray-500" />;
    default:
      return null;
  }
};

const TrendingKeywords: React.FC = () => {
  return (
    <Card className="border-gray-200">
      <CardHeader>
        <CardTitle className="text-base font-bold text-gray-800">실시간 토픽</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-1">
          {keywords.map((keyword) => (
            <li key={keyword.rank}>
              <a href="#" className="flex items-center justify-between p-2 rounded-md hover:bg-gray-100 transition-colors">
                <div className="flex items-center">
                  <span className="text-sm font-bold w-6 text-center text-blue-600">{keyword.rank}</span>
                  <span className="text-sm font-medium text-gray-700">{keyword.word}</span>
                </div>
                <TrendIcon change={keyword.change} />
              </a>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
};

export default TrendingKeywords;
