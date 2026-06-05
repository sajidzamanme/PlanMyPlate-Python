CREATE TABLE diets (
  diet_id INT NOT NULL AUTO_INCREMENT,
  diet_name VARCHAR(50) NOT NULL,
  PRIMARY KEY (diet_id),
  UNIQUE KEY diet_name (diet_name)
);

CREATE TABLE users (
  user_id INT NOT NULL AUTO_INCREMENT,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(150) NOT NULL,
  password VARCHAR(255) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  date_of_birth DATE DEFAULT NULL,
  age INT DEFAULT NULL,
  weight DECIMAL(5,2) DEFAULT NULL,
  budget DECIMAL(10,2) DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reset_token VARCHAR(100) DEFAULT NULL,
  reset_token_expiry TIMESTAMP NULL DEFAULT NULL,
  is_deleted TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id),
  UNIQUE KEY email (email),
  UNIQUE KEY phone (phone)
);

CREATE TABLE user_preferences (
  pref_id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  budget DECIMAL(10,2) DEFAULT NULL,
  height DECIMAL(5,2) DEFAULT NULL,
  weight DECIMAL(5,2) DEFAULT NULL,
  gender VARCHAR(10) DEFAULT NULL,
  PRIMARY KEY (pref_id),
  UNIQUE KEY user_id (user_id),
  CONSTRAINT fk_up_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE user_preferences_allergies (
  pref_id INT NOT NULL,
  ing_id INT NOT NULL,
  PRIMARY KEY (pref_id, ing_id),
  KEY ing_id (ing_id),
  CONSTRAINT fk_upa_pref FOREIGN KEY (pref_id) REFERENCES user_preferences(pref_id) ON DELETE CASCADE
);

CREATE TABLE user_preferences_dislikes (
  pref_id INT NOT NULL,
  ing_id INT NOT NULL,
  PRIMARY KEY (pref_id, ing_id),
  KEY ing_id (ing_id),
  CONSTRAINT fk_upd_pref FOREIGN KEY (pref_id) REFERENCES user_preferences(pref_id) ON DELETE CASCADE
);

CREATE TABLE user_preferences_diets (
  pref_id INT NOT NULL,
  diet_id INT NOT NULL,
  PRIMARY KEY (pref_id, diet_id),
  KEY diet_id (diet_id),
  CONSTRAINT fk_upd_diet_pref FOREIGN KEY (pref_id) REFERENCES user_preferences(pref_id) ON DELETE CASCADE,
  CONSTRAINT fk_upd_diet_diet FOREIGN KEY (diet_id) REFERENCES diets(diet_id) ON DELETE CASCADE
);

CREATE TABLE ingredients (
  ing_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(150) NOT NULL,
  price DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (ing_id),
  UNIQUE KEY name (name)
);

CREATE TABLE ingredient_tags (
  tag_id INT NOT NULL AUTO_INCREMENT,
  tag_name VARCHAR(50) NOT NULL,
  PRIMARY KEY (tag_id),
  UNIQUE KEY tag_name (tag_name)
);

CREATE TABLE ingredient_tag_map (
  ing_id INT NOT NULL,
  tag_id INT NOT NULL,
  PRIMARY KEY (ing_id, tag_id),
  KEY tag_id (tag_id),
  CONSTRAINT fk_itm_ingredient FOREIGN KEY (ing_id) REFERENCES ingredients(ing_id) ON DELETE CASCADE,
  CONSTRAINT fk_itm_tag FOREIGN KEY (tag_id) REFERENCES ingredient_tags(tag_id) ON DELETE CASCADE
);

CREATE TABLE recipe (
  recipe_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(200) NOT NULL,
  description TEXT DEFAULT NULL,
  calories INT DEFAULT NULL,
  protein FLOAT DEFAULT NULL,
  carbs FLOAT DEFAULT NULL,
  fat FLOAT DEFAULT NULL,
  fiber FLOAT DEFAULT NULL,
  prep_time INT DEFAULT NULL,
  cook_time INT DEFAULT NULL,
  instructions TEXT DEFAULT NULL,
  image_url VARCHAR(255) DEFAULT NULL,
  is_deleted TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (recipe_id)
);

CREATE TABLE recipe_ingredients (
  id INT NOT NULL AUTO_INCREMENT,
  recipe_id INT NOT NULL,
  ing_id INT NOT NULL,
  quantity FLOAT DEFAULT NULL,
  unit VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY recipe_id (recipe_id),
  KEY ing_id (ing_id),
  CONSTRAINT fk_ri_recipe FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id) ON DELETE CASCADE,
  CONSTRAINT fk_ri_ingredient FOREIGN KEY (ing_id) REFERENCES ingredients(ing_id) ON DELETE CASCADE
);

CREATE TABLE recipe_ratings (
  rating_id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  recipe_id INT NOT NULL,
  rating SMALLINT NOT NULL,
  review TEXT DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (rating_id),
  UNIQUE KEY uq_user_recipe_rating (user_id, recipe_id),
  KEY recipe_id (recipe_id),
  CONSTRAINT fk_rr_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_rr_recipe FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id) ON DELETE CASCADE
);

CREATE TABLE user_favorites (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  recipe_id INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_user_recipe_favorite (user_id, recipe_id),
  KEY recipe_id (recipe_id),
  CONSTRAINT fk_uf_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_uf_recipe FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id) ON DELETE CASCADE
);

CREATE TABLE meal_plan (
  mp_id INT NOT NULL AUTO_INCREMENT,
  start_date DATE DEFAULT NULL,
  duration INT DEFAULT NULL,
  status VARCHAR(50) DEFAULT NULL,
  user_id INT NOT NULL,
  PRIMARY KEY (mp_id),
  KEY user_id (user_id),
  CONSTRAINT fk_meal_plan_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE meal_slot (
  id INT NOT NULL AUTO_INCREMENT,
  mp_id INT NOT NULL,
  recipe_id INT NOT NULL,
  slot_index INT NOT NULL,
  meal_type VARCHAR(20) NOT NULL,
  day_number INT NOT NULL,
  servings_multiplier INT NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  KEY mp_id (mp_id),
  KEY recipe_id (recipe_id),
  CONSTRAINT fk_meal_slot_plan FOREIGN KEY (mp_id) REFERENCES meal_plan(mp_id) ON DELETE CASCADE,
  CONSTRAINT fk_meal_slot_recipe FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id) ON DELETE CASCADE
);

CREATE TABLE grocery_list (
  list_id INT NOT NULL AUTO_INCREMENT,
  date_created DATE DEFAULT NULL,
  status VARCHAR(50) DEFAULT NULL,
  user_id INT NOT NULL,
  PRIMARY KEY (list_id),
  KEY user_id (user_id),
  CONSTRAINT fk_grocery_list_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE grocery_list_ingredients (
  id INT NOT NULL AUTO_INCREMENT,
  list_id INT NOT NULL,
  ing_id INT NOT NULL,
  quantity FLOAT DEFAULT 1,
  unit VARCHAR(50) DEFAULT 'unit',
  PRIMARY KEY (id),
  KEY list_id (list_id),
  KEY ing_id (ing_id),
  CONSTRAINT fk_gli_list FOREIGN KEY (list_id) REFERENCES grocery_list(list_id) ON DELETE CASCADE,
  CONSTRAINT fk_gli_ingredient FOREIGN KEY (ing_id) REFERENCES ingredients(ing_id) ON DELETE CASCADE
);

CREATE TABLE inventory (
  inv_id INT NOT NULL AUTO_INCREMENT,
  last_update DATE DEFAULT NULL,
  user_id INT NOT NULL,
  PRIMARY KEY (inv_id),
  KEY user_id (user_id),
  CONSTRAINT fk_inventory_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE inv_item (
  item_id INT NOT NULL AUTO_INCREMENT,
  quantity FLOAT DEFAULT NULL,
  unit VARCHAR(50) DEFAULT 'unit',
  date_added DATE DEFAULT NULL,
  expiry_date DATE DEFAULT NULL,
  inv_id INT NOT NULL,
  ing_id INT NOT NULL,
  PRIMARY KEY (item_id),
  KEY inv_id (inv_id),
  KEY ing_id (ing_id),
  KEY idx_inv_item_expiry (expiry_date),
  CONSTRAINT fk_inv_item_inventory FOREIGN KEY (inv_id) REFERENCES inventory(inv_id) ON DELETE CASCADE,
  CONSTRAINT fk_inv_item_ingredient FOREIGN KEY (ing_id) REFERENCES ingredients(ing_id) ON DELETE CASCADE
);
