"""
Validation Service
處理表單驗證、驗證碼生成等業務邏輯
"""
import random
import logging

logger = logging.getLogger(__name__)


class ValidationService:
    """表單驗證服務"""
    
    @staticmethod
    def generate_captcha() -> str:
        """
        生成5位數驗證碼
        
        Returns:
            str: 5位數驗證碼字串
        """
        captcha = str(random.randint(10000, 99999))
        logger.info(f"生成新驗證碼: {captcha}")
        return captcha
    
    @staticmethod
    def validate_captcha(user_input: str, expected: str) -> bool:
        """
        驗證用戶輸入的驗證碼
        
        Args:
            user_input: 用戶輸入的驗證碼
            expected: 預期的驗證碼
            
        Returns:
            bool: 驗證是否通過
        """
        is_valid = user_input.strip() == expected.strip()
        logger.info(f"驗證碼驗證: {'通過' if is_valid else '失敗'}")
        return is_valid
    
    @staticmethod
    def validate_password_format(password: str) -> tuple[bool, str]:
        """
        驗證密碼格式（8-10位英文大小寫與數字組合）
        
        Args:
            password: 待驗證的密碼
            
        Returns:
            tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        if not password:
            return False, "密碼不能為空"
        
        if len(password) < 8 or len(password) > 10:
            return False, "密碼長度必須為8-10位"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "密碼必須包含大小寫字母和數字"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        驗證用戶名格式
        
        Args:
            username: 待驗證的用戶名
            
        Returns:
            tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        if not username:
            return False, "帳號不能為空"
        
        if len(username) < 3:
            return False, "帳號長度至少3位"
        
        return True, ""
    
    @staticmethod
    def validate_login_form(username: str, password: str, captcha_input: str, captcha_expected: str) -> tuple[bool, str]:
        """
        驗證整個登入表單
        
        Args:
            username: 用戶名
            password: 密碼
            captcha_input: 用戶輸入的驗證碼
            captcha_expected: 預期的驗證碼
            
        Returns:
            tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        # 驗證用戶名
        is_valid, error_msg = ValidationService.validate_username(username)
        if not is_valid:
            return False, error_msg
        
        # 驗證密碼
        is_valid, error_msg = ValidationService.validate_password_format(password)
        if not is_valid:
            return False, error_msg
        
        # 驗證驗證碼
        if not ValidationService.validate_captcha(captcha_input, captcha_expected):
            return False, "驗證碼錯誤"
        
        logger.info(f"登入表單驗證通過: {username}")
        return True, ""
