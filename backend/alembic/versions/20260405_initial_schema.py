"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-04-05 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create enum types (IF NOT EXISTS)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('Assessor', 'Lender', 'Insurer', 'Broker', 'Admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE assessment_status AS ENUM ('queued', 'processing', 'completed', 'failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('Assessor', 'Lender', 'Insurer', 'Broker', 'Admin', name='user_role'), nullable=False),
        sa.Column('organization', sa.String(255), nullable=True),
        sa.Column('is_active', sa.String(10), default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Vehicle registry table
    op.create_table(
        'vehicle_registry',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('make', sa.String(100), nullable=False, index=True),
        sa.Column('model', sa.String(100), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('variant', sa.String(200), nullable=True),
        sa.Column('fuel_type', sa.String(50), nullable=True),
        sa.Column('transmission', sa.String(50), nullable=True),
        sa.Column('base_price', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_vehicle_lookup', 'vehicle_registry', ['make', 'model', 'year', 'variant'])
    
    # Comparable vehicles table
    op.create_table(
        'comparable_vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vin', sa.String(17), nullable=True, index=True),
        sa.Column('make', sa.String(100), nullable=False, index=True),
        sa.Column('model', sa.String(100), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('variant', sa.String(200), nullable=True),
        sa.Column('fuel_type', sa.String(50), nullable=True),
        sa.Column('transmission', sa.String(50), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('listing_price', sa.Float(), nullable=False),
        sa.Column('listing_date', sa.DateTime(), nullable=True),
        sa.Column('listing_url', sa.String(500), nullable=True),
        sa.Column('embedding', Vector(1024), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_comparable_lookup', 'comparable_vehicles', ['make', 'model', 'year'])
    
    # Assessments table
    op.create_table(
        'assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('vin', sa.String(17), nullable=True, index=True),
        sa.Column('make', sa.String(100), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('variant', sa.String(200), nullable=True),
        sa.Column('fuel_type', sa.String(50), nullable=True),
        sa.Column('transmission', sa.String(50), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('registration_number', sa.String(50), nullable=True),
        sa.Column('persona', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), default='queued', nullable=False),
        sa.Column('current_stage', sa.String(100), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), default=0),
        sa.Column('fraud_result', postgresql.JSONB(), nullable=True),
        sa.Column('health_result', postgresql.JSONB(), nullable=True),
        sa.Column('price_prediction', postgresql.JSONB(), nullable=True),
        sa.Column('damage_detections', postgresql.JSONB(), nullable=True),
        sa.Column('ocr_results', postgresql.JSONB(), nullable=True),
        sa.Column('fraud_gate_triggered', sa.String(10), default='false'),
        sa.Column('manual_review_required', sa.String(10), default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
    )
    op.create_index('idx_assessment_status', 'assessments', ['status'])
    op.create_index('idx_assessment_user', 'assessments', ['user_id'])
    
    # Assessment photos table
    op.create_table(
        'assessment_photos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id'), nullable=False),
        sa.Column('angle', sa.String(50), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('storage_url', sa.String(500), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('quality_passed', sa.String(10), default='false'),
        sa.Column('quality_checks', postgresql.JSONB(), nullable=True),
        sa.Column('ocr_result', postgresql.JSONB(), nullable=True),
        sa.Column('damage_detections', postgresql.JSONB(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
    )
    
    # Manual review queue table
    op.create_table(
        'manual_review_queue',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id'), nullable=False),
        sa.Column('priority', sa.String(20), default='standard', nullable=False),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('override_values', postgresql.JSONB(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
    )
    
    # Fraud cases table
    op.create_table(
        'fraud_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id'), nullable=True),
        sa.Column('fraud_type', sa.String(100), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('evidence', postgresql.JSONB(), nullable=False),
        sa.Column('confirmed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
    )
    
    # Benchmarking metrics table
    op.create_table(
        'benchmarking_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('segment_value', sa.String(100), nullable=True),
        sa.Column('mape', sa.Float(), nullable=False),
        sa.Column('dataset_size', sa.Integer(), nullable=False),
        sa.Column('calculated_at', sa.DateTime(), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=True),
        sa.Column('period_end', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_metrics_category', 'benchmarking_metrics', ['category', 'segment_value'])
    
    # API usage table
    op.create_table(
        'api_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('service_name', sa.String(100), nullable=False, index=True),
        sa.Column('endpoint', sa.String(200), nullable=True),
        sa.Column('request_count', sa.Integer(), default=1),
        sa.Column('success_count', sa.Integer(), default=0),
        sa.Column('failure_count', sa.Integer(), default=0),
        sa.Column('total_duration_ms', sa.Float(), default=0),
        sa.Column('timestamp', sa.DateTime(), nullable=False, index=True),
        sa.Column('date', sa.String(10), nullable=False, index=True),
    )
    op.create_index('idx_api_usage_service_date', 'api_usage', ['service_name', 'date'])
    
    # Audit log table
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, index=True),
    )
    op.create_index('idx_audit_user', 'audit_log', ['user_id'])
    op.create_index('idx_audit_resource', 'audit_log', ['resource_type', 'resource_id'])


def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('api_usage')
    op.drop_table('benchmarking_metrics')
    op.drop_table('fraud_cases')
    op.drop_table('manual_review_queue')
    op.drop_table('assessment_photos')
    op.drop_table('assessments')
    op.drop_table('comparable_vehicles')
    op.drop_table('vehicle_registry')
    op.drop_table('users')
    
    op.execute('DROP TYPE IF EXISTS assessment_status')
    op.execute('DROP TYPE IF EXISTS user_role')
    op.execute('DROP EXTENSION IF EXISTS vector')
