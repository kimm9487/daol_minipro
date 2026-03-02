// src/pages/UserList.jsx
import React, { useState, useEffect } from "react";
import "./UserList.css";

const UserList = () => {
  const currentUser = localStorage.getItem("userName") || "정재훈";
  const isAdmin = localStorage.getItem("userRole") === "admin"; // [정재훈] 2026-03-02 추가: 관리자 여부 판단
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [sortOption, setSortOption] = useState("최신순");
  const [modelFilter, setModelFilter] = useState("전체 모델");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);

  // [정재훈] 2026-03-02 추가: 체크박스 선택 상태 관리 (문서 ID 배열)
  const [selectedItems, setSelectedItems] = useState([]);

  // [재훈] 2026-03-01 추가: 보기 버튼 클릭 시 해당 문서의 summary만 모달에 표시
  const [selectedSummary, setSelectedSummary] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // [정재훈] 2026-03-02 추가: 정렬 상태 관리 (컬럼명 + 방향)
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "asc" });

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
          const createdDate = doc.created_at ? new Date(doc.created_at) : null;

          return {
            id: doc.id || index + 1,
            userId: doc.user?.id || "N/A", // 내부용 (툴팁에만 사용)
            username: doc.user?.username || "알수없음", // 로그인 ID
            fullName: doc.user?.full_name || doc.user?.username || "알수없음", // 표시용 이름
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
            filename: doc.filename || "파일명 없음",
            model: doc.model_used || "gemma3:latest",
            charCount: doc.char_count ? doc.char_count.toLocaleString() : "0",
            status: "완료",
            summary: doc.summary || "요약 내용이 없습니다.",
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

  // [정재훈] 2026-03-02 추가: 체크박스 토글 함수 (관리자라면 전체 가능)
  const handleCheckboxChange = (docId, username, fullName) => {
    const numericId = Number(docId);

    // NaN이거나 유효하지 않으면 무시
    if (isNaN(numericId) || numericId <= 0) {
      console.warn("[정재훈] 유효하지 않은 docId:", docId);
      return;
    }

    // 관리자라면 무조건 체크/해제 가능
    if (isAdmin) {
      setSelectedItems((prev) =>
        prev.includes(numericId)
          ? prev.filter((id) => id !== numericId)
          : [...prev, numericId],
      );
      return;
    }

    // 일반 사용자: 본인 문서만 선택 가능
    if (username !== currentUser && fullName !== currentUser) return;

    setSelectedItems((prev) =>
      prev.includes(numericId)
        ? prev.filter((id) => id !== numericId)
        : [...prev, numericId],
    );
  };

  // [정재훈] 2026-03-02 최종 수정: Body에 user_id도 함께 보내기 (401 에러 완전 해결)
  const handleDownload = async () => {
    // 개선 3: 다운로드 버튼 클릭 시 즉시 로그 (디버깅용)
    console.log("📥 다운로드 버튼 클릭! 선택된 항목:", selectedItems);

    if (selectedItems.length === 0) {
      alert("다운로드할 항목을 선택하세요.");
      return;
    }

    const safeSelectedIds = selectedItems
      .map((id) => Number(id))
      .filter((id) => !isNaN(id) && id > 0);

    try {
      let sendUserId = currentUser;

      const usernameRes = await fetch(
        "http://localhost:8000/api/admin/current-username",
        {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: `user_id=${encodeURIComponent(currentUser)}`,
        },
      );

      // 개선 2: current-username 실패 시 더 명확한 로그
      if (usernameRes.ok) {
        const data = await usernameRes.json();
        sendUserId = data.username;
        console.log("[정재훈] 서버에서 조회한 실제 username:", sendUserId);
      } else {
        console.warn("⚠️ current-username 실패 → full_name 그대로 사용");
      }

      const response = await fetch(
        "http://localhost:8000/api/admin/download-selected",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            selected_ids: safeSelectedIds,
            user_id: sendUserId,
          }),
        },
      );

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`다운로드 실패: ${response.status} - ${errText}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${sendUserId}_선택_요약목록.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      // 개선 1: 다운로드 성공 시 알림 추가
      console.log("✅ 다운로드 완료!");
      alert(`${sendUserId}_선택_요약목록.csv 파일이 다운로드되었습니다!`);
    } catch (err) {
      console.error("다운로드 오류:", err);
      alert("다운로드 중 오류가 발생했습니다.\n" + err.message);
    }
  };

  // 보기 버튼 클릭 시 (관리자라면 모든 문서 보기 가능)
  const handleViewClick = (id) => {
    const item = data.find((d) => d.id === id);
    if (!item) {
      alert("문서를 찾을 수 없습니다.");
      return;
    }

    // 관리자라면 무조건 볼 수 있게 함 (가장 중요한 부분)
    if (isAdmin) {
      setSelectedSummary(item.summary);
      setIsModalOpen(true);
      return;
    }

    // 일반 사용자: 본인 문서만
    if (item.username === currentUser || item.fullName === currentUser) {
      setSelectedSummary(item.summary);
      setIsModalOpen(true);
    } else {
      alert("이 문서는 당신이 작성한 것이 아닙니다.");
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedSummary(null);
  };

  // 정렬 요청
  const requestSort = (key) => {
    let direction = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  // 정렬된 데이터
  const sortedData = React.useMemo(() => {
    let sortable = [...data];
    if (sortConfig.key) {
      sortable.sort((a, b) => {
        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];
        if (aVal < bVal) return sortConfig.direction === "asc" ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === "asc" ? 1 : -1;
        return 0;
      });
    }
    return sortable;
  }, [data, sortConfig]);

  // 필터링
  const filteredData = React.useMemo(() => {
    return sortedData.filter((item) =>
      [
        item.filename,
        item.fullName,
        item.username,
        item.model,
        item.status,
        item.charCount,
        item.datetime,
      ].some((val) =>
        val?.toString().toLowerCase().includes(searchTerm.toLowerCase()),
      ),
    );
  }, [sortedData, searchTerm]);

  // 페이지네이션
  const paginatedData = filteredData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage,
  );

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) setCurrentPage(page);
  };

  // 검색어 하이라이트 함수
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
      <div className="title-wrapper">
        <div className="title-bar"></div>
        <h2>04. 요약 목록 보기</h2>
        {isAdmin && (
          <span
            style={{
              marginLeft: "12px",
              background: "#e11d48",
              color: "white",
              padding: "4px 12px",
              borderRadius: "999px",
              fontSize: "14px",
              fontWeight: "bold",
            }}
          >
            관리자 모드
          </span>
        )}
      </div>

      <div className="description-wrapper">
        <div className="description-box">
          <span>
            전체 사용자의 요약 이력을 조회할 수 있습니다. (본인 포함 전체 공개)
          </span>
        </div>

        <button className="download-btn" onClick={handleDownload}>
          목록 다운로드
        </button>
      </div>

      {/* 관리자 전용 전체 선택/해제 버튼 */}
      {isAdmin && (
        <div style={{ margin: "12px 0", textAlign: "right" }}>
          <button
            className="download-btn"
            style={{ background: "#6b7280" }}
            onClick={() => {
              if (selectedItems.length === data.length) {
                setSelectedItems([]);
              } else {
                setSelectedItems(data.map((item) => item.id));
              }
            }}
          >
            {selectedItems.length === data.length ? "전체 해제" : "전체 선택"}
          </button>
        </div>
      )}

      {/* 검색/필터 바 */}
      <div className="filter-bar">
        <div className="search-group">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="파일명, 사용자, 모델 등 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select
          value={sortOption}
          onChange={(e) => setSortOption(e.target.value)}
        >
          <option value="최신순">최신순</option>
          <option value="오래된순">오래된순</option>
        </select>
        <select
          value={modelFilter}
          onChange={(e) => setModelFilter(e.target.value)}
        >
          <option value="전체 모델">전체 모델</option>
          <option value="gemma3:latest">gemma3:latest</option>
        </select>
        <button className="search-btn">검색</button>
      </div>

      {/* 테이블 */}
      <div className="table-wrapper">
        <table className="summary-table">
          <thead>
            <tr>
              <th>선택</th>
              <th>#</th>
              <th onClick={() => requestSort("datetime")} className="sortable">
                날짜 / 시간
                <span
                  className={`sort-icon ${sortConfig.key === "datetime" ? sortConfig.direction : "none"}`}
                >
                  {sortConfig.key === "datetime"
                    ? sortConfig.direction === "asc"
                      ? "▲"
                      : "▼"
                    : "↕"}
                </span>
              </th>
              <th>ID</th>
              <th>사용자</th>
              <th>파일명</th>
              <th>AI 모델</th>
              <th>원문자수</th>
              <th>상태</th>
              <th>보기</th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((item, idx) => (
              <tr
                key={item.id}
                className={
                  item.username === currentUser ||
                  item.fullName === currentUser ||
                  isAdmin
                    ? "my-item"
                    : ""
                }
              >
                <td>
                  <input
                    type="checkbox"
                    checked={selectedItems.includes(item.id)}
                    onChange={() =>
                      handleCheckboxChange(
                        item.id,
                        item.username,
                        item.fullName,
                      )
                    }
                    disabled={
                      !isAdmin &&
                      item.username !== currentUser &&
                      item.fullName !== currentUser
                    }
                  />
                </td>
                <td>{(currentPage - 1) * itemsPerPage + idx + 1}</td>
                <td>{item.datetime}</td>
                <td>{item.id}</td>
                <td className="user-cell" data-username={item.username}>
                  {item.fullName}
                </td>
                <td
                  dangerouslySetInnerHTML={{
                    __html: highlightText(item.filename, searchTerm),
                  }}
                />
                <td>{item.model}</td>
                <td
                  dangerouslySetInnerHTML={{
                    __html: highlightText(item.charCount, searchTerm),
                  }}
                />
                <td>{item.status}</td>
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

            {/* 빈 행으로 테이블 높이 유지 */}
            {Array.from({ length: itemsPerPage - paginatedData.length }).map(
              (_, i) => (
                <tr key={`empty-${i}`} className="empty-row">
                  <td colSpan={10}>&nbsp;</td>
                </tr>
              ),
            )}
          </tbody>
        </table>
      </div>

      {/* 모달 */}
      {isModalOpen && selectedSummary && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>
              ×
            </button>
            <h2>요약 내용</h2>
            <pre className="modal-text">{selectedSummary}</pre>
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

      {/* 하단 설명 그리드 */}
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
