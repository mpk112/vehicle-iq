"""add assessments tables

Revision ID: 20260405_add_assessments
Revises: 20260405_initial_schema
Create Date: 2026-04-05 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260405_add_assessments'
down_revision = '20260405_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create assessments table
    op.create_table(
        'assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization', sa.String(length=255), nullable=False),
        sa.Column('vin', sa.String(length=17), nullable=False),
        sa.Column('make', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('variant', sa.String(length=100), nullable=True),
        sa.Column('fuel_type', sa.String(length=50), nullable=True),
        sa.Column('transmission', sa.String(length=50), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('registration_number', sa.String(length=20), nullable=True),
        sa.Column('persona', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('current_stage', sa.String(length=100), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), nullable=True),
        sa.Column('fraud_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('health_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('price_prediction', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('damage_detections', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ocr_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('fraud_gate_triggered', sa.Boolean(), nullable=True),
        sa.Column('fraud_confidence', sa.Float(), nullable=True),
        sa.Column('requires_manual_review', sa.Boolean(), nullable=True),
        sa.Column('manual_review_reason', sa.String(length=255), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('override_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('actual_transaction_price', sa.Float(), nullable=True),
        sa.Column('transaction_date', sa.DateTime(), nullable=True),
        sa.Column('transaction_type', sa.String(length=50), nullable=True),
        sa.Column('prediction_error', sa.Float(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('processing_started_at', sa.DateTime(), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_assessments_vin'), 'assessments', ['vin'], unique=False)
    op.create_index(op.f('ix_assessments_make'), 'assessments', ['make'], unique=False)
    op.create_index(op.f('ix_assessments_model'), 'assessments', ['model'], unique=False)
    op.create_index(op.f('ix_assessments_year'), 'assessments', ['year'], unique=False)
    op.create_index(op.f('ix_assessments_registration_number'), 'assessments', ['registration_number'], unique=False)
    op.create_index(op.f('ix_assessments_status'), 'assessments', ['status'], unique=False)
    op.create_index(op.f('ix_assessments_fraud_gate_triggered'), 'assessments', ['fraud_gate_triggered'], unique=False)
    op.create_index(op.f('ix_assessments_fraud_confidence'), 'assessments', ['fraud_confidence'], unique=False)
    op.create_index(op.f('ix_assessments_requires_manual_review'), 'assessments', ['requires_manual_review'], unique=False)
    op.create_index(op.f('ix_assessments_created_at'), 'assessments', ['created_at'], unique=False)
    
    # Create assessment_photos table
    op.create_table(
        'assessment_photos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('photo_angle', sa.String(length=50), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=50), nullable=True),
        sa.Column('quality_passed', sa.Boolean(), nullable=True),
        sa.Column('quality_checks', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('quality_feedback', sa.Text(), nullable=True),
        sa.Column('ocr_extracted', sa.Boolean(), nullable=True),
        sa.Column('ocr_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ocr_confidence', sa.Float(), nullable=True),
        sa.Column('damage_detected', sa.Boolean(), nullable=True),
        sa.Column('damage_detections', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('damage_count', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_assessment_photos_assessment_id'), 'assessment_photos', ['assessment_id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_assessment_photos_assessment_id'), table_name='assessment_photos')
    op.drop_table('assessment_photos')
    
    op.drop_index(op.f('ix_assessments_created_at'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_requires_manual_review'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_fraud_confidence'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_fraud_gate_triggered'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_status'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_registration_number'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_year'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_model'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_make'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_vin'), table_name='assessments')
    op.drop_table('assessments')
