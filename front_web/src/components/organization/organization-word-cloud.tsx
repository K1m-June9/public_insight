"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useOrganizationWordCloudQuery } from "@/hooks/queries/useOrganizationQueries";
import { WordCloudByYear } from "@/lib/types/organization";

interface OrganizationWordCloudProps {
  organizationName: string;
}

export default function OrganizationWordCloud({ organizationName }: OrganizationWordCloudProps) {
  const [currentYearIndex, setCurrentYearIndex] = useState(0);
  const { data: wordCloudData, isLoading } = useOrganizationWordCloudQuery(organizationName);

  const wordClouds = wordCloudData?.data.wordclouds || [];
  const currentWordCloud: WordCloudByYear | undefined = wordClouds[currentYearIndex];
  const words = currentWordCloud?.words || [{ text: "관련 키워드 데이터가 없습니다", value: 100 }];
  
  const toggleYear = () => {
    if (wordClouds.length > 0) {
      setCurrentYearIndex((prevIndex) => (prevIndex + 1) % wordClouds.length);
    }
  };

  if (isLoading) {
    return <div className="bg-gray-200 h-[380px] rounded-lg shadow-sm border border-gray-200 animate-pulse"></div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900">{organizationName} 워드 클라우드</h2>
        {wordClouds.length > 1 && (
          <Button variant="outline" size="sm" onClick={toggleYear}>
            {`${wordClouds[(currentYearIndex + 1) % wordClouds.length]?.year}년 보기`}
          </Button>
        )}
      </div>
      {currentWordCloud && (
        <div className="text-center mb-2 text-sm text-gray-500">{currentWordCloud.year}년 키워드</div>
      )}
      <div className="h-[300px] flex items-center justify-center">
        <div className="flex flex-wrap justify-center gap-3 p-4">
          {words.map((word, index) => {
            const fontSize = 10 + (word.value / 100) * 22;
            const colorValue = 200 - (word.value / 100) * 150;
            const color = `rgb(${colorValue}, ${colorValue}, ${colorValue})`;
            return (
              <span key={index} className="inline-block transition-transform hover:scale-110 cursor-pointer" style={{ fontSize: `${fontSize}px`, color }}>
                {word.text}
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
}