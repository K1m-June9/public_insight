"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { User, Bookmark, Star, Lock } from "lucide-react";

// shadcn/ui components
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";

// Context & Hooks
import { useAuth } from "@/contexts/AuthContext";
import { useMyRatingsQuery, useMyBookmarksQuery } from "@/hooks/queries/useUserQueries";
import { useUpdateNicknameMutation, useUpdatePasswordMutation } from "@/hooks/mutations/useUserMutations";

// Components & Utils
import Header from "@/components/header";
import Footer from "@/components/footer";
import { formatDate } from "@/lib/utils/date";

// 마이페이지의 각 탭을 위한 개별 컴포넌트
function ProfileTab() {
  const { user } = useAuth();
  const { mutate: updateNickname, isPending } = useUpdateNicknameMutation();

  const [newNickname, setNewNickname] = useState(user?.nickname || "");
  const [editingNickname, setEditingNickname] = useState(false);

  useEffect(() => {
    if (user) setNewNickname(user.nickname);
  }, [user]);

  const handleSaveNickname = () => {
    if (newNickname.trim() && newNickname !== user?.nickname) {
      updateNickname(newNickname, {
        onSuccess: () => setEditingNickname(false),
      });
    } else {
      setEditingNickname(false);
    }
  };

  if (!user) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>기본 정보</CardTitle>
        <CardDescription>계정 정보를 확인하고 수정할 수 있습니다.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2"><Label>아이디</Label><Input value={user.user_id} disabled /></div>
        <div className="space-y-2"><Label>이메일</Label><Input value={user.email} disabled /></div>
        <div className="space-y-2">
          <Label>닉네임</Label>
          {editingNickname ? (
            <div className="flex gap-2"><Input value={newNickname} onChange={(e) => setNewNickname(e.target.value)} /><Button onClick={handleSaveNickname} disabled={isPending}>{isPending ? "저장 중..." : "저장"}</Button><Button variant="outline" onClick={() => setEditingNickname(false)}>취소</Button></div>
          ) : (
            <div className="flex items-center gap-2"><Input value={user.nickname} disabled /><Button onClick={() => setEditingNickname(true)}>수정</Button></div>
          )}
        </div>
        <div className="space-y-2"><Label>계정 유형</Label><Badge variant={user.role === "admin" ? "default" : "secondary"}>{user.role === "admin" ? "관리자" : "범부"}</Badge></div>
      </CardContent>
    </Card>
  );
}

function BookmarksTab() {
  const { data, isLoading, isError } = useMyBookmarksQuery({ page: 1, limit: 100 }); // 페이지네이션은 추후 구현

  if (isLoading) return <div className="text-center py-8">북마크 목록을 불러오는 중...</div>;
  if (isError) return <div className="text-center py-8 text-red-500">오류가 발생했습니다.</div>;

  const bookmarks = data?.data.bookmarks || [];

  return (
    <Card>
      <CardHeader><CardTitle>북마크한 피드</CardTitle><CardDescription>북마크한 게시물들을 확인할 수 있습니다.</CardDescription></CardHeader>
      <CardContent>
        {bookmarks.length === 0 ? <div className="text-center py-8 text-gray-500">북마크한 피드가 없습니다.</div> : (
          <div className="space-y-4">
            {bookmarks.map((feed) => (
              <div key={feed.feed_id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <Link href={`/feed/${feed.feed_id}`} className="block">
                  <h3 className="font-medium text-lg mb-2 hover:text-blue-600">{feed.feed_title}</h3>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
                    <Badge variant="outline">{feed.organization_name}</Badge>
                    <Badge variant="secondary">{feed.category_name}</Badge>
                    <span>{formatDate(feed.published_date)}</span><span>•</span><span>조회 {feed.view_count}</span>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function RatingsTab() {
  const { data, isLoading, isError } = useMyRatingsQuery({ page: 1, limit: 100 });

  if (isLoading) return <div className="text-center py-8">별점 목록을 불러오는 중...</div>;
  if (isError) return <div className="text-center py-8 text-red-500">오류가 발생했습니다.</div>;
  
  const ratings = data?.data.ratings || [];

  return (
    <Card>
      <CardHeader><CardTitle>별점 남긴 피드</CardTitle><CardDescription>별점을 매긴 게시물들을 확인할 수 있습니다.</CardDescription></CardHeader>
      <CardContent>
        {ratings.length === 0 ? <div className="text-center py-8 text-gray-500">별점을 남긴 피드가 없습니다.</div> : (
          <div className="space-y-4">
            {ratings.map((feed) => (
              <div key={feed.feed_id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <Link href={`/feed/${feed.feed_id}`} className="block">
                  <h3 className="font-medium text-lg mb-2 hover:text-blue-600">{feed.feed_title}</h3>
                  <div className="flex flex-wrap items-center gap-2 mb-2 text-xs text-gray-500">
                    <Badge variant="outline">{feed.organization_name}</Badge><Badge variant="secondary">{feed.category_name}</Badge>
                    <span>{formatDate(feed.published_date)}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1"><span className="text-gray-500">내 별점:</span><div className="flex">{[1, 2, 3, 4, 5].map(star => <Star key={star} className={`h-4 w-4 ${star <= feed.user_rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"}`} />)}</div><span className="ml-1">({feed.user_rating})</span></div>
                    <div className="flex items-center gap-1"><span className="text-gray-500">평균:</span><Star className="h-4 w-4 fill-yellow-400 text-yellow-400" /><span>{feed.average_rating.toFixed(1)}</span></div>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function PasswordTab() {
  const { mutate: updatePassword, isPending, isSuccess, reset } = useUpdatePasswordMutation();
  const [passwordData, setPasswordData] = useState({ current_password: "", new_password: "" });
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => setPasswordData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordData.new_password !== confirmPassword) {
      alert("새 비밀번호가 일치하지 않습니다."); return;
    }
    updatePassword(passwordData, {
        onSuccess: () => { setPasswordData({ current_password: "", new_password: "" }); setConfirmPassword(""); setTimeout(() => reset(), 3000) },
    });
  };

  return (
    <Card>
      <CardHeader><CardTitle>비밀번호 변경</CardTitle><CardDescription>보안을 위해 정기적으로 비밀번호를 변경해주세요.</CardDescription></CardHeader>
      <CardContent className="space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2"><Label htmlFor="current_password">현재 비밀번호</Label><Input id="current_password" name="current_password" type="password" value={passwordData.current_password} onChange={handleChange} required /></div>
          <div className="space-y-2"><Label htmlFor="new_password">새 비밀번호</Label><Input id="new_password" name="new_password" type="password" value={passwordData.new_password} onChange={handleChange} required /></div>
          <div className="space-y-2"><Label htmlFor="confirmPassword">새 비밀번호 확인</Label><Input id="confirmPassword" name="confirmPassword" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required /></div>
          <div className="flex justify-end"><Button type="submit" disabled={isPending}>{isPending ? "변경 중..." : "비밀번호 변경"}</Button></div>
          {isSuccess && <p className="text-sm text-green-600">비밀번호가 성공적으로 변경되었습니다.</p>}
        </form>
      </CardContent>
    </Card>
  );
}

// 메인 마이페이지 컴포넌트
export default function MyPage() {
  const router = useRouter();
  const { user, isLoading: isAuthLoading } = useAuth();

  useEffect(() => {
    // AuthContext가 로딩 중이 아닐 때, user가 없으면 로그인 페이지로 리디렉션
    if (!isAuthLoading && !user) {
      router.replace("/login");
    }
  }, [user, isAuthLoading, router]);

  if (isAuthLoading || !user) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Header />
        <main className="flex-grow"><div className="container px-4 py-8 md:px-6"><div className="flex justify-center items-center h-[60vh]"><div className="animate-pulse text-gray-500">사용자 정보를 불러오는 중...</div></div></div></main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow">
        <div className="container px-4 py-8 md:px-6">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold mb-6">마이페이지</h1>
            <Tabs defaultValue="profile" className="space-y-6">
              <TabsList className="grid grid-cols-4 w-full">
                <TabsTrigger value="profile"><User className="h-4 w-4 mr-2" />기본정보</TabsTrigger>
                <TabsTrigger value="bookmarks"><Bookmark className="h-4 w-4 mr-2" />북마크</TabsTrigger>
                <TabsTrigger value="ratings"><Star className="h-4 w-4 mr-2" />별점</TabsTrigger>
                <TabsTrigger value="password"><Lock className="h-4 w-4 mr-2" />비밀번호</TabsTrigger>
                {/* 관심 기관 탭은 주석 처리 */}
                {/* <TabsTrigger value="interests"><Building className="h-4 w-4 mr-2" />관심기관</TabsTrigger> */}
              </TabsList>
              <TabsContent value="profile"><ProfileTab /></TabsContent>
              <TabsContent value="bookmarks"><BookmarksTab /></TabsContent>
              <TabsContent value="ratings"><RatingsTab /></TabsContent>
              <TabsContent value="password"><PasswordTab /></TabsContent>
              {/* <TabsContent value="interests"> ... </TabsContent> */}
            </Tabs>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}