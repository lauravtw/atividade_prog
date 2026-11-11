import os
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload

st.set_page_config(page_title="Festa IFC Blumenau", page_icon="🎉", layout="wide")

if "DATABASE_URL" not in os.environ:
    try:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
    except (FileNotFoundError, KeyError):
        pass

from src.database import SessionLocal, initialize_database
from src.models import Food, Ingredient, Supplier, Volunteer


initialize_database()


def show_error(message: str) -> None:
    st.error(message)


def run_write(action) -> bool:
    try:
        with SessionLocal.begin() as session:
            action(session)
        return True
    except IntegrityError:
        show_error("Nao foi possivel salvar: existe um registro relacionado ou um nome duplicado.")
    except SQLAlchemyError as error:
        show_error(f"Erro ao acessar o banco de dados: {error}")
    return False


def get_records(model):
    with SessionLocal() as session:
        statement = select(model).order_by(model.id)
        if model is Ingredient:
            statement = statement.options(selectinload(Ingredient.supplier))
        elif model is Food:
            statement = statement.options(selectinload(Food.ingredients))
        return session.scalars(statement).all()


def supplier_page() -> None:
    st.header("Fornecedores e doadores")
    with st.form("create_supplier", clear_on_submit=True):
        name = st.text_input("Nome *")
        contact = st.text_input("Pessoa de contato")
        phone = st.text_input("Telefone ou e-mail")
        submitted = st.form_submit_button("Cadastrar fornecedor")
    if submitted:
        if not name.strip():
            show_error("Informe o nome do fornecedor.")
        elif run_write(lambda session: session.add(
            Supplier(name=name.strip(), contact=contact.strip(), phone=phone.strip())
        )):
            st.success("Fornecedor cadastrado.")

    records = get_records(Supplier)
    st.subheader("Fornecedores cadastrados")
    st.dataframe(
        [{"ID": item.id, "Nome": item.name, "Contato": item.contact, "Telefone/e-mail": item.phone}
         for item in records],
        width="stretch",
        hide_index=True,
    )
    if records:
        options = {f"{item.id} - {item.name}": item.id for item in records}
        selected = st.selectbox("Editar ou excluir fornecedor", options)
        item_id = options[selected]
        item = next(record for record in records if record.id == item_id)
        with st.form("edit_supplier"):
            new_name = st.text_input("Nome", value=item.name)
            new_contact = st.text_input("Pessoa de contato", value=item.contact)
            new_phone = st.text_input("Telefone ou e-mail", value=item.phone)
            col1, col2 = st.columns(2)
            update = col1.form_submit_button("Salvar alteracoes")
            delete = col2.form_submit_button("Excluir fornecedor")
        if update:
            if not new_name.strip():
                show_error("Informe o nome do fornecedor.")
            elif run_write(lambda session: session.query(Supplier).filter_by(id=item_id).update(
                {"name": new_name.strip(), "contact": new_contact.strip(), "phone": new_phone.strip()}
            )):
                st.success("Fornecedor atualizado.")
                st.rerun()
        if delete:
            if run_write(lambda session: session.delete(session.get(Supplier, item_id))):
                st.success("Fornecedor excluido.")
                st.rerun()


def ingredient_page() -> None:
    st.header("Insumos doados")
    suppliers = get_records(Supplier)
    supplier_options = {"Sem fornecedor informado": None}
    supplier_options.update({item.name: item.id for item in suppliers})
    with st.form("create_ingredient", clear_on_submit=True):
        name = st.text_input("Insumo *")
        unit = st.text_input("Unidade (kg, L, unidade...) *")
        quantity = st.number_input("Quantidade doada", min_value=0.0, step=1.0)
        supplier_name = st.selectbox("Fornecedor/doador", list(supplier_options))
        submitted = st.form_submit_button("Cadastrar insumo")
    if submitted:
        if not name.strip() or not unit.strip():
            show_error("Informe o nome e a unidade do insumo.")
        elif run_write(lambda session: session.add(Ingredient(
            name=name.strip(),
            unit=unit.strip(),
            quantity_donated=quantity,
            supplier_id=supplier_options[supplier_name],
        ))):
            st.success("Insumo cadastrado.")

    records = get_records(Ingredient)
    st.subheader("Insumos cadastrados")
    st.dataframe(
        [{"ID": item.id, "Insumo": item.name, "Unidade": item.unit,
          "Quantidade doada": item.quantity_donated,
          "Fornecedor/doador": item.supplier.name if item.supplier else "Nao informado"}
         for item in records],
        width="stretch",
        hide_index=True,
    )
    if records:
        options = {f"{item.id} - {item.name}": item.id for item in records}
        selected = st.selectbox("Editar ou excluir insumo", options)
        item_id = options[selected]
        item = next(record for record in records if record.id == item_id)
        supplier_names = list(supplier_options)
        current_supplier = next(
            (name for name, supplier_id in supplier_options.items()
             if supplier_id == item.supplier_id),
            "Sem fornecedor informado",
        )
        with st.form("edit_ingredient"):
            new_name = st.text_input("Insumo", value=item.name)
            new_unit = st.text_input("Unidade", value=item.unit)
            new_quantity = st.number_input(
                "Quantidade doada", min_value=0.0, value=float(item.quantity_donated), step=1.0
            )
            new_supplier_name = st.selectbox(
                "Fornecedor/doador", supplier_names, index=supplier_names.index(current_supplier)
            )
            col1, col2 = st.columns(2)
            update = col1.form_submit_button("Salvar alteracoes")
            delete = col2.form_submit_button("Excluir insumo")
        if update:
            if not new_name.strip() or not new_unit.strip():
                show_error("Informe o nome e a unidade do insumo.")
            elif run_write(lambda session: session.query(Ingredient).filter_by(id=item_id).update({
                "name": new_name.strip(),
                "unit": new_unit.strip(),
                "quantity_donated": new_quantity,
                "supplier_id": supplier_options[new_supplier_name],
            })):
                st.success("Insumo atualizado.")
                st.rerun()
        if delete:
            if run_write(lambda session: session.delete(session.get(Ingredient, item_id))):
                st.success("Insumo excluido.")
                st.rerun()


def food_page() -> None:
    st.header("Alimentos para venda")
    ingredients = get_records(Ingredient)
    ingredient_options = {f"{item.name} ({item.unit})": item.id for item in ingredients}
    with st.form("create_food", clear_on_submit=True):
        name = st.text_input("Alimento *")
        description = st.text_area("Descricao")
        sale_price = st.number_input("Preco de venda (R$)", min_value=0.0, step=0.5)
        selected_ingredients = st.multiselect("Insumos utilizados", list(ingredient_options))
        submitted = st.form_submit_button("Cadastrar alimento")
    if submitted:
        if not name.strip():
            show_error("Informe o nome do alimento.")
        else:
            def create_food(session):
                food = Food(name=name.strip(), description=description.strip(), sale_price=sale_price)
                food.ingredients = [
                    session.get(Ingredient, ingredient_options[label])
                    for label in selected_ingredients
                ]
                session.add(food)

            if run_write(create_food):
                st.success("Alimento cadastrado.")

    records = get_records(Food)
    st.subheader("Alimentos cadastrados")
    st.dataframe(
        [{"ID": item.id, "Alimento": item.name, "Descricao": item.description,
          "Preco de venda (R$)": item.sale_price,
          "Insumos": ", ".join(ingredient.name for ingredient in item.ingredients)}
         for item in records],
        width="stretch",
        hide_index=True,
    )
    if records:
        options = {f"{item.id} - {item.name}": item.id for item in records}
        selected = st.selectbox("Editar ou excluir alimento", options)
        item_id = options[selected]
        item = next(record for record in records if record.id == item_id)
        current_ingredients = {
            label for label, ingredient_id in ingredient_options.items()
            if any(ingredient.id == ingredient_id for ingredient in item.ingredients)
        }
        with st.form("edit_food"):
            new_name = st.text_input("Alimento", value=item.name)
            new_description = st.text_area("Descricao", value=item.description)
            new_price = st.number_input(
                "Preco de venda (R$)", min_value=0.0, value=float(item.sale_price), step=0.5
            )
            new_ingredients = st.multiselect(
                "Insumos utilizados",
                list(ingredient_options),
                default=list(current_ingredients),
            )
            col1, col2 = st.columns(2)
            update = col1.form_submit_button("Salvar alteracoes")
            delete = col2.form_submit_button("Excluir alimento")
        if update:
            if not new_name.strip():
                show_error("Informe o nome do alimento.")
            else:
                def update_food(session):
                    food = session.get(Food, item_id)
                    food.name = new_name.strip()
                    food.description = new_description.strip()
                    food.sale_price = new_price
                    food.ingredients = [
                        session.get(Ingredient, ingredient_options[label])
                        for label in new_ingredients
                    ]

                if run_write(update_food):
                    st.success("Alimento atualizado.")
                    st.rerun()
        if delete:
            if run_write(lambda session: session.delete(session.get(Food, item_id))):
                st.success("Alimento excluido.")
                st.rerun()


def volunteer_page() -> None:
    st.header("Pessoas que trabalharao na festa")
    categories = ["Aluno(a)", "Pai ou mae de aluno(a)", "Servidor(a)"]
    with st.form("create_volunteer", clear_on_submit=True):
        name = st.text_input("Nome *")
        category = st.selectbox("Categoria", categories)
        role = st.text_input("Atividade na festa")
        contact = st.text_input("Contato")
        submitted = st.form_submit_button("Cadastrar pessoa")
    if submitted:
        if not name.strip():
            show_error("Informe o nome da pessoa.")
        elif run_write(lambda session: session.add(Volunteer(
            name=name.strip(), category=category, role=role.strip(), contact=contact.strip()
        ))):
            st.success("Pessoa cadastrada.")

    records = get_records(Volunteer)
    st.subheader("Pessoas cadastradas")
    st.dataframe(
        [{"ID": item.id, "Nome": item.name, "Categoria": item.category,
          "Atividade": item.role, "Contato": item.contact} for item in records],
        width="stretch",
        hide_index=True,
    )
    if records:
        options = {f"{item.id} - {item.name} ({item.category})": item.id for item in records}
        selected = st.selectbox("Editar ou excluir pessoa", options)
        item_id = options[selected]
        item = next(record for record in records if record.id == item_id)
        with st.form("edit_volunteer"):
            new_name = st.text_input("Nome", value=item.name)
            new_category = st.selectbox("Categoria", categories, index=categories.index(item.category))
            new_role = st.text_input("Atividade na festa", value=item.role)
            new_contact = st.text_input("Contato", value=item.contact)
            col1, col2 = st.columns(2)
            update = col1.form_submit_button("Salvar alteracoes")
            delete = col2.form_submit_button("Excluir pessoa")
        if update:
            if not new_name.strip():
                show_error("Informe o nome da pessoa.")
            elif run_write(lambda session: session.query(Volunteer).filter_by(id=item_id).update({
                "name": new_name.strip(),
                "category": new_category,
                "role": new_role.strip(),
                "contact": new_contact.strip(),
            })):
                st.success("Cadastro atualizado.")
                st.rerun()
        if delete:
            if run_write(lambda session: session.delete(session.get(Volunteer, item_id))):
                st.success("Pessoa excluida.")
                st.rerun()


st.title("Festa do IFC Campus Blumenau")
st.caption("Organize os alimentos, insumos doados, fornecedores e equipes da festa.")
page = st.sidebar.radio(
    "Gerenciar",
    ["Visao geral", "Alimentos", "Insumos", "Fornecedores/doadores", "Pessoas"],
)

if page == "Visao geral":
    st.header("Painel da organizacao")
    foods = get_records(Food)
    ingredients = get_records(Ingredient)
    suppliers = get_records(Supplier)
    volunteers = get_records(Volunteer)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alimentos", len(foods))
    col2.metric("Insumos doados", len(ingredients))
    col3.metric("Fornecedores/doadores", len(suppliers))
    col4.metric("Pessoas na equipe", len(volunteers))
    if foods:
        st.subheader("Cardapio e precos")
        st.dataframe(
            [{"Alimento": food.name, "Preco de venda (R$)": food.sale_price} for food in foods],
            width="stretch",
            hide_index=True,
        )
elif page == "Alimentos":
    food_page()
elif page == "Insumos":
    ingredient_page()
elif page == "Fornecedores/doadores":
    supplier_page()
else:
    volunteer_page()
