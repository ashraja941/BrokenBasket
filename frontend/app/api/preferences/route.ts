import { NextRequest, NextResponse } from "next/server";
import { connectToDB } from "@/lib/mongodb";
import Preferences from "@/models/Preferences";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const userId = searchParams.get("userId");

  if (!userId) return NextResponse.json({ success: false, error: "Missing userId" }, { status: 400 });

  try {
    await connectToDB();
    const data = await Preferences.findOne({ userId });
    return NextResponse.json({ success: true, data: data || null });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(req: Request) {
  const { userId, preferences, profile, daysUntilCheatDay, mealPlan } = await req.json();

  if (!userId || !preferences || !profile) {
    return NextResponse.json({ success: false, error: "Missing data" }, { status: 400 });
  }

  try {
    await connectToDB();
    const updated = await Preferences.findOneAndUpdate(
      { userId },
      { preferences, profile, daysUntilCheatDay, mealPlan },
      { upsert: true, new: true }
    );
    return NextResponse.json({ success: true, data: updated });
  } catch (err: any) {
    return NextResponse.json({ success: false, error: err.message }, { status: 500 });
  }
}

