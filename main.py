from fastapi import FastAPI, HTTPExtencion
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
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
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

class TransactionBase(BaseModel):
    tanggal: date
    keterangan: str
    jenis: str
    jumlah: float

class updateTransaksi(BaseModel):
    tanggal: Optional[date] = None
    keterangan: Optional[str] = None
    jenis: Optional[str] = None
    jumlah: Optional[float] = None

@app.get("/")
def root():
    return {"message": "Welcome to the Kas RW Backend API!"}

@app.post("/transaksi", status_code=201)
def create_transaksi(transaksi: TransactionBase):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO transaksi (tanggal, keterangan, jenis, jumlah) VALUES (%s, %s, %s, %s)"
    values = (
        transaksi.tanggal,
        transaksi.keterangan,
        transaksi.jenis,
        transaksi.jumlah,
    )
    cursor.execute(query, values)
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": new_id, "message": "Transaction created successfully!"}