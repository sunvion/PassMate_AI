# Next.js 16 및 React 19 지원을 위한 Node 22 LTS Alpine 버전
FROM node:22-alpine

WORKDIR /app

# Alpine 리눅스 표준 패키지 관리자를 사용하여 필수 도구 설치
RUN apk update && apk add --no-cache curl bash

# 1. 의존성 정의 파일들만 먼저 복사 (빌드 캐시 최적화)
COPY package*.json ./

# 2. 패키지 설치
RUN npm install

# 3. 나머지 모든 소스코드 복사
COPY . .

# 3000번 포트 개방
EXPOSE 3000

# 4. 개발 서버 즉시 실행
CMD ["npm", "run", "dev"]