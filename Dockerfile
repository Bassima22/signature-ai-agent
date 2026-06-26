# 1. Use a lightweight Python 3.12 image
FROM python:3.12-slim

# 2. Set the working directory
WORKDIR /app

# 3. Install system tools needed for SQLite/Network
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 4. Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the project
COPY . .

# 6. Initialize a fresh database inside the container
RUN python database_setup.py

# 7. Open the port Gradio uses
EXPOSE 7860

# 8. Start the app
CMD ["python", "app.py"]