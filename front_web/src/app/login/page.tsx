"use client";

import type React from "react";
import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Eye, EyeOff } from "lucide-react";
import { useLoginMutation } from "@/hooks/mutations/useAuthMutations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import Header from "@/components/header";

export default function LoginPage() {
  //const router = useRouter();
  // 1. useLoginMutation 훅 사용
  const { mutate: login, isPending, error } = useLoginMutation();

  const [formData, setFormData] = useState({
    user_id: "", // 백엔드 LoginRequest 스키마에 맞춰 'user_id'
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    // 기본 유효성 검사 (프론트엔드)
    if (!formData.user_id.trim() || !formData.password.trim()) {
      alert("아이디와 비밀번호를 모두 입력해주세요.");
      return;
    }

    // 2. mutate 함수를 호출하여 로그인 요청
    login(formData);
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <div className="flex-grow flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold">로그인</CardTitle>
            <CardDescription>PublicInsight에 오신 것을 환영합니다</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* 3. 뮤테이션의 error 상태를 사용하여 에러 메시지 표시 */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>
                    {/* error.response.data.error.message와 같은 실제 에러 메시지를 표시할 수 있음. */}
                    아이디 또는 비밀번호가 올바르지 않습니다.
                  </AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="user_id">아이디</Label>
                <Input
                  id="user_id"
                  name="user_id"
                  type="text"
                  required
                  value={formData.user_id}
                  onChange={handleInputChange}
                  placeholder="아이디를 입력하세요"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">비밀번호</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    required
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="비밀번호를 입력하세요"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4 text-gray-400" /> : <Eye className="h-4 w-4 text-gray-400" />}
                  </Button>
                </div>
              </div>

              {/* 4. 뮤테이션의 isPending 상태를 사용하여 버튼 비활성화 */}
              <Button type="submit" className="w-full" disabled={isPending}>
                {isPending ? "로그인 중..." : "로그인"}
              </Button>
            </form>

            <div className="mt-6 text-center space-y-2">
              <div className="flex justify-center space-x-4 text-sm">
                {/* 아이디/비밀번호 찾기 페이지는 나중에 연결 */}
                <Link href="#" className="text-gray-500 hover:text-gray-700">
                  아이디 찾기
                </Link>
                <span className="text-gray-300">|</span>
                <Link href="#" className="text-gray-500 hover:text-gray-700">
                  비밀번호 찾기
                </Link>
              </div>
              <div className="text-sm">
                <span className="text-gray-500">계정이 없으신가요? </span>
                <Link href="/signup" className="text-blue-600 hover:text-blue-500 font-medium">
                  회원가입
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}