import React from 'react';
import { Search, Bell, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-bold text-blue-600">NewsBite</h1>
            <nav className="hidden md:flex items-center space-x-1">
              <Button variant="ghost" className="font-semibold">뉴스</Button>
              <Button variant="ghost" className="text-gray-600 font-semibold">인사이트</Button>
              <Button variant="ghost" className="text-gray-600 font-semibold">데이터</Button>
            </nav>
          </div>
          <div className="flex items-center space-x-2">
            <div className="relative hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input
                type="text"
                placeholder="관심있는 키워드를 검색해보세요"
                className="pl-10 w-64 bg-gray-100 border-transparent focus:bg-white focus:border-blue-500"
              />
            </div>
            <Button variant="ghost" size="icon" className="hover:bg-gray-100 rounded-full">
              <Bell className="h-5 w-5 text-gray-600" />
            </Button>
            <Button variant="ghost" size="icon" className="hover:bg-gray-100 rounded-full">
              <User className="h-5 w-5 text-gray-600" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
