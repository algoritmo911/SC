# Sapiens Coin (SC) Project

Welcome to the Sapiens Coin (SC) project repository. This project aims to build a decentralized platform focusing on knowledge sharing, processing, and valuation.

## Overview

Sapiens Coin (SC) is an initiative to create a system where knowledge itself is a fundamental asset. The project involves developing modules for:

*   **Knowledge Representation**: Defining and storing units of knowledge.
*   **Knowledge Processing**: Generating and linking knowledge units, including AI-driven mechanisms.
*   **API Services**: Providing interfaces for interacting with the knowledge base and its related services.
*   **Decentralized Aspects**: Exploring blockchain and distributed technologies for trust and value.

The core idea is to prepare a robust system ready for future upgrades, including potential quantum processing capabilities and immersive VR/AR experiences.

## 🌍 Sapiens Coin Roadmap (2024–2029)

[Полная дорожная карта SC](docs/roadmap_2024_2029.md)

## Modules & Structure

The project is currently organized into several key directories:

*   `sc/`: Contains the core Sapiens Coin application logic.
    *   `sc/models.py`: Data models, including `KnowledgeUnit`.
    *   `sc/services/`: Business logic, such as `ku_generator.py` for Knowledge Unit generation, `flowshield.py` for rate limiting, and `ku_graph.py` for managing links between KUs.
    *   `sc/api/`: FastAPI endpoints for `knowledge.py` (KU creation/retrieval) and `graph.py` (KU linking).
*   `tests/`: Unit and integration tests for the application.
    *   `tests/services/`: Tests for service-layer modules.
    *   `tests/api/`: Tests for API endpoints.
*   `docs/`: Project documentation, including the detailed roadmap.

## Getting Started

(Instructions for setup, running the application, and contributing will be added here as the project matures.)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*This README provides a high-level overview. For detailed tasks and architectural decisions, please refer to the project's issues, commit history, and the Sapiens Coin Roadmap.*
