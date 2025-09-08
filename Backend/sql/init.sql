-- NewsBite Database Initialization Script
-- Enable pgvector extension for vector similarity search

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create basic indexes for performance
-- These will be supplemented by Alembic migrations

-- Function to calculate cosine similarity for news embeddings
CREATE OR REPLACE FUNCTION cosine_similarity(a vector, b vector)
RETURNS float AS $$
BEGIN
    RETURN 1 - (a <=> b);
END;
$$ LANGUAGE plpgsql;

-- Insert default categories
INSERT INTO categories (name, display_name, description, color, icon, sort_order) VALUES
('politics', '정치', '정치 관련 뉴스', '#FF6B6B', 'government', 1),
('economy', '경제', '경제 및 금융 관련 뉴스', '#4ECDC4', 'trending-up', 2),
('society', '사회', '사회 및 사건사고 관련 뉴스', '#45B7D1', 'users', 3),
('science', '과학기술', '과학기술 및 IT 관련 뉴스', '#96CEB4', 'cpu', 4),
('culture', '문화', '문화 및 예술 관련 뉴스', '#FFEAA7', 'palette', 5),
('sports', '스포츠', '스포츠 관련 뉴스', '#DDA0DD', 'activity', 6),
('international', '국제', '해외 및 국제 관련 뉴스', '#98D8C8', 'globe', 7),
('entertainment', '연예', '연예 및 오락 관련 뉴스', '#F7DC6F', 'star', 8)
ON CONFLICT (name) DO NOTHING;

-- Insert major Korean companies
INSERT INTO companies (name, display_name, ticker_symbol, market, industry) VALUES
('삼성전자', '삼성전자', '005930', 'KOSPI', '반도체'),
('SK하이닉스', 'SK하이닉스', '000660', 'KOSPI', '반도체'),
('네이버', '네이버', '035420', 'KOSPI', 'IT서비스'),
('카카오', '카카오', '035720', 'KOSPI', 'IT서비스'),
('LG화학', 'LG화학', '051910', 'KOSPI', '화학'),
('현대자동차', '현대자동차', '005380', 'KOSPI', '자동차'),
('기아', '기아', '000270', 'KOSPI', '자동차'),
('포스코홀딩스', '포스코홀딩스', '005490', 'KOSPI', '철강'),
('KB금융', 'KB금융', '105560', 'KOSPI', '금융'),
('신한지주', '신한지주', '055550', 'KOSPI', '금융')
ON CONFLICT (name) DO NOTHING;