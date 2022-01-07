docker run -d \
  -p 5222:5222 \
  -v $(pwd)/prosody/config/:/etc/prosody/:ro \
  -v $(pwd)/prosody/certs/:/var/lib/prosody \
  prosody/prosody
