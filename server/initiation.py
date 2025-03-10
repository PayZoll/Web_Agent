import os
import csv

# Define the data directory
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Create the company employees CSV with dummy data
company_employees_path = os.path.join(DATA_DIR, "company_employees.csv")
with open(company_employees_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    # Write header row: columns should include name, address, salary, work_hours, etc.
    writer.writerow(["name", "address", "salary", "work_hours"])
    # Write some dummy employee rows
    writer.writerow(["Alice", "123 Main St", 0.8, 40])
    writer.writerow(["Bob", "456 Elm St", 0.5, 35])
    writer.writerow(["Charlie", "789 Oak St", 0.6, 38])

# Create an initial bulk transfer log CSV with just the header row
bulk_transfer_log_path = os.path.join(DATA_DIR, "bulk_transfer_log.csv")
with open(bulk_transfer_log_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["tx_hash", "status", "recipient", "amount", "timestamp"])

print("Initial CSV files created successfully.")
