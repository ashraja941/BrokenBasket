"use client";
import Navbar from "@/components/Navbar";

export default function Dashboard() {
  return (
    <>
      <Navbar />
      <main className="flex flex-col items-center justify-center h-[calc(100vh-4rem)] gap-6">
        <h1 className="text-3xl font-semibold">Dashboard</h1>
        <button
          onClick={() => location.href = "/chat"}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Go to Chat Page
        </button>
      </main>
    </>
  );
}
