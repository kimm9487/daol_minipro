import PyPDF2
import io
import time
from fastapi import UploadFile, HTTPException


async def extract_text_from_pdf(file: UploadFile) -> dict:
    """
    업로드된 PDF 파일에서 텍스트를 추출합니다.
    처리 시간과 상세한 결과 정보를 함께 반환합니다.
    """
    start_time = time.time()
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, 
            detail={
                "message": "PDF 파일만 업로드 가능합니다.",
                "reason": "잘못된 파일 형식",
                "suggestion": ".pdf 확장자를 가진 파일을 선택해주세요."
            }
        )

    try:
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "파일이 비어있습니다.",
                    "reason": "파일 크기 0바이트",
                    "suggestion": "유효한 PDF 파일을 업로드해주세요."
                }
            )

        # PyPDF2로 PDF 읽기
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "PDF 파일을 읽을 수 없습니다.",
                    "reason": f"PDF 형식 오류: {str(e)}",
                    "suggestion": "파일이 손상되었거나 암호화되어 있을 수 있습니다. 다른 PDF 파일을 시도해보세요."
                }
            )

        total_pages = len(pdf_reader.pages)
        if total_pages == 0:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "PDF에 페이지가 없습니다.",
                    "reason": "페이지 수: 0",
                    "suggestion": "유효한 내용이 있는 PDF 파일을 업로드해주세요."
                }
            )

        extracted_text = ""
        successful_pages = 0
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_text += f"\n[페이지 {page_num + 1}]\n{page_text}"
                    successful_pages += 1
            except Exception:
                # 개별 페이지 오류는 무시하고 계속 진행
                continue

        processing_time = time.time() - start_time

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "PDF에서 텍스트를 추출할 수 없습니다.",
                    "reason": "이미지 기반 PDF 또는 텍스트가 없는 문서",
                    "suggestion": "OCR(광학 문자 인식)이 필요한 스캔된 문서이거나 이미지만 포함된 PDF일 수 있습니다. 텍스트 기반 PDF를 사용해주세요.",
                    "pages_processed": total_pages,
                    "processing_time": f"{processing_time:.2f}초"
                }
            )

        return {
            "text": extracted_text.strip(),
            "total_pages": total_pages,
            "successful_pages": successful_pages,
            "processing_time": processing_time,
            "char_count": len(extracted_text.strip())
        }

    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500, 
            detail={
                "message": "PDF 처리 중 예상치 못한 오류가 발생했습니다.",
                "reason": f"시스템 오류: {str(e)}",
                "suggestion": "잠시 후 다시 시도해주세요. 문제가 계속되면 관리자에게 문의하세요.",
                "processing_time": f"{processing_time:.2f}초"
            }
        )
