import type { AIMessageData } from "../types/Message"


export function AIMessage({ message }: { message: AIMessageData }) {
    return (
        <div className="ai-message">
            <p>Response: {message.response}</p>
            <p>Justification: {message.justification}</p>
            <p>Sources:</p>
            <ul>
                {message.sources.map(source => (
                    <li key={source}><a href={source} target="_blank" rel="noopener noreferrer">{source}</a></li>
                ))}
            </ul>
        </div>
    )
}
