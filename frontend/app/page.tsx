"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type MealData = {
  name: string;
  calories: number;
  ingredients: {
    name: string;
    calories: number;
  }[];
};


type DailyMeal = {
  [key in "Breakfast" | "Lunch" | "Dinner"]?: MealData;
};

export default function Dashboard() {
  const router = useRouter();
  const [mealPlan, setMealPlan] = useState<Record<string, DailyMeal>>({});
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
        const res = await fetch("/meal_plan.json");
        const data = await res.json();

        const parsed: Record<string, any> = {};
        Object.entries(data).forEach(([dayIndex, meals]) => {
          const dayLabel = `Day ${parseInt(dayIndex) + 1}`;
          const mealKeys = Object.keys(meals);
          parsed[dayLabel] = {};

          mealKeys.forEach((mealName, i) => {
            const slot = ["Breakfast", "Lunch", "Dinner"][i % 3];
            const ingredients = meals[mealName].map((i: any[]) => ({
              name: i[1],
              calories: i[0],
            }));
            
            const calories = meals[mealName].reduce((sum: number, item: any[]) => sum + item[0], 0);

            parsed[dayLabel][slot] = {
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
    <main className="min-h-screen bg-pink-100 px-4 py-6 relative overflow-visible">
      <header className="flex justify-between items-center px-6">
        <h1 className="text-4xl font-cursive italic text-gray-800">Current Meal Plan</h1>
        <button className="bg-pink-500 text-white px-4 py-2 rounded-full hover:bg-pink-600 text-sm font-semibold shadow-md">
          ➕ Add new meal plan
        </button>
      </header>

      <div className="relative mt-16 mb-16 min-h-[420px] flex items-center justify-center">
        {/* Left Arrow */}
        <button
          onClick={prev}
          disabled={currentIndex === 0}
          className="absolute left-0 z-10 w-10 h-10 flex items-center justify-center rounded-full bg-white text-gray-700 shadow-md hover:bg-pink-200 disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none"
        >
          ◀
        </button>

        {/* Card Carousel */}
        <div className="overflow-hidden w-[1250px]">
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
                    isGhost ? "opacity-0 pointer-events-none" : "bg-pink-200"
                  } ${scale} rounded-3xl p-4 shadow-[inset_-4px_-4px_8px_#ffffff20,_4px_4px_12px_#ec4899]`}
                >
                  {!isGhost && (
                    <>
                      <h2 className="text-xl font-bold mb-4 text-center text-gray-700">{day}</h2>
                      {["Breakfast", "Lunch", "Dinner"].map((slot) => {
                        const meal = mealPlan[day][slot as keyof DailyMeal];
                        return (
                          meal && (
                            <div key={slot} className="mb-6 w-full">
                              <h3 className="text-pink-600 font-semibold mb-1">{slot}</h3>
                              <div
                                className="rounded-xl bg-white p-3 shadow-inner border border-pink-300 cursor-pointer hover:bg-pink-50"
                                onClick={() =>
                                  setSelectedMeal({
                                    day,
                                    time: slot,
                                    data: meal,
                                  })
                                }
                              >
                                <p className="font-semibold text-sm text-gray-800">{meal.name}</p>
                                <p className="text-xs text-gray-500">
                                  {meal.calories} kcal
                                </p>
                              </div>
                            </div>
                          )
                        );
                      })}
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
          className="absolute right-0 z-10 w-10 h-10 flex items-center justify-center rounded-full bg-white text-gray-700 shadow-md hover:bg-pink-200 disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none"
        >
          ▶
        </button>
      </div>

      <div className="flex justify-center mt-10">
        <button
          onClick={() => router.push("/chat")}
          className="px-6 py-3 bg-pink-500 text-white rounded-lg hover:bg-pink-600 shadow-md"
        >
          Chat Page
        </button>
      </div>

      {/* Meal Details Modal */}
      {selectedMeal && (
        <div
          className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center"
          onClick={() => setSelectedMeal(null)}
        >
          <div
            className="bg-white p-6 rounded-lg w-96 shadow-xl relative"
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
              <strong>Calories:</strong> {selectedMeal.data.calories} kcal
            </p>
            <p className="mb-2">
              <strong>Ingredients:</strong>
            </p>
            <ul className="list-disc ml-6 text-sm">
              {selectedMeal.data.ingredients.map((ingredient, index) => (
                <li key={index}>
                  {ingredient.name}: {ingredient.calories} kcal
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </main>
  );
}
