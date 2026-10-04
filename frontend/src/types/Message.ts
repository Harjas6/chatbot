export type UserMessageData = {
	id: string;
	role: "USER";
	prompt: string;
};

export type AIMessageData = {
	id: string;
	role: "AI";
	response: string;
	justification: string;
	sources: string[];
};

export type ErrorMessageData = {
	id: string;
	role: "ERROR";
	error: string;
};

export type Message = UserMessageData | AIMessageData | ErrorMessageData;
