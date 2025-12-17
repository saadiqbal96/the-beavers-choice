"""
Beaver's Choice Paper Company - Multi-Agent System
A comprehensive multi-agent solution for inventory management, quoting, and sales.

Author: AI Consultant
Framework: smolagents
"""

import pandas as pd
import numpy as np
import os
import time
import dotenv
import ast
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Dict, List, Union
from sqlalchemy import create_engine, Engine
from smolagents import CodeAgent, ToolCallingAgent, tool, LiteLLMModel

# Load environment variables
dotenv.load_dotenv()

# Create an SQLite database
db_engine = create_engine("sqlite:///munder_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

# ==================== DATABASE HELPER FUNCTIONS ====================

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """Generate inventory for a specified percentage of items from the paper supply list."""
    np.random.seed(seed)
    num_items = int(len(paper_supplies) * coverage)
    selected_indices = np.random.choice(range(len(paper_supplies)), size=num_items, replace=False)
    selected_items = [paper_supplies[i] for i in selected_indices]
    
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),
            "min_stock_level": np.random.randint(50, 150)
        })
    
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine, seed: int = 137) -> Engine:    
    """Set up the database with all required tables and initial records."""
    try:
        transactions_schema = pd.DataFrame({
            "id": [], "item_name": [], "transaction_type": [], 
            "units": [], "price": [], "transaction_date": [],
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)
        
        initial_date = datetime(2025, 1, 1).isoformat()
        
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)
        
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date
        
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))
        
        quotes_df = quotes_df[["request_id", "total_amount", "quote_explanation", 
                               "order_date", "job_type", "order_size", "event_type"]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)
        
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)
        initial_transactions = []
        
        initial_transactions.append({
            "item_name": None, "transaction_type": "sales",
            "units": None, "price": 50000.0, "transaction_date": initial_date,
        })
        
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })
        
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)
        
        return db_engine
    
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def create_transaction(item_name: str, transaction_type: str, quantity: int, 
                      price: float, date: Union[str, datetime]) -> int:
    """Record a transaction in the database."""
    try:
        date_str = date.isoformat() if isinstance(date, datetime) else date
        
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")
        
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])
        
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])
    
    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """Retrieve a snapshot of available inventory as of a specific date."""
    query = """
        SELECT item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """Retrieve the stock level of a specific item as of a given date."""
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()
    
    stock_query = """
        SELECT item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name AND transaction_date <= :as_of_date
    """
    
    return pd.read_sql(stock_query, db_engine, 
                      params={"item_name": item_name, "as_of_date": as_of_date})

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """Estimate the supplier delivery date based on order quantity."""
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        input_date_dt = datetime.now()
    
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7
    
    delivery_date_dt = input_date_dt + timedelta(days=days)
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """Calculate the current cash balance as of a specified date."""
    try:
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()
        
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine, params={"as_of_date": as_of_date},
        )
        
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)
        
        return 0.0
    
    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0

def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """Generate a complete financial report as of a specific date."""
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()
    
    cash = get_cash_balance(as_of_date)
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []
    
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value
        
        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })
    
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")
    
    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }

def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """Retrieve historical quotes matching the provided search terms."""
    conditions = []
    params = {}
    
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT qr.response AS original_request, q.total_amount, q.quote_explanation,
               q.job_type, q.order_size, q.event_type, q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """
    
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row) for row in result]

# ==================== AGENT TOOLS ====================

@tool
def check_inventory_tool(item_name: str, request_date: str) -> str:
    """
    Check the current stock level of a specific item.
    
    Args:
        item_name: Name of the item to check
        request_date: Date for the inventory check (YYYY-MM-DD format)
    
    Returns:
        String describing the current stock level and item details
    """
    try:
        # Get stock level
        stock_df = get_stock_level(item_name, request_date)
        current_stock = int(stock_df["current_stock"].iloc[0])
        
        # Get item details from inventory
        inventory_df = pd.read_sql("SELECT * FROM inventory WHERE item_name = :item", 
                                   db_engine, params={"item": item_name})
        
        if inventory_df.empty:
            return f"Item '{item_name}' is not in our inventory catalog."
        
        item_info = inventory_df.iloc[0]
        min_stock = int(item_info["min_stock_level"])
        unit_price = float(item_info["unit_price"])
        
        status = "ADEQUATE" if current_stock >= min_stock else "LOW - REORDER NEEDED"
        
        return (f"Item: {item_name}\n"
                f"Current Stock: {current_stock} units\n"
                f"Minimum Stock Level: {min_stock} units\n"
                f"Unit Price: ${unit_price:.2f}\n"
                f"Status: {status}")
    
    except Exception as e:
        return f"Error checking inventory for {item_name}: {str(e)}"

@tool
def get_all_inventory_tool(request_date: str) -> str:
    """
    Get a complete list of all items currently in stock.
    
    Args:
        request_date: Date for the inventory snapshot (YYYY-MM-DD format)
    
    Returns:
        String listing all items with their stock levels
    """
    try:
        inventory_dict = get_all_inventory(request_date)
        
        if not inventory_dict:
            return "No items currently in stock."
        
        result = "CURRENT INVENTORY:\n" + "="*50 + "\n"
        for item, stock in sorted(inventory_dict.items()):
            result += f"• {item}: {stock} units\n"
        
        return result
    
    except Exception as e:
        return f"Error retrieving inventory: {str(e)}"

@tool
def order_stock_tool(item_name: str, quantity: int, request_date: str) -> str:
    """
    Place an order with the supplier to restock an item.
    
    Args:
        item_name: Name of the item to order
        quantity: Quantity to order
        request_date: Date of the order (YYYY-MM-DD format)
    
    Returns:
        String confirming the order and delivery date
    """
    try:
        # Get item price
        inventory_df = pd.read_sql("SELECT * FROM inventory WHERE item_name = :item", 
                                   db_engine, params={"item": item_name})
        
        if inventory_df.empty:
            return f"Cannot order '{item_name}' - not in our catalog."
        
        unit_price = float(inventory_df.iloc[0]["unit_price"])
        total_cost = quantity * unit_price
        
        # Check if we have enough cash
        current_cash = get_cash_balance(request_date)
        if current_cash < total_cost:
            return (f"INSUFFICIENT FUNDS: Order costs ${total_cost:.2f} but only "
                   f"${current_cash:.2f} available. Cannot place order.")
        
        # Create stock order transaction
        transaction_id = create_transaction(
            item_name=item_name,
            transaction_type="stock_orders",
            quantity=quantity,
            price=total_cost,
            date=request_date
        )
        
        # Get delivery date
        delivery_date = get_supplier_delivery_date(request_date, quantity)
        
        return (f"STOCK ORDER CONFIRMED\n"
                f"Transaction ID: {transaction_id}\n"
                f"Item: {item_name}\n"
                f"Quantity: {quantity} units\n"
                f"Total Cost: ${total_cost:.2f}\n"
                f"Expected Delivery: {delivery_date}")
    
    except Exception as e:
        return f"Error placing stock order: {str(e)}"

@tool
def search_quote_history_tool(search_terms: str, limit: int = 5) -> str:
    """
    Search historical quotes for similar requests.
    
    Args:
        search_terms: Comma-separated search terms (e.g., "glossy,ceremony,cardstock")
        limit: Maximum number of results to return
    
    Returns:
        String with historical quote information
    """
    try:
        terms_list = [term.strip() for term in search_terms.split(",")]
        quotes = search_quote_history(terms_list, limit)
        
        if not quotes:
            return "No matching historical quotes found."
        
        result = f"FOUND {len(quotes)} SIMILAR HISTORICAL QUOTES:\n" + "="*60 + "\n"
        
        for i, quote in enumerate(quotes, 1):
            result += f"\nQuote #{i}:\n"
            result += f"  Event Type: {quote.get('event_type', 'N/A')}\n"
            result += f"  Order Size: {quote.get('order_size', 'N/A')}\n"
            result += f"  Total Amount: ${quote.get('total_amount', 0):.2f}\n"
            result += f"  Explanation: {quote.get('quote_explanation', 'N/A')[:100]}...\n"
        
        return result
    
    except Exception as e:
        return f"Error searching quote history: {str(e)}"

@tool
def calculate_quote_tool(items_and_quantities: str, request_date: str) -> str:
    """
    Calculate a quote for requested items with bulk discounts.
    
    Args:
        items_and_quantities: Format "item1:qty1,item2:qty2" (e.g., "A4 paper:500,Cardstock:200")
        request_date: Date of the quote request (YYYY-MM-DD format)
    
    Returns:
        Detailed quote with pricing breakdown and discounts
    """
    try:
        # Parse items and quantities
        items_list = []
        for item_qty in items_and_quantities.split(","):
            parts = item_qty.split(":")
            if len(parts) == 2:
                items_list.append((parts[0].strip(), int(parts[1].strip())))
        
        if not items_list:
            return "Invalid format. Use: 'item1:qty1,item2:qty2'"
        
        quote_details = []
        subtotal = 0.0
        unavailable_items = []
        
        for item_name, quantity in items_list:
            # Check if item exists in inventory
            inventory_df = pd.read_sql("SELECT * FROM inventory WHERE item_name = :item", 
                                       db_engine, params={"item": item_name})
            
            if inventory_df.empty:
                unavailable_items.append(item_name)
                continue
            
            unit_price = float(inventory_df.iloc[0]["unit_price"])
            item_total = quantity * unit_price
            subtotal += item_total
            
            quote_details.append({
                "item": item_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "item_total": item_total
            })
        
        # Apply bulk discounts
        if subtotal >= 5000:
            discount_rate = 0.15  # 15% for orders over $5000
        elif subtotal >= 2000:
            discount_rate = 0.10  # 10% for orders over $2000
        elif subtotal >= 1000:
            discount_rate = 0.05  # 5% for orders over $1000
        else:
            discount_rate = 0.0
        
        discount_amount = subtotal * discount_rate
        total = subtotal - discount_amount
        
        # Format quote
        result = "QUOTE DETAILS:\n" + "="*60 + "\n"
        
        for detail in quote_details:
            result += (f"{detail['item']}: {detail['quantity']} units × "
                      f"${detail['unit_price']:.2f} = ${detail['item_total']:.2f}\n")
        
        result += "\n" + "-"*60 + "\n"
        result += f"Subtotal: ${subtotal:.2f}\n"
        
        if discount_rate > 0:
            result += f"Bulk Discount ({discount_rate*100:.0f}%): -${discount_amount:.2f}\n"
        
        result += f"TOTAL: ${total:.2f}\n"
        
        if unavailable_items:
            result += f"\nNOTE: The following items are not available: {', '.join(unavailable_items)}\n"
        
        return result
    
    except Exception as e:
        return f"Error calculating quote: {str(e)}"

@tool
def check_stock_availability_tool(items_and_quantities: str, request_date: str) -> str:
    """
    Check if requested items are available in sufficient quantities.
    
    Args:
        items_and_quantities: Format "item1:qty1,item2:qty2"
        request_date: Date to check availability (YYYY-MM-DD format)
    
    Returns:
        Availability status for each item
    """
    try:
        items_list = []
        for item_qty in items_and_quantities.split(","):
            parts = item_qty.split(":")
            if len(parts) == 2:
                items_list.append((parts[0].strip(), int(parts[1].strip())))
        
        result = "STOCK AVAILABILITY CHECK:\n" + "="*60 + "\n"
        all_available = True
        
        for item_name, quantity in items_list:
            stock_df = get_stock_level(item_name, request_date)
            current_stock = int(stock_df["current_stock"].iloc[0])
            
            if current_stock >= quantity:
                status = "✓ AVAILABLE"
            else:
                status = f"✗ INSUFFICIENT (only {current_stock} available)"
                all_available = False
            
            result += f"{item_name}: Requested {quantity}, {status}\n"
        
        result += "\n" + "-"*60 + "\n"
        result += "Overall Status: " + ("ORDER CAN BE FULFILLED" if all_available else "CANNOT FULFILL - INSUFFICIENT STOCK")
        
        return result
    
    except Exception as e:
        return f"Error checking availability: {str(e)}"

@tool
def create_sale_tool(items_and_quantities: str, total_price: float, request_date: str) -> str:
    """
    Finalize a sale by creating sales transactions and updating inventory.
    
    Args:
        items_and_quantities: Format "item1:qty1,item2:qty2"
        total_price: Total sale amount
        request_date: Date of the sale (YYYY-MM-DD format)
    
    Returns:
        Confirmation of the sale with transaction details
    """
    try:
        items_list = []
        for item_qty in items_and_quantities.split(","):
            parts = item_qty.split(":")
            if len(parts) == 2:
                items_list.append((parts[0].strip(), int(parts[1].strip())))
        
        # First check if all items are available
        for item_name, quantity in items_list:
            stock_df = get_stock_level(item_name, request_date)
            current_stock = int(stock_df["current_stock"].iloc[0])
            
            if current_stock < quantity:
                return (f"SALE FAILED: Insufficient stock for {item_name}. "
                       f"Requested: {quantity}, Available: {current_stock}")
        
        # Create sales transactions
        transaction_ids = []
        for item_name, quantity in items_list:
            # Get unit price
            inventory_df = pd.read_sql("SELECT * FROM inventory WHERE item_name = :item", 
                                       db_engine, params={"item": item_name})
            unit_price = float(inventory_df.iloc[0]["unit_price"])
            item_price = quantity * unit_price
            
            trans_id = create_transaction(
                item_name=item_name,
                transaction_type="sales",
                quantity=quantity,
                price=item_price,
                date=request_date
            )
            transaction_ids.append(trans_id)
        
        # Get delivery estimate
        total_quantity = sum(qty for _, qty in items_list)
        delivery_date = get_supplier_delivery_date(request_date, total_quantity)
        
        result = "SALE COMPLETED SUCCESSFULLY!\n" + "="*60 + "\n"
        result += f"Transaction IDs: {', '.join(map(str, transaction_ids))}\n"
        result += f"Total Amount: ${total_price:.2f}\n"
        result += f"Estimated Delivery: {delivery_date}\n"
        result += "\nItems Sold:\n"
        
        for item_name, quantity in items_list:
            result += f"  • {item_name}: {quantity} units\n"
        
        return result
    
    except Exception as e:
        return f"Error creating sale: {str(e)}"

@tool
def get_delivery_estimate_tool(quantity: int, request_date: str) -> str:
    """
    Get estimated delivery date based on order quantity.
    
    Args:
        quantity: Total quantity of items in the order
        request_date: Order date (YYYY-MM-DD format)
    
    Returns:
        Estimated delivery date
    """
    try:
        delivery_date = get_supplier_delivery_date(request_date, quantity)
        
        if quantity <= 10:
            timeframe = "same day"
        elif quantity <= 100:
            timeframe = "1 business day"
        elif quantity <= 1000:
            timeframe = "4 business days"
        else:
            timeframe = "7 business days"
        
        return f"Estimated Delivery: {delivery_date} ({timeframe})"
    
    except Exception as e:
        return f"Error estimating delivery: {str(e)}"

# ==================== MULTI-AGENT SYSTEM ====================

# Initialize the LLM model
api_key = os.getenv("UDACITY_OPENAI_API_KEY")
if not api_key:
    raise ValueError("UDACITY_OPENAI_API_KEY not found in environment variables")

model = LiteLLMModel(
    model_id="openai/gpt-4o-mini",
    api_key=api_key,
    api_base="https://openai.vocareum.com/v1"
)

# Create specialist agents

inventory_agent = ToolCallingAgent(
    tools=[check_inventory_tool, get_all_inventory_tool, order_stock_tool, get_delivery_estimate_tool],
    model=model,
    name="InventoryAgent",
    description="Specialist in inventory management, stock checking, and reordering supplies."
)

quoting_agent = ToolCallingAgent(
    tools=[search_quote_history_tool, calculate_quote_tool, check_inventory_tool],
    model=model,
    name="QuotingAgent",
    description="Specialist in generating competitive quotes based on historical data and current pricing."
)

sales_agent = ToolCallingAgent(
    tools=[check_stock_availability_tool, create_sale_tool, get_delivery_estimate_tool],
    model=model,
    name="SalesAgent",
    description="Specialist in finalizing sales transactions and order fulfillment."
)

# Create orchestrator agent
orchestrator_agent = ToolCallingAgent(
    tools=[],
    model=model,
    name="OrchestratorAgent",
    description="Main coordinator that analyzes requests and delegates to specialist agents.",
    managed_agents=[inventory_agent, quoting_agent, sales_agent]
)

def process_customer_request(request: str, request_date: str) -> str:
    """
    Process a customer request through the multi-agent system.
    
    Args:
        request: Customer's request text
        request_date: Date of the request (YYYY-MM-DD format)
    
    Returns:
        Response from the multi-agent system
    """
    # Enhanced prompt for the orchestrator
    system_prompt = f"""You are the Orchestrator Agent for Beaver's Choice Paper Company.
    
Your role is to analyze customer requests and coordinate with specialist agents:
- InventoryAgent: For checking stock, reordering supplies
- QuotingAgent: For generating price quotes
- SalesAgent: For finalizing orders and sales

Current date: {request_date}

IMPORTANT GUIDELINES:
1. For quote requests: Use QuotingAgent to search history and calculate quotes
2. For inventory questions: Use InventoryAgent to check stock levels
3. For order placement: Use SalesAgent to verify availability and create sales
4. If stock is low after a sale, use InventoryAgent to reorder
5. Always provide clear, professional responses to customers
6. Include relevant details like pricing, delivery dates, and availability

Analyze the following request and coordinate the appropriate agents to fulfill it:

{request}
"""
    
    try:
        response = orchestrator_agent.run(system_prompt)
        return str(response)
    except Exception as e:
        return f"Error processing request: {str(e)}"

# ==================== TEST EXECUTION ====================

def run_test_scenarios():
    """Execute test scenarios using the multi-agent system."""
    print("="*80)
    print("BEAVER'S CHOICE PAPER COMPANY - MULTI-AGENT SYSTEM")
    print("="*80)
    print("\nInitializing Database...")
    init_database(db_engine)
    
    try:
        quote_requests_sample = pd.read_csv("data/quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return
    
    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]
    
    print(f"\nInitial Financial State:")
    print(f"  Cash Balance: ${current_cash:,.2f}")
    print(f"  Inventory Value: ${current_inventory:,.2f}")
    print(f"  Total Assets: ${current_cash + current_inventory:,.2f}")
    print("\n" + "="*80)
    
    results = []
    
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")
        
        print(f"\n{'='*80}")
        print(f"REQUEST #{idx+1}")
        print(f"{'='*80}")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Order Size: {row['need_size']}")
        print(f"Request Date: {request_date}")
        print(f"Current Cash: ${current_cash:,.2f}")
        print(f"Current Inventory Value: ${current_inventory:,.2f}")
        print(f"\nCustomer Request:\n{row['request']}")
        print(f"\n{'-'*80}")
        print("Processing request through multi-agent system...")
        print(f"{'-'*80}\n")
        
        # Process request with date context
        request_with_date = f"{row['request']}\n\n[Request Date: {request_date}]"
        response = process_customer_request(request_with_date, request_date)
        
        # Update financial state
        report = generate_financial_report(request_date)
        new_cash = report["cash_balance"]
        new_inventory = report["inventory_value"]
        
        cash_change = new_cash - current_cash
        inventory_change = new_inventory - current_inventory
        
        print(f"\nAGENT RESPONSE:")
        print(f"{'-'*80}")
        print(response)
        print(f"{'-'*80}")
        
        print(f"\nFINANCIAL UPDATE:")
        print(f"  Cash Balance: ${new_cash:,.2f} (Change: ${cash_change:+,.2f})")
        print(f"  Inventory Value: ${new_inventory:,.2f} (Change: ${inventory_change:+,.2f})")
        print(f"  Total Assets: ${new_cash + new_inventory:,.2f}")
        
        current_cash = new_cash
        current_inventory = new_inventory
        
        results.append({
            "request_id": idx + 1,
            "request_date": request_date,
            "job": row['job'],
            "event": row['event'],
            "need_size": row['need_size'],
            "cash_balance": current_cash,
            "inventory_value": current_inventory,
            "response": response,
        })
        
        time.sleep(2)  # Rate limiting
    
    # Final report
    print(f"\n{'='*80}")
    print("FINAL FINANCIAL REPORT")
    print(f"{'='*80}")
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    
    print(f"Report Date: {final_date}")
    print(f"Final Cash Balance: ${final_report['cash_balance']:,.2f}")
    print(f"Final Inventory Value: ${final_report['inventory_value']:,.2f}")
    print(f"Total Assets: ${final_report['total_assets']:,.2f}")
    
    print(f"\nTop Selling Products:")
    for i, product in enumerate(final_report['top_selling_products'], 1):
        print(f"  {i}. {product['item_name']}: ${product['total_revenue']:,.2f} revenue")
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv("results/test_results.csv", index=False)
    print(f"\nResults saved to 'results/test_results.csv'")
    print(f"{'='*80}\n")
    
    return results

if __name__ == "__main__":
    results = run_test_scenarios()
