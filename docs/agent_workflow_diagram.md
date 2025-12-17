# Multi-Agent System Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CUSTOMER REQUEST                                │
│                     (Quote/Inventory/Order Inquiry)                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR AGENT                                  │
│  - Analyzes customer request                                            │
│  - Determines request type (inventory query, quote, order)              │
│  - Delegates to appropriate specialist agent                            │
│  - Coordinates multi-step workflows                                     │
│  - Formats final response to customer                                   │
└────────┬──────────────────┬──────────────────┬─────────────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   INVENTORY    │  │    QUOTING     │  │     SALES      │
│     AGENT      │  │     AGENT      │  │     AGENT      │
└────────┬───────┘  └────────┬───────┘  └────────┬───────┘
         │                   │                   │
         │                   │                   │
    ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
    │ TOOLS:  │         │ TOOLS:  │         │ TOOLS:  │
    │         │         │         │         │         │
    │ • Check │         │ • Search│         │ • Check │
    │   Stock │         │   Quote │         │   Stock │
    │         │         │   Hist. │         │   Avail.│
    │ • Check │         │         │         │         │
    │   Min   │         │ • Calc. │         │ • Create│
    │   Level │         │   Price │         │   Trans.│
    │         │         │         │         │         │
    │ • Order │         │ • Apply │         │ • Update│
    │   Stock │         │   Disc. │         │   Inven.│
    │         │         │         │         │         │
    │ • Check │         │ • Check │         │ • Check │
    │   Deliv.│         │   Inven.│         │   Deliv.│
    │   Date  │         │         │         │   Date  │
    └─────────┘         └─────────┘         └─────────┘
         │                   │                   │
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   DATABASE LAYER       │
                │                        │
                │  • Inventory Table     │
                │  • Transactions Table  │
                │  • Quotes Table        │
                │  • Quote Requests      │
                └────────────────────────┘
```

## Agent Responsibilities

### 1. Orchestrator Agent
**Purpose:** Central coordinator that routes requests and manages workflow
**Responsibilities:**
- Parse and understand customer requests
- Identify request type (inventory inquiry, quote request, order placement)
- Delegate to appropriate specialist agents
- Aggregate responses from multiple agents
- Format customer-facing responses
**Tools:** None (delegates to other agents)

### 2. Inventory Agent
**Purpose:** Manage stock levels and reordering
**Responsibilities:**
- Check current stock levels for items
- Assess if stock is below minimum threshold
- Place reorder requests with suppliers
- Provide delivery timeline estimates
**Tools:**
- `check_inventory_tool`: Uses `get_stock_level()` and `get_all_inventory()`
- `check_reorder_need_tool`: Compares stock vs min_stock_level
- `order_stock_tool`: Uses `create_transaction()` for stock_orders
- `get_delivery_date_tool`: Uses `get_supplier_delivery_date()`

### 3. Quoting Agent
**Purpose:** Generate competitive quotes for customer requests
**Responsibilities:**
- Search historical quotes for similar requests
- Calculate pricing based on quantity and item type
- Apply bulk discounts strategically
- Verify inventory availability
- Provide detailed quote explanations
**Tools:**
- `search_quotes_tool`: Uses `search_quote_history()`
- `calculate_quote_tool`: Computes pricing with discounts
- `check_inventory_for_quote_tool`: Uses `get_stock_level()`

### 4. Sales Agent
**Purpose:** Finalize transactions and update records
**Responsibilities:**
- Verify inventory availability for orders
- Create sales transactions
- Update inventory records
- Confirm delivery timelines
- Handle order fulfillment
**Tools:**
- `check_stock_availability_tool`: Uses `get_stock_level()`
- `create_sale_tool`: Uses `create_transaction()` for sales
- `confirm_delivery_tool`: Uses `get_supplier_delivery_date()`

## Data Flow

### Scenario 1: Inventory Query
```
Customer → Orchestrator → Inventory Agent → Database → Response
```

### Scenario 2: Quote Request
```
Customer → Orchestrator → Quoting Agent → [Search History + Check Inventory] → Response
```

### Scenario 3: Order Placement
```
Customer → Orchestrator → Sales Agent → [Check Stock + Create Transaction] → Response
                              ↓
                       Inventory Agent (if reorder needed)
```

### Scenario 4: Complex Request (Quote + Order)
```
Customer → Orchestrator → Quoting Agent → Generate Quote
                              ↓
                         Sales Agent → Process Order
                              ↓
                       Inventory Agent → Check/Reorder Stock
```

## Tool-to-Function Mapping

| Tool Name | Helper Functions Used | Purpose |
|-----------|----------------------|---------|
| check_inventory_tool | get_stock_level(), get_all_inventory() | Check current stock |
| check_reorder_need_tool | get_stock_level(), inventory table | Assess reorder needs |
| order_stock_tool | create_transaction(), get_supplier_delivery_date() | Place stock orders |
| search_quotes_tool | search_quote_history() | Find similar past quotes |
| calculate_quote_tool | get_stock_level(), paper_supplies list | Calculate pricing |
| check_stock_availability_tool | get_stock_level() | Verify order feasibility |
| create_sale_tool | create_transaction() | Record sales |
| get_cash_balance_tool | get_cash_balance() | Check available funds |
| generate_report_tool | generate_financial_report() | Financial reporting |
