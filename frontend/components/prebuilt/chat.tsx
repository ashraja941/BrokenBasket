"use client";

import { useState } from "react";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { EndpointsContext } from "@/app/agent";
import { useActions } from "@/utils/client";
import { LocalContext } from "@/app/shared";
import { StreamEvent } from "@langchain/core/tracers/log_stream";
import { AIMessage } from "@/ai/message";
import { HumanMessageText } from "./message";

// Typing indicator animation
function TypingIndicator() {
  return (
    <div className="ml-2 mt-2 w-fit flex gap-1 items-center text-gray-500 text-sm">
      <span className="dot w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0s" }} />
      <span className="dot w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
      <span className="dot w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }} />
    </div>
  );
}

function convertFileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64String = reader.result as string;
      resolve(base64String.split(",")[1]);
    };
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
}

function FileUploadMessage({ file }: { file: File }) {
  return (
    <div className="flex w-full max-w-fit ml-auto">
      <p>File uploaded: {file.name}</p>
    </div>
  );
}

export default function Chat() {
  const actions = useActions<typeof EndpointsContext>();

  const [elements, setElements] = useState<JSX.Element[]>([]);
  const [history, setHistory] = useState<[role: string, content: string][]>([]);
  const [input, setInput] = useState("");
  const [selectedFile, setSelectedFile] = useState<File>();
  const [isTyping, setIsTyping] = useState(false);

  async function onSubmit(input: string) {
    const newElements = [...elements];

    let base64File: string | undefined;
    let fileExtension = selectedFile?.type.split("/")[1];
    if (selectedFile) {
      base64File = await convertFileToBase64(selectedFile);
    }

    // Push user input and loading dots immediately
    const tempKey = history.length;
    newElements.push(
      <div className="flex flex-col w-full gap-1 mt-auto" key={`temp-${tempKey}`}>
        {selectedFile && <FileUploadMessage file={selectedFile} />}
        <HumanMessageText content={input} />
        <TypingIndicator />
      </div>
    );
    setElements(newElements);
    setIsTyping(true);

    const element = await actions.agent({
      input,
      chat_history: history,
      file:
        base64File && fileExtension
          ? { base64: base64File, extension: fileExtension }
          : undefined,
    });

    setIsTyping(false); // Done typing

    // Replace typing dots with real output
    newElements[tempKey] = (
      <div className="flex flex-col w-full gap-1 mt-auto" key={tempKey}>
        {selectedFile && <FileUploadMessage file={selectedFile} />}
        <HumanMessageText content={input} />
        <div className="flex flex-col gap-1 w-full max-w-fit mr-auto">
          {element.ui}
        </div>
      </div>
    );

    // Parse final AI message for chat history
    (async () => {
      const lastEvent = await element.lastEvent;

      if (Array.isArray(lastEvent)) {
        if (lastEvent[0].invoke_model?.result) {
          setHistory((prev) => [
            ...prev,
            ["human", input],
            ["ai", lastEvent[0].invoke_model.result],
          ]);
        } else if (lastEvent[1]?.invoke_tools) {
          setHistory((prev) => [
            ...prev,
            ["human", input],
            ["ai", `Tool result: ${JSON.stringify(lastEvent[1].invoke_tools.tool_result)}`],
          ]);
        } else {
          setHistory((prev) => [...prev, ["human", input]]);
        }
      } else if (lastEvent?.invoke_model?.result) {
        setHistory((prev) => [
          ...prev,
          ["human", input],
          ["ai", lastEvent.invoke_model.result],
        ]);
      }
    })();

    setElements([...newElements]);
    setInput("");
    setSelectedFile(undefined);
  }

  return (
    <div className="w-[70vw] overflow-y-scroll h-[80vh] flex flex-col gap-4 mx-auto border-[1px] border-gray-200 rounded-lg p-3 shadow-sm bg-gray-50/25">
      <LocalContext.Provider value={onSubmit}>
        <div className="flex flex-col w-full gap-1 mt-auto">{elements}</div>
      </LocalContext.Provider>

      <form
        onSubmit={async (e) => {
          e.preventDefault();
          await onSubmit(input);
        }}
        className="w-full flex flex-row gap-2"
      >
        <Input
          placeholder="What's the weather like in San Francisco?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <div className="w-[300px]">
          <Input
            placeholder="Upload"
            id="image"
            type="file"
            accept="image/*"
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                setSelectedFile(e.target.files[0]);
              }
            }}
          />
        </div>
        <Button type="submit">Submit</Button>
      </form>
    </div>
  );
}
