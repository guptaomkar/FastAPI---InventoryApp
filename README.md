# FastAPI---InventoryApp
🧾 Inventory Management Application
A full-stack Inventory Management System built using ReactJS (frontend) and FastAPI (backend) with MongoDB as the database.
This application allows users to manage product details — including adding, updating, deleting, and viewing products — with real-time synchronization between the UI and the database.

🚀 Key Features

📦 Product Management: Add, edit, view, and delete products with unique product IDs.

🔍 Search & Filter: Quickly search and sort products by ID, name, description, price, or quantity.

🗄️ MongoDB Integration: Uses an asynchronous MongoDB connection via Motor for efficient CRUD operations.

⚙️ FastAPI Backend: Provides high-performance REST APIs with CORS-enabled endpoints.

💻 ReactJS Frontend: Interactive, responsive UI built with hooks and real-time API integration.

🔐 Custom Primary Key Logic: Uses manual id field as the unique key (not MongoDB’s default _id).

🧠 Smart Initialization: Auto-inserts initial data only if the collection is empty.

🧰 Tech Stack

Frontend: ReactJS, Axios, Material UI (or your UI library)

Backend: FastAPI (Python)

Database: MongoDB (using motor async driver)

Other Tools: Pydantic, CORS Middleware, Uvicorn
