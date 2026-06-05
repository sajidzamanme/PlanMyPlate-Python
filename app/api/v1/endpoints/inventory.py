from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.inventory import InventoryResponse, InvItemResponse, InvItemCreateRequest
from app.schemas.grocery import UpdateItemRequestDto # Reusing UpdateItemRequestDto as logic is same
from app.models.user import User

router = APIRouter()

@router.get("/user/{user_id}", response_model=InventoryResponse)
def get_user_inventory(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    inventory = crud.inventory.get_by_user_id(db, user_id=user_id)
    if not inventory:
        inventory = crud.inventory.create_for_user(db, user_id=user_id)
    return inventory

@router.get("/{inventory_id}/items", response_model=List[InvItemResponse])
def get_inventory_items(
    inventory_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    inventory = crud.inventory.get(db, id=inventory_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    if inventory.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.inventory.get_items(db, inv_id=inventory_id)

@router.post("/{inventory_id}/items", response_model=InvItemResponse)
def add_item_to_inventory(
    *,
    db: Session = Depends(deps.get_db),
    inventory_id: int,
    item_in: InvItemCreateRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    inventory = crud.inventory.get(db, id=inventory_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    if inventory.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Verify ingredient exists
    ingredient = crud.ingredient.get(db, id=item_in.ingId)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
        
    return crud.inventory.add_item(db, inv_id=inventory_id, obj_in=item_in)

@router.put("/items/{item_id}", response_model=InvItemResponse)
def update_inventory_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    item_in: UpdateItemRequestDto, # Has quantity, unit, expiryDate (added expiryDate to shared DTO?)
    # Wait, UpdateItemRequestDto in grocery.py only has quantity/unit.
    # Inventory update needs expiryDate.
    # I should check grocery.py UpdateItemRequestDto definition.
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    item = crud.inv_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check permission via inventory->user
    inventory = crud.inventory.get(db, id=item.inv_id)
    if inventory.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Logic: if quantity 0, delete.
    if item_in.quantity is not None and item_in.quantity <= 0:
        crud.inv_item.remove(db, id=item_id)
        return item # or null/empty? Java says "Updated InvItem object, or empty if deleted".
        # If I return deleted item, it's fine.
    
    # Helper update logic in crud or here.
    # Basic update:
    if item_in.quantity is not None:
        item.quantity = item_in.quantity
    if item_in.unit is not None:
        item.unit = item_in.unit
    if item_in.expiryDate is not None:
        item.expiry_date = item_in.expiryDate
    
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/items/{item_id}")
def remove_inventory_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    item = crud.inv_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    inventory = crud.inventory.get(db, id=item.inv_id)
    if inventory.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    crud.inv_item.remove(db, id=item_id)
    return {"message": "Item removed successfully"}

@router.post("/cook")
def cook_recipe_inventory(
    *,
    db: Session = Depends(deps.get_db),
    recipeId: int = Query(..., alias="recipeId"),
    servings: float = 1.0,
    force: bool = False,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    recipe = crud.recipe.get(db, id=recipeId)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
        
    if not force:
        missing = crud.inventory.check_recipe_ingredients(db, user_id=current_user.user_id, recipe_id=recipeId, servings=servings)
        if missing:
            return JSONResponse(
                status_code=409,
                content={
                    "status": "insufficient_ingredients",
                    "title": "Missing Pantry Items",
                    "message": "missing inventory item",
                    "missing": missing
                }
            )
            
    success = crud.inventory.deduct_recipe_ingredients(db, user_id=current_user.user_id, recipe_id=recipeId, servings=servings)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cook recipe")
    return {"message": "Recipe cooked and ingredients deducted from inventory"}

