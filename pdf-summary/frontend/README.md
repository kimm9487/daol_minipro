# PDF Summary Frontend

React + Vite 기반 프론트엔드입니다.
문서 업로드/OCR/요약/번역, 대화형 질의응답, 결제 흐름, 마이페이지, 관리자 대시보드 UI를 제공합니다.

## 1. 핵심 역할

- 인증 UI: 로그인/회원가입/소셜 로그인 진입
- 문서 UI: 업로드, OCR 선택, 요약/번역 결과 확인
- 대화 UI: Socket.IO 기반 문서 질의응답
- 마이페이지: 이력 조회, 프로필 수정, 회원탈퇴
- 결제 UI: KakaoPay 팝업 콜백 및 상태 갱신
- 관리자 UI: 사용자/문서/상태/결제 로그 모니터링

## 2. 최근 반영 사항 (2026-04)

### MyPage 프로필 정책 반영

- 프로필 수정 모달에서 이메일 변경을 비활성화했습니다.
- 현재 이메일은 조회 전용이며, 저장 시 이메일 필드를 전송하지 않습니다.

### MyPage 회원탈퇴 UX 개선

- 탈퇴 확인을 브라우저 confirm에서 전용 모달로 변경했습니다.
- 모달에 다음 안내를 명시합니다.
  - 탈퇴에 대한 책임 고지
  - 탈퇴 후 계정/문서/히스토리 복구 불가

## 3. 기술 스택

| 패키지 | 버전 |
| --- | --- |
| react | ^19.2.0 |
| react-dom | ^19.2.0 |
| react-router-dom | ^7.13.1 |
| react-hot-toast | ^2.6.0 |
| socket.io-client | ^4.8.3 |
| date-fns | ^4.1.0 |
| vite | ^7.3.1 |

## 4. 디렉토리 구조

```text
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── WebSocketChat.jsx
│   │   └── GuideChatbot/
│   ├── config/
│   │   └── api.js
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
│   │   ├── HomeHub/
│   │   ├── PdfSummary/
│   │   ├── ChatSummary/
│   │   ├── MyPage/
│   │   │   ├── index.jsx
│   │   │   ├── EditProfileModal.jsx
│   │   │   └── WithdrawConfirmModal.jsx
│   │   ├── UserList/
│   │   ├── AdminDashboard/
│   │   ├── Login/
│   │   ├── Register/
│   │   └── Payment/
│   │       ├── KakaoSuccess.jsx
│   │       └── KakaoFail.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
└── package.json
```

## 5. 라우트 구성

| Route | 접근 | 설명 |
| --- | --- | --- |
| /login | 공개 | 로그인 |
| /register | 공개 | 회원가입 |
| /payments/kakao/success | 공개 | 결제 성공 콜백 |
| /payments/kakao/fail | 공개 | 결제 실패 콜백 |
| / | 보호 | HomeHub |
| /pdf-summary | 보호 | 문서 업로드/OCR/요약/번역 |
| /chat-summary | 보호 | 문서 기반 Q&A |
| /mypage | 보호 | 이력/프로필/탈퇴 |
| /userlist | 보호 | 전체 목록/결제 |
| /admin | 보호 | 관리자 대시보드 |

참고:

- 결제 콜백 경로는 팝업에서 열리므로 공개 라우트로 유지합니다.
- App에서 로그인 상태 기준으로 Header와 GuideChatbot 표시를 제어합니다.

## 6. API/소켓 설정

설정 파일: src/config/api.js

```text
API_ORIGIN     : VITE_API_URL 우선, 미설정 시 hostname + VITE_API_PORT(기본 8000)
SOCKET_ORIGIN  : VITE_SOCKET_URL 우선, 미설정 시 ws://hostname + VITE_SOCKET_PORT(기본 8001)
API_BASE       : {API_ORIGIN}/api
buildApiUrl()  : 절대 API URL 생성 유틸
```

예시 env:

```env
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=ws://localhost:8001
```

## 7. 실행 방법

```bash
cd pdf-summary/frontend
npm install
npm run dev
```

검증/배포용:

```bash
npm run lint
npm run build
npm run preview
```

## 8. 주요 화면 흐름

### 결제 흐름

1. UserList에서 결제 대상 문서 선택
2. POST /api/payments/kakao/ready 호출
3. KakaoPay 팝업 오픈
4. /payments/kakao/success 또는 /payments/kakao/fail 콜백 처리
5. window.opener.postMessage로 부모 창 상태 동기화

### MyPage 계정 흐름

- 프로필 수정: 비밀번호 변경 가능, 이메일 변경 비활성
- 회원 탈퇴: WithdrawConfirmModal 확인 후 withdraw API 호출

## 9. 개발 체크포인트

- 세션 검증은 useSessionValidator 훅에서 처리합니다.
- 결제 UI는 requires_payment, is_paid_by_viewer 응답 필드에 의존합니다.
- GuideChatbot은 App 레벨 전역 컴포넌트입니다.
- 탈퇴 모달 도입으로 useDocumentHistory.deleteAccount는 confirm 없이 직접 API를 호출합니다.
