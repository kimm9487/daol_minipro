# backend/routers/websocket.py
import socketio
from datetime import datetime

from database import get_db, User, UserSession

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
)

websocket_app = socketio.ASGIApp(sio)

online_users_by_sid = {}
online_users_by_user = {}

# HISTORY_LIMIT = 500     # ← 사용 안 함

def has_entered(user_id):
    return False  # 더 이상 사용 안 함 (필요 시 제거 가능)

@sio.event
async def connect(sid, environ, auth=None):
    session_token = (auth or {}).get('session_token')
    if not session_token:
        await sio.disconnect(sid)
        return

    db = next(get_db())

    session_record = db.query(UserSession).filter(
        UserSession.session_token == session_token,
        UserSession.is_active == True
    ).first()

    if not session_record:
        await sio.disconnect(sid)
        return

    user = db.query(User).filter(User.id == session_record.user_id).first()

    user_id = user.username
    name = user.full_name or user.username

    # 등록
    online_users_by_sid[sid] = user_id
    online_users_by_user[user_id] = {"sid": sid, "name": name}

    online_list = [
        {"userId": user_id, "name": user_id}   # name 필드를 username으로 채움
        for user_id, info in online_users_by_user.items()
    ]

    await sio.emit("onlineUsers", online_list)
    print(f"[Socket] 접속 → {user_id}")

@sio.event
async def disconnect(sid):
    user_id = online_users_by_sid.pop(sid, None)
    if user_id:
        online_users_by_user.pop(user_id, None)

        online_list = [{"name": v["name"], "userId": k} for k, v in online_users_by_user.items()]
        await sio.emit("onlineUsers", online_list)

        # 퇴장 알림 원한다면 여기서 emit
        # leave_msg = {
        #     "senderId": "system",
        #     "content": f"{user_id}님이 퇴장했습니다.",
        #     "timestamp": datetime.utcnow().isoformat() + "Z",
        #     "isSystem": True
        # }
        # await sio.emit("receiveMessage", leave_msg)

        print(f"[Socket] 퇴장 → {user_id}")

@sio.event
async def logout(sid):
    user_id = online_users_by_sid.pop(sid, None)

    if user_id:
        online_users_by_user.pop(user_id, None)

        leave_msg = {
            "senderId": "system",
            "content": f"{user_id}님이 로그아웃했습니다.",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "isSystem": True
        }

        await sio.emit("receiveMessage", leave_msg)

        online_list = [
            {"name": v["name"], "userId": k}
            for k, v in online_users_by_user.items()
        ]

        await sio.emit("onlineUsers", online_list)
        print(f"[Socket] 로그아웃 처리 완료 → {sid}")

@sio.event
async def sendMessage(sid, data):
    user_id = online_users_by_sid.get(sid)
    if not user_id:
        return

    user_info = online_users_by_user.get(user_id)
    if not user_info:
        return

    msg = {
        "senderId": user_id,
        "content": data.get("content", "").strip(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "isSystem": False
    }

    # 전체 히스토리 저장 안 함 → receiveMessage로만 브로드캐스트
    await sio.emit("receiveMessage", msg)

print("✅ WebSocket 서버 - 실시간 스트림 모드")