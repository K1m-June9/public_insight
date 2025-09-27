import { Badge } from "@/components/ui/badge";

interface DocumentSummaryProps {
  // << [수정] string[] | undefined 타입을 받도록 하여, 데이터가 없을 경우를 명확히 처리함.
  summaryText?: string[];
}

// << [삭제] 기본값으로 사용되던 defaultSummary는 실제 데이터를 사용할 것이므로 삭제함.

export default function DocumentSummary({ summaryText }: DocumentSummaryProps) {
  
  // << [추가] summaryText가 없거나 비어있으면 컴포넌트를 렌더링하지 않음.
  if (!summaryText || summaryText.length === 0 || (summaryText.length === 1 && !summaryText[0])) {
    return null;
  }
  
  return (
    // 프로토타입의 UI 구조를 그대로 사용함.
    <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="w-1 h-16 bg-primary rounded-full flex-shrink-0 mt-1"></div>
        <div className="flex-1">
          <h2 className="font-semibold text-foreground mb-3 flex items-center gap-2">
            <span>문서 요약</span>
            <Badge variant="outline" className="text-xs">AI 생성</Badge>
          </h2>
          <div className="space-y-2 text-sm text-muted-foreground leading-relaxed">
            {summaryText.map((paragraph, index) => (
              <p key={index}>
                {paragraph}
              </p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}