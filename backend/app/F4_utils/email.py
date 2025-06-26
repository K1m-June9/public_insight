from fastapi import HTTPException
from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
import random

from app.F5_core.config import settings
from app.F5_core.redis import email_redis


class EmailVerificationService:
    def __init__(self):
        self.redis = email_redis 
        self.expire_seconds = 300 # 5분

    async def send_code(self, to_email: str):
        """인증 코드를 생성하고 이메일로 전송하는 메서드"""

        # 이미 코드가 Redis에 존재하면 예외 발생
        if await self._is_code_existing(to_email):
            raise HTTPException(status_code=400, detail="이미 인증 코드가 전송되었습니다. 5분 후 다시 시도하세요.")

        # 코드 생성 및 저장
        verification_code = self._generate_code()
        await self._save_code(to_email, verification_code)
        # 이메일 본문 생성
        html_contet = self._build_html_contet(verification_code)

        # 이메일 전송 시도
        try:    
            self._send_email(to_email, html_contet)
        except SMTPException:
            raise HTTPException(status_code=500, detail="이메일 전송 실패")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"예상치 못한 오류: {str(e)}")

    async def verify_code(self, email: str, code= str) -> bool:
        """사용자가 입력한 인증 코드가 Redis에 저장된 코드와 일치하는지 확인"""
        stored_code = await self.redis.get(email)
        return stored_code is not None and stored_code.decode() == code

    #==============================
    # 내부 유틸 메서드
    #==============================
    async def _save_code(self, email: str, code: str):
        """Redis에 인증 코드 저장"""
        await self.redis.set(email, code, ex=self.expire_seconds)
    
    async def _is_code_existing(self, email: str) -> bool:
        """Redis에 인증 코드가 이미 존재하는 지 확인"""
        existing = await self.redis.get(email)
        return existing is not None
    
    def _generate_code(self) -> str:
        """6자리 무작위 인증 코드 생성"""
        return str(random.randint(100000, 999999))
    
    def _build_html_contet(self, code: str)-> str:
        """인증 메일에 들어갈 HTML 콘텐츠 생성"""
        return f"""
        <html>
            <body style="font-family: 'Apple SD Gothic Neo', Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h2 style="color: #333;">안녕하세요, <span style="color:#4CAF50;">Public Insight</span>입니다.</h2>
                    <p style="font-size: 16px; color: #555;">
                        회원가입 절차를 완료하려면 아래 인증 코드를 입력해주세요:
                    </p>
                    <div style="background-color: #4CAF50; color: white; font-size: 24px; font-weight: bold; text-align: center; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        인증 코드 : {code}
                    </div>
                    <p style="color: #555; font-size: 14px; line-height: 1.5;">
                        이 코드는 <strong>5분 동안 유효</strong>합니다.<br/>
                        코드가 만료되었거나 문제가 발생하면 다시 시도해주세요.
                    </p>
                    <p style="color: #777; font-size: 12px; margin-top: 40px;">
                        감사합니다!<br/>
                        <em>Public Insight 팀 드림</em>
                    </p>
                </div>
            </body>
        </html>
        """
    
    def _send_email(self, to_email: str, html_content: str):
        """SMTP를 이용하여 인증 이메일 전송"""
        msg = MIMEText(html_content, "html")
        msg['Subject'] = "이메일 인증"
        msg['From'] = settings.EMAIL
        msg['To'] = to_email

        """SMTP 서버 접속 및 메일 전송"""
        with SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls() # TLS 보안 연결
            server.login(settings.EMAIL, settings.EMAIL_PASSWORD) # 로그인
            server.send_message(msg) # 메일 전송



