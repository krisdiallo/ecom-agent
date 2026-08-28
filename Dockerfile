# aivis MCP server.
#
# Deliberately minimal: the tool is pure standard library, so there is nothing to
# install and no build step. No pip, no requirements file, no wheel — copying two
# files onto a slim Python base is the entire image.
FROM python:3.12-slim

# Required by the MCP registry to prove this image belongs to the published server.
LABEL io.modelcontextprotocol.server.name="io.github.krisdiallo/aivis"
LABEL org.opencontainers.image.source="https://github.com/krisdiallo/ecom-agent"
LABEL org.opencontainers.image.description="Check whether AI assistants can read and buy from your ecommerce store. Read-only."
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY aivis.py aivis_mcp.py LICENSE ./

# Never run as root: this server makes outbound HTTP requests to sites it does not
# control, and there is no reason for it to have more privilege than that needs.
RUN useradd --create-home --uid 10001 aivis
USER aivis

# Unbuffered, because stdout IS the JSON-RPC channel — buffering would stall every
# response until the pipe filled.
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python3", "/app/aivis_mcp.py"]
