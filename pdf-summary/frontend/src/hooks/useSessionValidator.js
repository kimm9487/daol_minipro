import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * 세션 유효성을 주기적으로 검증하고, 강제 로그아웃 감지 시 처리
 * @param {number} checkInterval - 확인 간격 (밀리초), 기본값 600000 (10분)
 */
export const useSessionValidator = (checkInterval = 600000) => {
  const navigate = useNavigate();

  useEffect(() => {
    const validateSession = async () => {
      try {
        const userDbId = localStorage.getItem('userDbId');
        const sessionToken = localStorage.getItem('session_token');

        console.log('세션 검증 시작:', { userDbId, sessionToken: sessionToken ? 'exists' : 'missing' });

        // 로그인 정보가 없으면 검증 안 함
        if (!userDbId || !sessionToken) {
          console.log('로그인 정보 없음, 검증 스킵');
          return;
        }

        const validateUrl = `http://localhost:8000/auth/sessions/validate?user_id=${userDbId}&session_token=${sessionToken}`;
        console.log('검증 URL:', validateUrl);

        const response = await fetch(validateUrl, {
          method: 'GET',
          cache: 'no-store'
        });

        console.log('검증 응답 상태:', response.status);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: 세션 검증 실패`);
        }

        const data = await response.json();
        console.log('검증 결과:', data);

        if (!data.is_valid) {
          // 강제 로그아웃된 경우
          if (data.reason === '강제 로그아웃') {
            console.warn('강제 로그아웃 감지됨');
            alert('관리자에 의해 강제 로그아웃 되었습니다.');
          } else {
            console.warn('세션 무효화:', data.reason);
            alert(`세션이 무효화되었습니다: ${data.reason}`);
          }

          // localStorage 초기화
          console.log('localStorage 초기화 중...');
          localStorage.removeItem('userDbId');
          localStorage.removeItem('userName');
          localStorage.removeItem('userId');
          localStorage.removeItem('session_token');

          // 강제 로그아웃 플래그를 sessionStorage에 저장 (다른 탭 감지용)
          sessionStorage.setItem('forceLoggedOut', 'true');
          sessionStorage.removeItem('terminatedUserId'); // 정리

          // 로그인 페이지로 이동
          console.log('로그인 페이지로 이동');
          navigate('/login');
        }
      } catch (err) {
        console.error('세션 검증 중 오류:', err);
        // 에러가 발생해도 계속 진행 (네트워크 일시적 오류 등)
      }
    };

    // 현재 사용자 ID 확인
    const userDbId = localStorage.getItem('userDbId');
    const terminatedUserId = sessionStorage.getItem('terminatedUserId');
    const currentUserId = userDbId ? parseInt(userDbId) : null;
    
    // 자신이 강제 로그아웃 대상인지 확인
    const isForceLogoutTarget = terminatedUserId && currentUserId === parseInt(terminatedUserId);
    
    if (isForceLogoutTarget) {
      console.warn('⚠️ 현재 사용자가 강제 로그아웃 대상입니다! 즉시 검증 + 5초 주기로 설정');
      
      // 즉시 검증
      validateSession();
      
      // 5초 주기로 검증
      const interval = setInterval(validateSession, 5000);
      return () => clearInterval(interval);
    } else {
      // 일반 사용자: 지정된 주기로 검증 (기본 10분)
      console.log(`일반 검증 설정: ${checkInterval}ms 주기`);
      
      // 초기 검증 (약간 지연)
      const initialTimer = setTimeout(validateSession, 100);
      
      // 주기적 검증 설정
      const interval = setInterval(validateSession, checkInterval);
      
      return () => {
        clearTimeout(initialTimer);
        clearInterval(interval);
      };
    }
  }, [navigate, checkInterval]);
};
