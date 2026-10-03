import { UserMessage } from './UserMessage';
import { AIMessage } from './AIMessage';
import type { Message } from '../types/Message';

export function MessageList ({messages}: { messages: Message[] }){

return <div className="message-list">
 {messages.map(message => {
    if (message.role === 'USER') {
        return <UserMessage key={message.id} message={message} />;
    } else {
        return <AIMessage key={message.id} message={message} />;
    }
})}
</div>;
}
