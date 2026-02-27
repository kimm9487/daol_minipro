// src/pages/UserList.jsx
import React, { useState } from "react";
import "./UserList.css";

const UserList = () => {
  const currentUser = localStorage.getItem("userName") || "정재훈";

  const sampleData = [
    {
      id: 1,
      datetime: "2026-02-26 14:32",
      username: "정재훈",
      filename: "인공지능_트렌드_2026.pdf",
      model: "gemma3:latest",
      charCount: "12,540",
      status: "완료",
    },
    {
      id: 2,
      datetime: "2026-02-26 11:05",
      username: "이수진",
      filename: "React_v19_변경사항.pdf",
      model: "llama3:latest",
      charCount: "8,230",
      status: "완료",
    },
    {
      id: 3,
      datetime: "2026-02-25 16:48",
      username: "박민준",
      filename: "2025_신분증_보고서.pdf",
      model: "gemma3:latest",
      charCount: "21,300",
      status: "완료",
    },
    {
      id: 4,
      datetime: "2026-02-25 09:17",
      username: "정재훈",
      filename: "FastAPI공식문서_요약.pdf",
      model: "gemma3:latest",
      charCount: "5,780",
      status: "완료",
    },
    {
      id: 5,
      datetime: "2026-02-24 20:03",
      username: "김지은",
      filename: "머신러닝_입문서.pdf",
      model: "llama3:latest",
      charCount: "15,670",
      status: "완료",
    },
    {
      id: 6,
      datetime: "2026-02-23 15:45",
      username: "정재훈",
      filename: "AI_윤리_보고서.pdf",
      model: "gemma3:latest",
      charCount: "9,450",
      status: "완료",
    },
    {
      id: 7,
      datetime: "2026-02-22 10:30",
      username: "이수진",
      filename: "Python_고급_튜토리얼.pdf",
      model: "llama3:latest",
      charCount: "11,200",
      status: "완료",
    },
    {
      id: 8,
      datetime: "2026-02-21 18:20",
      username: "박민준",
      filename: "클라우드_컴퓨팅_개론.pdf",
      model: "gemma3:latest",
      charCount: "14,800",
      status: "완료",
    },
    {
      id: 9,
      datetime: "2026-02-20 09:55",
      username: "김지은",
      filename: "데이터사이언스_기초.pdf",
      model: "llama3:latest",
      charCount: "10,300",
      status: "완료",
    },
    {
      id: 10,
      datetime: "2026-02-19 14:10",
      username: "정재훈",
      filename: "빅데이터_분석_가이드.pdf",
      model: "gemma3:latest",
      charCount: "16,500",
      status: "완료",
    },
  ];

  const [searchTerm, setSearchTerm] = useState("");
  const [sortOption, setSortOption] = useState("최신순");
  const [modelFilter, setModelFilter] = useState("전체 모델");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);

  // 필터링 & 정렬
  let filteredData = sampleData.filter(
    (item) =>
      item.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.username.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  if (modelFilter !== "전체 모델") {
    filteredData = filteredData.filter((item) => item.model === modelFilter);
  }

  if (sortOption === "최신순") {
    filteredData.sort((a, b) => new Date(b.datetime) - new Date(a.datetime));
  } else if (sortOption === "오래된순") {
    filteredData.sort((a, b) => new Date(a.datetime) - new Date(b.datetime));
  }

  // 페이지네이션
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const indexOfLast = currentPage * itemsPerPage;
  const indexOfFirst = indexOfLast - itemsPerPage;
  const currentItems = filteredData.slice(indexOfFirst, indexOfLast);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) setCurrentPage(page);
  };

  return (
    <div className="summary-list-page">
      {/* 제목 */}
      <div className="title-wrapper">
        <div className="title-bar"></div>
        <h2>04. 요약 목록 보기</h2>
      </div>

      {/* 설명 + 다운로드 버튼 */}
      <div className="description-wrapper">
        <div className="description-box">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              width: "100%",
              gap: "16px", // ← 여기서 전체 요소 간 간격 조절
              flexWrap: "wrap",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                flex: 1,
              }}
            >
              <span className="blue-icon">📝</span>
              <p style={{ margin: 0 }}>
                전체 사용자의 요약 이력을 조회할 수 있습니다. (본인 포함 전체
                공개)
              </p>
            </div>

            <button className="download-btn">
              <span className="download-icon">⬇</span> 목록 다운로드
            </button>
          </div>
        </div>
      </div>

      {/* 필터 바 */}
      <div className="filter-container">
        <div className="filter-bar">
          <div className="search-group">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="파일명 또는 사용자 검색..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
            />
          </div>
          <select
            value={sortOption}
            onChange={(e) => {
              setSortOption(e.target.value);
              setCurrentPage(1);
            }}
          >
            <option>최신순</option>
            <option>오래된순</option>
          </select>
          <select
            value={modelFilter}
            onChange={(e) => {
              setModelFilter(e.target.value);
              setCurrentPage(1);
            }}
          >
            <option>전체 모델</option>
            <option>gemma3:latest</option>
            <option>llama3:latest</option>
          </select>
          <button className="search-btn">검색</button>
        </div>
      </div>

      {/* 테이블 */}
      <div className="table-wrapper">
        <table className="summary-table">
          <thead>
            <tr>
              <th>#</th>
              <th>날짜 / 시간</th>
              <th>사용자</th>
              <th>파일명</th>
              <th>AI 모델</th>
              <th>원문자수</th>
              <th>상태</th>
              <th>보기</th>
            </tr>
          </thead>
          <tbody>
            {currentItems.map((item, index) => (
              <tr
                key={item.id}
                className={item.username === currentUser ? "my-item" : ""}
              >
                <td>{indexOfFirst + index + 1}</td>
                <td>{item.datetime}</td>
                <td>{item.username}</td>
                <td>{item.filename}</td>
                <td>{item.model}</td>
                <td>{item.charCount}</td>
                <td>
                  <span className="status-badge">{item.status}</span>
                </td>
                <td>
                  <button className="view-btn">보기</button>
                </td>
              </tr>
            ))}
            {/* 빈 행으로 높이 고정 */}
            {Array.from({ length: itemsPerPage - currentItems.length }).map(
              (_, i) => (
                <tr key={`empty-${i}`} className="empty-row">
                  <td colSpan="8">&nbsp;</td>
                </tr>
              ),
            )}
          </tbody>
        </table>
      </div>

      {/* 하단 바 - 페이지네이션 + 페이지당 개수 선택 */}
      <div className="list-bottom-bar">
        <div className="pagination-left">
          <div className="my-summary-indicator">
            <span className="blue-bar"></span>
            <span className="my-summary-text">= 내가 요약한 항목</span>
          </div>
        </div>

        <div className="pagination">
          <button
            className="page-arrow"
            onClick={() => goToPage(currentPage - 1)}
            disabled={currentPage === 1}
          >
            &lt;
          </button>

          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              className={`page-number ${currentPage === page ? "active" : ""}`}
              onClick={() => goToPage(page)}
            >
              {page}
            </button>
          ))}

          <button
            className="page-arrow"
            onClick={() => goToPage(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            &gt;
          </button>
        </div>

        <div className="items-per-page">
          페이지당
          <select
            value={itemsPerPage}
            onChange={(e) => {
              setItemsPerPage(Number(e.target.value));
              setCurrentPage(1);
            }}
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
          건 표시
        </div>
      </div>

      {/* 하단 설명 박스 - 내용 추가 완료 */}
      <div className="bottom-notes-grid">
        <div className="note-box">
          <div className="note-title">
            <span className="note-icon">🔍</span> 검색 / 필터
          </div>
          <p>• 파일명 또는 사용자 이름 검색</p>
          <p>• 모델 및 정렬 기준 선택 가능</p>
        </div>

        <div className="note-box">
          <div className="note-title">
            <span className="note-icon">📋</span> 목록 보기
          </div>
          <p>• 전체 사용자의 요약 이력 조회</p>
          <p>• 기본 정렬 : 최신순</p>
        </div>

        <div className="note-box">
          <div className="note-title">
            <span className="note-icon blue-dot">●</span> 내 항목 강조
          </div>
          <p>• 내가 작성한 요약은 파란 배경</p>
          <p>• 왼쪽에 파란색 바 표시</p>
        </div>

        <div className="note-box">
          <div className="note-title">
            <span className="note-icon">👁️</span> 상세 보기
          </div>
          <p>• 보기 버튼 클릭 시 요약 내용 확인</p>
          <p>• 원문 + 요약 결과 표시 예정</p>
        </div>

        <div className="note-box">
          <div className="note-title">
            <span className="note-icon">📄</span> 페이지네이션
          </div>
          <p>• 페이지당 5~100건 선택 가능</p>
          <p>• 총 건수 실시간 표시</p>
        </div>
      </div>
    </div>
  );
};

export default UserList;
