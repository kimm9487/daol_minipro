import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * 세션 유효성을 주기적으로 검증하고, 강제 로그아웃 감지 시 처리
 * @param {number} checkInterval - 확인 간격 (밀리초), 기본값 30000 (30초)
 */
export const useSessionValidator = (checkInterval = 30000) => {
  const navigate = useNavigate();

  useEffect(() => {
    const validateSession = async () => {
      try {
        const userDbId = localStorage.getItem('userDbId');
        const sessionToken = localStorage.getItem('session_token');

        // 로그인 정보가 없으면 검증 안 함
        if (!userDbId || !sessionToken) {
          return;
        }

        const response = await fetch(
          `http://localhost:8000/auth/sessions/validate?user_id=${userDbId}&session_token=${sessionToken}`,
          {
            method: 'GET',
            cache: 'no-store'
          }
        );

        if (!response.ok) {
          throw new Error('세션 검증 실패');
        }

        const data = await response.json();

        if (!data.is_valid) {
          // 강제 로그아웃된 경우
          if (data.reason === '강제 로그아웃') {
            alert('관리자에 의해 강제 로그아웃 되었습니다.');
          } else {
            alert(`세션이 무효화되었습니다: ${data.reason}`);
          }

          // localStorage 초기화
          localStorage.removeItem('userDbId');
          localStorage.removeItem('userName');
          localStorage.removeItem('userId');
          localStorage.removeItem('session_token');

          // 로그인 페이지로 이동
          navigate('/login');
        }
      } catch (err) {
        console.error('세션 검증 중 오류:', err);
        // 에러가 발생해도 계속 진행 (네트워크 일시적 오류 등)
      }
    };

    // 초기 검증
    validateSession();

    // 주기적 검증 설정
    const interval = setInterval(validateSession, checkInterval);

    return () => clearInterval(interval);
  }, [navigate, checkInterval]);
};
