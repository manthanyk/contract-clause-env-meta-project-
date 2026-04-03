from setuptools import setup, find_packages

setup(
    name="resource-allocation-env",
    version="1.0.0",
    description="A real-world RL environment for resource allocation optimization",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=2.0.0",
        "openenv-core>=0.1.0",
        "openai>=1.0.0",
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