"use client";

import Chat from "@/components/prebuilt/chat";
import Navbar from "@/components/Navbar"; // make sure the path is correct

export default function ChatPage() {
  return (
    <>
      <Navbar />
      <main className="pt-20 flex h-[calc(100vh-4rem)] flex-col items-center justify-between px-24">
        <div className="w-full min-w-[600px] flex flex-col gap-4">
          <Chat />
        </div>
      </main>
    </>
  );
}