"use client";

import type React from "react";
import { useState, type FormEvent } from "react";
import Link from "next/link";
import { Eye, EyeOff, Check, X } from "lucide-react";
import { useRegisterMutation, useCheckIdMutation } from "@/hooks/mutations/useAuthMutations";
import { isValidUserId, isValidEmail, isValidPassword } from "@/lib/utils/validation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Checkbox } from "@/components/ui/checkbox";
import Header from "@/components/header";

export default function SignupPage() {
  // 1. 뮤테이션 훅 사용
  const { mutate: register, isPending: isRegistering } = useRegisterMutation();
  const { mutate: checkId, isPending: isCheckingId, data: checkIdData, error: checkIdError } = useCheckIdMutation();

  const [formData, setFormData] = useState({
    user_id: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreements, setAgreements] = useState({
    terms_agreed: false, // 백엔드 스키마에 맞춰 키 이름 변경
    privacy_agreed: false,
    notification_agreed: false,
  });
  
  // 2. 파생된 상태(Derived State)로 UI 상태 관리
  const isUsernameChecked = checkIdData !== undefined || checkIdError !== null;
  const isUsernameAvailable = checkIdData?.success === true;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCheckId = () => {
    if (!isValidUserId(formData.user_id)) {
      alert("아이디는 8~20자의 영문 소문자와 숫자 조합이어야 하며, 숫자로 시작할 수 없습니다.");
      return;
    }
    checkId({ user_id: formData.user_id });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    // 3. 프론트엔드 유효성 검사
    if (!isUsernameChecked || !isUsernameAvailable) {
      alert("아이디 중복 확인을 완료해주세요.");
      return;
    }
    if (!isValidEmail(formData.email)) {
      alert("올바른 이메일 형식을 입력해주세요.");
      return;
    }
    if (!isValidPassword(formData.password)) {
      alert("비밀번호는 10~25자, 영문/숫자/특수문자를 포함해야 하며, 특수문자로 시작할 수 없습니다.");
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      alert("비밀번호가 일치하지 않습니다.");
      return;
    }
    if (!agreements.terms_agreed || !agreements.privacy_agreed) {
      alert("필수 약관에 동의해주세요.");
      return;
    }

    // 4. register 뮤테이션 호출
    register({
      user_id: formData.user_id,
      email: formData.email,
      password: formData.password,
      ...agreements
    });
  };

  const handleAgreementChange = (key: keyof typeof agreements, checked: boolean) => {
    setAgreements((prev) => ({ ...prev, [key]: checked }));
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <div className="flex-grow flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold">회원가입</CardTitle>
            <CardDescription>PublicInsight 계정을 만들어보세요</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="user_id">아이디</Label>
                <div className="flex gap-2">
                  <Input id="user_id" name="user_id" type="text" required value={formData.user_id} onChange={handleInputChange} placeholder="8~20자 영문, 숫자" className="flex-1" />
                  <Button type="button" variant="outline" onClick={handleCheckId} disabled={isCheckingId || !formData.user_id.trim()}>
                    {isCheckingId ? "확인 중..." : "중복확인"}
                  </Button>
                </div>
                {isUsernameChecked && (
                  <div className={`flex items-center gap-1 text-sm ${isUsernameAvailable ? "text-green-600" : "text-red-600"}`}>
                    {isUsernameAvailable ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                    {isUsernameAvailable ? "사용 가능한 아이디입니다." : "이미 사용 중인 아이디입니다."}
                  </div>
                )}
              </div>

              {/* ... (이메일, 비밀번호, 비밀번호 확인 Input 필드들은 이전과 동일) ... */}
              
              <div className="space-y-3 pt-4">
                <div className="flex items-center space-x-2">
                  <Checkbox id="terms" checked={agreements.terms_agreed} onCheckedChange={(checked) => handleAgreementChange("terms_agreed", checked as boolean)} />
                  <label htmlFor="terms" className="text-sm"><span className="text-red-500">*</span> 이용약관 동의 <Link href="/terms" className="text-blue-600 hover:underline">(보기)</Link></label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="privacy" checked={agreements.privacy_agreed} onCheckedChange={(checked) => handleAgreementChange("privacy_agreed", checked as boolean)} />
                  <label htmlFor="privacy" className="text-sm"><span className="text-red-500">*</span> 개인정보처리방침 동의 <Link href="/privacy" className="text-blue-600 hover:underline">(보기)</Link></label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="marketing" checked={agreements.notification_agreed} onCheckedChange={(checked) => handleAgreementChange("notification_agreed", checked as boolean)} />
                  <label htmlFor="marketing" className="text-sm">알림 수신 동의 (선택)</label>
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={isRegistering}>
                {isRegistering ? "회원가입 중..." : "회원가입"}
              </Button>
            </form>
            
            <div className="mt-6 text-center text-sm">
              <span className="text-gray-500">이미 계정이 있으신가요? </span>
              <Link href="/login" className="text-blue-600 hover:text-blue-500 font-medium">로그인</Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}