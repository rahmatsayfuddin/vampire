-- SQL Script for Project Management System Database Schema (SQLite)
-- This script creates all necessary tables and indexes.

-- Enable Foreign Key support in SQLite
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------
-- Table `Roles`
-- Stores different user roles within the system.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Roles` (
    `role_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `role_name` VARCHAR(50) NOT NULL UNIQUE,
    `description` TEXT
);

-- Index for fast lookup on role_name
CREATE INDEX IF NOT EXISTS `idx_roles_role_name` ON `Roles` (`role_name`);

-- -----------------------------------------------------
-- Table `Users`
-- Stores information about system users.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Users` (
    `user_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `full_name` VARCHAR(100) NOT NULL,
    `role_id` INTEGER NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`role_id`) REFERENCES `Roles` (`role_id`) ON DELETE RESTRICT
);

-- Indexes for fast lookups and join performance
CREATE INDEX IF NOT EXISTS `idx_users_username` ON `Users` (`username`);
CREATE INDEX IF NOT EXISTS `idx_users_email` ON `Users` (`email`);
CREATE INDEX IF NOT EXISTS `idx_users_role_id` ON `Users` (`role_id`);

-- -----------------------------------------------------
-- Table `Menus`
-- Stores information about the application's menu items.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Menus` (
    `menu_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `menu_name` VARCHAR(100) NOT NULL UNIQUE,
    `menu_url` VARCHAR(255) NOT NULL UNIQUE
);

-- Indexes for fast lookups on menu attributes
CREATE INDEX IF NOT EXISTS `idx_menus_menu_name` ON `Menus` (`menu_name`);
CREATE INDEX IF NOT EXISTS `idx_menus_menu_url` ON `Menus` (`menu_url`);

-- -----------------------------------------------------
-- Table `RoleMenuAccess`
-- Junction table for the many-to-many relationship between Roles and Menus.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `RoleMenuAccess` (
    `role_id` INTEGER NOT NULL,
    `menu_id` INTEGER NOT NULL,
    PRIMARY KEY (`role_id`, `menu_id`),
    FOREIGN KEY (`role_id`) REFERENCES `Roles` (`role_id`) ON DELETE CASCADE,
    FOREIGN KEY (`menu_id`) REFERENCES `Menus` (`menu_id`) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table `Products`
-- Stores information about products, which act as containers for projects.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Products` (
    `product_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `product_name` VARCHAR(100) NOT NULL UNIQUE,
    `product_logo_url` VARCHAR(255),
    `description` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast lookup on product_name
CREATE INDEX IF NOT EXISTS `idx_products_product_name` ON `Products` (`product_name`);

-- -----------------------------------------------------
-- Table `Projects`
-- Stores details about individual projects.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Projects` (
    `project_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `project_name` VARCHAR(255) NOT NULL UNIQUE,
    `description` TEXT,
    `product_id` INTEGER NOT NULL,
    `start_date` DATE NOT NULL,
    `end_date` DATE,
    `status` VARCHAR(50) NOT NULL DEFAULT 'Planned', -- e.g., 'Planned', 'In Progress', 'Completed', 'On Hold'
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`product_id`) REFERENCES `Products` (`product_id`) ON DELETE RESTRICT
);

-- Indexes for efficient querying by product, status, and name
CREATE INDEX IF NOT EXISTS `idx_projects_product_id` ON `Projects` (`product_id`);
CREATE INDEX IF NOT EXISTS `idx_projects_status` ON `Projects` (`status`);
CREATE INDEX IF NOT EXISTS `idx_projects_name` ON `Projects` (`project_name`);

-- -----------------------------------------------------
-- Table `PICs` (Persons In Charge)
-- Stores information about individuals designated as Persons In Charge.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `PICs` (
    `pic_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `pic_name` VARCHAR(100) NOT NULL,
    `pic_title` VARCHAR(100),
    `pic_email` VARCHAR(100) UNIQUE,
    `pic_phone` VARCHAR(20)
);

-- Indexes for searching and unique email lookup
CREATE INDEX IF NOT EXISTS `idx_pics_pic_email` ON `PICs` (`pic_email`);
CREATE INDEX IF NOT EXISTS `idx_pics_pic_name` ON `PICs` (`pic_name`);

-- -----------------------------------------------------
-- Table `ProjectPICs`
-- Junction table for the many-to-many relationship between Projects and PICs.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ProjectPICs` (
    `project_id` INTEGER NOT NULL,
    `pic_id` INTEGER NOT NULL,
    `assignment_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`project_id`, `pic_id`),
    FOREIGN KEY (`project_id`) REFERENCES `Projects` (`project_id`) ON DELETE CASCADE,
    FOREIGN KEY (`pic_id`) REFERENCES `PICs` (`pic_id`) ON DELETE CASCADE
);

-- Index for finding projects a specific PIC is assigned to
CREATE INDEX IF NOT EXISTS `idx_projectpics_pic_id` ON `ProjectPICs` (`pic_id`);

-- -----------------------------------------------------
-- Table `Scannings`
-- Records details of each scanning activity associated with a project.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Scannings` (
    `scan_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `project_id` INTEGER NOT NULL,
    `scan_date` DATETIME NOT NULL,
    `scan_type` VARCHAR(50) NOT NULL, -- e.g., 'Vulnerability Scan', 'Code Review', 'Manual Test'
    `scan_status` VARCHAR(50) NOT NULL DEFAULT 'Completed', -- e.g., 'Scheduled', 'In Progress', 'Completed', 'Failed'
    `scan_tool_used` VARCHAR(100),
    `scan_report_url` VARCHAR(255),
    `summary` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`project_id`) REFERENCES `Projects` (`project_id`) ON DELETE CASCADE
);

-- Indexes for efficient querying by project, date, and type
CREATE INDEX IF NOT EXISTS `idx_scannings_project_id` ON `Scannings` (`project_id`);
CREATE INDEX IF NOT EXISTS `idx_scannings_scan_date` ON `Scannings` (`scan_date`);
CREATE INDEX IF NOT EXISTS `idx_scannings_scan_type` ON `Scannings` (`scan_type`);

-- -----------------------------------------------------
-- Table `ScanningResultsDetail`
-- Stores granular, raw results from a scanning activity.
-- These are the individual items reported by a scan, which may or may not become 'Findings'.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ScanningResultsDetail` (
    `scan_result_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `scan_id` INTEGER NOT NULL,
    `raw_title` VARCHAR(255) NOT NULL,
    `raw_description` TEXT,
    `raw_severity` VARCHAR(50), -- e.g., 'High', 'Medium', 'Low' as reported by the tool
    `raw_confidence` VARCHAR(50), -- e.g., 'Certain', 'Firm', 'Tentative'
    `location` VARCHAR(255), -- e.g., file path, URL, line number
    `recommendation` TEXT, -- Added: Raw recommendation from the scanning tool
    `additional_data_json` TEXT, -- JSON blob for tool-specific extra details
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`scan_id`) REFERENCES `Scannings` (`scan_id`) ON DELETE CASCADE
);

-- Indexes for efficient querying of scan results
CREATE INDEX IF NOT EXISTS `idx_scanningresultsdetail_scan_id` ON `ScanningResultsDetail` (`scan_id`);
CREATE INDEX IF NOT EXISTS `idx_scanningresultsdetail_raw_severity` ON `ScanningResultsDetail` (`raw_severity`);


-- -----------------------------------------------------
-- Table `Findings`
-- Stores details about identified findings, which can originate from scans or be added manually.
-- Note: `scan_id` here indicates the *overall scan event* a finding might belong to,
-- but the specific raw results it's based on are linked via `FindingSourceScanResults`.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Findings` (
    `finding_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `project_id` INTEGER NOT NULL,
    `scan_id` INTEGER, -- NULLABLE, refers to the *main* scan event if applicable (can be multiple raw results from one scan)
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `severity` VARCHAR(50) NOT NULL, -- e.g., 'Critical', 'High', 'Medium', 'Low', 'Informational' (curated)
    `status` VARCHAR(50) NOT NULL DEFAULT 'Open', -- e.g., 'Open', 'In Progress', 'Resolved', 'Closed', 'False Positive'
    `remediation` TEXT, -- Added: Curated remediation steps for the finding
    `reported_by_user_id` INTEGER,
    `assigned_to_user_id` INTEGER,
    `reported_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `resolved_date` DATETIME,
    `last_updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`project_id`) REFERENCES `Projects` (`project_id`) ON DELETE CASCADE,
    FOREIGN KEY (`scan_id`) REFERENCES `Scannings` (`scan_id`) ON DELETE SET NULL, -- If a scan is deleted, set this to NULL
    FOREIGN KEY (`reported_by_user_id`) REFERENCES `Users` (`user_id`) ON DELETE SET NULL,
    FOREIGN KEY (`assigned_to_user_id`) REFERENCES `Users` (`user_id`) ON DELETE SET NULL
);

-- Indexes for efficient querying by project, scan, severity, status, and assigned user
CREATE INDEX IF NOT EXISTS `idx_findings_project_id` ON `Findings` (`project_id`);
CREATE INDEX IF NOT EXISTS `idx_findings_scan_id` ON `Findings` (`scan_id`);
CREATE INDEX IF NOT EXISTS `idx_findings_severity` ON `Findings` (`severity`);
CREATE INDEX IF NOT EXISTS `idx_findings_status` ON `Findings` (`status`);
CREATE INDEX IF NOT EXISTS `idx_findings_reported_date` ON `Findings` (`reported_date`);
CREATE INDEX IF NOT EXISTS `idx_findings_assigned_to_user_id` ON `Findings` (`assigned_to_user_id`);


-- -----------------------------------------------------
-- Table `FindingSourceScanResults`
-- Junction table linking a curated `Finding` to one or more raw `ScanningResultsDetail` entries.
-- This defines which specific scan results contributed to a 'Finding'.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `FindingSourceScanResults` (
    `finding_id` INTEGER NOT NULL,
    `scan_result_id` INTEGER NOT NULL,
    PRIMARY KEY (`finding_id`, `scan_result_id`),
    FOREIGN KEY (`finding_id`) REFERENCES `Findings` (`finding_id`) ON DELETE CASCADE,
    FOREIGN KEY (`scan_result_id`) REFERENCES `ScanningResultsDetail` (`scan_result_id`) ON DELETE CASCADE
);

-- Indexes for efficient lookup of source scan results for a finding, and vice versa
CREATE INDEX IF NOT EXISTS `idx_findingsourcescanresults_scan_result_id` ON `FindingSourceScanResults` (`scan_result_id`);

-- Optional: Initial data insertion examples (uncomment if needed)
-- INSERT INTO Roles (role_name, description) VALUES ('Admin', 'System Administrator');
-- INSERT INTO Roles (role_name, description) VALUES ('Project Manager', 'Manages projects');
-- INSERT INTO Roles (role_name, description) VALUES ('Developer', 'Works on findings');

-- INSERT INTO Menus (menu_name, menu_url) VALUES ('Dashboard', '/dashboard');
-- INSERT INTO Menus (menu_name, menu_url) VALUES ('Users', '/users');
-- INSERT INTO Menus (menu_name, menu_url) VALUES ('Projects', '/projects');
-- INSERT INTO Menus (menu_name, menu_url) VALUES ('Findings', '/findings');

-- INSERT INTO RoleMenuAccess (role_id, menu_id) VALUES (1, 1); -- Admin can access Dashboard
-- INSERT INTO RoleMenuAccess (role_id, menu_id) VALUES (1, 2); -- Admin can access Users
