// app/page.tsx
"use client";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const router = useRouter();

  return (
    <main className="flex flex-col items-center justify-center h-screen gap-6">
      <h1 className="text-3xl font-semibold">Dashboard</h1>
      <button
        onClick={() => router.push("/chat")}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Go to Chat Page
      </button>
    </main>
  );
}
