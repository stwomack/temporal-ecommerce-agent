# Quick Start Guide

Get the Multi-Agent E-commerce Order Processing demo running in minutes!

## Prerequisites

- Python 3.9+
- OpenAI API key
- Temporal CLI (optional, for UI access)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Install Temporal CLI (optional):**
   ```bash
   # macOS
   brew install temporal
   
   # Or download from: https://docs.temporal.io/cli/installation
   ```

## Running the Demo

### Option 1: Full Demo (Recommended)
```bash
make demo
```

This will:
- Start Temporal server
- Start the worker
- Run the demo
- Clean up processes

### Option 2: Manual Steps

1. **Start Temporal server:**
   ```bash
   temporal server start-dev
   ```

2. **In another terminal, start the worker:**
   ```bash
   python -m src.worker
   ```

3. **In another terminal, run the demo:**
   ```bash
   python -m src.demo
   ```

4. **View Temporal UI (optional):**
   ```bash
   temporal web
   ```

## What You'll See

The demo processes 4 different order scenarios:

1. **Normal Order** - Successfully processed through all agents
2. **Suspicious Order** - Escalated to customer service for review
3. **Inventory Issue Order** - Handled by fulfillment agent
4. **Payment Issue Order** - Payment retry logic demonstrated

Each order showcases different agent handoffs and decision-making processes.

## Architecture Overview

```
Order Input → Order Intake Agent → Payment Agent → Fulfillment Agent → Customer Service Agent
     ↓              ↓                   ↓               ↓                    ↓
Temporal Workflow → Validate → Process Payment → Ship → Handle Exceptions
```

## Troubleshooting

- **OpenAI API errors:** Check your API key in `.env`
- **Temporal connection errors:** Ensure Temporal server is running
- **Import errors:** Run `pip install -e .` to install the package

## Next Steps

- Modify agent instructions in `src/agents/`
- Add new activities in `src/activities/`
- Create new workflows in `src/workflows/`
- Run tests with `make test` 