from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class Fornecedor(Base):
    __tablename__ = 'fornecedores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    contato = Column(String(100))

class Pessoa(Base):
    __tablename__ = 'pessoas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # Aluno, Pai de Aluno, Servidor

class Alimento(Base):
    __tablename__ = 'alimentos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255))
    preco_venda = Column(Float, nullable=False)
    
    # Chave estrangeira para o fornecedor do insumo doado
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'))
    fornecedor = relationship("Fornecedor")

'''from sqlalchemy import Float, ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


food_ingredients = Table(
    "food_ingredients",
    Base.metadata,
    Column("food_id", ForeignKey("foods.id", ondelete="CASCADE"), primary_key=True),
    Column("ingredient_id", ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True),
)


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    contact: Mapped[str] = mapped_column(String(120), default="")
    phone: Mapped[str] = mapped_column(String(40), default="")

    ingredients: Mapped[list["Ingredient"]] = relationship(back_populates="supplier")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    unit: Mapped[str] = mapped_column(String(30))
    quantity_donated: Mapped[float] = mapped_column(Float, default=0)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="SET NULL"))

    supplier: Mapped[Supplier | None] = relationship(back_populates="ingredients")
    foods: Mapped[list["Food"]] = relationship(
        secondary=food_ingredients, back_populates="ingredients"
    )


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(500), default="")
    sale_price: Mapped[float] = mapped_column(Float, default=0)

    ingredients: Mapped[list[Ingredient]] = relationship(
        secondary=food_ingredients, back_populates="foods"
    )


class Volunteer(Base):
    __tablename__ = "volunteers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    category: Mapped[str] = mapped_column(String(30))
    role: Mapped[str] = mapped_column(String(120), default="")
    contact: Mapped[str] = mapped_column(String(120), default="")
'''