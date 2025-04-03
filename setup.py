from setuptools import setup, find_packages

setup(
    name="themis",
    version="0.1.0",
    packages=find_packages(),
    scripts=["themis.py"],
    install_requires=[
        "PyPDF2",
        "requests",
        "tqdm",
        "colorama",
    ],
    author="Hunter Rose",
    # author_email="example@example.com",
    description="A comprehensive legal document analysis and defense generation system",
    keywords="legal, document analysis, defense generation, LLM, Ollama",
    url="https://github.com/HunterR0se/Themis",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "Topic :: Office/Business",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    package_data={
        "": ["questions.md"]
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "themis=themis:main"
        ]
    }
)
