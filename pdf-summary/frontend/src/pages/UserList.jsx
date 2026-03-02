// src/pages/UserList.jsx
import React, { useState, useEffect } from "react";
import "./UserList.css";

const UserList = () => {
  const currentUser = localStorage.getItem("userName") || "정재훈";

  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [sortOption, setSortOption] = useState("최신순");
  const [modelFilter, setModelFilter] = useState("전체 모델");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);

  // [재훈] 2026-03-01 추가: 보기 버튼 클릭 시 해당 문서의 summary만 모달에 표시
  const [selectedSummary, setSelectedSummary] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          "http://localhost:8000/api/admin/documents",
        );
        if (!response.ok) throw new Error("데이터 불러오기 실패");

        const result = await response.json();

        const mappedData = result.documents.map((doc, index) => {
          // [재훈] 2026-03-01 추가: 정렬 안정성을 위해 실제 Date 객체 저장
          const createdDate = doc.created_at ? new Date(doc.created_at) : null;

          return {
            id: doc.id || index + 1,
            datetime: createdDate
              ? createdDate
                  .toLocaleString("ko-KR", {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    hour12: false,
                  })
                  .replace(/\. /g, "-")
                  .replace(" ", " ")
              : "날짜 없음",
            username: doc.user?.full_name || doc.user?.username || "알수없음",
            filename: doc.filename || "파일명 없음",
            model: doc.model_used || "gemma3:latest",
            charCount: doc.char_count ? doc.char_count.toLocaleString() : "0",
            status: "완료",
            summary: doc.summary || "요약 내용이 없습니다.",
            // [재훈] 2026-03-01 핵심: 정렬용 실제 Date 객체 (최신순/오래된순 모두 정확하게 동작)
            sortDate: createdDate,
          };
        });

        setData(mappedData);
      } catch (err) {
        setError(err.message);
        console.error("데이터 로드 오류:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // [재훈] 2026-03-01 추가: 보기 버튼 클릭 → 현재 사용자와 일치하는 summary만 표시
  const handleViewClick = (docId) => {
    const doc = data.find((item) => item.id === docId);
    if (!doc) {
      alert("해당 문서를 찾을 수 없습니다.");
      return;
    }

    if (doc.username !== currentUser) {
      alert("이 문서는 당신이 작성한 것이 아닙니다.");
      return;
    }

    setSelectedSummary(doc.summary);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedSummary(null);
  };

  if (loading)
    return (
      <div style={{ padding: "40px", textAlign: "center" }}>
        데이터 로딩 중...
      </div>
    );
  if (error)
    return <div style={{ padding: "40px", color: "red" }}>오류: {error}</div>;

  let filteredData = data.filter(
    (item) =>
      item.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      // [재훈] 2026-03-01 추가: 필터 범위 확장 → 모델, 상태, 문자수 등 모든 컬럼 검색 가능
      item.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.status.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.charCount.includes(searchTerm) || // 숫자 검색도 가능
      item.datetime.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  if (modelFilter !== "전체 모델") {
    filteredData = filteredData.filter((item) => item.model === modelFilter);
  }

  // [재훈] 2026-03-01 수정: 정렬 시 sortDate (Date 객체) 사용 → 문자열 파싱 오류 완전 제거
  if (sortOption === "최신순") {
    filteredData.sort(
      (a, b) => (b.sortDate || new Date(0)) - (a.sortDate || new Date(0)),
    );
  } else if (sortOption === "오래된순") {
    filteredData.sort(
      (a, b) => (a.sortDate || new Date(0)) - (b.sortDate || new Date(0)),
    );
  }

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const indexOfLast = currentPage * itemsPerPage;
  const indexOfFirst = indexOfLast - itemsPerPage;
  const currentItems = filteredData.slice(indexOfFirst, indexOfLast);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) setCurrentPage(page);
  };

  // [재훈] 2026-03-01 추가: 검색어 하이라이트 함수 (영문/숫자/한글 상관없이 매칭 부분 파란색 강조)
  // 모든 컬럼에 적용 가능하도록 함수화
  const highlightText = (text, query) => {
    if (!query || !text) return text || "";
    const regex = new RegExp(
      `(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`,
      "gi",
    );
    return text.toString().replace(regex, '<span class="highlight">$1</span>');
  };

  return (
    <div className="summary-list-page">
      {/* 제목 */}
      <div className="title-wrapper">
        <div className="title-bar"></div>
        <h2>04. 요약 목록 보기</h2>
      </div>

      {/* 설명 박스 */}
      <div className="description-wrapper">
        <div className="description-box">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              width: "100%",
              gap: "16px",
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
              placeholder="파일명, 사용자, 모델 등 검색..."
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
                {/* [재훈] 2026-03-01 추가: 모든 컬럼에 검색어 하이라이트 적용 */}
                <td
                  dangerouslySetInnerHTML={{
                    __html: highlightText(item.datetime, searchTerm),
                  }}
                />
                <td
                  dangerouslySetInnerHTML={{
                    __html: highlightText(item.username, searchTerm),
                  }}
                />
                <td
                  dangerouslySetInnerHTML={{
                    __html: highlightText(item.filename, searchTerm),
                  }}
                />
                <td
                  dangerouslySetInnerHTML={{
                    __html: highlightText(item.model, searchTerm),
                  }}
                />
                <td
                  dangerouslySetInnerHTML={{
                    __html: highlightText(item.charCount, searchTerm),
                  }}
                />
                <td
                  dangerouslySetInnerHTML={{
                    __html: highlightText(item.status, searchTerm),
                  }}
                />
                <td>
                  <button
                    className="view-btn"
                    onClick={() => handleViewClick(item.id)}
                  >
                    보기
                  </button>
                </td>
              </tr>
            ))}
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

      {/* [재훈] 2026-03-01 추가: 요약 내용 표시 모달 */}
      {isModalOpen && selectedSummary && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>
              ×
            </button>
            <h2>내 요약 내용</h2>
            <div className="modal-section">
              <pre className="modal-text">{selectedSummary}</pre>
            </div>
          </div>
        </div>
      )}

      {/* 하단 바 */}
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

      {/* 하단 설명 박스 */}
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
