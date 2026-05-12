-- Migration: Add recipe_ratings and user_favorites tables
-- Run against `plan_my_plate` database

-- --------------------------------------------------------
-- Table structure for table `recipe_ratings`
-- One rating per user per recipe (upsert semantics)
-- --------------------------------------------------------

CREATE TABLE `recipe_ratings` (
  `rating_id`  int(11)   NOT NULL AUTO_INCREMENT,
  `user_id`    int(11)   NOT NULL,
  `recipe_id`  int(11)   NOT NULL,
  `rating`     tinyint   NOT NULL,
  `review`     text      DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`rating_id`),
  UNIQUE KEY `uq_user_recipe` (`user_id`, `recipe_id`),
  CONSTRAINT `fk_rr_user`   FOREIGN KEY (`user_id`)   REFERENCES `users`(`user_id`)    ON DELETE CASCADE,
  CONSTRAINT `fk_rr_recipe` FOREIGN KEY (`recipe_id`) REFERENCES `recipe`(`recipe_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Table structure for table `user_favorites`
-- Simple join table linking users to their favorite recipes
-- --------------------------------------------------------

CREATE TABLE `user_favorites` (
  `id`         int(11)   NOT NULL AUTO_INCREMENT,
  `user_id`    int(11)   NOT NULL,
  `recipe_id`  int(11)   NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_fav_recipe` (`user_id`, `recipe_id`),
  CONSTRAINT `fk_uf_user`   FOREIGN KEY (`user_id`)   REFERENCES `users`(`user_id`)    ON DELETE CASCADE,
  CONSTRAINT `fk_uf_recipe` FOREIGN KEY (`recipe_id`) REFERENCES `recipe`(`recipe_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
