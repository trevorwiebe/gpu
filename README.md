# GPU Sharing Platform

A distributed compute platform that connects clients needing AI processing power with GPU owners looking to monetize their idle hardware.

## Overview

This platform bridges the gap between expensive closed-source AI models and cost-prohibitive hardware requirements by creating a marketplace for GPU compute power. Clients get simple API access to open-source models at competitive prices, while GPU owners earn revenue from their idle hardware.

## Problem & Solution

**The Problem:**
- AI processing demand is skyrocketing
- Closed-source models (OpenAI/Claude) are expensive
- Open-source alternatives require costly hardware
- GPU owners have idle time (nights, weekends) they can't monetize

**Our Solution:**
A platform that makes AI processing as simple as getting an API key, with supply/demand pricing that naturally undercuts major providers while incentivizing GPU owners to participate.

## Key Features

### For Clients
- 🔑 Simple API access compatible with OpenAI SDK
- 💰 Dynamic pricing cheaper than closed-source alternatives  
- 🔄 Support for popular open-source models
- 📊 Real-time usage dashboard and billing
- ⚡ No hardware requirements

### For GPU Owners
- 💵 Monetize idle GPU time
- 🎛️ Full control - choose models and availability
- 📈 Transparent earnings and demand analytics
- 🐳 Docker-based isolation and security
- 🔧 Simple setup via automated script

### Platform Features
- 🔄 Round-robin load balancing
- 💓 Health monitoring and failover
- 🔐 Model verification and hardware validation
- 💳 Automated billing and payouts
- 📊 Supply/demand pricing engine

## Technical Architecture

### Core Components
- **Central Router**: FastAPI-based routing and load balancing with Redis caching
- **Host Software**: Docker-containerized inference engines (vLLM/TGI)
- **Web Dashboard**: React/TypeScript frontend with Vite build system
- **Database**: Redis for caching, sessions, and real-time data

### Infrastructure Stack
- **Backend**: Python/FastAPI, Redis, cryptographic security utilities
- **Frontend**: React/TypeScript, Vite, RTK Query for state management
- **Host Platform**: Ubuntu with Docker
- **Inference Engine**: vLLM (primary), Text Generation Inference
- **Containerization**: Docker Compose orchestration
- **Build System**: Modern TypeScript/ESLint configuration

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Redis server
- Node.js (for frontend development)

### Quick Start
```bash
# Start all services
./scripts/startup.sh

# Add a new node
./scripts/add-node.sh

# View logs
./scripts/logs.sh

# Shutdown services
./scripts/shutdown.sh
```

### For Clients
1. Create account and generate API key
2. Use OpenAI-compatible completion endpoint
3. Monitor usage via React dashboard
4. Track completions and model performance

### For GPU Owners
1. Register host account via API
2. Run Docker containers using provided scripts
3. Configure models through web interface
4. Monitor node health and earnings

## API Endpoints

### Router Service
- `POST /completion` - OpenAI-compatible text completion
- `GET /health` - System health check
- `GET /users/me/node` - User node management
- `GET /users/me/library` - User model library

### Node Service
- `POST /generate` - Text generation endpoint
- `GET /info` - Node information and capabilities
- `POST /setup` - Model setup and configuration

## Model Support

Starting with popular open-source LLMs:
- Llama 3.1 (8B, 70B variants)
- Mistral (7B, Mixtral 8x7B)
- Qwen series
- Gemma models

**Note**: All models are carefully vetted for licensing compliance. Platform includes clear license information and attribution requirements.

## Development

### Backend Development
```bash
# Rebuild router
./scripts/rebuild-router.sh

# Rebuild nodes
./scripts/rebuild-nodes.sh

# Clear Redis cache
./scripts/clear_redis.sh

# Dump Redis data
./scripts/dump_redis.sh
```

### Frontend Development
```bash
cd front-end
npm install
npm run dev
```

The frontend features:
- TypeScript with strict type checking
- RTK Query for API state management
- Component-based architecture
- Real-time model and node management
- Responsive design with modern CSS

For detailed technical specifications, architecture decisions, and development roadmap, see [GUIDE.md](./GUIDE.md).

## Security & Privacy

- Docker containerization for host isolation
- Cryptographic utilities for secure communications
- Redis-based session management
- API key authentication with revocation
- Health monitoring and validation systems
- Rate limiting and DDoS protection

## Pricing Model

- **Per-token pricing** following industry standards
- **Dynamic pricing** based on supply and demand per model
- **Real-time completion tracking** with detailed metrics
- **Transparent cost monitoring** through dashboard

## Legal & Compliance

- Comprehensive Terms of Service for both clients and hosts
- Model license compliance and attribution requirements
- Client responsibility for license compliance at scale
- Data privacy and security considerations

## Roadmap

### Current Implementation
- FastAPI-based router with Redis backend
- React/TypeScript frontend with modern tooling
- Docker-based node management
- Real-time health monitoring
- Model library management
- OpenAI-compatible API endpoints

### Future Enhancements
- Advanced load balancing algorithms
- Geographic optimization
- Enhanced analytics and monitoring
- Automated scaling and deployment
- Image generation and other model types

---

*This platform aims to democratize AI processing by creating a fair marketplace that benefits both clients seeking affordable compute and GPU owners looking to maximize their hardware investments.*