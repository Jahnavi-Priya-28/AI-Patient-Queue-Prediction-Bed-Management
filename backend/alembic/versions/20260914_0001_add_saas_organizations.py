"""add SaaS organizations and tenant ownership

Revision ID: 20260914_0001
Revises:
Create Date: 2026-09-14
"""
from alembic import op
import sqlalchemy as sa


revision = "20260914_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "organizations" not in tables:
        op.create_table(
            "organizations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=150), nullable=False),
            sa.Column("slug", sa.String(length=80), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
        op.create_index("ix_organizations_name", "organizations", ["name"], unique=True)

    bind.execute(sa.text("insert into organizations (name, slug, is_active) select 'PatientFlow General Hospital', 'patientflow-general', 1 where not exists (select 1 from organizations where slug = 'patientflow-general')"))
    default_org_id = bind.execute(sa.text("select id from organizations where slug = 'patientflow-general'")).scalar()

    for table in ["users", "patients", "doctors", "departments", "wards", "appointments", "queue_entries"]:
        columns = [column["name"] for column in inspector.get_columns(table)]
        if "organization_id" not in columns:
            op.add_column(table, sa.Column("organization_id", sa.Integer(), nullable=True))
            op.create_index(f"ix_{table}_organization_id", table, ["organization_id"])
        bind.execute(sa.text(f"update {table} set organization_id = :org_id where organization_id is null"), {"org_id": default_org_id})

    bind.execute(sa.text("update users set role = 'HOSPITAL_ADMIN' where role = 'ADMIN'"))


def downgrade() -> None:
    for table in ["queue_entries", "appointments", "wards", "departments", "doctors", "patients", "users"]:
        op.drop_index(f"ix_{table}_organization_id", table_name=table, if_exists=True)
        op.drop_column(table, "organization_id")
    op.drop_index("ix_organizations_slug", table_name="organizations", if_exists=True)
    op.drop_index("ix_organizations_name", table_name="organizations", if_exists=True)
    op.drop_table("organizations")
