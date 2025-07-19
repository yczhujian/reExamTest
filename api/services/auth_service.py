"""用户认证服务模块"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from db import db
import os

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

class AuthService:
    """认证服务封装"""
    
    def __init__(self):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """解码令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    async def register_user(self, email: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
        """注册新用户"""
        try:
            # 使用Supabase Auth注册
            result = self.db.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name or email.split("@")[0]
                    }
                }
            })
            
            if result.user:
                # 创建用户订阅记录
                await self._create_user_subscription(result.user.id)
                
                return {
                    "success": True,
                    "user_id": result.user.id,
                    "email": result.user.email,
                    "message": "注册成功，请查收邮件进行验证"
                }
            else:
                return {
                    "success": False,
                    "message": "注册失败"
                }
                
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            # 检查是否是邮箱已存在
            if "already registered" in str(e).lower():
                return {
                    "success": False,
                    "message": "该邮箱已被注册"
                }
            raise
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        try:
            # 使用Supabase Auth登录
            result = self.db.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if result.user and result.session:
                # 创建自定义JWT令牌
                access_token = self.create_access_token(
                    data={
                        "sub": result.user.id,
                        "email": result.user.email
                    }
                )
                
                return {
                    "success": True,
                    "user_id": result.user.id,
                    "email": result.user.email,
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            else:
                return {
                    "success": False,
                    "message": "邮箱或密码错误"
                }
                
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            return {
                "success": False,
                "message": "登录失败，请重试"
            }
    
    async def logout_user(self, token: str) -> bool:
        """用户登出"""
        try:
            # 使用Supabase Auth登出
            self.db.client.auth.sign_out()
            # TODO: 可以将token加入黑名单
            return True
        except Exception as e:
            logger.error(f"用户登出失败: {e}")
            return False
    
    async def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        try:
            # 解码令牌
            payload = self.decode_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # 获取用户信息
            result = self.db.client.auth.get_user(token)
            if result.user:
                return {
                    "user_id": result.user.id,
                    "email": result.user.email,
                    "name": result.user.user_metadata.get("name", ""),
                    "created_at": result.user.created_at
                }
            
            return None
            
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    async def reset_password_request(self, email: str) -> Dict[str, Any]:
        """请求重置密码"""
        try:
            # 发送重置密码邮件
            self.db.client.auth.reset_password_for_email(email)
            
            return {
                "success": True,
                "message": "重置密码邮件已发送，请查收"
            }
        except Exception as e:
            logger.error(f"重置密码请求失败: {e}")
            return {
                "success": False,
                "message": "发送重置邮件失败"
            }
    
    async def update_password(self, user_id: str, new_password: str) -> Dict[str, Any]:
        """更新密码"""
        try:
            # 更新密码
            result = self.db.client.auth.update_user({
                "password": new_password
            })
            
            if result.user:
                return {
                    "success": True,
                    "message": "密码更新成功"
                }
            else:
                return {
                    "success": False,
                    "message": "密码更新失败"
                }
                
        except Exception as e:
            logger.error(f"更新密码失败: {e}")
            return {
                "success": False,
                "message": "更新密码失败"
            }
    
    async def _create_user_subscription(self, user_id: str):
        """创建用户订阅记录"""
        try:
            # 创建免费套餐订阅
            self.db.client.table("user_subscriptions").insert({
                "user_id": user_id,
                "plan_type": "starter",
                "status": "active",
                "monthly_analyses_limit": 3,
                "monthly_analyses_used": 0,
                "current_period_start": datetime.utcnow().isoformat(),
                "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"创建用户订阅失败: {e}")

# 创建全局实例
auth = AuthService()