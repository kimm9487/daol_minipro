// src/components/websocketchat/ChatHeader.jsx
export default function ChatHeader({ isConnected }) {
  return (
    <div className="px-4 py-3.5 bg-blue-600 text-white font-semibold flex items-center justify-between shadow-sm">
      <span>실시간 채팅</span>
      <span className="text-sm opacity-90">
        {isConnected ? '(연결됨)' : '(연결 시도 중...)'}
      </span>
    </div>
  );
}