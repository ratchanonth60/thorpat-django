FROM node:alpine AS build

WORKDIR /app

# คัดลอกแค่ไฟล์ package.json เพื่อติดตั้ง dependencies
# เราจะไม่คัดลอก package-lock.json เพื่อป้องกันปัญหาเรื่องสถาปัตยกรรม
COPY package.json ./
COPY frontend/web/package.json ./frontend/web/

# ติดตั้ง dependencies
RUN npm install

# เปิด Port ของ Vite dev server
EXPOSE 5173
