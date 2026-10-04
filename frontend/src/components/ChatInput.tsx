import { useState, type SubmitEvent } from "react";

type ChatInputProps = {
    onSubmit: (message: string) => void;
    disabled: boolean;
};

export function ChatInput({ onSubmit, disabled }: ChatInputProps) {
    const [inputValue, setInputValue] = useState("");

    function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        const trimmedInputValue = inputValue.trim();
        if (!trimmedInputValue) {
            return;
        }
        onSubmit(trimmedInputValue);
        setInputValue("");
    }

    return (
        <div className="chat-input">
            <form onSubmit={handleSubmit}>
                <input type="text"
                    placeholder="Type your message..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    disabled={disabled}
                    autoComplete="off"
                />
                <button type="submit" disabled={disabled}>Send</button>
            </form>
        </div>
    );
}
