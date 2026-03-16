import React from 'react';

const SecurityOptions = ({
    isImportant,
    setIsImportant,
    documentPassword,
    setDocumentPassword,
    isPublic,
    setIsPublic,
}) => {
    return (
        <div className="important-doc-section">
            <label className="checkbox-label">
                <input
                    type="checkbox"
                    checked={isImportant}
                    onChange={(e) => setIsImportant(e.target.checked)}
                />
                <span className="checkbox-text">🔒 중요문서 (비밀번호 보호)</span>
            </label>

            {isImportant && (
                <div className="password-input-group">
                    <input
                        type="text"
                        placeholder="4자리 숫자"
                        value={documentPassword}
                        onChange={(e) => {
                            const value = e.target.value
                                .replace(/[^0-9]/g, '')
                                .slice(0, 4);
                            setDocumentPassword(value);
                        }}
                        maxLength="4"
                        className="password-input"
                    />
                    <span className="password-hint">
                        {documentPassword.length}/4 (숫자만 입력)
                    </span>
                </div>
            )}

            <label className="checkbox-label">
                <input
                    type="checkbox"
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                />
                <span className="checkbox-text">📖 공개 (체크 해제 시 비공개)</span>
            </label>
        </div>
    );
};

export default SecurityOptions;
