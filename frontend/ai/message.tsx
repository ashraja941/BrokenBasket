"use client";

import { AIMessageText } from "@/components/prebuilt/message";
import { StreamableValue, useStreamableValue } from "ai/rsc";
import { isJsonContent } from "@/utils/json-utils";

export function AIMessage(props: { value: StreamableValue<string> }) {
  const [data] = useStreamableValue(props.value);

  if (!data) {
    return null;
  }

  // Check if the content is JSON and hide it if it is
  if (isJsonContent(data)) {
    return null; // Don't display JSON messages
  }

  return <AIMessageText content={data} />;
}
