import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Header.css'; // 스타일 파일도 따로 만들면 깔끔해요!

function Header({ setIsLoggedIn }) {
  const navigate = useNavigate();
  // 로그인 상태를 관리할 state
  const [isLoggedInLocal, setIsLoggedInLocal] = useState(false);
  const [userName, setUserName] = useState('');

  // 컴포넌트가 로드될 때 로그인 상태 확인
  useEffect(() => {
    const status = localStorage.getItem("isLoggedIn") === "true";
    const name = localStorage.getItem("userName");
    setIsLoggedInLocal(status);
    setUserName(name || '');
  }, []);

  const handleLogout = async () => {
    try {
      const userDbId = localStorage.getItem('userDbId');
      const sessionToken = localStorage.getItem('session_token');
      
      console.log('로그아웃 시작:', { userDbId, sessionToken: sessionToken ? 'exists' : 'missing' });
      
      // 백엔드로 로그아웃 요청 (선택사항, 실패해도 진행)
      if (userDbId) {
        try {
          const formData = new FormData();
          formData.append('user_id', userDbId);
          if (sessionToken) {
            formData.append('session_token', sessionToken);
          }
          
          const response = await fetch('http://localhost:8000/auth/logout', {
            method: 'POST',
            body: formData
          });
          console.log('백엔드 로그아웃 응답:', response.status, response.statusText);
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('백엔드 로그아웃 실패:', errorData);
          }
        } catch (err) {
          console.error('백엔드 로그아웃 요청 실패 (계속 진행):', err);
        }
      }
      
      // localStorage 초기화
      console.log('localStorage 초기화 중...');
      localStorage.removeItem("isLoggedIn");
      localStorage.removeItem("userName");
      localStorage.removeItem("userId"); 
      localStorage.removeItem("userDbId");
      localStorage.removeItem("session_token");
      
      // sessionStorage도 초기화
      sessionStorage.removeItem('forceLoggedOut');
      
      setIsLoggedInLocal(false);
      
      // App 컴포넌트의 상태도 업데이트
      if (setIsLoggedIn) {
        setIsLoggedIn(false);
      }
      
      console.log('로그아웃 완료, 로그인 페이지로 이동');
      alert("로그아웃 되었습니다.");
      navigate("/login");
    } catch (err) {
      console.error('로그아웃 중 오류:', err);
      alert('로그아웃 중 오류가 발생했습니다.');
    }
  };

  return (
    <nav className="header-nav">
      <div className="header-logo">
        <Link to="/">PDF DAOL</Link>
      </div>
      <div className="header-menu">
        {isLoggedInLocal ? (
          <>
            <span className="user-welcome"><b>{userName}</b>님 환영합니다</span>
            <button onClick={() => navigate("/mypage")} className="nav-btn">마이페이지</button>
            <button onClick={handleLogout} className="nav-btn logout">로그아웃</button>
          </>
        ) : (
          <>
            <button onClick={() => navigate("/login")} className="nav-btn">로그인</button>
            <button onClick={() => navigate("/register")} className="nav-btn register">회원가입</button>
          </>
        )}
      </div>
    </nav>
  );
}

export default Header;