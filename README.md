# Attendance Tracker

**Student:** Reia S
**SRN:** PES2UG24CS921
**Assignment:** L5_61_attendance-tracker

## Overview

A Python attendance tracker for recording student attendance,
calculating attendance percentages, checking eligibility,
identifying shortages, detecting consecutive absences, and
exporting reports to CSV.

## Features

- Add students and sections
- Record attendance with duplicate prevention
- Calculate attendance percentages
- Check the minimum attendance requirement of 75%
- Generate a shortage list
- Detect consecutive absences
- Find the latest attendance date
- Export attendance data to CSV
- Create compressed report backups
- Prepare reminder jobs
- Optionally sync with a configured ERP endpoint

## Requirements

- Python 3
- requests

## Installation

Install the required dependency:

    python3 -m pip install -r requirements.txt

## Run

    python3 attendance_tracker.py

The program generates attendance.csv in the current directory.

## Attendance Status## Attendance Status##Absent
- L: Late
- H: Ho- H: Ho- H: Ho- H: H included attendance records are sample data.
The reminder function prepares a job but does not send SMS.
ERP synchronization requires a real, aERP synchronization requires a real, aERP synchronizriables.

## License

For academic use.
