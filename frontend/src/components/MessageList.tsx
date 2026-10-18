import { useEffect, useRef } from "react";
import { UserMessage } from "./Messages/UserMessage";
import { AIMessage } from "./Messages/AIMessage";
import type { Message } from "../types/Message";
import { ErrorMessage } from "./Messages/ErrorMessage";
import { SuccessMessage } from "./Messages/SuccessMessage";

export function MessageList({
	messages,
	loading,
}: {
	messages: Message[];
	loading: boolean;
}) {
	const bottomRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		bottomRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages, loading]);

	return (
		<div className="message-list">
			{messages.map((message) => {
				if (message.role === "USER") {
					return <UserMessage key={message.id} message={message} />;
				} else if (message.role === "AI") {
					return <AIMessage key={message.id} message={message} />;
				} else if (message.role === "SUCCESS") {
					return <SuccessMessage key={message.id} message={message} />;
				} else {
					return <ErrorMessage key={message.id} message={message} />;
				}
			})}
			{loading && (
				<div className="ai-message loading-message">
					<span className="dot" />
					<span className="dot" />
					<span className="dot" />
				</div>
			)}
			<div ref={bottomRef} />
		</div>
	);
}
