"use client";

import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// PDF.js 워커 경로 설정 (라이브러리 필수 요구사항)
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

interface PdfViewerProps {
  fileUrl: string;
}

export function PdfViewer({ fileUrl }: PdfViewerProps) {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }): void {
    setNumPages(numPages);
  }

  const goToPrevPage = () => setPageNumber(prev => Math.max(prev - 1, 1));
  const goToNextPage = () => setPageNumber(prev => Math.min(prev + 1, numPages || 1));
  
  // API 서버의 기본 URL을 환경 변수에서 가져옴
  // 백엔드에서 상대경로('/static/...')를 주면, 프론트엔드에서 조합
  // const fullPdfUrl = `${process.env.NEXT_PUBLIC_API_URL}${fileUrl}`;
  const fullPdfUrl = `${fileUrl}`;

  return (
    <div className="w-full flex flex-col items-center">
      <div className="border border-gray-300 rounded-lg overflow-hidden w-full">
        <Document
          file={fullPdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={<div className="text-center p-10">PDF 파일을 불러오는 중...</div>}
          error={<div className="text-center p-10 text-red-500">PDF 파일을 불러오는 데 실패했습니다.</div>}
        >
          <Page pageNumber={pageNumber} renderTextLayer={true} />
        </Document>
      </div>

      {numPages && numPages > 1 && (
        <div className="flex items-center justify-center gap-4 mt-4">
          <Button variant="outline" onClick={goToPrevPage} disabled={pageNumber <= 1}>
            <ChevronLeft className="h-4 w-4" />
            이전
          </Button>
          <p className="text-sm">
            {pageNumber} / {numPages}
          </p>
          <Button variant="outline" onClick={goToNextPage} disabled={pageNumber >= numPages}>
            다음
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}