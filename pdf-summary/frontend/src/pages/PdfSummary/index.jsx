import React, { useState } from "react";
import { usePdfSummary } from "../../hooks/usePdfSummary";
import "./style.css";

import Header from "./Header";
import FileUpload from "./FileUpload";
import ModelSelection from "./ModelSelection";
import SecurityOptions from "./SecurityOptions";
import StatusDisplay from "./StatusDisplay";
import Results from "./Results";

// 채팅 관련 import 추가
import WebSocketChatWindow from "../../components/WebSocketChatWindow";
import "../../components/websocketchat/WebSocketChat.css";

const PdfSummary = () => {
  const {
    file,
    fileName,
    models,
    selectedModel,
    setSelectedModel,
    ocrModels,
    selectedOcrModel,
    setSelectedOcrModel,
    loading,
    summarizing,
    status,
    result,
    isDragActive,
    translatingOriginal,
    translatingSummary,
    streamingSummary,
    extractionProgress,
    translations,
    isImportant,
    setIsImportant,
    documentPassword,
    setDocumentPassword,
    isPublic,
    setIsPublic,
    getAcceptByModel,
    handleFileChange,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleExtract,
    handleSummarizeExtracted,
    handleTranslate,
    handleDownload,
  } = usePdfSummary();

  // 채팅 열림/닫힘 상태 추가
  const [showChat, setShowChat] = useState(false);

  const progressPercent =
    extractionProgress.total > 0
      ? Math.round(
          (extractionProgress.current / extractionProgress.total) * 100,
        )
      : null;

  const progressLabel =
    {
      page: "페이지 추출 중",
      ocr_page: "OCR 처리 중",
      ocr: "OCR 처리 중",
      chunk: "텍스트 전송 중",
    }[extractionProgress.mode] ?? "";

  return (
    <>
      <div className="container">
        <div className="card">
          <Header />
          <FileUpload
            file={file}
            fileName={fileName}
            isDragActive={isDragActive}
            loading={loading}
            getAcceptByModel={getAcceptByModel}
            selectedOcrModel={selectedOcrModel}
            handleDragOver={handleDragOver}
            handleDragLeave={handleDragLeave}
            handleDrop={handleDrop}
            handleFileChange={handleFileChange}
            handleExtract={handleExtract}
          />
          <ModelSelection
            models={models}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            ocrModels={ocrModels}
            selectedOcrModel={selectedOcrModel}
            setSelectedOcrModel={setSelectedOcrModel}
          />
          <SecurityOptions
            isImportant={isImportant}
            setIsImportant={setIsImportant}
            documentPassword={documentPassword}
            setDocumentPassword={setDocumentPassword}
            isPublic={isPublic}
            setIsPublic={setIsPublic}
          />
          <StatusDisplay status={status} />
          <Results
            result={result}
            translations={translations}
            translatingOriginal={translatingOriginal}
            translatingSummary={translatingSummary}
            summarizing={summarizing}
            streamingSummary={streamingSummary}
            fileName={fileName}
            handleTranslate={handleTranslate}
            handleSummarizeExtracted={handleSummarizeExtracted}
            handleDownload={handleDownload}
          />
        </div>
      </div>

      {loading && extractionProgress.mode != null && (
        <div className="progress-toast">
          <div className="progress-toast-label">
            {progressLabel}
            {progressPercent !== null
              ? ` ${progressPercent}% (${extractionProgress.current}/${extractionProgress.total})`
              : ""}
          </div>
          <div className="progress-bar-track">
            {progressPercent !== null ? (
              <div
                className="progress-bar-fill"
                style={{ width: `${progressPercent}%` }}
              />
            ) : (
              <div className="progress-bar-indeterminate" />
            )}
          </div>
        </div>
      )}
      
      {/* ← 여기로 Floating Chat 옮김 */}
      <button
        className="floating-chat-btn"
        onClick={() => setShowChat(!showChat)}
        title="실시간 채팅 열기"
      >
        💬
      </button>

      {showChat && (
        <div className="floating-chat-panel">
          <div className="chat-header">
            <h3>실시간 채팅</h3>
            <button onClick={() => setShowChat(false)}>✕</button>
          </div>
          <div className="chat-body">
            <WebSocketChatWindow />
          </div>
        </div>
      )}
    </>
  );
};

export default PdfSummary;
