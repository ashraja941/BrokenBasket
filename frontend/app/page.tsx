"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import './globals.css';
import { ChevronLeft, ChevronRight } from "lucide-react";

type MealData = {
  name: string;
  calories: number;
  ingredients: {
    name: string;
    calories: number;
  }[];
};

export default function Dashboard() {
  const router = useRouter();
  const [mealPlan, setMealPlan] = useState<Record<string, Record<string, MealData>>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedMeal, setSelectedMeal] = useState<null | {
    day: string;
    time: string;
    data: MealData;
  }>(null);

  const cardWidth = 250;
  const visibleCount = 5;
  const centerOffset = 2;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`/api/preferences?userId=${'medhamajumdar1'}`);
        const data = await res.json();
        console.log("Fetched data:", data);

        if (!data.success) throw new Error(data.error);
        const parsed: Record<string, any> = {};
        Object.entries(data.data.mealPlan).forEach(([dayIndex, meals]) => {
          const dayLabel = `Day ${parseInt(dayIndex) + 1}`;
          const mealKeys = Object.keys(meals);
          parsed[dayLabel] = {};

          mealKeys.forEach((mealName) => {
            const ingredients = meals[mealName].map((i: any[]) => ({
              name: i[1],
              calories: i[0],
            }));
            const calories = ingredients.reduce((sum: number, item) => sum + item.calories, 0);

            parsed[dayLabel][mealName] = {
              name: mealName,
              calories,
              ingredients,
            };
          });
        });

        setMealPlan(parsed);
      } catch (err) {
        console.error("Error loading meal plan:", err);
      }
    };

    fetchData();
  }, []);

  const days = Object.keys(mealPlan);
  const totalCards = days.length + 4;

  const next = () => {
    if (currentIndex < totalCards - visibleCount) {
      setCurrentIndex((i) => i + 1);
    }
  };

  const prev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((i) => i - 1);
    }
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen px-8 py-6 relative overflow-visible w-full">
        <header className="flex justify-between items-center px-6 mt-5">
          <h1 className="text-4xl font-cursive italic text-[#DA8359] text-center w-full">
            Current Meal Plan
          </h1>
        </header>

        <div className="relative mt-16 mb-16 min-h-[420px] flex items-center justify-center">
          {/* Left Arrow */}
          <button
            onClick={prev}
            disabled={currentIndex === 0}
            className="absolute left-0 z-10 w-10 h-10 flex items-center justify-center rounded-full bg-white text-[#DA8359] shadow-md hover:bg-[#ECDFCC] disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          {/* Card Carousel */}
          <div className="overflow-hidden w-full max-w-[1400px] mx-auto px-4">
            <div
              className="flex transition-transform duration-500 ease-in-out"
              style={{
                transform: `translateX(-${currentIndex * cardWidth}px)`,
                width: `${totalCards * cardWidth}px`,
              }}
            >


              {Array.from({ length: totalCards }).map((_, i) => {
                const realIndex = i - 2;
                const day = days[realIndex];
                const isGhost = realIndex < 0 || realIndex >= days.length;

                const distanceFromCenter = Math.abs(i - (currentIndex + centerOffset));
                let scale = "scale-90";
                if (distanceFromCenter === 0) scale = "scale-95";
                else if (distanceFromCenter === 1) scale = "scale-90";

                return (
                  <div
                    key={i}
                    className={`transform transition-all duration-500 ease-in-out mx-2 flex-shrink-0 w-[250px] ${
                      isGhost ? "opacity-0 pointer-events-none" : "bg-[#A5B68D]"
                    } ${scale} rounded-3xl p-4 shadow-[inset_-4px_-4px_8px_#ffffff20,_4px_4px_12px_#6F826A]`}
                  >
                    {!isGhost && (
                      <>
                        <h2 className="text-xl font-bold mb-4 text-center text-white">{day}</h2>
                        {Object.entries(mealPlan[day]).map(([_, mealData], index) => (
                          <div key={index} className="mb-6 w-full">
                            <h3 className="text-white font-semibold mb-1">Meal {index + 1}</h3>
                            <div
                              className="rounded-xl bg-[#FCFAEE] p-3 shadow-inner border border-[#ECDFCC] cursor-pointer hover:bg-[#ECDFCC]"
                              onClick={() =>
                                setSelectedMeal({
                                  day,
                                  time: `Meal ${index + 1}`,
                                  data: mealData,
                                })
                              }
                            >
                              <p className="font-semibold text-sm text-[#DA8359]">
                                {mealData.name}
                              </p>
                              {/* <p className="text-xs text-gray-600">{mealData.calories} kcal</p> */}
                            </div>
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Arrow */}
          <button
            onClick={next}
            disabled={currentIndex >= totalCards - visibleCount}
            className="absolute right-0 z-10 w-10 h-10 flex items-center justify-center rounded-full bg-white text-[#DA8359] shadow-md hover:bg-[#ECDFCC] disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* Meal Details Modal */}
        {selectedMeal && (
          <div
            className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center"
            onClick={() => setSelectedMeal(null)}
          >
            <div
              className="bg-[#ECDFCC] p-6 rounded-lg w-96 shadow-xl relative text-[#444]"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setSelectedMeal(null)}
                className="absolute top-2 right-3 text-xl text-gray-500 hover:text-black"
              >
                ×
              </button>
              <h2 className="text-xl font-bold mb-2">{selectedMeal.data.name}</h2>
              <p className="mb-2">
                <strong>Ingredients:</strong>
              </p>
              <ul className="list-disc ml-6 text-sm">
                {selectedMeal.data.ingredients.map((ingredient, index) => (
                  <li key={index}>
                    {ingredient.name}: {ingredient.calories} g
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </main>
    </>
  );
}
