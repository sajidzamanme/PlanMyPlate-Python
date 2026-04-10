# PlanMyPlate API Documentation

This document provides a detailed reference for the PlanMyPlate Python (FastAPI) API. It is designed to help developers, including Android developers, understand and integrate with the backend services.

**Base URL:** `/api`

**Interactive Docs (Swagger UI):** Available at `http://localhost:8000/docs` when the server is running.

---

## 1. Authentication

### Sign Up
Register a new user account.

- **URL:** `/api/auth/signup`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": "securePassword123"
  }
  ```
- **Response Body:**
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "access_token": "eyJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "email": "john.doe@example.com",
    "name": "John Doe",
    "userId": 1
  }
  ```

### Sign In
Authenticate an existing user.

- **URL:** `/api/auth/signin`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "email": "john.doe@example.com",
    "password": "securePassword123"
  }
  ```
- **Response Body:**
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "access_token": "eyJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "email": "john.doe@example.com",
    "name": "John Doe",
    "userId": 1
  }
  ```

### OAuth2 Token (Swagger UI)
Dedicated endpoint for Swagger UI's "Authorize" button.

- **URL:** `/api/auth/token`
- **Method:** `POST`
- **Content-Type:** `application/x-www-form-urlencoded`
- **Form Fields:**
  - `username`: User's email
  - `password`: User's password
- **Response Body:** Same as Sign In.

### Forgot Password
Initiate password reset process.

- **URL:** `/api/auth/forgot-password`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "email": "john.doe@example.com"
  }
  ```
- **Response Body:**
  ```json
  {
    "message": "Password reset token sent to email. Token: 1234"
  }
  ```

### Reset Password
Complete password reset.

- **URL:** `/api/auth/reset-password`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "resetToken": "1234",
    "newPassword": "newSecurePassword456"
  }
  ```
- **Response Body:**
  ```json
  {
    "message": "Password reset successfully"
  }
  ```

---

## 2. Users

All user endpoints require authentication (`Authorization: Bearer <token>`).

### Get Current User
Retrieve profile of the currently authenticated user.

- **URL:** `/api/users/me`
- **Method:** `GET`
- **Headers:** `Authorization: Bearer <token>`
- **Response Body:**
  ```json
  {
    "userId": 1,
    "name": "John Doe",
    "userName": "john_doe",
    "email": "john.doe@example.com"
  }
  ```

### Get User by ID
- **URL:** `/api/users/{user_id}`
- **Method:** `GET`
- **Headers:** `Authorization: Bearer <token>`
- **Response Body:** Same structure as Get Current User.

### Update User
- **URL:** `/api/users/{user_id}`
- **Method:** `PUT`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "name": "John Updated",
    "userName": "john_updated",
    "age": 25,
    "weight": 70.5,
    "budget": 500.00
  }
  ```
  > All fields are optional. Only provided fields are updated.
- **Response Body:** Updated User object.

### Delete User
- **URL:** `/api/users/{user_id}`
- **Method:** `DELETE`
- **Headers:** `Authorization: Bearer <token>`
- **Response Body:**
  ```json
  {
    "message": "User deleted successfully"
  }
  ```

---

## 3. User Preferences
Manage dietary preferences, allergies, and dislikes. Requires authentication.

### Get Preferences
- **URL:** `/api/user-preferences/{user_id}`
- **Method:** `GET`
- **Headers:** `Authorization: Bearer <token>`
- **Response Body:**
  ```json
  {
    "prefId": 10,
    "userId": 1,
    "diet": "Vegan",
    "allergies": ["Peanuts", "Shellfish"],
    "dislikes": ["Mushrooms"],
    "servings": 2,
    "budget": 150.00
  }
  ```

### Set/Update Preferences
- **URL:** `/api/user-preferences/{user_id}`
- **Method:** `POST`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "userId": 1,
    "diet": "Vegan",
    "allergies": ["Peanuts"],
    "dislikes": [],
    "servings": 4,
    "budget": 200.00
  }
  ```
- **Response Body:** Updated preferences object (same structure as GET).

---

## 4. Recipes

### Get All Recipes
- **URL:** `/api/recipes`
- **Method:** `GET`
- **Query Parameters:** `skip` (default: 0), `limit` (default: 100)
- **Response Body:** List of Recipe objects.
  ```json
  [
    {
      "recipeId": 1,
      "name": "Chicken Bhuna",
      "description": "Spicy dry chicken curry",
      "calories": 520,
      "prepTime": 15,
      "cookTime": 35,
      "servings": 3,
      "instructions": "...",
      "imageUrl": "https://...",
      "recipeIngredients": [
        {
          "id": 1,
          "ingredient": { "ingId": 2, "name": "Chicken", "price": 4.50, "tags": [] },
          "quantity": 500,
          "unit": "g"
        }
      ]
    }
  ]
  ```

### Search Recipes
- **URL:** `/api/recipes/search?name=chicken`
- **Method:** `GET`
- **Response Body:** List of matching Recipe objects.

### Filter by Calories
- **URL:** `/api/recipes/filter/calories?minCalories=200&maxCalories=500`
- **Method:** `GET`
- **Response Body:** List of Recipe objects within calorie range.

### Create Recipe
- **URL:** `/api/recipes`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "name": "Custom Pasta",
    "description": "My special pasta recipe",
    "calories": 450,
    "prepTime": 30,
    "cookTime": 20,
    "servings": 4,
    "instructions": "1. Boil water\n2. Cook pasta\n3. Add sauce",
    "imageUrl": "https://example.com/custom_pasta.jpg",
    "ingredients": [
      {
        "ingId": 1,
        "quantity": 200,
        "unit": "g"
      }
    ]
  }
  ```
- **Response Body (201 Created):** Created Recipe object with assigned `recipeId`.

### Get Recipe by ID
- **URL:** `/api/recipes/{id}`
- **Method:** `GET`
- **Response Body:** Single Recipe object.

### Update Recipe
- **URL:** `/api/recipes/{id}`
- **Method:** `PUT`
- **Request Body:** Same format as Create Recipe.
- **Response Body:** Updated Recipe object.

### Delete Recipe
- **URL:** `/api/recipes/{id}`
- **Method:** `DELETE`
- **Response Body:**
  ```json
  {
    "message": "Recipe deleted successfully"
  }
  ```

---

## 5. Ingredients

### Get All Ingredients
- **URL:** `/api/ingredients`
- **Method:** `GET`
- **Response Body:** List of Ingredient objects.
  ```json
  [
    {
      "ingId": 1,
      "name": "Rice",
      "price": 1.50,
      "tags": []
    }
  ]
  ```

### Search Ingredients
- **URL:** `/api/ingredients/search?name=chicken`
- **Method:** `GET`
- **Response Body:** List of matching Ingredient objects.

### Filter by Price
- **URL:** `/api/ingredients/filter/price?minPrice=1.00&maxPrice=5.00`
- **Method:** `GET`
- **Response Body:** List of Ingredient objects within price range.

### Create Ingredient
- **URL:** `/api/ingredients`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "name": "Coconut",
    "price": 3.50
  }
  ```
- **Response Body (201 Created):** Created Ingredient object.

### Get Ingredient by ID
- **URL:** `/api/ingredients/{id}`
- **Method:** `GET`

### Update Ingredient
- **URL:** `/api/ingredients/{id}`
- **Method:** `PUT`
- **Request Body:**
  ```json
  {
    "name": "Updated Name",
    "price": 4.00
  }
  ```

### Delete Ingredient
- **URL:** `/api/ingredients/{id}`
- **Method:** `DELETE`

---

## 6. Meal Plans
All meal plan endpoints require authentication.

### Get User Meal Plans
- **URL:** `/api/meal-plans/user/{user_id}`
- **Method:** `GET`
- **Response Body:** List of MealPlan objects.

### Get Weekly Meal Plans
Retrieve active 7-day meal plans for a user.

- **URL:** `/api/meal-plans/user/{user_id}/weekly`
- **Method:** `GET`
- **Response Body:** List of MealPlan objects.
  ```json
  [
    {
      "mpId": 5,
      "userId": 1,
      "startDate": "2026-03-27",
      "duration": 7,
      "status": "active",
      "slots": [
        {
          "id": 101,
          "slotIndex": 0,
          "mealType": "Breakfast",
          "dayNumber": 1,
          "recipe": { "recipeId": 1, "name": "..." }
        }
      ]
    }
  ]
  ```

### Get Meal Plans by Status
- **URL:** `/api/meal-plans/user/{user_id}/status/{status}`
- **Method:** `GET`
- **Response Body:** List of MealPlan objects matching the status.

### Get Meal Plan by ID
- **URL:** `/api/meal-plans/{id}`
- **Method:** `GET`
- **Response Body:** Single MealPlan object.

### Create Meal Plan (Simple)
Create a new empty meal plan. Deactivates existing active plans.

- **URL:** `/api/meal-plans/user/{user_id}`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "startDate": "2026-04-01",
    "duration": 7,
    "status": "active"
  }
  ```
- **Response Body (201 Created):** Created MealPlan object.

### Create Meal Plan with Recipes
Generate a meal plan with selected recipes. Also creates a grocery list with aggregated ingredients.

- **URL:** `/api/meal-plans/user/{user_id}/create`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "recipeIds": [1, 5, 12, 3, 8, 15, 2, 6, 10, 4, 7, 13, 1, 5, 12, 3, 8, 15, 2, 6, 10],
    "duration": 7,
    "startDate": "2026-04-01"
  }
  ```
  > Provide up to 21 recipe IDs (3 meals × 7 days). Recipes are auto-assigned: indices 0,1,2 → Day 1 (Breakfast, Lunch, Dinner), etc.

- **Response Body (201 Created):** Created MealPlan object with populated slots.

### Update Meal Plan
- **URL:** `/api/meal-plans/{id}`
- **Method:** `PUT`
- **Request Body:**
  ```json
  {
    "status": "inactive",
    "duration": 5
  }
  ```

### Delete Meal Plan
- **URL:** `/api/meal-plans/{id}`
- **Method:** `DELETE`

---

## 7. Grocery Lists
All grocery list endpoints require authentication.

### Get Grocery Lists by User
- **URL:** `/api/grocery-lists/user/{user_id}`
- **Method:** `GET`
- **Response Body:** List of GroceryList objects.
  ```json
  [
    {
      "listId": 1,
      "userId": 1,
      "dateCreated": "2026-03-27",
      "status": "active",
      "items": [
        {
          "id": 501,
          "ingredient": {
            "ingId": 2,
            "name": "Chicken",
            "price": 4.50,
            "tags": []
          },
          "quantity": 500,
          "unit": "g"
        }
      ]
    }
  ]
  ```

### Get Grocery Lists by Status
- **URL:** `/api/grocery-lists/user/{user_id}/status/{status}`
- **Method:** `GET`
- **Response Body:** List of GroceryList objects matching the status.

### Get Grocery List by ID
- **URL:** `/api/grocery-lists/{id}`
- **Method:** `GET`

### Create Grocery List
- **URL:** `/api/grocery-lists/user/{user_id}`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "status": "active"
  }
  ```
- **Response Body (201 Created):** Created GroceryList object.

### Update Grocery List
- **URL:** `/api/grocery-lists/{id}`
- **Method:** `PUT`
- **Request Body:**
  ```json
  {
    "status": "completed"
  }
  ```

### Delete Grocery List
- **URL:** `/api/grocery-lists/{id}`
- **Method:** `DELETE`

### Purchase Items
Mark specific grocery list items as purchased. Purchased items are moved to the user's inventory.

- **URL:** `/api/grocery-lists/{id}/purchase`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "items": [
      { "itemId": 501, "quantity": 500 },
      { "itemId": 502, "quantity": 200 }
    ]
  }
  ```
  > Use grocery list **item IDs** (from the `id` field in grocery list items) and the **quantity** purchased.
  >
  > If the purchased quantity is less than the amount in the grocery list, the remaining quantity stays. If equal or greater, the item is removed.
  >
  > If the user doesn't have an inventory yet, one is automatically created.

- **Response Body:** `{"message": "Items purchased successfully"}`

### Update Grocery List Item
Update quantity or unit of a specific item.

- **URL:** `/api/grocery-lists/{listId}/items/{itemId}`
- **Method:** `PUT`
- **Request Body:**
  ```json
  {
    "quantity": 3,
    "unit": "Pack"
  }
  ```
- **Response Body:** Updated `GroceryListItem` object.

---

## 8. Inventory (Pantry)
All inventory endpoints require authentication.

### Get User Inventory
- **URL:** `/api/inventory/user/{user_id}`
- **Method:** `GET`
- **Response Body:**
  ```json
  {
    "invId": 1,
    "userId": 1,
    "lastUpdate": "2026-03-27",
    "items": [
      {
        "itemId": 50,
        "ingredient": { "ingId": 2, "name": "Chicken", "price": 4.50, "tags": [] },
        "quantity": 500,
        "unit": "g",
        "dateAdded": "2026-03-27",
        "expiryDate": "2026-04-03"
      }
    ]
  }
  ```
  > Returns 404 if the user doesn't have an inventory yet. An inventory is auto-created when items are purchased from a grocery list.

### Create Inventory
Manually create an empty inventory for a user.

- **URL:** `/api/inventory/user/{user_id}`
- **Method:** `POST`
- **Response Body:** Created Inventory object.

### Get Inventory by ID
- **URL:** `/api/inventory/{id}`
- **Method:** `GET`

### Get Inventory Items
- **URL:** `/api/inventory/{inventory_id}/items`
- **Method:** `GET`
- **Response Body:** List of InvItem objects.

### Add Item to Inventory
- **URL:** `/api/inventory/{inventory_id}/items`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "ingId": 2,
    "quantity": 500,
    "unit": "g",
    "expiryDate": "2026-04-03"
  }
  ```
- **Response Body:** Created InvItem object.

### Update Inventory Item
- **URL:** `/api/inventory/items/{item_id}`
- **Method:** `PUT`
- **Request Body:**
  ```json
  {
    "quantity": 300,
    "unit": "g",
    "expiryDate": "2026-04-05"
  }
  ```
  > If quantity is set to 0 or below, the item is automatically removed.

- **Response Body:** Updated InvItem object.

### Remove Item from Inventory
- **URL:** `/api/inventory/items/{item_id}`
- **Method:** `DELETE`
- **Response Body:** `{"message": "Item removed successfully"}`

### Delete Inventory
- **URL:** `/api/inventory/{id}`
- **Method:** `DELETE`

---

## 9. Reference Data

### Get All Diets
- **URL:** `/api/reference-data/diets`
- **Method:** `GET`
- **Response Body:**
  ```json
  [
    { "dietId": 1, "dietName": "Omnivore" },
    { "dietId": 2, "dietName": "Vegetarian" },
    { "dietId": 3, "dietName": "Vegan" }
  ]
  ```

### Get All Allergies
- **URL:** `/api/reference-data/allergies`
- **Method:** `GET`
- **Response Body:**
  ```json
  [
    { "allergyId": 1, "allergyName": "Peanuts" },
    { "allergyId": 2, "allergyName": "Milk" }
  ]
  ```

### Get All Ingredients (for Dislikes selection)
- **URL:** `/api/reference-data/dislikes`
- **Method:** `GET`
- **Response Body:**
  ```json
  [
    { "ingId": 1, "name": "Rice" },
    { "ingId": 2, "name": "Chicken" }
  ]
  ```

---

## 10. File Uploads

### Upload Image
Upload an image file to the server and get a URL to use in recipes.

> The `imageUrl` field in Recipe endpoints accepts either an external online URL (e.g., Unsplash) or the internal URL returned by this upload endpoint.

- **URL:** `/api/files/upload`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Request Parameters:**
    - `file`: The image file
- **Response Body:**
  ```json
  {
    "url": "http://localhost:8000/uploads/uuid-filename.jpg",
    "filename": "uuid-filename.jpg"
  }
  ```

---

## 11. AI Recipe Generation
Requires authentication and a configured Gemini API key.

### Generate Recipe with AI
Generate a custom recipe using Google Gemini AI based on user preferences and constraints.

- **URL:** `/api/ai/generate-recipe`
- **Method:** `POST`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "availableIngredients": ["chicken", "tomatoes", "garlic", "pasta"],
    "maxCalories": 600,
    "cuisineType": "Italian",
    "allergies": ["peanuts"],
    "dietaryPreference": "None",
    "mood": "Comfort Food",
    "servings": 4,
    "maxCookingTime": 45
  }
  ```

**Request Parameters:**
- `availableIngredients` (optional): List of ingredients you have available
- `maxCalories` (optional): Maximum calories per serving (50-5000)
- `cuisineType` (optional): Desired cuisine (e.g., Italian, Indian, Mexican)
- `allergies` (optional): List of allergens to avoid
- `dietaryPreference` (optional): Dietary restriction (e.g., Vegan, Vegetarian, Keto)
- `mood` (optional): Occasion or mood (e.g., Comfort Food, Quick & Easy)
- `servings` (required): Number of servings (1-20)
- `maxCookingTime` (optional): Maximum total cooking time in minutes (5-300)

- **Response Body (201 Created):** Created Recipe object (same structure as Recipe endpoints).

> - The AI will create new ingredients in the database if they don't already exist
> - Generated recipes are automatically saved to the database
> - Set your Gemini API key in `.env`: `GEMINI_API_KEY=YOUR_KEY`

### Generate Weekly Meal Plan with AI
Generate a complete weekly meal plan (21 meals) based on user preferences.

- **URL:** `/api/ai/generate-meal-plan`
- **Method:** `POST`
- **Headers:** `Authorization: Bearer <token>`
- **Query Parameters:**
    - `userId` (required): ID of the user
    - `startDate` (optional): Start date in YYYY-MM-DD format (defaults to today)
- **Response Body (201 Created):** Created MealPlan object with 21 slots.

---

## 12. Error Handling

The API uses standard HTTP status codes and returns structured error responses.

### Error Response Structure
```json
{
  "detail": "Recipe not found"
}
```

### Common Status Codes
| Status Code | Description | Scenario |
|-------------|-------------|----------|
| `200 OK` | Success | Request completed successfully. |
| `201 Created` | Created | Resource was successfully created. |
| `400 Bad Request` | Client Error | Missing required fields, invalid format, or not enough permissions. |
| `403 Forbidden` | Auth Error | Could not validate credentials (invalid JWT token). |
| `404 Not Found` | Not Found | Requested resource does not exist. |
| `409 Conflict` | Conflict | Resource already exists (e.g., duplicate inventory). |
| `422 Unprocessable Entity` | Validation Error | Request body fails Pydantic validation. |
| `500 Server Error` | Internal Error | Something went wrong on the server. |

### Validation Error Response
FastAPI returns detailed validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---
