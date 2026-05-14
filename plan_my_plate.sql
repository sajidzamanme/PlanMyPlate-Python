-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jan 30, 2026 at 00:00 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `plan_my_plate`
--

-- --------------------------------------------------------

--
-- Table structure for table `diets`
--

CREATE TABLE `diets` (
  `diet_id` int(11) NOT NULL,
  `diet_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `grocery_list`
--

CREATE TABLE `grocery_list` (
  `list_id` int(11) NOT NULL,
  `date_created` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `grocery_list_ingredients`
--

CREATE TABLE `grocery_list_ingredients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `list_id` int(11) NOT NULL,
  `ing_id` int(11) NOT NULL,
  `quantity` float DEFAULT 1,
  `unit` varchar(50) DEFAULT 'unit',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ingredients`
--

CREATE TABLE `ingredients` (
  `ing_id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `price` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ingredient_tags`
--

CREATE TABLE `ingredient_tags` (
  `tag_id` int(11) NOT NULL,
  `tag_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ingredient_tag_map`
--

CREATE TABLE `ingredient_tag_map` (
  `ing_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inventory`
--

CREATE TABLE `inventory` (
  `inv_id` int(11) NOT NULL,
  `last_update` date DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inv_item`
--

CREATE TABLE `inv_item` (
  `item_id` int(11) NOT NULL,
  `quantity` float DEFAULT NULL,
  `unit` varchar(50) DEFAULT 'unit',
  `date_added` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `inv_id` int(11) NOT NULL,
  `ing_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `meal_plan`
--

CREATE TABLE `meal_plan` (
  `mp_id` int(11) NOT NULL,
  `start_date` date DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `meal_slot`
--

CREATE TABLE `meal_slot` (
  `id` int(11) NOT NULL,
  `mp_id` int(11) NOT NULL,
  `recipe_id` int(11) NOT NULL,
  `slot_index` int(11) NOT NULL,
  `meal_type` varchar(20) NOT NULL,
  `day_number` int(11) NOT NULL,
  `servings_multiplier` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `recipe`
--

CREATE TABLE `recipe` (
  `recipe_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `calories` int(11) DEFAULT NULL,
  `prep_time` int(11) DEFAULT NULL,
  `cook_time` int(11) DEFAULT NULL,
  `servings` int(11) DEFAULT NULL,
  `instructions` text DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `recipe_ingredients`
--

CREATE TABLE `recipe_ingredients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipe_id` int(11) NOT NULL,
  `ing_id` int(11) NOT NULL,
  `quantity` float DEFAULT NULL,
  `unit` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `weight` decimal(5,2) DEFAULT NULL,
  `budget` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `reset_token` varchar(100) DEFAULT NULL,
  `reset_token_expiry` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_preferences`
--

CREATE TABLE `user_preferences` (
  `pref_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `diet_id` int(11) DEFAULT NULL,
  `budget` decimal(10,2) DEFAULT NULL,
  `height` decimal(5,2) DEFAULT NULL COMMENT 'Height in cm',
  `weight` decimal(5,2) DEFAULT NULL COMMENT 'Weight in kg',
  `gender` varchar(10) DEFAULT NULL COMMENT 'male, female, or other'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_preferences_allergies`
-- Links user preferences to ingredients the user is allergic to.
-- Allergens are stored as ingredient IDs (same lookup as dislikes).
--

CREATE TABLE `user_preferences_allergies` (
  `pref_id` int(11) NOT NULL,
  `ing_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_preferences_dislikes`
-- Links user preferences to ingredients the user dislikes.
--

CREATE TABLE `user_preferences_dislikes` (
  `pref_id` int(11) NOT NULL,
  `ing_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

ALTER TABLE `diets`
  ADD PRIMARY KEY (`diet_id`),
  ADD UNIQUE KEY `diet_name` (`diet_name`);

ALTER TABLE `grocery_list`
  ADD PRIMARY KEY (`list_id`),
  ADD KEY `user_id` (`user_id`);

ALTER TABLE `grocery_list_ingredients`
  ADD KEY `list_id` (`list_id`),
  ADD KEY `ing_id` (`ing_id`);

ALTER TABLE `ingredients`
  ADD PRIMARY KEY (`ing_id`),
  ADD UNIQUE KEY `name` (`name`);

ALTER TABLE `ingredient_tags`
  ADD PRIMARY KEY (`tag_id`),
  ADD UNIQUE KEY `tag_name` (`tag_name`);

ALTER TABLE `ingredient_tag_map`
  ADD PRIMARY KEY (`ing_id`,`tag_id`),
  ADD KEY `tag_id` (`tag_id`);

ALTER TABLE `inventory`
  ADD PRIMARY KEY (`inv_id`),
  ADD KEY `user_id` (`user_id`);

ALTER TABLE `inv_item`
  ADD PRIMARY KEY (`item_id`),
  ADD KEY `inv_id` (`inv_id`),
  ADD KEY `ing_id` (`ing_id`),
  ADD KEY `idx_inv_item_expiry` (`expiry_date`);

ALTER TABLE `meal_plan`
  ADD PRIMARY KEY (`mp_id`),
  ADD KEY `user_id` (`user_id`);

ALTER TABLE `meal_slot`
  ADD PRIMARY KEY (`id`),
  ADD KEY `mp_id` (`mp_id`),
  ADD KEY `recipe_id` (`recipe_id`);

ALTER TABLE `recipe`
  ADD PRIMARY KEY (`recipe_id`);

ALTER TABLE `recipe_ingredients`
  ADD KEY `recipe_id` (`recipe_id`),
  ADD KEY `ing_id` (`ing_id`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `phone` (`phone`);

ALTER TABLE `user_preferences`
  ADD PRIMARY KEY (`pref_id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `diet_id` (`diet_id`);

ALTER TABLE `user_preferences_allergies`
  ADD PRIMARY KEY (`pref_id`,`ing_id`),
  ADD KEY `ing_id` (`ing_id`);

ALTER TABLE `user_preferences_dislikes`
  ADD PRIMARY KEY (`pref_id`,`ing_id`),
  ADD KEY `ing_id` (`ing_id`);

--
-- AUTO_INCREMENT for dumped tables
--

ALTER TABLE `diets`
  MODIFY `diet_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `grocery_list`
  MODIFY `list_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `grocery_list_ingredients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `ingredients`
  MODIFY `ing_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `ingredient_tags`
  MODIFY `tag_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `inventory`
  MODIFY `inv_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `inv_item`
  MODIFY `item_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `meal_plan`
  MODIFY `mp_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `meal_slot`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `recipe`
  MODIFY `recipe_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `recipe_ingredients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `user_preferences`
  MODIFY `pref_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Foreign key constraints
--

ALTER TABLE `grocery_list`
  ADD CONSTRAINT `fk_grocery_list_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE;

ALTER TABLE `grocery_list_ingredients`
  ADD CONSTRAINT `fk_gli_list` FOREIGN KEY (`list_id`) REFERENCES `grocery_list`(`list_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_gli_ingredient` FOREIGN KEY (`ing_id`) REFERENCES `ingredients`(`ing_id`) ON DELETE CASCADE;

ALTER TABLE `ingredient_tag_map`
  ADD CONSTRAINT `fk_itm_ingredient` FOREIGN KEY (`ing_id`) REFERENCES `ingredients`(`ing_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_itm_tag` FOREIGN KEY (`tag_id`) REFERENCES `ingredient_tags`(`tag_id`) ON DELETE CASCADE;

ALTER TABLE `inventory`
  ADD CONSTRAINT `fk_inventory_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE;

ALTER TABLE `inv_item`
  ADD CONSTRAINT `fk_inv_item_inventory` FOREIGN KEY (`inv_id`) REFERENCES `inventory`(`inv_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_inv_item_ingredient` FOREIGN KEY (`ing_id`) REFERENCES `ingredients`(`ing_id`) ON DELETE CASCADE;

ALTER TABLE `meal_plan`
  ADD CONSTRAINT `fk_meal_plan_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE;

ALTER TABLE `meal_slot`
  ADD CONSTRAINT `fk_meal_slot_plan` FOREIGN KEY (`mp_id`) REFERENCES `meal_plan`(`mp_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_meal_slot_recipe` FOREIGN KEY (`recipe_id`) REFERENCES `recipe`(`recipe_id`) ON DELETE CASCADE;

ALTER TABLE `recipe_ingredients`
  ADD CONSTRAINT `fk_ri_recipe` FOREIGN KEY (`recipe_id`) REFERENCES `recipe`(`recipe_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_ri_ingredient` FOREIGN KEY (`ing_id`) REFERENCES `ingredients`(`ing_id`) ON DELETE CASCADE;

ALTER TABLE `user_preferences`
  ADD CONSTRAINT `fk_up_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_up_diet` FOREIGN KEY (`diet_id`) REFERENCES `diets`(`diet_id`) ON DELETE SET NULL;

ALTER TABLE `user_preferences_allergies`
  ADD CONSTRAINT `fk_upa_pref` FOREIGN KEY (`pref_id`) REFERENCES `user_preferences`(`pref_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_upa_ingredient` FOREIGN KEY (`ing_id`) REFERENCES `ingredients`(`ing_id`) ON DELETE CASCADE;

ALTER TABLE `user_preferences_dislikes`
  ADD CONSTRAINT `fk_upd_pref` FOREIGN KEY (`pref_id`) REFERENCES `user_preferences`(`pref_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_upd_ingredient` FOREIGN KEY (`ing_id`) REFERENCES `ingredients`(`ing_id`) ON DELETE CASCADE;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
