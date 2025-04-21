"use client";

import { useRouter, usePathname } from "next/navigation";
import * as Dialog from "@radix-ui/react-dialog";
import { useEffect, useState } from "react";
import { Plus, Minus } from "lucide-react";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const isOnChatPage = pathname === "/chat";
  const [open, setOpen] = useState(false);

  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [isEditingPreferences, setIsEditingPreferences] = useState(false);
  const [daysUntilCheatDay, setDaysUntilCheatDay] = useState(1);

  const [profile, setProfile] = useState({
    weight: 65,
    height: 170,
    calories: 2200,
    age: 28,
  });

  const [mealPlan, setMealPlan] = useState({});

  const [preferencesText, setPreferencesText] = useState("");
  const userId = "medhamajumdar1";

  const updateCheatDay = async (value: number) => {
    try {
      const preferences = preferencesText
        .split(",")
        .map((p) => p.trim())
        .filter((p) => p.length > 0);
  
      const res = await fetch("/api/preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId,
          preferences,
          profile,
          daysUntilCheatDay: value,
          mealPlan,
        }),
      });
  
      const data = await res.json();
      if (!data.success) throw new Error(data.error);
  
      // Only update state if DB save was successful
      setDaysUntilCheatDay(value);
    } catch (err) {
      console.error("Failed to update cheat day progress:", err);
    }
  };
  

  // 🟩 Fetch data on load
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`/api/preferences?userId=${userId}`);
        const data = await res.json();
        if (data.success && data.data) {
          if (typeof data.data.daysUntilCheatDay === "number")
            setDaysUntilCheatDay(data.data.daysUntilCheatDay);
          if (data.data.profile) setProfile(data.data.profile);
          if (data.data.preferences?.length)
            setPreferencesText(data.data.preferences.join(", "));
          if (data.data.mealPlan) setMealPlan(data.data.mealPlan);
        }
      } catch (err) {
        console.error("Failed to fetch preferences:", err);
      }
    };
    fetchData();
  }, []);

  // 🟩 Save to DB
  const handleSave = async () => {
    try {
      const preferences = preferencesText
        .split(",")
        .map((p) => p.trim())
        .filter((p) => p.length > 0);

      const res = await fetch("/api/preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId, preferences, profile, daysUntilCheatDay, mealPlan }),
      });

      const data = await res.json();
      if (!data.success) throw new Error(data.error);
    } catch (err) {
      console.error("Failed to save:", err);
    }

    setIsEditingProfile(false);
    setIsEditingPreferences(false);
  };

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <nav
        className={`fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-[#ECDFCC] shadow-md ${
          open ? "backdrop-blur-sm" : ""
        }`}
      >
        <div className="flex items-center gap-2">
          <img src="/logo_basket.png" alt="Basket Icon" className="h-14 w-auto" />
          <img src="/logo_text.png" alt="Broken Basket" className="h-10 w-auto" />
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push(isOnChatPage ? "/" : "/chat")}
            className="w-28 px-4 py-2 bg-[#6F826A] text-white rounded hover:brightness-110"
          >
            {isOnChatPage ? "Dashboard" : "Chat"}
          </button>

          <Dialog.Trigger asChild>
            <button className="w-10 h-10 flex items-center justify-center rounded-full bg-[#6F826A] text-white text-lg font-bold hover:brightness-110">
              S
              {/* <img src="/profile.jpg" alt="Profile" className="w-full h-full object-cover" /> */}
            </button>
          </Dialog.Trigger>
        </div>
      </nav>

      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40" />
        <Dialog.Content className="fixed z-50 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#FCFAEE] p-8 rounded-lg shadow-xl w-[95%] max-w-5xl">
          <Dialog.Title className="text-2xl font-semibold mb-4">Your Profile</Dialog.Title>
            {/* Days to Cheat Day Progress */}
            <div className="mb-6 flex flex-col gap-1">
            <p className="text-sm font-medium text-gray-700">
              Days left until Cheat Day:{" "}
              <span
                className="font-semibold"
                style={{
                  color:
                    daysUntilCheatDay <= 2
                      ? "#ef4444"
                      : daysUntilCheatDay <= 5
                      ? "#f59e0b"
                      : "#10b981",
                }}
              >
                {daysUntilCheatDay}
              </span>
            </p>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    if (daysUntilCheatDay > 0) {
                      const newVal = daysUntilCheatDay - 1;
                      updateCheatDay(newVal);
                    }
                  }}
                  className="w-7 h-7 bg-[#DA8359] hover:brightness-110 text-white rounded-full flex items-center justify-center text-lg"
                >
                  <Minus className="w-4 h-4" />
                </button>
                <div className="w-64 bg-[#ECDFCC] rounded-full h-3 overflow-hidden shadow-inner border border-[#A5B68D]">
                    <div
                      className="h-full rounded-full transition-all duration-300"
                      style={{
                        width: `${(daysUntilCheatDay / 7) * 100}%`,
                        backgroundColor:
                          daysUntilCheatDay <= 2
                            ? "#ef4444" // red
                            : daysUntilCheatDay <= 5
                            ? "#f59e0b" // orange
                            : "#10b981", // green
                      }}
                    ></div>
                  </div>
                  <button
                    onClick={() => {
                      if (daysUntilCheatDay < 7) {
                        const newVal = daysUntilCheatDay + 1;
                        updateCheatDay(newVal);
                      }
                    }}
                    className="w-7 h-7 bg-[#6F826A] hover:brightness-110 text-white rounded-full flex items-center justify-center text-lg"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
              </div>
              <button
              onClick={() => updateCheatDay(0)}
              className="mt-2 text-sm text-red-600 hover:underline self-start"
            >
              Reset Progress
            </button>
            </div>
          <div className="flex flex-col md:flex-row gap-6">
            {/* Profile Box */}
            <div className="flex-1 p-4 bg-[#ECDFCC] rounded-lg shadow-inner border border-[#A5B68D]">
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-lg font-semibold text-[#3F4F44]">Your Current Profile</h2>
                {!isEditingProfile && (
                  <button
                    onClick={() => setIsEditingProfile(true)}
                    className="text-[#DA8359] hover:underline"
                  >
                    Edit
                  </button>
                )}
              </div>

              {isEditingProfile ? (
                <div className="grid grid-cols-2 gap-4">
                  {(["weight", "height", "calories", "age"] as (keyof typeof profile)[]).map(
                    (key) => (
                      <div key={key}>
                        <label className="block text-sm font-medium text-gray-700 capitalize">
                          {key}
                        </label>
                        <input
                          type="number"
                          value={profile[key]}
                          onChange={(e) =>
                            setProfile({ ...profile, [key]: Number(e.target.value) })
                          }
                          className="mt-1 w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    )
                  )}
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4 text-sm text-gray-800">
                  <p>Weight: {profile.weight} kg</p>
                  <p>Height: {profile.height} cm</p>
                  <p>Calories: {profile.calories} kcal</p>
                  <p>Age: {profile.age}</p>
                </div>
              )}
            </div>

            {/* Preferences Box */}
            <div className="flex-1 p-4 bg-[#ECDFCC] rounded-lg shadow-inner border border-[#A5B68D]">
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-lg font-semibold text-[#3F4F44]">Your Preferences</h2>
                {!isEditingPreferences && (
                  <button
                    onClick={() => setIsEditingPreferences(true)}
                    className="text-[#DA8359] hover:underline"
                  >
                    Edit
                  </button>
                )}
              </div>

              {isEditingPreferences ? (
                <textarea
                  value={preferencesText}
                  onChange={(e) => setPreferencesText(e.target.value)}
                  className="w-full min-h-[120px] p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter comma-separated preferences, e.g., Vegetarian, No dairy"
                />
              ) : (
                <ul className="list-none text-sm text-gray-800 space-y-1">
                  {preferencesText
                    .split(",")
                    .map((p) => p.trim())
                    .filter((p) => p.length > 0)
                    .map((pref, index) => (
                      <li key={index}>{pref}</li>
                    ))}
                </ul>
              )}
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-4">
            {(isEditingProfile || isEditingPreferences) && (
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-[#6F826A] text-white rounded hover:brightness-110"
              >
                Save
              </button>
            )}
            <Dialog.Close asChild>
              <button className="px-4 py-2 bg-[#3F4F44] text-white rounded hover:brightness-110">
                Close
              </button>
            </Dialog.Close>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}