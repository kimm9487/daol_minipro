import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Login.css';

const Login = ({ setIsLoggedIn }) => {
    console.log("🔐 Login 컴포넌트 렌더링됨");
    const [userId, setUserId] = useState('');
    const [userPw, setUserPw] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); // 이전 오류 메시지 초기화
    
    try {
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('user_pw', userPw);
        
        const response = await fetch("http://localhost:8000/auth/login", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            
            // 로그인 정보를 localStorage에 저장
            localStorage.setItem("userName", data.user_name);
            localStorage.setItem("userId", data.user_id);
            localStorage.setItem("userDbId", data.user_db_id);
            localStorage.setItem("isLoggedIn", "true");
            
            // App 컴포넌트의 로그인 상태 업데이트
            if (setIsLoggedIn) {
                setIsLoggedIn(true);
            }
    
            alert(`${data.user_name}님 환영합니다!`);
    
            // 사용자 역할에 따라 리다이렉트 (navigate는 App에서 처리됨)
            // navigate는 제거하고 App.jsx에서 자동 리다이렉트되도록 함
        } else {
            const errorData = await response.json();
            setError(errorData.detail || "로그인에 실패했습니다.");
        }
    } catch (error) {
        console.error("로그인 에러:", error);
        setError("서버 연결에 실패했습니다. 서버가 실행 중인지 확인하세요.");
    }
    };

    return (
        <div className="login-body">
            <div className="login-container">
                <h2>PDF Summary</h2>
                <form onSubmit={handleLogin}>
                    <div className="form-group">
                        <label>아이디</label>
                        <input 
                            type="text" 
                            placeholder="아이디를 입력하세요" 
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                            required 
                        />
                    </div>
                    <div className="form-group">
                        <label>비밀번호</label>
                        <input 
                            type="password" 
                            placeholder="비밀번호를 입력하세요" 
                            value={userPw}
                            onChange={(e) => setUserPw(e.target.value)}
                            required 
                        />
                    </div>
                    {error && <p className="error-msg">{error}</p>}
                    <button type="submit">로그인</button>
                </form>

                <div className="footer-links">
                    계정이 없으신가요? <Link to="/register">회원가입</Link>
                </div>
            </div>
        </div>
    );
};

export default Login;