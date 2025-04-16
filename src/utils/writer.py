import os
import csv
from typing import List, Dict

def sanitize_contract(contract: dict, fields: List[str]) -> dict:
    return {field: contract.get(field, None) for field in fields}

def write_contracts_to_csv(
        contracts: List[Dict[str, str]],
        file_path: str,
        fieldnames: List[str]
    ) -> None:

    file_exists = os.path.isfile(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for contract in contracts:
            writer.writerow(contract)
