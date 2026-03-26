-- EV Analytics Database Schema
-- This script is executed once in MySQL Workbench

CREATE DATABASE IF NOT EXISTS ev_analytics;
USE ev_analytics;

CREATE TABLE IF NOT EXISTS ev_data (
    VehicleID VARCHAR(50),
    Manufacturer VARCHAR(100),
    Model VARCHAR(100),
    Segment VARCHAR(50),
    BatterykWh FLOAT,
    Rangekm FLOAT,
    ExShowroomPriceINR FLOAT,
    OperatingCostINR FLOAT,
    RevenueINR FLOAT,
    ProfitINR FLOAT,
    City VARCHAR(50),
    UsageType VARCHAR(50)
);
