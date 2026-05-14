-- Migration: Add height, weight, gender to user_preferences for BMI calculation
-- Run this against your plan_my_plate database

ALTER TABLE `user_preferences`
  ADD COLUMN `height` DECIMAL(5,2) DEFAULT NULL COMMENT 'Height in cm',
  ADD COLUMN `weight` DECIMAL(5,2) DEFAULT NULL COMMENT 'Weight in kg',
  ADD COLUMN `gender` VARCHAR(10) DEFAULT NULL COMMENT 'male, female, or other';
