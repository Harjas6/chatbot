import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import type { Message } from "../types/Message";
import { useState } from "react";

async function sendMessageToServer(
	prompt: string,
	previousTransactionId: string | null
): // promise matches backend JSON response structure
Promise<{
	response: string;
	justification: string;
	sources: string[];
	transaction_id: string;
}> {
	// names has to match the structure of the request body expected by the backend
	const payload = {
		message: prompt,
		previous_transaction_id: previousTransactionId,
	};
	const result = await fetch("http://127.0.0.1:8000/chat", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(payload),
	});

	if (!result.ok) {
		throw new Error(`Server error: ${result.statusText}`);
	}

	return result.json();
}

export function ChatScreen() {
	const [messages, setMessages] = useState<Message[]>([]);
	const [loading, setLoading] = useState(false);
	const [previousTransactionId, setPreviousTransactionId] = useState<
		string | null
	>(null);

	async function onSubmit(prompt: string) {
		setLoading(true);
		setMessages((prevMessages) => [
			...prevMessages,
			{ id: crypto.randomUUID(), role: "USER", prompt },
		]);
		try {
			const result = await sendMessageToServer(prompt, previousTransactionId);
			setMessages((prevMessages) => [
				...prevMessages,
				{
					id: crypto.randomUUID(),
					role: "AI",
					response: result.response,
					justification: result.justification,
					sources: result.sources,
				},
			]); // backend syntax contains transaction_id, instead of transactionId
			setPreviousTransactionId(result.transaction_id);
		} catch (error) {
			setMessages((prevMessages) => [
				...prevMessages,
				{
					id: crypto.randomUUID(),
					role: "ERROR",
					error: `Failed to get response from server: ${
						error instanceof Error ? error.message : String(error)
					}`,
				},
			]);
			console.error("Error sending message:", error);
		} finally {
			setLoading(false);
		}
	}
	return (
		<div className="chat-screen">
			<MessageList messages={messages} loading={loading} />
			<ChatInput onSubmit={onSubmit} disabled={loading} />
		</div>
	);
}
