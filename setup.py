from setuptools import setup, find_packages

setup(
    name="czech-anonymization-platform",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "spacy==3.5.3",
        "presidio-analyzer==2.2.32",
        "presidio-anonymizer==2.2.32",
        "streamlit==1.22.0",
        "numpy==1.23.5",
    ],
    extras_require={
        "dev": ["pytest==7.3.1"],
    },
    python_requires=">=3.8,<3.12",
)
