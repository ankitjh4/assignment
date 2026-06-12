"""Public catalog endpoints used by the frontend."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models import Product, Promotion, SupportArticle

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


def _product_to_dict(p: Product) -> Dict[str, Any]:
    return {
        "id": p.id,
        "sku": p.sku,
        "name": p.name,
        "category": p.category,
        "flavor": p.flavor,
        "is_sparkling": bool(p.is_sparkling),
        "sugar_g_per_100ml": p.sugar_g_per_100ml,
        "calories_per_100ml": p.calories_per_100ml,
        "price_cents": p.price_cents,
        "currency": p.currency,
        "in_stock": bool(p.in_stock),
        "supports_bulk": bool(p.supports_bulk),
        "description": p.description,
    }


@router.get("/products")
def list_products(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(default=None),
    sparkling: Optional[bool] = Query(default=None),
    bulk: Optional[bool] = Query(default=None),
    max_sugar: Optional[float] = Query(default=None),
) -> Dict[str, Any]:
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if sparkling is not None:
        query = query.filter(Product.is_sparkling == (1 if sparkling else 0))
    if bulk is not None:
        query = query.filter(Product.supports_bulk == (1 if bulk else 0))
    if max_sugar is not None:
        query = query.filter(Product.sugar_g_per_100ml <= max_sugar)
    products = query.order_by(Product.name.asc()).all()
    return {"count": len(products), "products": [_product_to_dict(p) for p in products]}


@router.get("/promotions")
def list_promotions(db: Session = Depends(get_db), only_active: bool = True) -> Dict[str, Any]:
    query = db.query(Promotion)
    if only_active:
        query = query.filter(Promotion.is_active == 1)
    promos = query.order_by(Promotion.id.asc()).all()
    return {
        "count": len(promos),
        "promotions": [
            {
                "id": pr.id,
                "code": pr.code,
                "title": pr.title,
                "description": pr.description,
                "applies_to_category": pr.applies_to_category,
                "discount_pct": pr.discount_pct,
                "starts_at": pr.starts_at,
                "ends_at": pr.ends_at,
                "is_active": bool(pr.is_active),
            }
            for pr in promos
        ],
    }


@router.get("/support")
def list_support(db: Session = Depends(get_db)) -> Dict[str, Any]:
    articles = db.query(SupportArticle).order_by(SupportArticle.id.asc()).all()
    return {
        "count": len(articles),
        "articles": [
            {
                "id": a.id,
                "slug": a.slug,
                "title": a.title,
                "body": a.body,
                "tags": (a.tags or "").split(",") if a.tags else [],
            }
            for a in articles
        ],
    }
