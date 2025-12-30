# GPU Sharing Platform - Project Document

## Problem Statement

Demand for AI data processing is increasing dramatically. Current options use expensive closed source models. There are open source models that are just as good as the closed source models, but obtaining proper hardware to run them is cost prohibitive.

With training and hobby GPU rigs, there is downtime during the night or on the weekend. During this time the GPUs could be used to make additional money for the owners.

This app brings together the people needing easy AI data processing and people who own GPUs and would like to make additional money.

---

## Value Proposition

**For Clients:**
- Simple API access like OpenAI/Claude
- Cheaper pricing through distributed compute
- Support for open-source models
- No hardware requirements

**For Hosts:**
- Monetize idle GPU time
- Choose which models to run
- Retain control when they want to run
- Transparent earnings dashboard

**Platform Differentiator:**
The goal is extreme simplicity - clients think "I need an API key for AI processing in my web app" and come here to get it. Supply/demand pricing (like Uber disrupting taxis) will naturally make this cheaper than OpenAI/Claude while incentivizing hosts to join.

---

## Development & Automation

### CI/CD Pipeline
The project includes automated documentation updates through GitHub Actions. When code changes are pushed to the main branch, an intelligent system powered by Claude AI automatically reviews the changes and updates this README as needed to reflect new features, API changes, or setup instructions.

**Workflow Features:**
- Automatic detection of significant changes requiring documentation updates
- AI-powered commit message generation for documentation changes
- Seamless integration with existing development workflow
- Maintains documentation consistency and accuracy

---

## Core Requirements

### Client Requirements
- Performance comparable to leading AI providers
- 100% reliability expectation
- Lower pricing than closed-source alternatives
- User-friendly web interface matching OpenAI/Claude quality

### Host Requirements
- Hardware must meet minimum requirements per model
- Ability to choose which models to run
- Ability to stop processing and reclaim GPUs for personal workload
- Network must meet minimum performance standards
- Simple setup process via script

---

## Pricing & Economics
### All pricing and economics is for MVP and later

### Pricing Model
- **Standard**: Price per token (industry standard)
- **Mechanism**: Dynamic pricing based on supply and demand per model
- **Platform Fee**: TBD (not critical for MVP)

### Supply/Demand Dynamics
- Popular models will initially cost more
- Higher prices attract more hosts to run that model
- Increased supply drives prices down
- Hosts can see earnings data by model to make investment decisions
- Hosts can upgrade hardware to run higher-demand, higher-earning models

### Economic Incentives
- Pricing will naturally settle at a point cheaper than OpenAI/Claude (due to utilizing idle consumer hardware)
- Hosts earn revenue during otherwise idle time (nights, weekends)
- Target: Make it worthwhile even for small earnings (e.g., $2/night on idle GPU)

---

## Technical Architecture

### Request Routing & Load Balancing

**Routing Strategy:**
- Round-robin distribution among available hosts running the requested model
- Central routing system maintains registry of available hosts and their models

**GPU Parallelization:**
- GPUs can process multiple requests in parallel
- When all hosts are busy, requests continue but return data slower (no hard queuing/failure needed initially)

**Host Availability Management:**
- Hosts can disable processing via CLI (MVP) or web interface (future)
- When disabled:
  1. In-flight requests complete processing
  2. Host finishes current work
  3. System publishes to central router that node is unavailable
  4. New requests stop being routed to that host
- Prevents impact on reliability while giving hosts full control

### Quality Control & Verification

**Model Verification System:**
- Service on host connects to central routing system
- Reports: health status, models running, hardware specs
- Performs random validation requests to verify model authenticity
- Prevents hosts from running smaller/faster models and claiming premium ones

**Hardware Requirements:**
- Checked during initial setup script
- Script validates:
  - Available VRAM
  - GPU compute capability
  - Minimum tokens/second for selected model(s)
- Setup only completes if hardware meets requirements for chosen models

**Network Requirements:**
- Monitored via central routing heartbeat system
- Continuous tracking of:
  - Upload/download speeds
  - Latency
  - Connection stability

---

## Reliability & SLA

### Client Expectations
- **Target**: 100% reliability from client perspective
- System must handle host failures gracefully

### Host Flexibility
- Easy for hosts to take machines in/out of service
- No rigid uptime commitments (this is the platform's unique value)

### Failure Handling - Work in progress
When a host goes offline mid-request:
- Nodes will send heartbeats to central router, if router does not get a heartbeat it's removed from the pool
- If the requests fails or times out (short timeout), the central router will mark node as down and try a new node
- The node that failed to process will not be paid

---

## Security & Trust

### Data Privacy - Work in progress
**Client data is processed on untrusted consumer hardware**
- Clients will understand the architecture and be told how this system works
- Hosts will run in a docker container and every effort will be made to isolate from environment
- The platform is willing to forfeit a little privacy for lower processing costs
- New hosts will be briefly vetted

### Host Verification - Work in progress
- Setup script will make sure no other docker container is running
- During setup, the host will sign into their host account

### API Security
- Standard API key management
- Key revocation capability
- **Rate Limiting**: Prefer no limits (charge by usage), but may be necessary if demand exceeds supply
- DDoS protection

---

## Payment Processing

### Client Billing
- **Method**: Batched billing
- **Trigger**: When balance drops below threshold (client-configurable)
- **Recharge**: Client sets recharge amount
- **Processor**: Likely Stripe (industry standard)

### Host Payouts
- **Frequency**: When earnings hit threshold (not time-based)
- **Minimum Payout**: Required to avoid micro-transactions

---

## Technical Stack

### Infrastructure Components Needed

**Central Hub Must Handle:**
- Authentication for clients and hosts
- Request routing
- Health monitoring of hundreds/thousands of hosts
- Bidirectional payment processing
- Usage metrics storage
- Real-time dashboards for both clients and hosts

**Backend or Router:**
- API Framework: Python/FastAPI
- Database: PostgreSQL
- Message Queue: Redis
- Caching: Redis for session management, routing tables
- Monitoring: Prometheus + Grafana? Datadog? Custom? - Work in progress

**Host Software:**
- Platform: Ubuntu only (best GPU support)
- Containerization: Docker
- Inference Engine: vLLM? Text Generation Inference? Ollama? LMDeploy? - Work in progress (maybe vLLM)
  - **vLLM**: High performance, production-ready, good for serving
  - **TGI**: HuggingFace native, well-supported
  - **Ollama**: Simple, might be too abstracted for your needs
- Auto-updates: Script should auto-update (security, features, bug fixes)

**Frontend:**
- Client dashboard: React
- Host dashboard: Same stack as client dashboard, React
- When signing in, if the user is attached to both, give an option to show which dashboard they want

---

## Model Selection & Licensing

### Initial Scope
- **Model Types**: LLMs only (MVP)
- **Model Selection**: Popular open-source models only

**Popular Models to Consider:**
- Llama 3.1 (8B, 70B variants)
- Mistral (7B, Mixtral 8x7B)
- Qwen
- Gemma

### Model Licensing

**🚨 CRITICAL UNDERSTANDING REQUIRED:**

Not all "open source" models are truly open source or allow unrestricted commercial use. This is a complex legal landscape that could expose your platform to liability.

#### Common License Types

**1. Permissive Licenses (✅ Safe for your platform)**
- **Apache 2.0**: Allows free use, modification, and distribution for any purpose including commercial use
- **MIT**: Similar to Apache 2.0 but simpler, fewer requirements
- Examples: Mistral 7B, Falcon, MPT-7B, many EleutherAI models

**2. Custom/Restricted Licenses (⚠️ Requires careful review)**
- **Llama License**: Free for commercial use UNLESS you have over 700 million monthly active users, then you need special permission from Meta
  - Must display "Built with Meta Llama 3" prominently on website/UI
  - Cannot use to improve competing LLM models
  - Not technically "open source" by OSI definition due to restrictions
- **Gemma License**: Similar restrictions (100M user limit)
- **Qwen License**: Restrictions on outputs being used to train other models

**3. Research-Only Licenses (❌ Cannot use)**
- Some models explicitly prohibit commercial use
- Example: Some Cohere models, certain fine-tunes built on restricted base models

#### The Derivative Model Problem

**CRITICAL WARNING:** Models fine-tuned on restricted base models inherit those restrictions - for example, Vicuna shows Apache 2.0 license but is built on LLaMA, making it research-only despite the misleading license label

**For your platform:** You must verify BOTH the model license AND the base model license if it's a fine-tune.

#### Specific Implications for Your Platform

**Your platform has TWO relationships with licenses:**

1. **You (the platform) using the models**: You're generally safe under Llama license since you won't hit 700M users
2. **Your clients' usage**: This is where it gets tricky

**Example scenario:**
- Client builds app using your platform with Llama 3
- Client's app grows to 700M+ users
- **Who's liable?** Unclear - could be client, could be you as intermediary

**Recommendation:** Terms of Service must clearly state:
- Client is responsible for license compliance
- Client must verify model licenses suit their use case
- Platform provides models "as available" with no warranty of license compliance

#### Attribution Requirements

Even permissive licenses often require:
- Displaying license text with distributions
- Attribution notices
- **For your platform**: You're not distributing models, hosts are running them, but check if inference-as-a-service counts as distribution

#### Action Items Before Launch

**Legal Protection:**
1. ✅ Consult with IP lawyer about your specific use case
2. ✅ Draft Terms of Service that transfers license compliance responsibility to clients
3. ✅ Create clear documentation about which models have which restrictions
4. ✅ Add disclaimers that clients must verify licenses for their scale

**Technical Protection:**
1. ✅ Display license information prominently for each model in your dashboard
2. ✅ Require clients to acknowledge license terms when selecting a model
3. ✅ Consider blocking Llama models for clients approaching 700M MAU (if detectable)

**For MVP:**
- Start with 1-2 models with clearest licenses (Apache 2.0)
- Add restricted models (like Llama) in phase 2 with proper legal framework
- Document everything clearly for hosts and clients

### Host Model Selection
- Hosts can view popularity and earnings by model
- Dashboard shows which models are in highest demand
- Hosts make investment decisions (upgrade hardware for profitable models)
- System shows hosts which models their hardware can support

---

## MVP Scope

### Critical MVP Questions

1. **Initial Model Coverage:**
   - Start with single model (e.g., Llama 3.1 8B)

2. **Host Onboarding:**
   - Invite-only initially

3. **Geographic Scope:**
   - US-only initially
  

### MVP Feature Set

**Client Features (MVP):**
- Account creation/authentication
- API key generation
- Basic usage dashboard (tokens processed, cost)
- Credit card connection (Stripe)
- Batched billing with configurable threshold
- API endpoint compatible with OpenAI SDK format (for easy switching)

**Host Features (MVP):**
- Account creation/authentication  
- Ubuntu setup script
- CLI to enable/disable processing
- Connection to central hub (heartbeat, health reporting)
- Model selection and download from HuggingFace
- Automated hardware/network validation
- Basic earnings dashboard
- Payout threshold configuration

**Platform Features (MVP):**
- Central routing service
- Round-robin load balancing
- Health monitoring and node registry
- Random validation requests
- Usage tracking and billing calculation
- Basic admin dashboard

**Explicitly Out of Scope for MVP:**
- Web interface for host management (CLI only)
- Advanced analytics
- Image generation, STT, or other model types
- Geographic routing optimization
- Multiple redundant requests
- Advanced fraud detection

---

## Major Open Questions & Risks

### Technical Risks
1. **Latency**: Consumer internet connections may cause high latency vs data centers

### Business/Legal Risks  
1. **Liability**: Who's responsible if a host generates illegal content?
2. **Data breaches**: If client data is stolen from a host's machine?
3. **Tax compliance**: Complex with international hosts/clients
4. **Payment fraud**: Stolen credit cards, chargeback abuse
5. **Model licensing**: Unknowingly violating license terms

### Market Risks
1. **Competition**: RunPod, Vast.ai, Together AI already exist - what's your unfair advantage?
2. **Cold start problem**: Need hosts before clients, need clients before hosts
3. **Pricing pressure**: If too cheap, hosts won't participate; if too expensive, clients won't use it
4. **Reliability perception**: Consumer hardware stigma vs enterprise solutions

### Operational Risks
2. **Fraud detection**: Bad hosts, bad clients, payment fraud
3. **Scaling infrastructure**: Can your central hub handle 10x, 100x growth?

---

## Questions for You

1. **What's your technical background?** Can you build this yourself, or do you need to recruit a technical co-founder/team?
- I'm very technical and do not have too much worry about building this.

2. **Do you have any committed hosts?** Friends with GPUs willing to beta test?
- First, I'm going to use Vast.ai for hosts initially.  Once I have a prototype, I'll reach out to other developers via email and see if they are willing to test

4. **What's your go-to-market strategy?** How will you acquire your first 100 clients? First 100 hosts?
- Once I have a prototype, (host on vast.ai), I start reaching out to other developers and see if they want to use it for free
- Create a sub-reddit and discord server

5. **Have you used the existing competitors?** (Vast.ai, Together AI, Replicate) - what do they do poorly that you can do better?
- No of these market to the developer in quite the way I want to. Developer says "I need to add AI processing to my app.  Here is a good cheap alternative to OpenAi/Claude"

6. **Are you committed to the supply/demand pricing model?** This adds significant complexity vs fixed pricing.
- Yes, this is an integral part of the design

---

## Resources & Research Needed

**Technical Research:**
- [ ] Deep dive into vLLM, TGI, and other inference engines
- [ ] Study existing distributed compute platforms' architectures
- [ ] Research GPU sharing protocols and best practices
- [ ] Investigate model licensing for commercial use

**Legal Research:**
- [ ] Consult lawyer on platform liability
- [ ] Research contractor vs employee classification
- [ ] International tax implications
- [ ] Terms of service for both hosts and clients
- [ ] GDPR, CCPA, and other data privacy compliance

**Market Research:**
- [ ] Competitive analysis: Vast.ai, Together AI, Replicate, RunPod
- [ ] Survey potential hosts: what earnings threshold makes it worthwhile?
- [ ] Survey potential clients: what price point makes them switch from OpenAI?
- [ ] Analyze current market pricing ($/token by model)

**Financial Planning:**
- [ ] Infrastructure costs projection
- [ ] Customer acquisition cost estimates  
- [ ] Unit economics model
- [ ] Runway calculation

---

*This document should be treated as a living document and updated as decisions are made and the project evolves.*