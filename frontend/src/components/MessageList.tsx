import { useEffect, useRef } from "react";
import { UserMessage } from "./UserMessage";
import { AIMessage } from "./AIMessage";
import type { Message } from "../types/Message";
import { ErrorMessage } from "./ErrorMessage";

export function MessageList({ messages }: { messages: Message[] }) {
	const bottomRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		bottomRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages]);

	return (
		<div className="message-list">
			{messages.map((message) => {
				if (message.role === "USER") {
					return <UserMessage key={message.id} message={message} />;
				} else if (message.role === "AI") {
					return <AIMessage key={message.id} message={message} />;
				} else {
					return <ErrorMessage key={message.id} message={message} />;
				}
			})}
			<div ref={bottomRef} />
		</div>
	);
}
