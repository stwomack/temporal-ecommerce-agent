from setuptools import setup, find_packages

setup(
    name="temporal-ecommerce-agent",
    version="0.1.0",
    description="Multi-Agent E-commerce Order Processing with Temporal and OpenAI Agents SDK",
    author="Demo Developer",
    author_email="demo@example.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "temporalio>=1.5.0",
        "openai-agents>=0.1.0",
        "pydantic>=2.0.0",
        "httpx>=0.24.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "temporal-ecommerce-worker=src.worker:main",
            "temporal-ecommerce-demo=src.demo:run_demo",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 