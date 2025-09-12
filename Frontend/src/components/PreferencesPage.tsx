import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { Navigate } from "react-router-dom";
import Spinner from "./Spinner";

// 임시 데이터
const availableCategories = [
  { id: 1, name: "정치", description: "국정 운영, 정책, 정치인 소식" },
  { id: 2, name: "경제", description: "금융, 증시, 부동산, 경제정책" },
  { id: 3, name: "사회", description: "사건사고, 사회 이슈, 지역 소식" },
  { id: 4, name: "IT/과학", description: "기술, 과학, 연구 개발 소식" },
  { id: 5, name: "문화/연예", description: "영화, 음악, 연예계 소식" },
];

const availableCompanies = [
  { id: 1, name: "삼성전자", description: "대한민국 대표 전자기업" },
  { id: 2, name: "LG전자", description: "생활가전 및 전자제품 제조업체" },
  { id: 3, name: "SK하이닉스", description: "메모리 반도체 전문기업" },
  { id: 4, name: "현대자동차", description: "자동차 제조업체" },
  { id: 5, name: "NAVER", description: "국내 대표 IT기업" },
];

const PreferencesPage: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<number[]>([]);

  const handleToggle = (id: number, type: "category" | "company") => {
    const setter =
      type === "category" ? setSelectedCategories : setSelectedCompanies;
    setter((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleSavePreferences = async () => {
    setLoading(true);
    try {
      // 실제 API 호출 로직으로 대체 필요
      console.log("Saving:", {
        categories: selectedCategories,
        companies: selectedCompanies,
      });
      await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate API call
      alert("관심사가 저장되었습니다!");
    } catch (error) {
      console.error("관심사 저장 오류:", error);
      alert("관심사 저장에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 임시 로직: 실제로는 API를 통해 사용자 설정 불러오기
    setSelectedCategories([2, 4]);
    setSelectedCompanies([1, 5]);
  }, []);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="container py-12">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-h2 font-bold text-gray-900">관심사 설정</h1>
          <p className="mt-2 text-md text-gray-600">
            맞춤형 뉴스 브리핑을 위해 관심 분야와 기업을 선택해주세요.
          </p>
        </div>

        <div className="space-y-12">
          {/* 카테고리 섹션 */}
          <div>
            <h2 className="text-h3 font-semibold text-gray-900 mb-4">
              뉴스 카테고리
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {availableCategories.map((category) => (
                <PreferenceCard
                  key={`cat-${category.id}`}
                  item={category}
                  isSelected={selectedCategories.includes(category.id)}
                  onToggle={() => handleToggle(category.id, "category")}
                />
              ))}
            </div>
          </div>

          {/* 기업 섹션 */}
          <div>
            <h2 className="text-h3 font-semibold text-gray-900 mb-4">
              관심 기업
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {availableCompanies.map((company) => (
                <PreferenceCard
                  key={`com-${company.id}`}
                  item={company}
                  isSelected={selectedCompanies.includes(company.id)}
                  onToggle={() => handleToggle(company.id, "company")}
                />
              ))}
            </div>
          </div>
        </div>

        {/* 저장 버튼 */}
        <div className="mt-12 pt-8 border-t border-line-soft text-center">
          <button
            onClick={handleSavePreferences}
            disabled={loading}
            className="btn btn-primary btn-lg disabled:opacity-50 flex items-center justify-center"
          >
            {loading ? (
              <>
                <Spinner size="sm" color="border-white" className="mr-3" />
                <span>저장 중...</span>
              </>
            ) : (
              "설정 저장하기"
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

const PreferenceCard = ({ item, isSelected, onToggle }: any) => (
  <div
    className={`card p-4 flex items-center justify-between cursor-pointer transition-all duration-200 ${
      isSelected
        ? "border-brand-primary ring-2 ring-brand-primarySoft"
        : "border-line-soft hover:border-line-strong"
    }`}
    onClick={onToggle}
  >
    <div className="flex-1">
      <h3 className="font-semibold text-gray-900">{item.name}</h3>
      <p className="text-sm text-gray-600 mt-1">{item.description}</p>
    </div>
    <div
      className={`w-6 h-6 rounded-full flex items-center justify-center border-2 ${
        isSelected ? "border-brand-primary bg-brand-primary" : "border-gray-300"
      }`}
    >
      {isSelected && (
        <svg
          className="w-4 h-4 text-white"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
            clipRule="evenodd"
          />
        </svg>
      )}
    </div>
  </div>
);

export default PreferencesPage;
