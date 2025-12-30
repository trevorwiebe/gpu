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
- **Central Router**: FastAPI-based routing and load balancing
- **Host Software**: Docker-containerized inference engines (vLLM/TGI)
- **Web Dashboard**: React-based client and host interfaces
- **Database**: PostgreSQL for metrics, Redis for caching/sessions

### Infrastructure Stack
- **Backend**: Python/FastAPI, PostgreSQL, Redis
- **Frontend**: React
- **Host Platform**: Ubuntu with Docker
- **Inference Engine**: vLLM (primary), Text Generation Inference
- **Payments**: Stripe integration
- **Monitoring**: Custom health monitoring system

## Getting Started

### For Clients
1. Create account and generate API key
2. Add credits via Stripe integration
3. Use OpenAI-compatible endpoint in your application
4. Monitor usage and costs in dashboard

### For GPU Owners
1. Register host account
2. Run setup script on Ubuntu system
3. Select models based on hardware capabilities
4. Enable/disable processing via CLI
5. Track earnings and payouts in dashboard

## Model Support

Starting with popular open-source LLMs:
- Llama 3.1 (8B, 70B variants)
- Mistral (7B, Mixtral 8x7B)
- Qwen series
- Gemma models

**Note**: All models are carefully vetted for licensing compliance. Platform includes clear license information and attribution requirements.

## Security & Privacy

- Docker containerization for host isolation
- Standard API key management with revocation
- Client data processed on distributed hardware (transparency provided)
- Host verification and validation systems
- DDoS protection and rate limiting

## Pricing Model

- **Per-token pricing** following industry standards
- **Dynamic pricing** based on supply and demand per model
- **Batched billing** with configurable thresholds
- **Threshold-based payouts** for hosts

## Development

For detailed technical specifications, architecture decisions, and development roadmap, see [GUIDE.md](./GUIDE.md).

## Legal & Compliance

- Comprehensive Terms of Service for both clients and hosts
- Model license compliance and attribution requirements
- Client responsibility for license compliance at scale
- Data privacy and GDPR considerations

## Roadmap

### MVP Focus
- Single model support (Llama 3.1 8B)
- Invite-only host onboarding
- US-only geographic scope
- CLI-based host management
- Basic dashboards and billing

### Future Enhancements
- Multi-model support with advanced routing
- Web-based host management
- Geographic optimization
- Advanced analytics and fraud detection
- Image generation and other model types

---

*This platform aims to democratize AI processing by creating a fair marketplace that benefits both clients seeking affordable compute and GPU owners looking to maximize their hardware investments.*