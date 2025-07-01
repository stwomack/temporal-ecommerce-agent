# Multi-Agent E-commerce Order Processing Demo

This demo showcases building AI agents with Temporal and the OpenAI Agents SDK for a realistic e-commerce order processing pipeline.

## Overview

The demo implements a multi-agent system that processes e-commerce orders through four specialized agents:

1. **Order Intake Agent**: Validates order details and checks inventory
2. **Payment Agent**: Handles payment processing with retry logic
3. **Fulfillment Agent**: Coordinates shipping and tracking
4. **Customer Service Agent**: Handles exceptions requiring human intervention

This demonstrates OpenAI SDK's agent handoffs with Temporal's durability for business-critical workflows.

## Features

- Multi-agent workflow with intelligent handoffs
- Temporal durability for reliable order processing
- Realistic e-commerce scenarios with inventory and payment simulation
- Exception handling with human intervention
- Comprehensive logging and tracing

## Prerequisites

- Python 3.9+
- Temporal server running locally
- OpenAI API key

## Setup

1. Install dependencies:
```bash
pip install -e .
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

3. Start Temporal server (if not already running):
```bash
temporal server start-dev
```

## Usage

1. Start the worker:
```bash
python -m src.worker
```

2. Run the demo:
```bash
python -m src.demo
```

3. Monitor workflows in Temporal UI:
```bash
temporal web
```

## Project Structure

```
src/
├── agents/           # Agent definitions
├── workflows/        # Temporal workflows
├── activities/       # Temporal activities
├── models/          # Data models
├── worker.py        # Temporal worker
└── demo.py          # Demo runner
```

## Architecture

The system uses Temporal workflows to orchestrate the multi-agent process:

1. **Order Intake**: Validates order and checks inventory
2. **Payment Processing**: Handles payment with retry logic
3. **Fulfillment**: Manages shipping and tracking
4. **Customer Service**: Handles exceptions and escalations

Each step can handoff to specialized AI agents for decision-making while maintaining workflow durability.

## License

MIT 