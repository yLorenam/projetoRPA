"""
Protótipo de automação de faturamento e emissão de notas fiscais
- Integração financeira simulada
- Cálculo de impostos
- Emissão de nota via API ou fallback RPA (simulado)
- Salvamento de XML e HTML detalhado
- Envio de e-mail (simulado)
- Registro no ERP (simulado)
"""

import os
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
import random

from dotenv import load_dotenv

# --- Carrega .env ---
load_dotenv()

DRY_RUN = os.getenv("DRY_RUN", "True") == "True"
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "prototype_output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("faturamento_prototype")

# --- Taxas ---
TAX_RATES = {
    "ICMS": 0.18,
    "PIS": 0.0165,
    "COFINS": 0.076
}

# --- Funções auxiliares ---

def calculate_taxes(item_value):
    icms = round(item_value * TAX_RATES["ICMS"], 2)
    pis = round(item_value * TAX_RATES["PIS"], 2)
    cofins = round(item_value * TAX_RATES["COFINS"], 2)
    total_taxes = round(icms + pis + cofins, 2)
    total_with_taxes = round(item_value + total_taxes, 2)
    return {
        "ICMS": icms,
        "PIS": pis,
        "COFINS": cofins,
        "total_taxes": total_taxes,
        "total_with_taxes": total_with_taxes
    }

def simulate_financial_integration(sale):
    logger.info(f"Integrando venda id={sale['sale_id']} ao sistema financeiro...")
    financial_id = f"FIN-{sale['sale_id']}-{random.randint(1000,9999)}"
    logger.info(f"Recebido financial_id={financial_id}")
    return financial_id

def simulate_emit_invoice_api(sale, taxes, financial_id):
    logger.info(f"Tentando emitir nota via API para sale_id={sale['sale_id']}...")
    api_available = True if DRY_RUN else random.random() > 0.2
    if api_available:
        xml = f"<nota><id>{sale['sale_id']}</id><cliente>{sale['customer_name']}</cliente><valor>{sale['amount']}</valor><icms>{taxes['ICMS']}</icms></nota>"
        logger.info("Emissão via API sucedida.")
        return {"method":"api", "xml":xml}
    else:
        raise ConnectionError("API SEFAZ indisponível")

def simulate_emit_invoice_rpa(sale, taxes, financial_id):
    logger.info(f"Executando RPA (simulado) para sale_id={sale['sale_id']}...")
    rpa_success = True if DRY_RUN else random.random() > 0.1
    if rpa_success:
        xml = f"<nota-rpa><id>{sale['sale_id']}</id><cliente>{sale['customer_name']}</cliente><valor>{sale['amount']}</valor></nota-rpa>"
        logger.info("RPA gerou a nota com sucesso.")
        return {"method":"rpa", "xml":xml}
    else:
        raise RuntimeError("RPA failed")

def generate_invoice_html(sale, taxes):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Nota Fiscal - {sale['sale_id']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .right {{ text-align: right; }}
            .total {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Nota Fiscal</h1>
        <p><strong>Venda ID:</strong> {sale['sale_id']}</p>
        <p><strong>Cliente:</strong> {sale['customer_name']} ({sale['customer_email']})</p>
        <p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <table>
            <tr>
                <th>Descrição</th>
                <th class="right">Valor (R$)</th>
            </tr>
            <tr>
                <td>Produto/Serviço</td>
                <td class="right">{sale['amount']:.2f}</td>
            </tr>
            <tr>
                <td>ICMS ({TAX_RATES['ICMS']*100:.1f}%)</td>
                <td class="right">{taxes['ICMS']:.2f}</td>
            </tr>
            <tr>
                <td>PIS ({TAX_RATES['PIS']*100:.2f}%)</td>
                <td class="right">{taxes['PIS']:.2f}</td>
            </tr>
            <tr>
                <td>COFINS ({TAX_RATES['COFINS']*100:.2f}%)</td>
                <td class="right">{taxes['COFINS']:.2f}</td>
            </tr>
            <tr class="total">
                <td>Total</td>
                <td class="right">{taxes['total_with_taxes']:.2f}</td>
            </tr>
        </table>
        <p><strong>Observações:</strong> Documento gerado automaticamente pelo sistema.</p>
    </body>
    </html>
    """
    return html_content

def save_documents_html(sale, xml_content, html_content):
    now = datetime.now()
    subdir = OUTPUT_DIR / f"{now.year}" / f"{now.month:02d}"
    subdir.mkdir(parents=True, exist_ok=True)

    xml_path = subdir / f"nota_{sale['sale_id']}.xml"
    html_path = subdir / f"nota_{sale['sale_id']}.html"

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"Arquivos salvos: {xml_path}, {html_path}")
    return {"xml": str(xml_path), "html": str(html_path)}

def simulate_send_email(sale, attachments, to_email):
    logger.info(f"Enviando e-mail para {to_email} com anexos {attachments} (simulado)...")
    return True

def simulate_record_in_erp(sale, financial_id, nota_files):
    logger.info(f"Lançando venda {sale['sale_id']} no ERP (simulado).")
    erp_entry_id = f"ERP-{sale['sale_id']}-{random.randint(100,999)}"
    erp_record = {
        "sale_id": sale['sale_id'],
        "financial_id": financial_id,
        "erp_entry_id": erp_entry_id,
        "amount": sale['amount'],
        "nota_files": nota_files,
        "timestamp": datetime.now().isoformat()
    }
    erp_log_path = OUTPUT_DIR / "erp_records.jsonl"
    with open(erp_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(erp_record, ensure_ascii=False) + "\n")
    return erp_entry_id

def process_sale(sale):
    try:
        financial_id = simulate_financial_integration(sale)
        taxes = calculate_taxes(sale['amount'])
        try:
            emission = simulate_emit_invoice_api(sale, taxes, financial_id)
        except Exception as e:
            logger.warning(f"API failed: {e}. Falling back to RPA.")
            emission = simulate_emit_invoice_rpa(sale, taxes, financial_id)
        html_invoice = generate_invoice_html(sale, taxes)
        nota_paths = save_documents_html(sale, emission['xml'], html_invoice)
        email_sent = simulate_send_email(sale, [nota_paths['html'], nota_paths['xml']], sale['customer_email'])
        erp_id = simulate_record_in_erp(sale, financial_id, nota_paths)
        return {
            "sale_id": sale['sale_id'],
            "financial_id": financial_id,
            "erp_id": erp_id,
            "emission_method": emission['method'],
            "xml_path": nota_paths['xml'],
            "html_path": nota_paths['html'],
            "email_sent": email_sent,
            "taxes": taxes,
            "status": "success"
        }
    except Exception as e:
        logger.exception(f"Erro ao processar venda {sale.get('sale_id')}: {e}")
        return {"sale_id": sale.get('sale_id'), "status": "error", "error": str(e)}

# --- Dados de exemplo ---
SAMPLE_SALES = [
    {"sale_id":"S1001", "customer_name":"Empresa A Ltda", "customer_email":"contato@empresaA.com", "amount":1200.00},
    {"sale_id":"S1002", "customer_name":"João Silva", "customer_email":"joao.silva@email.com", "amount":350.50},
    {"sale_id":"S1003", "customer_name":"Escola Municipal", "customer_email":"financeiro@escola.gov.br", "amount":7800.00}
]

def run_pipeline(sales):
    results = []
    report_csv = OUTPUT_DIR / "processing_report.csv"
    for s in sales:
        logger.info(f"=== Processando venda {s['sale_id']} ===")
        res = process_sale(s)
        results.append(res)
    with open(report_csv, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["sale_id","status","emission_method","financial_id","erp_id","xml_path","html_path","email_sent","total_with_taxes"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row = {
                "sale_id": r.get("sale_id"),
                "status": r.get("status"),
                "emission_method": r.get("emission_method"),
                "financial_id": r.get("financial_id"),
                "erp_id": r.get("erp_id"),
                "xml_path": r.get("xml_path"),
                "html_path": r.get("html_path"),
                "email_sent": r.get("email_sent"),
                "total_with_taxes": r.get("taxes", {}).get("total_with_taxes")
            }
            writer.writerow(row)
    logger.info(f"Relatório CSV gerado: {report_csv}")
    return results

if __name__ == "__main__":
    run_pipeline(SAMPLE_SALES)
