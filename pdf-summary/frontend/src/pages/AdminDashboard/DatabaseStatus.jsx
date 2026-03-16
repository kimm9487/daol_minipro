import React, { useState, useEffect } from "react";
import { API_BASE } from "../../config/api";

const DatabaseStatus = () => {
  const [dbStatus, setDbStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDatabaseStatus = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/admin/database-status`, {
        cache: "no-store",
      });
      if (!response.ok) {
        throw new Error("DB 상태 확인 실패");
      }
      const data = await response.json();
      setDbStatus(data);
    } catch (err) {
      setError(err.message);
      console.error("DB 상태 로드 오류:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatabaseStatus();
  }, []);

  return (
    <section className="admin-card">
      <div className="card-header">
        <span>🔧 데이터베이스 상태</span>
        <button className="btn-refresh" onClick={loadDatabaseStatus}>
          새로고침
        </button>
      </div>
      {loading ? (
        <div className="loading">데이터베이스 상태를 확인하는 중...</div>
      ) : dbStatus ? (
        <div className="status-grid">
          <div className="status-item success">
            <h4>연결 상태</h4>
            <p>{dbStatus.database_connection}</p>
            <small>버전: {dbStatus.database_version}</small>
          </div>
          <div
            className={`status-item ${dbStatus.pdf_documents_table_exists ? "success" : "warning"}`}
          >
            <h4>테이블 상태</h4>
            <p>테이블 수: {dbStatus.tables.length}개</p>
            <p>
              pdf_documents:{" "}
              {dbStatus.pdf_documents_table_exists ? "✅ 존재" : "⚠️ 없음"}
            </p>
          </div>
          {dbStatus.data_statistics && (
            <div className="status-item">
              <h4>문서 통계</h4>
              <p>전체 문서: {dbStatus.data_statistics.total_documents}개</p>
            </div>
          )}
        </div>
      ) : (
        <div className="error">{error || "데이터를 불러올 수 없습니다."}</div>
      )}
    </section>
  );
};

export default DatabaseStatus;
