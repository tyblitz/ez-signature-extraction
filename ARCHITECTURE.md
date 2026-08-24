# EZ Project Architecture

## Folder Structure

```
EZ/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   ├── controllers/
│   │   └── middleware/
│   ├── processors/
│   ├── utils/
│   ├── models/
│   ├── tests/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── services/
│   │   └── router/
│   └── public/
├── docs/
├── temp/
├── output/
└── README.md
```

## Folder Purposes

### Root Level

| Folder/File | Purpose |
|-------------|---------|
| `backend/` | Contains all Python backend code for signature extraction logic |
| `frontend/` | Contains Vue 3 + Ionic frontend application |
| `docs/` | Project documentation, diagrams, and architectural decisions |
| `temp/` | Temporary storage for uploaded files and intermediate processing data |
| `output/` | Processed signature images and ZIP archives for download |

### Backend Structure

| Folder/File | Purpose |
|-------------|---------|
| `backend/api/routes/` | API endpoint definitions (REST routes) |
| `backend/api/controllers/` | Request handlers and business logic for each endpoint |
| `backend/api/middleware/` | Request/response middleware (validation, logging, CORS) |
| `backend/processors/` | Core processing modules: input_handler.py, pdf_processor.py, image_processor.py, signature_detector.py, background_remover.py, output_handler.py |
| `backend/utils/` | Shared utility functions and helpers |
| `backend/models/` | Data models and type definitions |
| `backend/tests/` | Unit and integration tests |
| `backend/main.py` | Application entry point and server initialization |

### Frontend Structure

| Folder/File | Purpose |
|-------------|---------|
| `frontend/src/components/` | Reusable Vue components (upload, preview, progress) |
| `frontend/src/views/` | Page-level Vue components and layouts |
| `frontend/src/services/` | API service calls to backend |
| `frontend/src/router/` | Vue Router configuration |
| `frontend/public/` | Static assets and index.html |

## Design Decisions

- Separation of concerns: API layer isolated from processing logic
- Modular processors allow independent development and testing
- Temp/output folders at root for easy access and cleanup
- Docs folder for versioned documentation alongside code
- Frontend follows standard Vue 3 application structure