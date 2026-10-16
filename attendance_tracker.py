
import csv
import os
import ssl
import tarfile
from pathlib import Path
from datetime import datetime
import requests

students = {}
MIN_ATTENDANCE = 75
VALID_STATUSES = {"P", "A", "L", "H"}

def addStudent(roll_no, name, section="A"):
    """Add a student to the attendance register."""
    if roll_no in students:
        raise ValueError(f"Student {roll_no} already exists")

    students[roll_no] = {
        "name": name,
        "section": section,
        "records": []
    }


def markAttendance(roll_no, date, status, register=None):
    """Mark attendance and prevent duplicate entries."""
    if roll_no not in students:
        raise ValueError(f"Unknown student: {roll_no}")

    # Validate and normalize date
    date = datetime.strptime(date, "%Y-%m-%d").date().isoformat()

    status = status.upper()
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid attendance status: {status}")

    if register is None:
        register = {}

    records = students[roll_no]["records"]

    # Prevent duplicate attendance for the same student and date
    if any(record_date == date for record_date, _ in records):
        raise ValueError(
            f"Attendance already marked for {roll_no} on {date}"
        )

    records.append((date, status))
    register.setdefault(date, []).append(roll_no)

    return register


def attendancePercentage(roll_no):
    """Calculate attendance percentage."""
    records = students[roll_no]["records"]

    if not records:
        return 0

    present = sum(1 for _, status in records if status == "P")
    total = len(records)

    return int(present / total * 100)


def isEligible(percentage):
    """Check whether a student meets the minimum attendance."""
    return percentage >= MIN_ATTENDANCE


def shortageList():
    """Return students below the minimum attendance."""
    result = []

    for roll_no in students:
        percentage = attendancePercentage(roll_no)

        if not isEligible(percentage):
            result.append(roll_no)

    return result


def hasLongAbsence(roll_no, days=3):
    """Check for consecutive absences in recorded sessions."""
    if days <= 0:
        raise ValueError("days must be greater than zero")

    records = sorted(students[roll_no]["records"])

    consecutive_absences = 0

    for _, status in records:
        if status == "A":
            consecutive_absences += 1

            if consecutive_absences >= days:
                return True
        else:
            consecutive_absences = 0

    return False


def latestDate(roll_no):
    """Return the latest attendance date in ISO format."""
    records = students[roll_no]["records"]

    if not records:
        return None

    dates = [
        datetime.strptime(date, "%Y-%m-%d").date()
        for date, _ in records
    ]

    return max(dates).isoformat()


def safe_csv_value(value):
    """Prevent spreadsheet formula execution in exported text."""
    text = str(value)

    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text

    return text


def exportCsv(path="attendance.csv"):
    """Export attendance percentages to a CSV file."""
    output_path = Path(path)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["roll_no", "name", "percentage"])

        for roll_no, student in students.items():
            writer.writerow([
                safe_csv_value(roll_no),
                safe_csv_value(student["name"]),
                attendancePercentage(roll_no)
            ])

    return str(output_path)


def syncToErp(roll_no):
    """Sync only when a real ERP endpoint and key are configured."""
    erp_url = os.environ.get("ERP_URL")
    api_key = os.environ.get("ERP_API_KEY")

    if not erp_url or not api_key:
        return "ERP sync skipped: configure ERP_URL and ERP_API_KEY"

    if roll_no not in students:
        raise ValueError(f"Unknown student: {roll_no}")

    payload = {
        "roll_no": roll_no,
        "pct": attendancePercentage(roll_no)
    }

    response = requests.post(
        erp_url,
        json=payload,
        headers={"X-API-Key": api_key},
        timeout=10,
        verify=True
    )

    response.raise_for_status()
    return response.status_code


def backupReports():
    """Create a compressed backup of CSV reports without shell commands."""
    reports = list(Path(".").glob("*.csv"))

    if not reports:
        return "No CSV reports to back up"

    backup_path = Path("reports_backup.tgz")

    with tarfile.open(backup_path, "w:gz") as archive:
        for report in reports:
            if report.is_file() and report != backup_path:
                archive.add(report, arcname=report.name)

    return str(backup_path)


def legacyChannel(version=None):
    """Create a secure TLS context using system defaults."""
    return ssl.create_default_context()


def runJob(command, shell=False):
    """Describe a job without executing arbitrary commands."""
    return {
        "command": command,
        "shell": False,
        "executed": False
    }


def scheduleReminders():
    """Prepare a reminder job; does not send actual SMS messages."""
    return runJob("send_sms --shortage")


def main():
    # Create sample students
    addStudent("R01", "Aditi")
    addStudent("R02", "Bharat")

    # Use one shared register for every attendance entry
    register = {}

    # R01: 3 present, 1 late, 1 holiday
    r01_records = [
        ("2026-09-01", "P"),
        ("2026-09-02", "P"),
        ("2026-09-03", "L"),
        ("2026-09-04", "P"),
        ("2026-09-05", "H")
    ]

    for date, status in r01_records:
        markAttendance("R01", date, status, register)

    # R02: 2 present and 3 consecutive absences
    r02_records = [
        ("2026-09-01", "P"),
        ("2026-09-02", "A"),
        ("2026-09-03", "A"),
        ("2026-09-04", "A"),
        ("2026-09-05", "P")
    ]

    for date, status in r02_records:
        markAttendance("R02", date, status, register)

    # Display results
    print("R01 attendance %:", attendancePercentage("R01"))
    print("R02 attendance %:", attendancePercentage("R02"))
    print("Is 75% eligible?", isEligible(75))
    print("Shortage list:", shortageList())
    print("R02 long absence?", hasLongAbsence("R02"))
    print("R02 latest date:", latestDate("R02"))
    print(
        "Register entries for 2026-09-01:",
        register.get("2026-09-01", [])
    )
    print("Exported to:", exportCsv())
    print("Reminder job:", scheduleReminders())
    print("ERP sync:", syncToErp("R01"))


if __name__ == "__main__":
    main()
