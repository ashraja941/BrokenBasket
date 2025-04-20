// models/Preferences.ts
import mongoose from "mongoose";

const PreferencesSchema = new mongoose.Schema({
    userId: { type: String, required: true, unique: true },
    profile: {
      weight: Number,
      height: Number,
      calories: Number,
      age: Number,
    },
    preferences: [String],
    daysUntilCheatDay: { type: Number, default: 1 },
  });

export default mongoose.models.Preferences ||
  mongoose.model("Preferences", PreferencesSchema);
