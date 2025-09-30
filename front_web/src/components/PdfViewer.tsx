"use client";

import { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Expand, X } from 'lucide-react';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

interface PdfViewerProps {
  fileUrl: string;
}

export function PdfViewer({ fileUrl }: PdfViewerProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState(1);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [scale, setScale] = useState(1.0);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsFullScreen(false);
    };
    if (isFullScreen) document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isFullScreen]);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }): void {
    setNumPages(numPages);
  }

  const goToPrevPage = () => setPageNumber(prev => Math.max(prev - 1, 1));
  const goToNextPage = () => setPageNumber(prev => Math.min(prev + 1, numPages || 1));
  const zoomIn = () => setScale(prev => Math.min(prev + 0.2, 3.0));
  const zoomOut = () => setScale(prev => Math.max(prev - 0.2, 0.4));

  return (
    <div className="w-full flex flex-col items-center">
      <div className="w-full flex flex-wrap items-center justify-center gap-4 p-2 mb-4 bg-muted/50 rounded-md border">
        {!isFullScreen && numPages > 1 && (
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={goToPrevPage} disabled={pageNumber <= 1}><ChevronLeft className="h-4 w-4" /> 이전</Button>
            <p className="text-sm font-medium"> {pageNumber} / {numPages} </p>
            <Button variant="outline" size="sm" onClick={goToNextPage} disabled={pageNumber >= numPages}>다음 <ChevronRight className="h-4 w-4" /></Button>
          </div>
        )}
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" className="h-9 w-9" onClick={zoomOut}><ZoomOut className="h-4 w-4" /></Button>
          <span className="text-sm font-medium w-16 text-center">{Math.round(scale * 100)}%</span>
          <Button variant="outline" size="icon" className="h-9 w-9" onClick={zoomIn}><ZoomIn className="h-4 w-4" /></Button>
        </div>
        {!isFullScreen && numPages > 0 && (
          <Button variant="outline" size="sm" onClick={() => setIsFullScreen(true)}><Expand className="h-4 w-4 mr-2" /> 전체보기</Button>
        )}
      </div>
      <div className="border border-gray-300 rounded-lg w-full overflow-auto">
        <Document
          file={fileUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={<div className="text-center p-10">PDF 파일을 불러오는 중...</div>}
          error={<div className="text-center p-10 text-red-500">PDF 파일을 불러오는 데 실패했습니다.</div>}
        >
          <div className="flex justify-center">
            <Page pageNumber={pageNumber} scale={scale} renderTextLayer={true} />
          </div>
        </Document>
      </div>

      {isFullScreen && (
        <div className="fixed inset-0 bg-black/80 z-50 flex flex-col p-4">
          <div className="flex-shrink-0 text-right mb-4">
            <Button variant="destructive" size="icon" onClick={() => setIsFullScreen(false)}><X className="h-5 w-5" /></Button>
          </div>
          <div className="flex-grow overflow-y-auto">
            <Document
              file={fileUrl}
              loading={<div className="text-center p-10 text-white">전체 페이지를 불러오는 중...</div>}
              error={<div className="text-center p-10 text-red-500">파일을 불러오는 데 실패했습니다.</div>}
            >
              <div className="flex flex-col items-center gap-4">
                {Array.from({ length: numPages }, (_, i) => i + 1).map(page => (
                  <div key={`page_wrapper_${page}`} className="overflow-auto bg-white shadow-lg">
                    <Page
                      pageNumber={page}
                      scale={scale}
                      renderTextLayer={true}
                    />
                  </div>
                ))}
              </div>
            </Document>
          </div>
        </div>
      )}
    </div>
  );
}