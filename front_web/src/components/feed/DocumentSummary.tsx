import { Badge } from "@/components/ui/badge";

interface DocumentSummaryProps {
  summaryText?: string[];
}

export default function DocumentSummary({ summaryText }: DocumentSummaryProps) {
  
  if (!summaryText || summaryText.length === 0 || (summaryText.length === 1 && !summaryText[0])) {
    return null;
  }
  
  return (
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