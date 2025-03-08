# Proxyception

This repository contains a simple Python TCP proxy that establishes a CONNECT tunnel through a Squid proxy server to a backend host. It is designed to run in a Docker container and is configurable using environment variables. The proxy transparently forwards data between the client and the backend server, making it suitable for handling HTTP, plain TCP streams, WebSockets, or any other protocol running over TCP.

## Features

- **CONNECT Tunnel:** Establishes a tunnel via a Squid proxy server.
- **Protocol Agnostic:** Works on the TCP layer so it supports HTTP, WebSockets, streaming, etc.
- **Environment Configurable:** All host and port configurations are set via environment variables.
- **Docker Ready:** Includes a Dockerfile to build a container image for easy deployment.

## Getting Started

### Prerequisites

- Python 3.9 or later
- Docker/Podman (if you want to run it in a container)
- A running Squid proxy that accepts CONNECT requests on the configured port

### Environment Variables

The proxy is configurable via the following environment variables:

| Variable      | Description                                             | Default Value   |
|---------------|---------------------------------------------------------|-----------------|
| `LISTEN_HOST` | The IP address on which the proxy server listens.     | `0.0.0.0`       |
| `LISTEN_PORT` | The port on which the proxy server listens.           | `8888`          |
| `SQUID_HOST`  | The Squid proxy server's IP address.                  | `192.168.1.244` |
| `SQUID_PORT`  | The Squid proxy server's port.                        | `8080`          |
| `TARGET_HOST` | The backend server's IP address.                      | `10.0.0.100`    |
| `TARGET_PORT` | The backend server's port.                            | `3000`          |

### Running Locally

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name

2. **Run the Proxy:**
This project is self-contained with only Python standard libraries. You can run the proxy directly:

    ```bash
    python proxy.py

3. **Test the Proxy:**
Use a tool like `curl` to test if the CONNECT tunnel is established properly:

    ```bash
    curl -x http://localhost:8888 -p -v http://10.0.0.100:3000

### Running with Docker

1. **Build the Docker image:**

   ```bash
   docker build -t my-proxy .

2. **Run the Docker container:**
Replace the environment variables as needed:

    ```bash
    docker run -d -p 8888:8888 \
    -e LISTEN_HOST="0.0.0.0" \
    -e LISTEN_PORT="8888" \
    -e SQUID_HOST="192.168.1.244" \
    -e SQUID_PORT="8080" \
    -e TARGET_HOST="10.0.0.100" \
    -e TARGET_PORT="3000" \
    --name my-proxy-container my-proxy

3. **Verify the Container:**
Check the container logs to ensure the proxy is running:

    ```bash
    docker logs my-proxy-container

### How It Works

- CONNECT Request: When a client connects to the proxy, the Python script establishes a TCP connection to the Squid proxy server. It then sends a CONNECT request in the following format:

    ```ruby
    CONNECT <TARGET_HOST>:<TARGET_PORT> HTTP/1.1
    Host: <TARGET_HOST>:<TARGET_PORT>
    Proxy-Connection: Keep-Alive
  
- Tunnel Establishment: If Squid responds with 200 Connection established, the tunnel is open and the script begins forwarding all traffic between the client and the backend server.
- Transparent Data Forwarding: The proxy is protocol-agnostic, meaning it simply relays bytes in both directions without interpreting the application-level protocol. This ensures compatibility with HTTP, WebSockets, streaming data, etc.

### Troubleshooting

- Squid Connection Issues:
If you see an error message like "Error: Squid did not establish the connection," verify that:
    - The Squid proxy is running and reachable on the configured IP and port.
    - The Squid configuration allows CONNECT requests to the specified `TARGET_HOST` and `TARGET_PORT`.
- Environment Variable Misconfiguration:
Ensure all necessary environment variables are set correctly if the proxy is not behaving as expected.

### License
This project is licensed under the MIT License.