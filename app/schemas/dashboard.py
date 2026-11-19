from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class AssetClassShare(BaseModel):
    name: str
    value: Decimal
    percent: Decimal


class DashboardOut(BaseModel):
    net_worth: Decimal
    asset_classes: list[AssetClassShare]


class SnapshotOut(BaseModel):
    date: date
    net_worth: Decimal

    model_config = {"from_attributes": True}
