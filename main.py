from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Kas RW Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "192.168.56.11"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME", "kasrw"),
        user=os.getenv("DB_USER", "kasrw_user"),
        password=os.getenv("DB_PASSWORD", "password123"),
    )

class TransactionBase(BaseModel):
    date: date
    keterangan: str
    jenis: str
    jumlah: float

@app.get("/")
def read_root():
    return {"message": "Welcome to Kas RW Backend API!"}

@app.post("/transaksi", status_code=201)
def create_transaction(transaction: TransactionBase):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO transaksi (date, keterangan, jenis, jumlah) VALUES (%s, %s, %s, %s)"
        values = (transaction.date, transaction.keterangan, transaction.jenis, transaction.jumlah)
        cursor.execute(query, values)
        conn.commit()
        new_id = cursor.lastrowid
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()
    return {"id": new_id, "message": "Transaction created successfully!"}

@app.get("/transaksi")
def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM transaksi ORDER BY id DESC")
        rows = cursor.fetchall()
        for row in rows:
            if row.get("date"):
                row["date"] = str(row["date"])
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()
    return rows
