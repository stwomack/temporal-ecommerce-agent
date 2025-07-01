import asyncio
import logging
import os
from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker
from src.activities.order_activities import (
    process_order_intake,
    process_payment,
    process_fulfillment,
    handle_customer_service,
    update_order_status,
    update_payment_status,
    update_shipping_status,
    send_notification,
    log_order_event
)
from src.workflows.order_processing import OrderProcessingWorkflow

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    client = await Client.connect(
        os.getenv("TEMPORAL_HOST", "localhost:7233"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default")
    )
    
    worker = Worker(
        client,
        task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "ecommerce-order-processing"),
        workflows=[OrderProcessingWorkflow],
        activities=[
            process_order_intake,
            process_payment,
            process_fulfillment,
            handle_customer_service,
            update_order_status,
            update_payment_status,
            update_shipping_status,
            send_notification,
            log_order_event
        ]
    )
    
    logger.info("Starting Temporal worker for e-commerce order processing...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main()) 