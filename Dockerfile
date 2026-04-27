FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV TZ=Asia/Seoul
# 포트 설정 추가
EXPOSE 8501
# 실행 명령
CMD ["streamlit", "run", "app.py"]