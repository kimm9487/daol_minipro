import React from "react";

const WithdrawConfirmModal = ({ show, loading, onClose, onConfirm }) => {
  if (!show) {
    return null;
  }

  return (
    <div className="modal-overlay" onClick={loading ? undefined : onClose}>
      <div className="modal-content withdraw-modal" onClick={(e) => e.stopPropagation()}>
        <h2>회원 탈퇴 확인</h2>
        <div className="modal-body">
          <p className="withdraw-modal-title">정말 회원 탈퇴하시겠습니까?</p>
          <div className="withdraw-warning-box">
            <p>탈퇴에 대한 책임은 당사가 지지 않습니다.</p>
            <p>탈퇴 후 계정 및 모든 문서/히스토리는 복구되지 않습니다.</p>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn-cancel" onClick={onClose} disabled={loading}>
            취소
          </button>
          <button
            className="btn-confirm btn-danger"
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "탈퇴 처리 중..." : "탈퇴하기"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default WithdrawConfirmModal;