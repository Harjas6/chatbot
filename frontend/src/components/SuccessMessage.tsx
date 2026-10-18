import type { SuccessMessageData } from "../types/Message";

export function SuccessMessage({ message }: { message: SuccessMessageData }) {
	return (
		<div className="ai-message success-message">
			<strong>Success:</strong> {message.message}
		</div>
	);
}
