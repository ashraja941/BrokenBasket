"use client";

import { useRouter, usePathname } from "next/navigation";
import * as Dialog from "@radix-ui/react-dialog";
import { useState } from "react";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const isOnChatPage = pathname === "/chat";
  const [open, setOpen] = useState(false);

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <nav
        className={`fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-gray-100 shadow-md ${
          open ? "backdrop-blur-sm" : ""
        }`}
      >
        <div className="text-xl font-bold">Broken Basket</div>
        <div className="flex items-center gap-4">
          {/* Chat/Dashboard Button */}
          <button
            onClick={() => router.push(isOnChatPage ? "/" : "/chat")}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {isOnChatPage ? "Dashboard" : "Chat"}
          </button>

          {/* Profile Button */}
          <Dialog.Trigger asChild>
            <button className="w-10 h-10 flex items-center justify-center rounded-full bg-gray-800 text-white text-lg font-bold hover:bg-gray-900">
              S
            </button>
          </Dialog.Trigger>
        </div>
      </nav>

      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40" />
        <Dialog.Content className="fixed z-50 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white p-8 rounded-lg shadow-xl w-[95%] max-w-5xl">
          <Dialog.Title className="text-2xl font-semibold mb-4">Your Profile</Dialog.Title>

          {/* Edit states and data */}
          {(() => {
            const [isEditingProfile, setIsEditingProfile] = useState(false);
            const [isEditingPreferences, setIsEditingPreferences] = useState(false);

            const [profile, setProfile] = useState({
              weight: 65,
              height: 170,
              calories: 2200,
              age: 28,
            });

            const [preferences, setPreferences] = useState([
              "Vegetarian",
              "No dairy",
              "Low sugar",
              "High protein",
            ]);

            return (
              <>
                <div className="flex flex-col md:flex-row gap-6">
                  {/* Current Profile Box */}
                  <div className="flex-1 p-4 bg-gray-100 rounded-lg shadow-sm">
                    <div className="flex justify-between items-center mb-3">
                      <h2 className="text-lg font-semibold">Your Current Profile</h2>
                      {!isEditingProfile && (
                        <button
                          onClick={() => setIsEditingProfile(true)}
                          className="text-blue-600 hover:underline"
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
                                  setProfile({
                                    ...profile,
                                    [key]: Number(e.target.value),
                                  })
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
                  <div className="flex-1 p-4 bg-gray-100 rounded-lg shadow-sm">
                    <div className="flex justify-between items-center mb-3">
                      <h2 className="text-lg font-semibold">Your Preferences</h2>
                      {!isEditingPreferences && (
                        <button
                          onClick={() => setIsEditingPreferences(true)}
                          className="text-blue-600 hover:underline"
                        >
                          Edit
                        </button>
                      )}
                    </div>

                    {isEditingPreferences ? (
                      <ul className="space-y-2">
                        {preferences.map((pref, index) => (
                          <li key={index}>
                            <input
                              type="text"
                              value={pref}
                              onChange={(e) => {
                                const newPrefs = [...preferences];
                                newPrefs[index] = e.target.value;
                                setPreferences(newPrefs);
                              }}
                              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
                            />
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <ul className="list-disc list-inside text-sm text-gray-800 space-y-1">
                        {preferences.map((pref, index) => (
                          <li key={index}>{pref || "—"}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                {/* Button Row */}
                <div className="mt-6 flex justify-end gap-4">
                  {(isEditingProfile || isEditingPreferences) && (
                    <button
                      onClick={() => {
                        setIsEditingProfile(false);
                        setIsEditingPreferences(false);
                      }}
                      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      Save
                    </button>
                  )}
                  <Dialog.Close asChild>
                    <button className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                      Close
                    </button>
                  </Dialog.Close>
                </div>
              </>
            );
          })()}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

