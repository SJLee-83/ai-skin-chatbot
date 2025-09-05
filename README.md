# 🤖 AI 스킨케어 어드바이저 챗봇

**[프로젝트 목표]** 사용자의 피부 데이터(설문, 사진 분석)를 기반으로 개인 맞춤형 스킨케어 솔루션을 제공하는 AI 챗봇 애플리케이션입니다.

**[Live Demo Link]** - [🎥 YouTube 전체 데모 영상 보기 (59초)](https://youtube.com/shorts/Shnw9ZDk6kM?feature=share)

---

## 📸 데모 영상 및 스크린샷

| 데모 GIF (자동 재생) | 사용자 맞춤 예상 질문 | 지능형 제품 추천 | 상세 설명 및 프리셋 저장 |
| :---: | :---: | :---: | :---: |
| ![앱 데모 GIF](docs/images/demo.gif) | ![사용자 맞춤 예상 질문](docs/images/screenshot-questions.png) | ![지능형 제품 추천](docs/images/screenshot-recommend.png) | ![상세 설명 및 프리셋 저장](docs/images/screenshot-preset.png) |
---

## ✨ 주요 기능

- **👤 개인화된 추천 질문:** 사용자 데이터 분석을 통해 가장 궁금해할 만한 질문을 자동으로 생성하여 제안합니다.
- **🧴 지능형 제품 추천:** 사용자의 질문 의도를 파악하여, 수많은 제품 중 가장 적합한 제품을 RAG(검색 증강 생성) 기술을 활용해 추천합니다.
- **💬 동적 대화 시스템:** 상태(State) 기반으로 대화의 흐름을 관리하여, 단순 문답을 넘어 제품 상세 설명, 프리셋 저장 등 다단계의 상호작용이 가능합니다.
- **🔄 대화 기록 관리:** 이전 대화 내용을 기억하고 이어갈 수 있으며, 언제든지 대화 기록을 초기화할 수 있습니다.
- **🎨 직관적인 UI/UX:** 타이핑 애니메이션, 빠른 응답 버튼 등을 통해 사용자가 실제 대화처럼 느낄 수 있는 몰입감 있는 채팅 환경을 제공합니다.

---

## 🏗️ 시스템 아키텍처

이 프로젝트는 최신 기술 스택을 활용하여 프론트엔드와 백엔드가 명확하게 분리된 MSA(마이크로서비스 아키텍처) 구조로 설계되었습니다.

![시스템 아키텍처 다이어그램](docs/images/architecture.png)

---

## 🛠️ 기술 스택

### Backend
- **Python 3.11+**
- **FastAPI**: 현대적이고 빠른 Python 웹 프레임워크
- **Uvicorn**: ASGI 서버
- **PostgreSQL**: 주 데이터베이스
- **Psycopg2**: Python PostgreSQL 어댑터
- **Redis**: 채팅 세션 관리를 위한 인메모리 캐시
- **Azure OpenAI Service (gpt-4o-mini)**: 핵심 AI 추론 및 임베딩 모델
- **python-dotenv**: 환경 변수 관리

### Frontend
- **React Native (Expo)**: 크로스 플랫폼 모바일 앱 개발 프레임워크
- **JavaScript (ES6+)**
- **Axios**: HTTP 통신 라이브러리
- **React Navigation**: 화면 전환 및 라우팅
