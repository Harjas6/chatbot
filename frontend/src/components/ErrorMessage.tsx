import type { ErrorMessageData } from "../types/Message";

export function ErrorMessage({ message }: { message: ErrorMessageData }) {
	return (
		<div className="ai-message error-message">
			<strong>Error:</strong> {message.error}
		</div>
	);
}
