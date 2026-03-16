import React from "react";

const Results = ({
  result,
  translations,
  translatingOriginal,
  translatingSummary,
  summarizing,
  fileName,
  handleTranslate,
  handleSummarizeExtracted,
  handleDownload,
}) => {
  if (!result) return null;

  return (
    <div className="result-section visible">
      <hr className="divider" />
      <div className="section-header">
        <span className="section-title">📃 원문 전체</span>
        <span className="section-meta">
          총 {result.original_length?.toLocaleString()}자
        </span>
      </div>
      <div className="original-box">{result.extracted_text}</div>

      <div className="translation-section">
        <button
          className="btn-translate"
          onClick={() => handleTranslate("original")}
          disabled={translatingOriginal}
        >
          {translatingOriginal ? (
            <>
              <div className="spinner-small"></div> 번역 중...
            </>
          ) : (
            <>🌐 원문을 영문으로 번역</>
          )}
        </button>
      </div>

      {translations.original && (
        <div className="translated-box">
          <div className="translated-header">📝 영문 원문</div>
          <div className="translated-content">{translations.original}</div>
        </div>
      )}

      <hr className="divider" />
      <div className="section-header">
        <span className="section-title">🤖 AI 요약 결과</span>
        <span className="section-meta">
          {result.model_used || "아직 요약 전"}
        </span>
      </div>

      {!result.summary && (
        <div className="translation-section">
          <button
            className="btn-translate"
            onClick={handleSummarizeExtracted}
            disabled={summarizing}
          >
            {summarizing ? (
              <>
                <div className="spinner-small"></div> 요약 중...
              </>
            ) : (
              <>🧠 추출 문서 LLM 요약하기</>
            )}
          </button>
        </div>
      )}

      {result.summary && <div className="summary-box">{result.summary}</div>}

      {result.summary && (
        <div className="translation-section">
          <button
            className="btn-translate"
            onClick={() => handleTranslate("summary")}
            disabled={translatingSummary}
          >
            {translatingSummary ? (
              <>
                <div className="spinner-small"></div> 번역 중...
              </>
            ) : (
              <>🌐 요약을 영문으로 번역</>
            )}
          </button>
        </div>
      )}

      {translations.summary && (
        <div className="translated-box">
          <div className="translated-header">📝 영문 요약</div>
          <div className="translated-content">{translations.summary}</div>
        </div>
      )}

      {result.summary && (
        <div className="result-actions">
          <button className="btn-download" onClick={handleDownload}>
            TXT 다운로드
          </button>
        </div>
      )}
    </div>
  );
};

export default Results;
