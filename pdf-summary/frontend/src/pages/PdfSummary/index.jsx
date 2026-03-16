import React from "react";
import { usePdfSummary } from "../../hooks/usePdfSummary";
import "./style.css";

import Header from "./Header";
import FileUpload from "./FileUpload";
import ModelSelection from "./ModelSelection";
import SecurityOptions from "./SecurityOptions";
import StatusDisplay from "./StatusDisplay";
import Results from "./Results";

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
    isAdmin,
    isDragActive,
    translatingOriginal,
    translatingSummary,
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

  return (
    <div className="container">
      <div className="card">
        <Header isAdmin={isAdmin} />
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
          fileName={fileName}
          handleTranslate={handleTranslate}
          handleSummarizeExtracted={handleSummarizeExtracted}
          handleDownload={handleDownload}
        />
      </div>
    </div>
  );
};

export default PdfSummary;
