// src/App.tsx
import { MessageList } from "./components/MessageList";
import type { Message } from "./types/Message";

const messages: Message[] = [
  {
    id: "1",
    role: "USER",
    prompt: "What's new in generative AI this week?",
  },
  {
    id: "2",
    role: "AI",
    response: "Several new papers on agent evaluation were released.",
    justification: "These were the most recent arXiv submissions in the genAI category.",
    sources: [
      "https://arxiv.org/abs/0000.00001",
      "https://arxiv.org/abs/0000.00002",
    ],
  },
  {
    id: "3",
    role: "USER",
    prompt: "Any news outside of research?",
  },
  {
    id: "4",
    role: "AI",
    response: "Nothing I could verify.",
    justification: "No reliable sources found.",
    sources: [],
  },
  {
    id: "5",
    role: "USER",
    prompt: "More text from me?",
  },
  {
    id: "10",
    role: "USER",
    prompt: "Any news outside of research?",
  },
  {
    id: "6",
    role: "USER",
    prompt: "Any news outside of research?",
  },
  {
    id: "8",
    role: "USER",
    prompt: "Any news outside of research?",
  },
  {
    id: "11",
    role: "AI",
    response: "Nothing I could verify.",
    justification: "No reliable sources found.",
    sources: [],
  },
  {
    id: "4111",
    role: "AI",
    response: "Nothing I could verify.",
    justification: "No reliable sources found.",
    sources: [],
  },
];


export default function App() {
  return <MessageList messages={messages} />;
}
