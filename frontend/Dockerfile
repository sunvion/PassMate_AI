# Next.js 16 및 React 19 지원을 위한 Node 22 LTS Alpine 버전
FROM node:22-alpine

WORKDIR /app

# Alpine 리눅스 표준 패키지 관리자를 사용하여 필수 도구 설치
RUN apk update && apk add --no-cache curl bash

# 컨테이너가 켜진 직후 실행될 실행 스크립트
# 1. app/ 폴더가 없으면 임시 디렉터리에서 스타터 팩을 충돌 없이 완전히 구운 뒤 복사함
# 2. 의존성 패키지 재검증 후 개발 서버 실행
CMD ["/bin/bash", "-c", "\
  if [ ! -d 'app' ]; then \
    echo '🚀 스타터 팩이 감지되지 않아 임시 공간에서 인프라 생성을 시작합니다...'; \
    mkdir -p /tmp/install && cd /tmp/install && \
    npx create-next-app@16.2.9 . \
      --ts \
      --tailwind \
      --eslint \
      --app \
      --src-dir no \
      --import-alias '@/*' \
      --use-npm --skip-install --force && \
    echo '🚚 생성된 소스코드를 작업 디렉터리로 안전하게 이동 중...'; \
    cp -r /tmp/install/* /app/ 2>/dev/null || true && \
    cd /app && rm -rf /tmp/install; \
  fi && \
  echo '📦 의존성 라이브러리 검증 및 셋업 중...' && \
  npm install && \
  npm run dev"]