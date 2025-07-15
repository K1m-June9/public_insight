// 이거 아직 사용 안합니다 ~~~~~~~~~~~~~~~~~~~~~~
// API가 없으므로 mock 데이터를 그대로 사용

"use client";

import { useState } from "react";
import Link from "next/link";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface OrganizationCommunityProps {
  organizationName: string;
}

interface CommunityPost {
  id: number;
  title: string;
  likes: number;
  dislikes: number;
}

export default function OrganizationCommunity({ organizationName }: OrganizationCommunityProps) {
  const [communityPosts] = useState<CommunityPost[]>([
    { id: 1, title: `${organizationName} 관련 커뮤니티 글(사실아님 ㅋㅋ)`, likes: 45, dislikes: 5 },
    { id: 2, title: `아직 없는 데이터`, likes: 38, dislikes: 12 },
    { id: 3, title: `이건 또 언제 만들어서 언제 연결해놓냐`, likes: 72, dislikes: 8 },
  ]);

  const likedPosts = [...communityPosts].sort((a, b) => b.likes - a.likes);
  const dislikedPosts = [...communityPosts].sort((a, b) => b.dislikes - a.dislikes);

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-xl font-bold mb-4 text-gray-900">커뮤니티 (준비 중)</h2>
      <Tabs defaultValue="likes">
        <TabsList className="grid grid-cols-2 mb-4">
          <TabsTrigger value="likes" className="flex items-center gap-1"><ThumbsUp className="h-4 w-4" /><span>좋아요</span></TabsTrigger>
          <TabsTrigger value="dislikes" className="flex items-center gap-1"><ThumbsDown className="h-4 w-4" /><span>싫어요</span></TabsTrigger>
        </TabsList>
        <TabsContent value="likes">
          <ul className="space-y-3">
            {likedPosts.map((post) => (
              <li key={post.id} className="border-b border-gray-100 pb-2">
                <Link href={`#`} className="block hover:bg-gray-50 rounded p-1 -m-1 transition-colors">
                  <div className="flex justify-between">
                    <span className="font-medium">{post.title}</span>
                    <span className="text-sm text-gray-500 flex items-center"><ThumbsUp className="h-3 w-3 mr-1 text-blue-500" />{post.likes}</span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </TabsContent>
        <TabsContent value="dislikes">
          <ul className="space-y-3">
            {dislikedPosts.map((post) => (
              <li key={post.id} className="border-b border-gray-100 pb-2">
                <Link href={`#`} className="block hover:bg-gray-50 rounded p-1 -m-1 transition-colors">
                  <div className="flex justify-between">
                    <span className="font-medium">{post.title}</span>
                    <span className="text-sm text-gray-500 flex items-center"><ThumbsDown className="h-3 w-3 mr-1 text-red-500" />{post.dislikes}</span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </TabsContent>
      </Tabs>
    </div>
  );
}