from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.grocery import GroceryListResponse, GroceryListCreate, PurchaseRequestDto, UpdateItemRequestDto, GroceryListItemResponse
from app.models.user import User

router = APIRouter()

@router.get("/user/{user_id}", response_model=List[GroceryListResponse])
def get_user_grocery_lists(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.grocery_list.get_by_user_id(db, user_id=user_id)

@router.get("/{id}", response_model=GroceryListResponse)
def get_grocery_list(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    grocery_list = crud.grocery_list.get(db, id=id)
    if not grocery_list:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    if grocery_list.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return grocery_list

@router.post("/user/{user_id}", response_model=GroceryListResponse, status_code=201)
def create_grocery_list(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    grocery_list_in: GroceryListCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    # Using generic create but need to set user_id
    # Generic create uses model(**obj_in_data). GroceryListCreate has status only.
    # I should use custom create method if needed or update obj_in_data.
    # But crud base `create` takes `obj_in`.
    # I can create a new object manually or override create.
    # Let's override create logic here by manually creating model.
    from app.models.grocery import GroceryList
    from datetime import date
    
    grocery_list = GroceryList(
        user_id=user_id,
        date_created=date.today(),
        status=grocery_list_in.status
    )
    db.add(grocery_list)
    db.commit()
    db.refresh(grocery_list)
    return grocery_list

@router.put("/{id}", response_model=GroceryListResponse)
def update_grocery_list(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    grocery_list_in: GroceryListCreate, # Reusing Create schema as update has status too
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    grocery_list = crud.grocery_list.get(db, id=id)
    if not grocery_list:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    if grocery_list.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.grocery_list.update(db, db_obj=grocery_list, obj_in=grocery_list_in)

@router.delete("/{id}")
def delete_grocery_list(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    grocery_list = crud.grocery_list.get(db, id=id)
    if not grocery_list:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    if grocery_list.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    crud.grocery_list.remove(db, id=id)
    return {"message": "Grocery list deleted successfully"}

@router.post("/{id}/purchase")
def purchase_items(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    purchase_in: PurchaseRequestDto,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    grocery_list = crud.grocery_list.get(db, id=id)
    if not grocery_list:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    if grocery_list.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    crud.grocery_list.purchase_items(db, list_id=id, items=purchase_in.items)
    return {"message": "Items purchased successfully"}

@router.put("/{listId}/items/{itemId}", response_model=GroceryListItemResponse)
def update_grocery_list_item(
    *,
    db: Session = Depends(deps.get_db),
    listId: int,
    itemId: int,
    item_in: UpdateItemRequestDto,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    grocery_list = crud.grocery_list.get(db, id=listId)
    if not grocery_list:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    if grocery_list.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    item = crud.grocery_list_item.get(db, id=itemId)
    if not item or item.list_id != listId:
        raise HTTPException(status_code=404, detail="Item not found in this list")
        
    return crud.grocery_list_item.update(db, db_obj=item, obj_in=item_in)

@router.get("/user/{user_id}/status/{status}", response_model=List[GroceryListResponse])
def get_grocery_lists_by_status(
    user_id: int,
    status: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.grocery_list.get_by_user_id_and_status(db, user_id=user_id, status=status)
