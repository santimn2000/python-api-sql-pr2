import base64
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, BLOB
#from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from pydantic import BaseModel

app = FastAPI()
engine = create_engine('mysql+pymysql://santimn:rootroot@db4free.net/iesdaw45')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


class Videojuego(Base):
    __tablename__ = 'videojuegos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80))
    categoria = Column(String(80))
    blob_img = Column(BLOB, nullable=True)
    url_img = Column(String(80), nullable=True)
    multijugador = Column(Integer)  # Campo entero para indicar si es multijugador
    precio = Column(Float)  # Campo de tipo flotante para el precio
    desarrolladora = Column(String(80))
    # Otros campos de tu tabla videojuegos

    def __repr__(self):
        return f'<Videojuego {self.nombre}>'


class VideojuegoCreate(BaseModel):
    nombre: str
    categoria: str
    blob_img: bytes = None
    url_img: str = None
    multijugador: int
    precio: float
    desarrolladora: str
    # Agrega otros campos según la estructura de tu tabla
    
class VideojuegoUpdate(BaseModel):
    nombre: str = None
    categoria: str = None
    multijugador: int = None
    precio: float = None
    desarrolladora: str = None
    # Otros campos del videojuego que se pueden actualizar
    
    
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/videojuegos/{videojuego_id}/imagen")
def obtener_imagen(videojuego_id: int):
    db = SessionLocal()
    videojuego = db.query(Videojuego).filter(Videojuego.id == videojuego_id).first()
    db.close()

    if videojuego:
        if videojuego.blob_img:
            # Codificar la imagen como base64
            imagen_codificada = base64.b64encode(videojuego.blob_img).decode('utf-8')
            return {"imagen_base64": imagen_codificada}
        else:
            return {"mensaje": "El videojuego no tiene imagen"}
    else:
        return {"mensaje": "Videojuego no encontrado"}

@app.get("/videojuegos/")
def obtener_videojuegos():
    db = SessionLocal()
    videojuegos = db.query(Videojuego).all()
    db.close()

    if videojuegos:
        videojuegos_con_imagenes = []
        for videojuego in videojuegos:
            videojuego_dict = {
                "id": videojuego.id,
                "nombre": videojuego.nombre,
                "categoria": videojuego.categoria,
                "multijugador": videojuego.multijugador,
                "desarrolladora": videojuego.desarrolladora,
                "precio": videojuego.precio,
                # Otros campos del videojuego
            }

            if videojuego.blob_img:
                imagen_codificada = "Tiene imagen"
                #imagen_codificada = base64.b64encode(videojuego.blob_img).decode('utf-8')
                videojuego_dict["imagen_base64"] = imagen_codificada

            videojuegos_con_imagenes.append(videojuego_dict)

        return {"videojuegos": videojuegos_con_imagenes}
    else:
        return {"mensaje": "No se encontraron videojuegos"}
    

# Ruta para obtener un videojuego por su ID
@app.get("/videojuego/{id}")
def obtener_videojuego(id: int):
    db = SessionLocal()
    videojuego = db.query(Videojuego).filter(Videojuego.id == id).first()
    

    if videojuego:
        videojuego_dict = {
            "id": videojuego.id,
            "nombre": videojuego.nombre,
            "categoria": videojuego.categoria,
            "multijugador": videojuego.multijugador,
            "desarrolladora": videojuego.desarrolladora,
            "precio": videojuego.precio,
            # Otros campos del videojuego
        }

        if videojuego.blob_img:
            imagen_codificada = "Tiene imagen"
            #imagen_codificada = base64.b64encode(videojuego.blob_img).decode('utf-8')
            videojuego_dict["imagen_base64"] = imagen_codificada
            
    else:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado")

    db.close()
    
    return videojuego_dict

    
@app.post("/videojuego/")
def crear_videojuego(videojuego_data: VideojuegoCreate):
    
    campos_obligatorios = ["nombre", "categoria", "multijugador", "precio", "desarrolladora"]
    
    for campo in campos_obligatorios:
        if not hasattr(videojuego_data, campo) or getattr(videojuego_data, campo) is None:
            raise HTTPException(status_code=400, detail=f"El campo '{campo}' es obligatorio y no puede ser nulo")

    
    db = SessionLocal()

    nuevo_videojuego = Videojuego(
        nombre=videojuego_data.nombre,
        categoria=videojuego_data.categoria,
        blob_img=videojuego_data.blob_img,
        url_img=videojuego_data.url_img,
        multijugador=videojuego_data.multijugador,
        precio=videojuego_data.precio,
        desarrolladora=videojuego_data.desarrolladora
        # Asigna otros campos según la estructura de tu tabla
    )

    db.add(nuevo_videojuego)
    db.commit()
    db.refresh(nuevo_videojuego)
    db.close()

    return {"mensaje": "Videojuego creado exitosamente", "id": nuevo_videojuego.id} 
    

@app.put("/videojuego/{id}")
def modificar_videojuego(id: int, videojuego_data: VideojuegoUpdate):
    
    db = SessionLocal()
    videojuego = db.query(Videojuego).filter(Videojuego.id == id).first()

    if not videojuego:
        db.close()
        raise HTTPException(status_code=404, detail="Videojuego no encontrado")
    
    for field, value in videojuego_data.model_dump(exclude_unset=True).items():
        setattr(videojuego, field, value)

    db.commit()
    db.refresh(videojuego)
    db.close()

    return {"mensaje": f"Videojuego con ID {id} modificado exitosamente"}


# Ruta para eliminar un usuario por su ID
@app.delete("/videojuego/{id}")
def eliminar_videojuego(id: int):
    db = SessionLocal()

    videojuego = db.query(Videojuego).filter(Videojuego.id == id).first()

    if not videojuego:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado")

    db.delete(videojuego)
    db.commit()
    db.close()

    return {"mensaje": f"Usuario con ID {id} eliminado exitosamente"}