from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_router import api_router  # 👈 분리한 라우터 통합 파일 로드 
from app.core.config import settings      # 👈 환경 설정 객체 로드

# 1. FastAPI 애플리케이션 초기화 
app = FastAPI(
    title="PassMate AI API Server", 
    description="PassCertificate 소셜 로그인 및 RAG 백엔드 시스템 API",  
    version="1.0.0" 
)

# 2. 프론트엔드 컨테이너(포트 3001)와의 통신을 위한 CORS 설정 
# settings.py 환경 변수나 .env 파일에 origins 목록을 관리해도 좋습니다.
origins = [
    "http://localhost:3000",   
    "http://127.0.0.1:3000",   
]

app.add_middleware(
    CORSMiddleware,             
    allow_origins=origins,      
    allow_credentials=True,    
    allow_methods=["*"],        
    allow_headers=["*"],       
)

# 3. 핵심 라우터 연결 
# config.py에 정의된 API_V1_STR ("/api/v1") 주소를 접두사(prefix)로 사용하여 모든 라우터를 하나로 묶어 등록합니다. 
app.include_router(api_router, prefix=settings.API_V1_STR)

# 4. 서버 헬스체크용 루트 엔드포인트 
@app.get("/")
async def root(): 
    """
    백엔드 서버 작동 여부 확인용 헬스체크
    """
    return {  
        "status": "healthy",
        "message": "Welcome to PassMate AI Backend API Server"  
    } # 👈 깔끔하게 중괄호로만 끝나야 합니다. 뒷부분의 불필요한 문자열은 모두 지워주세요.