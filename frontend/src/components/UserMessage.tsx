import type { UserMessageData } from "../types/Message"

export function UserMessage({ message }: { message: UserMessageData }) {
    return (
        <div className="user-message">
            <p>User: {message.prompt}</p>
        </div>
    )

}