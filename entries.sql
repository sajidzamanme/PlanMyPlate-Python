INSERT INTO diets (diet_name) VALUES
('Omnivore'),
('Vegetarian'),
('Vegan'),
('Pescatarian'),
('Low Carb'),
('High Protein'),
('Diabetic Friendly');

INSERT INTO ingredient_tags (tag_name) VALUES
('Protein'),
('Vegetable'),
('Carb'),
('Dairy'),
('Fat'),
('Seafood'),
('Spice'),
('Plant-Based');

INSERT INTO ingredients (name, price) VALUES
('Rice', 1.50),
('Chicken', 4.50),
('Beef', 7.50),
('Mutton', 9.00),
('Hilsa Fish', 12.00),
('Rui Fish', 6.50),
('Shrimp', 8.00),
('Eggs', 3.00),
('Milk', 1.50),
('Yogurt', 1.20),
('Lentils (Dal)', 2.00),
('Potato', 0.80),
('Onion', 0.60),
('Garlic', 0.50),
('Ginger', 0.50),
('Green Chili', 0.30),
('Tomato', 0.70),
('Spinach', 1.00),
('Cauliflower', 1.20),
('Cabbage', 1.10),
('Eggplant', 1.30),
('Mustard Oil', 2.50),
('Soybean Oil', 2.00),
('Turmeric', 0.20),
('Cumin', 0.20),
('Coriander Powder', 0.20),
('Red Chili Powder', 0.20),
('Salt', 0.10),
('Sugar', 0.20),
('Bread', 1.50),
('Puffed Rice (Muri)', 0.80),
('Chickpeas', 2.00),
('Peanuts', 1.50),
('Tofu', 2.50),
('Carrot', 0.60);

INSERT INTO recipe (name, description, calories, prep_time, cook_time, instructions, image_url) VALUES
('Chicken Bhuna', 'Spicy dry chicken curry', 520, 15, 35, 'Wash and clean chicken thoroughly. Heat oil in a pan and add sliced onions. Fry until golden brown. Add ginger-garlic paste and sauté until fragrant. Add turmeric, chili powder and salt. Mix well and add chicken pieces. Cook on medium heat until chicken releases water. Continue cooking on low heat, stirring frequently, until oil separates and chicken becomes dry and tender.', 'https://images.unsplash.com/photo-1764304733301-3a9f335f0c67'),
('Beef Bhuna', 'Slow cooked beef curry', 650, 20, 90, 'Cut beef into medium pieces and wash well. Heat oil and fry onions until dark brown. Add ginger-garlic paste and spices, cook until oil separates. Add beef and mix thoroughly. Cover and cook on very low heat, stirring occasionally. Add small amounts of water if needed. Cook until beef is soft and gravy becomes thick.', 'https://images.unsplash.com/photo-1545247181-516773cae754'),
('Mutton Rezala', 'Mughlai style mutton', 720, 25, 80, 'Marinate mutton with yogurt, ginger-garlic paste and spices for 30 minutes. Heat oil and fry whole spices lightly. Add marinated mutton and cook on low heat. Stir gently and add water as needed. Cook until mutton becomes very soft and gravy turns creamy.', 'https://images.unsplash.com/photo-1708782344137-21c48d98dfcc'),
('Hilsa Bhapa', 'Steamed hilsa with mustard', 600, 15, 25, 'Clean hilsa pieces carefully. Make mustard paste with green chili and salt. Coat fish with mustard paste and mustard oil. Place in a covered bowl and steam for 20-25 minutes until fish is fully cooked.', 'https://images.unsplash.com/photo-1654863404432-cac67587e25d'),
('Rui Machher Jhol', 'Light fish curry', 450, 15, 30, 'Marinate fish with turmeric and salt. Lightly fry fish and set aside. In the same oil fry onion and spices. Add water to make thin gravy. Gently add fish pieces and simmer for 10 minutes.', 'https://sinfullyspicy.com/wp-content/uploads/2021/07/FCA582ED-6D91-4A04-885B-7431ABBEA2AB-1024x1536.jpeg'),
('Chingri Malai Curry', 'Shrimp coconut curry', 580, 20, 30, 'Clean shrimp and marinate lightly with salt. Fry onions in oil until soft. Add ginger paste and spices. Pour coconut milk and bring to gentle boil. Add shrimp and cook briefly until tender.', 'https://media.istockphoto.com/id/1003411832/photo/creamy-shrimp-curry.jpg'),
('Dal Tadka', 'Spiced lentil curry', 320, 10, 25, 'Wash lentils and boil until soft. Heat oil in another pan and fry garlic, cumin and chili. Pour this tempering over the lentils. Mix well and simmer for a few minutes.', 'https://media.istockphoto.com/id/1413306580/photo/yellow-shahi-dal-tarka-with-rice-and-roti-nan-served-in-a-dish-isolated-on-dark-background.jpg'),
('Khichuri', 'Rice and lentils', 500, 15, 40, 'Wash rice and lentils. Heat oil and fry spices lightly. Add rice, lentils and water. Cook covered on medium heat until soft and mushy.', 'https://rumkisgoldenspoon.com/wp-content/uploads/2021/05/Bhuna-khichuri-recipe.jpg'),
('Egg Curry', 'Spicy egg curry', 420, 10, 25, 'Boil eggs, peel and lightly fry them. Prepare onion-tomato gravy with spices. Add eggs and simmer until gravy thickens.', 'https://images.unsplash.com/photo-1764315197254-94385571df22'),
('Chicken Biryani', 'Traditional biryani', 700, 30, 60, 'Marinate chicken with yogurt and spices. Parboil rice with whole spices. Layer rice and chicken in a pot. Seal tightly and cook on low heat (dum) until aroma develops.', 'https://images.unsplash.com/photo-1719239885399-f87d992e0f18'),
('Tehari', 'Beef rice dish', 680, 25, 70, 'Cook beef with spices until partially tender. Add washed rice and water. Cook together until rice is fully cooked and beef is soft.', 'https://as1.ftcdn.net/v2/jpg/05/36/14/84/1000_F_536148409_1rZN008upPGyxRkeWCh1dtAgPNdFHjKZ.jpg'),
('Vegetable Khichuri', 'Veg rice and dal', 450, 15, 35, 'Cook rice and lentils with mixed vegetables, spices and water until soft.', 'https://images.unsplash.com/photo-1630409349416-24884761a307'),
('Begun Bhorta', 'Mashed eggplant', 280, 10, 20, 'Roast eggplant over flame or oven. Remove skin and mash flesh. Mix with onion, green chili, salt and mustard oil.', 'https://media.istockphoto.com/id/1607315227/photo/begun-bhorta-or-mashed-eggplant-served-in-dish-isolated-on-background-top-view-of-bangladesh.jpg'),
('Alu Bhorta', 'Mashed potato', 260, 10, 15, 'Boil potatoes, peel and mash. Mix with onion, chili, salt and oil.', 'https://as2.ftcdn.net/v2/jpg/07/68/06/39/1000_F_768063902_QhGvB39IoRbZcoZThszsKoYXYlvToSAC.jpg'),
('Shak Bhaji', 'Spinach fry', 200, 5, 15, 'Wash spinach and chop. Fry garlic in oil, add spinach and cook until soft.', 'https://images.unsplash.com/photo-1766323106504-6b44debfa313'),
('Mixed Vegetable Curry', 'Vegetable curry', 300, 15, 30, 'Cook mixed vegetables with spices and water until tender.', 'https://plus.unsplash.com/premium_photo-1726783359110-de1b5d04179c'),
('Chickpea Curry', 'Chola dal', 350, 20, 40, 'Soak chickpeas overnight. Boil until soft. Cook with onion, tomato and spices until thick.', 'https://plus.unsplash.com/premium_photo-1695456064603-aa7568121827'),
('Chicken Korma', 'Mild chicken curry', 540, 20, 45, 'Cook chicken with yogurt, onion paste and mild spices on low heat until creamy.', 'https://images.unsplash.com/photo-1728542575492-47e02eb3305c'),
('Beef Curry', 'Traditional beef curry', 620, 20, 80, 'Cook beef slowly with spices and water until meat is tender and gravy thickens.', 'https://images.unsplash.com/photo-1534939561126-855b8675edd7'),
('Fish Fry', 'Pan fried fish', 400, 10, 15, 'Marinate fish with spices and shallow fry until golden.', 'https://images.unsplash.com/photo-1656389863341-1dfd38ee6edc'),
('Chicken Jhal Fry', 'Spicy chicken fry', 550, 15, 35, 'Fry chicken with onions, chilies and spices until dry and spicy.', 'https://images.unsplash.com/photo-1577194509876-4bb24787a641'),
('Egg Bhurji', 'Spicy scrambled eggs', 380, 5, 15, 'Fry onion and chili, add beaten eggs and scramble until cooked.', 'https://plus.unsplash.com/premium_photo-1700004501749-85a6db76a1de'),
('Vegetable Pulao', 'Rice with vegetables', 430, 15, 30, 'Cook rice with vegetables and aromatic spices.', 'https://images.unsplash.com/photo-1645177628172-a94c1f96e6db'),
('Plain Rice and Dal', 'Daily staple meal', 360, 10, 25, 'Serve steamed rice with simply cooked lentils.', 'https://plus.unsplash.com/premium_photo-1694506375078-792776cef19d'),
('Muri Mix', 'Puffed rice snack', 250, 5, 10, 'Mix puffed rice with onion, chili, oil and spices.', 'https://www.istockphoto.com/photo/jhal-muri-gm1466425998-498431072'),
('Chicken Soup', 'Light chicken soup', 300, 15, 30, 'Boil chicken with vegetables and seasoning. Strain if needed.', 'https://images.unsplash.com/photo-1604908812231'),
('Vegetable Soup', 'Healthy soup', 220, 15, 25, 'Boil vegetables and blend lightly. Season and simmer.', 'https://images.unsplash.com/photo-1665594051407-7385d281ad76'),
('Chicken Cutlet', 'Fried chicken patty', 480, 20, 20, 'Mix minced chicken with spices. Shape patties and shallow fry.', 'https://plus.unsplash.com/premium_photo-1764240756021-edc73e293689'),
('Vegetable Cutlet', 'Veg patty', 350, 20, 20, 'Mix mashed vegetables with spices, shape and fry.', 'https://images.unsplash.com/photo-1589302168002'),
('Shrimp Bhuna', 'Spicy shrimp curry', 560, 15, 30, 'Cook shrimp with spices until thick and oil separates.', 'https://images.unsplash.com/photo-1761545832792-535fafbad368'),
('Fish Curry with Potato', 'Fish potato curry', 470, 15, 35, 'Cook fish and potatoes in light spiced gravy.', 'https://www.shutterstock.com/shutterstock/photos/2370555929/display_1500/stock-photo-machher-jhol-or-machha-jhola-is-a-traditional-spicy-fish-curry-in-bengali-and-odia-cuisines-2370555929.jpg'),
('Spinach Dal', 'Dal with spinach', 330, 10, 25, 'Cook lentils and spinach together with spices.', 'https://media.istockphoto.com/id/1088329282/photo/dal-palak-or-lentil-spinach-curry-popular-indian-main-course-healthy-recipe-served-in-a.jpg'),
('Eggplant Curry', 'Begun jhol', 310, 15, 30, 'Cook eggplant pieces with spices and light gravy.', 'https://plus.unsplash.com/premium_photo-1723708915584-1d3d88e0d451'),
('Cabbage Fry', 'Stir fried cabbage', 240, 10, 20, 'Stir fry cabbage with garlic and spices.', 'https://images.unsplash.com/photo-1695712373714-304af07e2c67'),
('Cauliflower Curry', 'Phulkopi jhol', 290, 15, 30, 'Cook cauliflower with spices and water until soft.', 'https://plus.unsplash.com/premium_photo-1707227861789-475326479c2b'),
('Chicken Fried Rice', 'Rice with chicken', 620, 20, 25, 'Stir fry rice with chicken, egg and vegetables.', 'https://images.unsplash.com/photo-1603133872878-684f208fb84b'),
('Vegetable Fried Rice', 'Rice with veggies', 520, 15, 25, 'Stir fry rice with vegetables and seasoning.', 'https://images.unsplash.com/photo-1723691802798-fa6efc67b2c9'),
('Beef Fried Rice', 'Rice with beef', 670, 20, 30, 'Stir fry rice with beef slices and vegetables.', 'https://media.istockphoto.com/id/960867816/photo/pilaf-or-pilau-style-rice-and-lamb-with-carrots.jpg'),
('Egg Fried Rice', 'Rice with egg', 590, 10, 20, 'Stir fry rice with scrambled eggs.', 'https://images.unsplash.com/photo-1687020836451-41977907509e'),
('Tofu Vegetable Curry', 'Plant based curry', 420, 15, 30, 'Cook tofu and vegetables with spices.', 'https://plus.unsplash.com/premium_photo-1713089366140-814130d69933'),
('Vegan Dal Khichuri', 'Plant protein meal', 480, 15, 40, 'Cook rice and lentils using oil only, no animal products.', 'https://media.istockphoto.com/id/1204839738/photo/famous-indian-food-khichdi-is-ready-to-serve.jpg'),
('Low Carb Chicken Bowl', 'Chicken and veggies', 400, 15, 25, 'Grill chicken and sauté vegetables lightly.', 'https://images.unsplash.com/photo-1761315600943-d8a5bb0c499f'),
('High Protein Egg Bowl', 'Egg focused meal', 430, 10, 20, 'Boil eggs and serve with vegetables.', 'https://images.unsplash.com/photo-1694111133960-73fde2d294e4'),
('Diabetic Fish Curry', 'Low oil fish curry', 390, 15, 30, 'Cook fish with very little oil and mild spices.', 'https://images.unsplash.com/photo-1574484284002-952d92456975'),
('Mustard Fish Curry', 'Fish in mustard', 460, 15, 30, 'Cook fish in mustard seed paste gravy.', 'https://images.unsplash.com/photo-1736680056361-6a2f6e35fa50'),
('Chicken Vegetable Stir Fry', 'Healthy stir fry', 410, 10, 20, 'Stir fry chicken and vegetables on high heat.', 'https://images.unsplash.com/photo-1662611284583-f34180194370'),
('Beef Vegetable Stir Fry', 'Protein veg dish', 520, 15, 25, 'Stir fry beef with vegetables and spices.', 'https://images.unsplash.com/photo-1760504526069-ff0f8bf6e4ca'),
('Simple Omelette', 'Egg breakfast', 300, 5, 10, 'Beat eggs with salt and cook omelette in a pan.', 'https://images.unsplash.com/photo-1646579933415-92109f9805df');

INSERT INTO recipe_ingredients (recipe_id, ing_id, quantity, unit)
SELECT r.recipe_id, i.ing_id, 500, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Bhuna' AND i.name='Chicken'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Bhuna' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 30, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Bhuna' AND i.name='Garlic'
UNION ALL SELECT r.recipe_id, i.ing_id, 20, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Bhuna' AND i.name='Ginger'
UNION ALL SELECT r.recipe_id, i.ing_id, 5, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Bhuna' AND i.name='Turmeric'
UNION ALL SELECT r.recipe_id, i.ing_id, 30, 'ml' FROM recipe r, ingredients i WHERE r.name='Chicken Bhuna' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 600, 'g' FROM recipe r, ingredients i WHERE r.name='Beef Bhuna' AND i.name='Beef'
UNION ALL SELECT r.recipe_id, i.ing_id, 250, 'g' FROM recipe r, ingredients i WHERE r.name='Beef Bhuna' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 30, 'g' FROM recipe r, ingredients i WHERE r.name='Beef Bhuna' AND i.name='Garlic'
UNION ALL SELECT r.recipe_id, i.ing_id, 40, 'ml' FROM recipe r, ingredients i WHERE r.name='Beef Bhuna' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 600, 'g' FROM recipe r, ingredients i WHERE r.name='Mutton Rezala' AND i.name='Mutton'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Mutton Rezala' AND i.name='Yogurt'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Mutton Rezala' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 25, 'g' FROM recipe r, ingredients i WHERE r.name='Mutton Rezala' AND i.name='Garlic'
UNION ALL SELECT r.recipe_id, i.ing_id, 500, 'g' FROM recipe r, ingredients i WHERE r.name='Hilsa Bhapa' AND i.name='Hilsa Fish'
UNION ALL SELECT r.recipe_id, i.ing_id, 20, 'g' FROM recipe r, ingredients i WHERE r.name='Hilsa Bhapa' AND i.name='Green Chili'
UNION ALL SELECT r.recipe_id, i.ing_id, 30, 'ml' FROM recipe r, ingredients i WHERE r.name='Hilsa Bhapa' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 500, 'g' FROM recipe r, ingredients i WHERE r.name='Rui Machher Jhol' AND i.name='Rui Fish'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Rui Machher Jhol' AND i.name='Potato'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Rui Machher Jhol' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 30, 'ml' FROM recipe r, ingredients i WHERE r.name='Rui Machher Jhol' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Chingri Malai Curry' AND i.name='Shrimp'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Chingri Malai Curry' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'ml' FROM recipe r, ingredients i WHERE r.name='Chingri Malai Curry' AND i.name='Milk'
UNION ALL SELECT r.recipe_id, i.ing_id, 250, 'g' FROM recipe r, ingredients i WHERE r.name='Dal Tadka' AND i.name='Lentils (Dal)'
UNION ALL SELECT r.recipe_id, i.ing_id, 20, 'g' FROM recipe r, ingredients i WHERE r.name='Dal Tadka' AND i.name='Garlic'
UNION ALL SELECT r.recipe_id, i.ing_id, 5, 'g' FROM recipe r, ingredients i WHERE r.name='Dal Tadka' AND i.name='Cumin'
UNION ALL SELECT r.recipe_id, i.ing_id, 20, 'ml' FROM recipe r, ingredients i WHERE r.name='Dal Tadka' AND i.name='Soybean Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Khichuri' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Khichuri' AND i.name='Lentils (Dal)'
UNION ALL SELECT r.recipe_id, i.ing_id, 30, 'ml' FROM recipe r, ingredients i WHERE r.name='Khichuri' AND i.name='Soybean Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 6, 'pcs' FROM recipe r, ingredients i WHERE r.name='Egg Curry' AND i.name='Eggs'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Egg Curry' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Egg Curry' AND i.name='Tomato'
UNION ALL SELECT r.recipe_id, i.ing_id, 600, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Biryani' AND i.name='Chicken'
UNION ALL SELECT r.recipe_id, i.ing_id, 500, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Biryani' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Biryani' AND i.name='Yogurt'
UNION ALL SELECT r.recipe_id, i.ing_id, 500, 'g' FROM recipe r, ingredients i WHERE r.name='Tehari' AND i.name='Beef'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Tehari' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 250, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Khichuri' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Khichuri' AND i.name='Lentils (Dal)'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Khichuri' AND i.name='Potato'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Khichuri' AND i.name='Cauliflower'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Begun Bhorta' AND i.name='Eggplant'
UNION ALL SELECT r.recipe_id, i.ing_id, 50, 'g' FROM recipe r, ingredients i WHERE r.name='Begun Bhorta' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 15, 'ml' FROM recipe r, ingredients i WHERE r.name='Begun Bhorta' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Alu Bhorta' AND i.name='Potato'
UNION ALL SELECT r.recipe_id, i.ing_id, 50, 'g' FROM recipe r, ingredients i WHERE r.name='Alu Bhorta' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 15, 'ml' FROM recipe r, ingredients i WHERE r.name='Alu Bhorta' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Shak Bhaji' AND i.name='Spinach'
UNION ALL SELECT r.recipe_id, i.ing_id, 15, 'g' FROM recipe r, ingredients i WHERE r.name='Shak Bhaji' AND i.name='Garlic'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Mixed Vegetable Curry' AND i.name='Potato'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Mixed Vegetable Curry' AND i.name='Cauliflower'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Mixed Vegetable Curry' AND i.name='Cabbage'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Chickpea Curry' AND i.name='Chickpeas'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Chickpea Curry' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Chickpea Curry' AND i.name='Tomato'
UNION ALL SELECT r.recipe_id, i.ing_id, 500, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Korma' AND i.name='Chicken'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Korma' AND i.name='Yogurt'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Korma' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 600, 'g' FROM recipe r, ingredients i WHERE r.name='Beef Curry' AND i.name='Beef'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Beef Curry' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Fish Fry' AND i.name='Rui Fish'
UNION ALL SELECT r.recipe_id, i.ing_id, 50, 'ml' FROM recipe r, ingredients i WHERE r.name='Fish Fry' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 500, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Jhal Fry' AND i.name='Chicken'
UNION ALL SELECT r.recipe_id, i.ing_id, 30, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Jhal Fry' AND i.name='Green Chili'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Jhal Fry' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 4, 'pcs' FROM recipe r, ingredients i WHERE r.name='Egg Bhurji' AND i.name='Eggs'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Egg Bhurji' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 15, 'g' FROM recipe r, ingredients i WHERE r.name='Egg Bhurji' AND i.name='Green Chili'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Pulao' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Pulao' AND i.name='Cauliflower'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Pulao' AND i.name='Carrot'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Plain Rice and Dal' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Plain Rice and Dal' AND i.name='Lentils (Dal)'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Muri Mix' AND i.name='Puffed Rice (Muri)'
UNION ALL SELECT r.recipe_id, i.ing_id, 50, 'g' FROM recipe r, ingredients i WHERE r.name='Muri Mix' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 15, 'ml' FROM recipe r, ingredients i WHERE r.name='Muri Mix' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Soup' AND i.name='Chicken'
UNION ALL SELECT r.recipe_id, i.ing_id, 15, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Soup' AND i.name='Garlic'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Soup' AND i.name='Carrot'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Soup' AND i.name='Potato'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Cutlet' AND i.name='Chicken'
UNION ALL SELECT r.recipe_id, i.ing_id, 2, 'pcs' FROM recipe r, ingredients i WHERE r.name='Chicken Cutlet' AND i.name='Eggs'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Cutlet' AND i.name='Potato'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Cutlet' AND i.name='Cauliflower'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Shrimp Bhuna' AND i.name='Shrimp'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Shrimp Bhuna' AND i.name='Onion'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Fish Curry with Potato' AND i.name='Rui Fish'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Fish Curry with Potato' AND i.name='Potato'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Spinach Dal' AND i.name='Spinach'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Spinach Dal' AND i.name='Lentils (Dal)'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Eggplant Curry' AND i.name='Eggplant'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Eggplant Curry' AND i.name='Potato'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Cabbage Fry' AND i.name='Cabbage'
UNION ALL SELECT r.recipe_id, i.ing_id, 15, 'g' FROM recipe r, ingredients i WHERE r.name='Cabbage Fry' AND i.name='Garlic'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Cauliflower Curry' AND i.name='Cauliflower'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Cauliflower Curry' AND i.name='Potato'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Fried Rice' AND i.name='Chicken'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Fried Rice' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 2, 'pcs' FROM recipe r, ingredients i WHERE r.name='Chicken Fried Rice' AND i.name='Eggs'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Fried Rice' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 100, 'g' FROM recipe r, ingredients i WHERE r.name='Vegetable Fried Rice' AND i.name='Cauliflower'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Beef Fried Rice' AND i.name='Beef'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Beef Fried Rice' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 4, 'pcs' FROM recipe r, ingredients i WHERE r.name='Egg Fried Rice' AND i.name='Eggs'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Egg Fried Rice' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Tofu Vegetable Curry' AND i.name='Tofu'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Tofu Vegetable Curry' AND i.name='Cauliflower'
UNION ALL SELECT r.recipe_id, i.ing_id, 300, 'g' FROM recipe r, ingredients i WHERE r.name='Vegan Dal Khichuri' AND i.name='Rice'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Vegan Dal Khichuri' AND i.name='Lentils (Dal)'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Low Carb Chicken Bowl' AND i.name='Chicken'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Low Carb Chicken Bowl' AND i.name='Spinach'
UNION ALL SELECT r.recipe_id, i.ing_id, 6, 'pcs' FROM recipe r, ingredients i WHERE r.name='High Protein Egg Bowl' AND i.name='Eggs'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='High Protein Egg Bowl' AND i.name='Spinach'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Diabetic Fish Curry' AND i.name='Rui Fish'
UNION ALL SELECT r.recipe_id, i.ing_id, 15, 'ml' FROM recipe r, ingredients i WHERE r.name='Diabetic Fish Curry' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Mustard Fish Curry' AND i.name='Rui Fish'
UNION ALL SELECT r.recipe_id, i.ing_id, 30, 'ml' FROM recipe r, ingredients i WHERE r.name='Mustard Fish Curry' AND i.name='Mustard Oil'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Vegetable Stir Fry' AND i.name='Chicken'
UNION ALL SELECT r.recipe_id, i.ing_id, 150, 'g' FROM recipe r, ingredients i WHERE r.name='Chicken Vegetable Stir Fry' AND i.name='Cauliflower'
UNION ALL SELECT r.recipe_id, i.ing_id, 400, 'g' FROM recipe r, ingredients i WHERE r.name='Beef Vegetable Stir Fry' AND i.name='Beef'
UNION ALL SELECT r.recipe_id, i.ing_id, 200, 'g' FROM recipe r, ingredients i WHERE r.name='Beef Vegetable Stir Fry' AND i.name='Cabbage'
UNION ALL SELECT r.recipe_id, i.ing_id, 3, 'pcs' FROM recipe r, ingredients i WHERE r.name='Simple Omelette' AND i.name='Eggs'
UNION ALL SELECT r.recipe_id, i.ing_id, 30, 'ml' FROM recipe r, ingredients i WHERE r.name='Simple Omelette' AND i.name='Milk';
