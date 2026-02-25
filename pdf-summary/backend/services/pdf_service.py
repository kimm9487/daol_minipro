import PyPDF2
from fastapi import UploadFile, HTTPException


async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    업로드된 PDF 파일에서 텍스트를 추출합니다.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    try:
        contents = await file.read()

        # BytesIO로 변환하여 PyPDF2로 읽기
        import io
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))

        extracted_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text += f"\n[페이지 {page_num + 1}]\n{page_text}"

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail="PDF에서 텍스트를 추출할 수 없습니다. 이미지 기반 PDF일 수 있습니다."
            )

        return extracted_text.strip()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 처리 중 오류 발생: {str(e)}")
