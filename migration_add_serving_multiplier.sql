-- Migration: Drop family servings, add per-slot serving multiplier
-- Date: 2026-05-07
-- Description: Remove the unused global 'servings' from user_preferences
--              and add a per-slot 'servings_multiplier' (1-6) to meal_slot.

-- Step 1: Add servings_multiplier to meal_slot (default 1 for existing rows)
ALTER TABLE `meal_slot`
  ADD COLUMN `servings_multiplier` INT NOT NULL DEFAULT 1;

-- Step 2: Remove servings from user_preferences
ALTER TABLE `user_preferences`
  DROP COLUMN `servings`;
