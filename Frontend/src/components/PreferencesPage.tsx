import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

interface Category {
  id: number
  name: string
  description: string
  color: string
}

interface Company {
  id: number
  name: string
  description: string
  logo_url?: string
}

const PreferencesPage: React.FC = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [selectedCategories, setSelectedCategories] = useState<number[]>([])
  const [selectedCompanies, setSelectedCompanies] = useState<number[]>([])
  
  // 임시 데이터 (실제로는 API에서 가져와야 함)
  const availableCategories: Category[] = [
    { id: 1, name: '정치', description: '국정 운영, 정책, 정치인 소식', color: 'bg-red-100 text-red-800' },
    { id: 2, name: '경제', description: '금융, 증시, 부동산, 경제정책', color: 'bg-blue-100 text-blue-800' },
    { id: 3, name: '사회', description: '사건사고, 사회 이슈, 지역 소식', color: 'bg-green-100 text-green-800' },
    { id: 4, name: 'IT/과학', description: '기술, 과학, 연구 개발 소식', color: 'bg-purple-100 text-purple-800' },
    { id: 5, name: '문화/연예', description: '영화, 음악, 연예계 소식', color: 'bg-pink-100 text-pink-800' },
  ]
  
  const availableCompanies: Company[] = [
    { id: 1, name: '삼성전자', description: '대한민국 대표 전자기업' },
    { id: 2, name: 'LG전자', description: '생활가전 및 전자제품 제조업체' },
    { id: 3, name: 'SK하이닉스', description: '메모리 반도체 전문기업' },
    { id: 4, name: '현대자동차', description: '자동차 제조업체' },
    { id: 5, name: 'NAVER', description: '국내 대표 IT기업' },
  ]

  const handleCategoryToggle = (categoryId: number) => {
    setSelectedCategories(prev => 
      prev.includes(categoryId) 
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    )
  }

  const handleCompanyToggle = (companyId: number) => {
    setSelectedCompanies(prev => 
      prev.includes(companyId) 
        ? prev.filter(id => id !== companyId)
        : [...prev, companyId]
    )
  }

  const handleSavePreferences = async () => {
    setLoading(true)
    try {
      // API 호출 대신 임시로 로컬스토리지에 저장
      localStorage.setItem('user-preferences', JSON.stringify({
        categories: selectedCategories,
        companies: selectedCompanies
      }))
      
      alert('관심사가 저장되었습니다!')
    } catch (error) {
      console.error('관심사 저장 오류:', error)
      alert('관심사 저장에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // 페이지 로드시 저장된 관심사 불러오기
    const savedPreferences = localStorage.getItem('user-preferences')
    if (savedPreferences) {
      const preferences = JSON.parse(savedPreferences)
      setSelectedCategories(preferences.categories || [])
      setSelectedCompanies(preferences.companies || [])
    }
  }, [])

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            로그인이 필요합니다
          </h2>
          <p className="text-gray-600">
            관심사 설정을 위해 로그인해주세요.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">
              관심사 설정 ⚙️
            </h1>
            <p className="mt-2 text-gray-600">
              개인 맞춤형 뉴스를 받기 위해 관심 있는 분야와 기업을 선택해주세요.
            </p>
          </div>

          <div className="p-6">
            {/* 카테고리 선택 섹션 */}
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                📰 관심 뉴스 카테고리
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                매일 받아보고 싶은 뉴스 카테고리를 선택하세요.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableCategories.map(category => (
                  <div
                    key={category.id}
                    className={`
                      border-2 rounded-lg p-4 cursor-pointer transition-colors
                      ${selectedCategories.includes(category.id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                      }
                    `}
                    onClick={() => handleCategoryToggle(category.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">
                          {category.name}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {category.description}
                        </p>
                      </div>
                      <div className={`
                        w-5 h-5 rounded border-2 flex items-center justify-center
                        ${selectedCategories.includes(category.id)
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-300'
                        }
                      `}>
                        {selectedCategories.includes(category.id) && (
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 기업 선택 섹션 */}
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                🏢 관심 기업
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                뉴스를 추적하고 감정분석을 받고 싶은 기업을 선택하세요.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableCompanies.map(company => (
                  <div
                    key={company.id}
                    className={`
                      border-2 rounded-lg p-4 cursor-pointer transition-colors
                      ${selectedCompanies.includes(company.id)
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300'
                      }
                    `}
                    onClick={() => handleCompanyToggle(company.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">
                          {company.name}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {company.description}
                        </p>
                      </div>
                      <div className={`
                        w-5 h-5 rounded border-2 flex items-center justify-center
                        ${selectedCompanies.includes(company.id)
                          ? 'border-green-500 bg-green-500'
                          : 'border-gray-300'
                        }
                      `}>
                        {selectedCompanies.includes(company.id) && (
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 저장 버튼 */}
            <div className="flex justify-center pt-6 border-t border-gray-200">
              <button
                onClick={handleSavePreferences}
                disabled={loading}
                className={`
                  px-8 py-3 rounded-lg font-medium text-white
                  ${loading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700'
                  }
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                  transition-colors
                `}
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    저장 중...
                  </span>
                ) : (
                  '관심사 저장하기'
                )}
              </button>
            </div>

            {/* 선택 요약 */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">선택 요약</h3>
              <p className="text-sm text-gray-600">
                카테고리 {selectedCategories.length}개, 관심기업 {selectedCompanies.length}개가 선택되었습니다.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PreferencesPage