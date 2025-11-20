# services/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.auth import SignupRequest, CustomerResponse
from repositories.auth import CustomerRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def validate_signup(data: SignupRequest) -> None:
        # 비밀번호 길이 체크
        if len(data.password) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")

        # 개인정보 동의 체크
        if not data.agree_privacy:
            raise ValueError("개인정보 제공에 동의해야 합니다.")

    @staticmethod
    async def signup(db: AsyncSession, data: SignupRequest) -> CustomerResponse:
        # 0) 입력 검증
        AuthService.validate_signup(data)

        # 1) 이메일 중복 검사
        existing = await CustomerRepository.get_customer_by_email(db, data.email)
        if existing:
            raise ValueError("이미 등록된 이메일입니다.")

        # 2) 비밀번호 해싱
        hashed_pw = AuthService.hash_password(data.password)

        # 3) 이름 조합
        full_name = f"{data.last_name}{data.first_name}"

        # 4) Customer 생성
        customer = await CustomerRepository.create_customer(
            db=db,
            name=full_name,
            email=data.email,
            hashed_pw=hashed_pw,
            category=data.site_type,  # 예: "Cafe24"
        )

        # 5) Site 생성
        await CustomerRepository.create_site(
            db=db,
            customer_id=customer.customer_id,
            site_name=data.site_name,
            site_url=data.site_url,
            site_tz=data.site_tz,
            site_category=data.site_category,
        )

        # 6) commit
        await db.commit()
        await db.refresh(customer)

        # 7) 응답 DTO 변환
        return CustomerResponse.model_validate(customer)
