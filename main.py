from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Ajusta tu cadena de conexión (sin tildes/ñ) o usa URL encoding
DATABASE_URL = "postgresql://postgres:uPxBHn]Ag9H~N4'K@20.84.99.214:443/nu100221"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Estudiante(Base):
    __tablename__ = "estudiantes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    edad = Column(Integer, nullable=False)
    foto_url = Column(String(255), nullable=True)  # <--- Nuevo campo

Base.metadata.create_all(bind=engine)

class EstudianteSchema(BaseModel):
    nombre: str
    edad: int
    foto_url: str | None = None  # <--- Nuevo campo opcional

app = FastAPI()

# CORS (para que la app Android pueda llamar sin problemas)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción restringe dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/estudiantes/")
def insertar_estudiante(estudiante: EstudianteSchema):
    db = SessionLocal()
    try:
        nuevo = Estudiante(nombre=estudiante.nombre, edad=estudiante.edad , foto_url=estudiante.foto_url)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return {"mensaje": "Estudiante insertado", "data": nuevo.id}
    finally:
        db.close()

@app.get("/estudiantes/")
def listar_estudiantes():
    db = SessionLocal()
    try:
        return db.query(Estudiante).all()
    finally:
        db.close()

@app.put("/estudiantes/{id}")
def actualizar_estudiante(
    id: int = Path(..., description="ID del estudiante a actualizar"),
    estudiante: EstudianteSchema = None
):
    db = SessionLocal()
    try:
        est = db.query(Estudiante).filter(Estudiante.id == id).first()
        if not est:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        est.nombre = estudiante.nombre
        est.edad = estudiante.edad
        est.foto_url = estudiante.foto_url
        db.commit()
        db.refresh(est)
        return {"mensaje": "Estudiante actualizado",
                "data": {"id": est.id, "nombre": est.nombre, "edad": est.edad, "foto_url": est.foto_url}}
    finally:
        db.close()

@app.delete("/estudiantes/{id}")
def eliminar_estudiante(id: int):
    db = SessionLocal()
    try:
        est = db.query(Estudiante).filter(Estudiante.id == id).first()
        if not est:
            raise HTTPException(status_code=404, detail="No encontrado")
        db.delete(est)
        db.commit()
        return {"mensaje": "Estudiante eliminado"}
    finally:
        db.close()



