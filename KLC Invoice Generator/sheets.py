def authenticate():
    raise NotImplementedError

def search_invoices(drive, prefix: str) -> list[dict]:
    raise NotImplementedError

def search_template(drive) -> dict | None:
    raise NotImplementedError

def copy_invoice(drive, source_id: str, new_name: str, folder_id: str) -> str:
    raise NotImplementedError

def write_invoice_cells(gc, sheet_id: str, data: dict) -> None:
    raise NotImplementedError

def export_pdf(creds, file_id: str, dest_path: str) -> None:
    raise NotImplementedError

def create_invoice(data: dict) -> tuple[str, str]:
    raise NotImplementedError
