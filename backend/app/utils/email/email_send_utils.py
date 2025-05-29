from fastapi import HTTPException
from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText

# 커스텀 모듈
from app.core.config import settings 
from app.utils.email.email_redis_utils import (
    utils_save_code,
    utils_generate_verification_code,
    utils_is_code_existing
)

# 이메일 전송 함수
async def utils_email_send_code(to_email: str):
    try:
        # 이메일, 코드가 이미 있는 경우 - 유효기간 내 재전송 불가
        if await utils_is_code_existing(to_email):
            raise HTTPException (status_code=400, detail="이미 인증 코드가 전송되었습니다. 5분 후 다시 시도하세요.")
        
        # 새로운 인증 코드 생성 및 저장
        verification_code = await utils_generate_verification_code()
        await utils_save_code(to_email, verification_code)

        html_content = f"""
        <html>
            <body style="font-family: 'Apple SD Gothic Neo', Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h2 style="color: #333;">안녕하세요, <span style="color:#4CAF50;">Public Insight</span>입니다.</h2>
                    <p style="font-size: 16px; color: #555;">
                        회원가입 절차를 완료하려면 아래 인증 코드를 입력해주세요:
                    </p>
                    <div style="background-color: #4CAF50; color: white; font-size: 24px; font-weight: bold; text-align: center; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        인증 코드 : {verification_code}
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

        # 이메일 전송 로직
        msg = MIMEText(html_content, "html")
        msg['Subject'] = "이메일 인증"
        msg['From'] = settings.EMAIL
        msg['To'] = to_email

        with SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL, settings.EMAIL_PASSWORD)
            server.send_message(msg)

    except SMTPException:
        raise HTTPException(status_code=500, detail="이메일 전송 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예상치 못한 오류: {str(e)}")


