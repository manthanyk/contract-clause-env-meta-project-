from setuptools import setup, find_packages

setup(
    name="contract-clause-env",
    version="1.0.0",
    description="A real-world contract clause review environment for AI agents",
    author="ManthanYk",
    packages=find_packages(include=["common", "common.*", "*"]),
    py_modules=["__init__", "models", "client", "inference"],
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=2.0.0",
        "openenv-core>=0.1.0",
        "openai>=1.0.0",
        "httpx>=0.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    python_requires=">=3.10",
)
