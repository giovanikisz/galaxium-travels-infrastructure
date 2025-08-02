from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import date
import os
import random

app = FastAPI(title="Galaxium Travels HR API")

class Employee(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    department: str
    position: str
    hire_date: str
    salary: float

def read_employees():
    try:
        df = pd.read_csv('data/employees.md', sep='|', skiprows=3)
        print("LEU O ARQUIVO")
        df = df.iloc[:, 1:-1]  # Remove first and last empty columns
        print("REMOVEU COLUNAS")
        df.columns = [col.strip() for col in df.columns]
        df_new = df.iloc[1:]
        df_stripped = df_new.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        print(df_new.head(10))
        print(df_stripped.head(10))
        print("STRIP")
        return df_stripped
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading database: {str(e)}")

def write_employees(df):
    try:
        # Create the markdown header
        header = "# Galaxium Travels HR Database\n\n## Employees\n\n"
        # Convert DataFrame to markdown table
        markdown_table = df.to_markdown(index=False)
        # Write to file
        with open('data/employees.md', 'w') as f:
            f.write(header + markdown_table)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing to database: {str(e)}")

@app.get("/employees", response_model=List[Employee])
async def get_employees():
    df = read_employees()
    print(df.to_dict('records'))
    return df.to_dict('records')

@app.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: int):
    df = read_employees()
    df['id'] = df['id'].astype(int)
    employee = df[df['id'] == employee_id]
    if employee.empty:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee.iloc[0].to_dict()

@app.post("/employees", response_model=Employee)
async def create_employee(employee: Employee):
    df = read_employees()
    print(df.head(10))
    df['id'] = df['id'].astype(int)
    print(df['id'].max())
    new_id = df['id'].max() + 1 if not df.empty else 1
    employee_dict = employee.dict()
    employee_dict['id'] = new_id
    df = pd.concat([df, pd.DataFrame([employee_dict])], ignore_index=True)
    write_employees(df)
    return employee_dict

@app.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: int, employee: Employee):
    df = read_employees()
    df['id'] = df['id'].astype(int)
    if employee_id not in df['id'].values:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee_dict = employee.dict()
    employee_dict['id'] = employee_id
    df.loc[df['id'] == employee_id] = employee_dict
    write_employees(df)
    return employee_dict

@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int):
    df = read_employees()
    df['id'] = df['id'].astype(int)
    if employee_id not in df['id'].values:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    df = df[df['id'] != employee_id]
    write_employees(df)
    return {"message": "Employee deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 