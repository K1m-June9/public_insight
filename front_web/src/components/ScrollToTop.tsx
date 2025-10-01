"use client";

import { useEffect, useState, useRef } from "react";
import { ArrowUp, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

function SettingsPanel() {
  // '기본' 버튼 클릭 시
  const handleNormalSize = () => {
    document.body.style.zoom = '1';
  };

  // '확대' 버튼 클릭 시
  const handleLargeSize = () => {
    document.body.style.zoom = '1.2';
  };

  return (
    <div className="absolute bottom-full right-0 mb-2 w-64 rounded-lg bg-card p-4 shadow-2xl border border-border">
      <h4 className="text-sm font-semibold mb-3">화면 크기</h4>
      <div className="grid grid-cols-2 gap-2">
        <button onClick={handleNormalSize} className="p-4 rounded-md border text-center space-y-2 hover:bg-accent">
          <div className="text-lg">가 Aa</div>
          <div className="text-xs">기본</div>
        </button>
        <button onClick={handleLargeSize} className="p-4 rounded-md border text-center space-y-2 hover:bg-accent">
          <div className="text-xl">가 Aa</div>
          <div className="text-xs">확대</div>
        </button>
      </div>
    </div>
  );
}

export function ScrollToTopButton() {
  const [isVisible, setIsVisible] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const toggleVisibility = () => {
    //if (window.scrollY >= 0) 
    setIsVisible(true);
    //else setIsVisible(false);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  useEffect(() => {
    window.addEventListener("scroll", toggleVisibility);
    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  return (
    <div className={cn(
        "fixed bottom-5 right-5 z-50 flex items-center gap-2 transition-opacity duration-300",
        isVisible ? "opacity-100" : "opacity-0 pointer-events-none"
    )}>
      {isSettingsOpen && <SettingsPanel />}
      <Button variant="outline" size="icon" className="rounded-full h-12 w-12 shadow-lg" onClick={scrollToTop}>
        <ArrowUp className="h-6 w-6" />
      </Button>
      <Button variant="outline" size="icon" className="rounded-full h-12 w-12 shadow-lg" onClick={() => setIsSettingsOpen(!isSettingsOpen)}>
        <Settings className="h-6 w-6" />
      </Button>
    </div>
  );
}