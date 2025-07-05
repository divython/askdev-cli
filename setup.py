from setuptools import setup, find_packages

setup(
    name="askdev",
    version="1.0.0",
    description="Android Error CLI Assistant",
    author="askdev contributors",
    packages=find_packages(),
    py_modules=["app"],
    install_requires=[
        "typer[all]",
        "python-dotenv",
        "requests",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "askdev=app:run_main"
        ]
    },
    include_package_data=True,
    package_data={"": ["error_db.json"]},
    python_requires=">=3.7",
)
