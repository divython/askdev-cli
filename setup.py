from setuptools import setup

setup(
    name="askdev",
    version="0.1.0",
    py_modules=["app"],
    install_requires=[
        "typer[all]",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "askdev=app:run_main"
        ]
    },
    author="Divyanshu",
    author_email="divyanshu@example.com",
    description="Android Error CLI Assistant: Explain and fix Android errors from your terminal.",
    long_description=open("README.md").read() if __import__('os').path.exists('README.md') else "",
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)
