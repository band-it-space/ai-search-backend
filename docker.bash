docker-compose down -v
docker system prune -a
docker-compose up --build
docker-compose up --build -d
docker-compose logs -f fastapi


curl https://api.openai.com/v1/assistants/asst_L2dinWmMc8orcVkSEtc3KwFZ \
  -H "Authorization: Bearer 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" \
  -H "OpenAI-Beta: assistants=v2" \
  -H "Content-Type: application/json"
