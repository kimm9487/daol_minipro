import React from 'react';
import { useNavigate } from 'react-router-dom';

const Header = ({ isAdmin }) => {
    const navigate = useNavigate();

    return (
        <div className="card-header">
            <div className="card-title">PDF 요약 도구 - AI Analysis</div>
            <div className="header-buttons">
                <button
                    className="summary-list-btn"
                    onClick={() => navigate('/userlist')}
                    title="요약 목록 조회"
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                    >
                        <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2" />
                        <line x1="9" y1="12" x2="15" y2="12" />
                        <line x1="9" y1="16" x2="15" y2="16" />
                    </svg>
                    요약 목록 보기
                </button>
                {isAdmin && (
                    <button
                        className="admin-dashboard-btn"
                        onClick={() => navigate('/admin')}
                        title="관리자 대시보드"
                    >
                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                        >
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                        </svg>
                        관리자 대시보드
                    </button>
                )}
            </div>
        </div>
    );
};

export default Header;
