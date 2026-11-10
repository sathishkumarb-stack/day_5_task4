import logging
from fastapi import FastAPI, Depends, HTTPException, Query, Request, Header, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import get_db, Base, engine
from src.models import Customer
from src.schemas import CustomerCreate, CustomerUpdate, CustomerOut
from src.security import verify_api_key, verify_webhook_signature

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Day 5 Task 4 - Integration Testing")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    new_customer = Customer(**customer.model_dump())
    db.add(new_customer)

    try:
        db.commit()
        db.refresh(new_customer)
        return new_customer
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")


@app.get("/customers", response_model=list[CustomerOut])
def get_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    return (
        db.query(Customer)
        .order_by(Customer.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )


@app.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@app.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for key, value in customer_data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)

    try:
        db.commit()
        db.refresh(customer)
        return customer
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")


@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}


def process_event(payload: bytes):
    logging.info("Webhook event received: %s", payload.decode("utf-8"))


@app.post("/webhooks/customer-events")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: str = Header(default=None)
):
    raw_body = await request.body()

    if not verify_webhook_signature(raw_body, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    background_tasks.add_task(process_event, raw_body)

    return {"status": "accepted"}