import React from "react";

const FileUpload = ({
  file,
  fileName,
  isDragActive,
  loading,
  getAcceptByModel,
  selectedOcrModel,
  handleDragOver,
  handleDragLeave,
  handleDrop,
  handleFileChange,
  handleExtract,
}) => {
  return (
    <div
      className={`upload-row ${isDragActive ? "drag-active" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <label className={`file-label ${file ? "has-file" : ""}`}>
        <input
          type="file"
          onChange={handleFileChange}
          accept={getAcceptByModel(selectedOcrModel)}
          style={{ display: "none" }}
        />
        <svg
          className="file-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
        <span className={`file-name ${file ? "selected" : ""}`}>
          {fileName}
        </span>
      </label>

      <button
        className="btn-summarize"
        onClick={handleExtract}
        disabled={!file || loading}
      >
        {!loading ? <span>추출하기</span> : <div className="spinner"></div>}
      </button>
    </div>
  );
};

export default FileUpload;
