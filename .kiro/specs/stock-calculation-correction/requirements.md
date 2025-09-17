# Stock Calculation Correction - Requirements Document

## Introduction

The current migration system from MS Access to PostgreSQL needs correction for historical stock calculation logic. The system needs to properly calculate stock levels for any given date by processing stock movements, particularly handling movements with documento_referencia "000000" which represent stock resets rather than actual movements.

## Requirements

### Requirement 1: Stock Reset Logic for "000000" Movements

**User Story:** As a system user, I want movements with documento_referencia "000000" to reset the stock to a specific value at that date, so that historical stock calculations are accurate from that point forward.

#### Acceptance Criteria

1. WHEN a movement has documento_referencia = "000000" THEN the system SHALL treat this as a stock reset to the movement's quantidade value
2. WHEN calculating stock for a date THEN the system SHALL find the most recent "000000" movement before or on that date as the base stock
3. WHEN a "000000" movement exists THEN the system SHALL ignore all movements before this reset date for stock calculations
4. WHEN multiple "000000" movements exist for the same product THEN the system SHALL use the most recent one before the target date

### Requirement 2: Historical Stock Calculation Logic

**User Story:** As a system user, I want to calculate the stock level of any product for any historical date, so that I can track inventory changes over time.

#### Acceptance Criteria

1. WHEN calculating stock for a specific date THEN the system SHALL start with the most recent "000000" reset before that date
2. WHEN no "000000" reset exists before the target date THEN the system SHALL start with zero stock
3. WHEN processing movements after the reset date THEN the system SHALL apply entrada (+) and saída (-) movements chronologically
4. WHEN calculating stock THEN the system SHALL only include movements up to and including the target date

### Requirement 3: Stock Calculation Function

**User Story:** As a developer, I want a function that can calculate the stock level for any product at any given date, so that the system can provide accurate historical stock information.

#### Acceptance Criteria

1. WHEN calling the stock calculation function THEN it SHALL accept product_id and target_date as parameters
2. WHEN calculating stock THEN the function SHALL return the calculated stock quantity for that date
3. WHEN the calculation encounters a "000000" movement THEN it SHALL use that as the base stock and ignore earlier movements
4. WHEN no movements exist for a product THEN the function SHALL return the current estoque_atual from the produtos table

### Requirement 4: Current Stock Validation

**User Story:** As a system administrator, I want to validate that the current stock in the produtos table matches the calculated stock as of today, so that I can identify any discrepancies.

#### Acceptance Criteria

1. WHEN running validation THEN the system SHALL calculate stock for each product as of the current date
2. WHEN validation runs THEN the system SHALL compare calculated stock with produtos.estoque_atual
3. WHEN discrepancies are found THEN the system SHALL report the differences with product details
4. WHEN validation is complete THEN the system SHALL provide a summary of products with correct vs incorrect stock

### Requirement 5: Migration Data Correction

**User Story:** As a system administrator, I want to correct any stock movement data issues during migration, so that historical calculations are accurate.

#### Acceptance Criteria

1. WHEN migrating movements THEN the system SHALL properly identify and flag "000000" documento_referencia records
2. WHEN processing movements THEN the system SHALL ensure proper chronological ordering by data_movimentacao
3. WHEN migration encounters invalid movement types THEN the system SHALL log warnings and skip those records
4. WHEN migration is complete THEN the system SHALL provide a report of any data quality issues found