# Step 1: Base image
FROM python:3.10

# Step 2: Set working directory
WORKDIR /app

# Step 3: Copy all project files into container
COPY . .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
