# PDF Summary Frontend

React + Vite 기반 프론트엔드입니다.
문서(PDF·HWP) 업로드·OCR·요약·번역, 대화형 질의응답, 결제 연동, 관리자 대시보드 UI를 제공합니다.

## 1. 주요 기능

- 로그인 / 회원가입 / 소셜 로그인(Kakao)
- PDF·HWP 문서 업로드, OCR 모델 선택, 요약·번역
- 문서 기반 대화형 질의응답 (Socket.IO)
- 마이페이지 (이력 조회, 프로필 관리)
- 전체 요약 목록 (UserList): 결제 정책 UI 포함
  - 공개+중요+미결제 문서에 결제 버튼 표시
  - 결제 완료 시 배지·열람 상태 즉시 갱신
- 관리자 대시보드 (사용자·문서·DB 상태·Chroma 상태·결제 로그·활성 세션)
- KakaoPay 결제 팝업 콜백 처리
- 전역 가이드 챗봇 (GuideChatbot)

## 2. 기술 스택

| 패키지 | 버전 |
| --- | --- |
| react | ^19.2.0 |
| react-dom | ^19.2.0 |
| react-router-dom | ^7.13.1 |
| socket.io-client | ^4.8.3 |
| react-hot-toast | ^2.6.0 |
| date-fns | ^4.1.0 |
| vite | ^7.3.1 |

## 3. 폴더 구조

```text
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── Header.css
│   │   ├── WebSocketChat.jsx       # Socket.IO 채팅 컴포넌트
│   │   ├── websocketchat/
│   │   └── GuideChatbot/           # 전역 가이드 챗봇
│   │       └── GuideChatbot.jsx
│   ├── config/
│   │   └── api.js                  # API·Socket URL 설정
│   ├── hooks/
│   │   ├── useLogin.js
│   │   ├── useLogout.js
│   │   ├── useRegister.js
│   │   ├── usePdfSummary.js
│   │   ├── useUserList.js
│   │   ├── useDocumentHistory.js
│   │   ├── useSessionValidator.js
│   │   └── useAuthRedirect.js
│   ├── pages/
│   │   ├── HomeHub/                # 홈 허브
│   │   ├── PdfSummary/             # 문서 업로드·OCR·요약·번역
│   │   ├── ChatSummary/            # 문서 기반 대화형 Q&A
│   │   ├── MyPage/                 # 이력 조회·프로필 관리
│   │   ├── UserList/               # 전체 요약 목록·결제
│   │   ├── AdminDashboard/         # 통합 관리자 대시보드
│   │   │   ├── index.jsx
│   │   │   ├── UserManagement.jsx
│   │   │   ├── DocumentList.jsx
│   │   │   ├── DatabaseStatus.jsx
│   │   │   ├── ChromaStatus.jsx
│   │   │   ├── PaymentLogList.jsx
│   │   │   └── ActiveSessions.jsx
│   │   ├── Login/
│   │   ├── Register/
│   │   └── Payment/
│   │       ├── KakaoSuccess.jsx    # 결제 성공 콜백
│   │       └── KakaoFail.jsx       # 결제 실패 콜백
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
└── package.json
```

## 4. 주요 라우트

| 경로 | 접근 | 페이지 |
| --- | --- | --- |
| /login | 공개 | Login |
| /register | 공개 | Register |
| /payments/kakao/success | 공개 | KakaoSuccess |
| /payments/kakao/fail | 공개 | KakaoFail |
| / | 보호 | HomeHub |
| /pdf-summary | 보호 | PdfSummary |
| /chat-summary | 보호 | ChatSummary |
| /mypage | 보호 | MyPage |
| /userlist | 보호 | UserList |
| /admin | 보호 | AdminDashboard |

> 결제 콜백 라우트는 팝업에서 열리므로 세션 검증 리디렉트 대상에서 제외합니다.

## 5. API 설정

파일: `src/config/api.js`

```js
export const API_ORIGIN   // VITE_API_URL 또는 http://{hostname}:{VITE_API_PORT|8000}
export const SOCKET_ORIGIN // VITE_SOCKET_URL 또는 ws://{hostname}:{VITE_SOCKET_PORT|8001}
export const API_BASE      // {API_ORIGIN}/api
export const buildApiUrl(path)  // {API_ORIGIN}{path}
```

프론트 `.env` 예시:

```env
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=ws://localhost:8001
```

Docker Compose에서는 `VITE_API_URL`, `VITE_SOCKET_URL`을 컨테이너 환경 변수로 주입합니다.

## 6. 실행 방법

```bash
npm install
npm run dev
```

- 개발 서버 기본: http://localhost:5173

빌드/검증:

```bash
npm run build
npm run preview
npm run lint
```

## 7. 결제 연동 흐름

1. UserList에서 결제 대상 문서 클릭
2. `POST /api/payments/kakao/ready` 호출 → `next_redirect_pc_url` 수신
3. KakaoPay 결제창을 새 팝업으로 열기
4. 팝업 콜백(`/payments/kakao/success|fail`)에서 `POST /api/payments/kakao/approve` 처리
5. `window.opener.postMessage`로 부모창(UserList) 배지·열람 상태 즉시 갱신

## 8. 개발 유의사항

- 로그인 세션 검증은 `useSessionValidator` 훅에서 수행합니다.
- 결제 콜백 페이지는 `useSessionValidator`에 의해 리디렉트되지 않도록 공개 라우트로 유지합니다.
- 결제 정책 UI는 백엔드 응답 필드 `requires_payment`, `is_paid_by_viewer`에 의존합니다.
- GuideChatbot은 `App.jsx`에서 전역으로 렌더링되어 모든 페이지에 표시됩니다.
- `useRegister.js` 훅이 회원가입 폼 로직을 담당합니다.
