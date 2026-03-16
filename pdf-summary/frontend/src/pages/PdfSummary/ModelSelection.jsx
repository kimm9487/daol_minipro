import React from "react";

const ModelSelection = ({
  models,
  selectedModel,
  setSelectedModel,
  ocrModels,
  selectedOcrModel,
  setSelectedOcrModel,
}) => {
  return (
    <>
      <div className="model-row">
        <span className="model-label">LLM 요약 모델:</span>
        <select
          className="model-select"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
        >
          {models.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>

      <div className="model-row">
        <span className="model-label">OCR 추출 모델:</span>
        <select
          className="model-select"
          value={selectedOcrModel}
          onChange={(e) => setSelectedOcrModel(e.target.value)}
        >
          {ocrModels.map((m) => (
            <option key={m.id} value={m.id}>
              {m.id} - {m.label}
            </option>
          ))}
        </select>
      </div>
    </>
  );
};

export default ModelSelection;
