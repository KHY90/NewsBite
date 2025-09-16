import React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ThumbsUp, MessageSquare, Share2 } from 'lucide-react';

type NewsCardProps = {
  article: {
    title: string;
    source: string;
    time: string;
    content: string;
    category: string;
    imageUrl?: string;
  };
};

const NewsCard: React.FC<NewsCardProps> = ({ article }) => {
  return (
    <Card className="mb-6 bg-white overflow-hidden hover:shadow-md transition-shadow duration-200 border border-gray-200">
      <div className="flex">
        <div className="flex-grow p-6">
          <CardHeader className="p-0 mb-4">
            <CardTitle className="text-lg font-semibold text-gray-800 hover:text-blue-600 cursor-pointer">{article.title}</CardTitle>
            <div className="flex items-center text-xs text-gray-500 pt-2">
              <span>{article.source}</span>
              <span className="mx-2">·</span>
              <span>{article.time}</span>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <p className="text-sm text-gray-600 leading-relaxed">{article.content}</p>
          </CardContent>
        </div>
        {article.imageUrl && (
          <div className="w-48 flex-shrink-0 p-4">
            <img src={article.imageUrl} alt={article.title} className="rounded-lg object-cover w-full h-full aspect-square" />
          </div>
        )}
      </div>
      <CardFooter className="bg-white py-2 px-6 flex justify-between items-center border-t border-gray-100">
        <div className="flex space-x-2 text-gray-500">
            <Badge variant="outline">{article.category}</Badge>
        </div>
        <div className="flex items-center space-x-1">
            <button className="p-2 rounded-full hover:bg-gray-100">
                <ThumbsUp className="h-4 w-4 text-gray-600" />
            </button>
            <button className="p-2 rounded-full hover:bg-gray-100">
                <MessageSquare className="h-4 w-4 text-gray-600" />
            </button>
            <button className="p-2 rounded-full hover:bg-gray-100">
                <Share2 className="h-4 w-4 text-gray-600" />
            </button>
        </div>
      </CardFooter>
    </Card>
  );
};

export default NewsCard;
