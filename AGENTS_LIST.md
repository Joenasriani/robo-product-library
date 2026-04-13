AI AGENTS LIST

Status legend:
- planned
- specification
- testing
- ready
- live
- paused

1. Tender Analyzer GCC
- Type: Agent
- Status: testing
- Priority: high
- Folder: agents/tender_analyzer_gcc_product
- Port: 8000
- Purpose: Evaluate GCC tenders from text or uploaded files
- Features: multi-provider LLM, PDF upload, credit system, admin panel, analysis history, Stripe billing

2. Sales Outreach Agent
- Type: Agent
- Status: testing
- Priority: high
- Folder: agents/sales_outreach_agent
- Port: 8001
- Purpose: Research leads and generate tailored B2B outreach sequences for GCC/Middle East

3. Lead Research Agent
- Type: Agent
- Status: testing
- Priority: high
- Folder: agents/lead_research_agent
- Port: 8002
- Purpose: Research target companies, classify opportunities, and prepare structured lead intelligence

4. Enterprise RFP Response Assistant
- Type: Agent
- Status: testing
- Priority: high
- Folder: agents/enterprise_rfp_response_assistant
- Port: 8003
- Purpose: Parse RFP documents, extract requirements, and generate structured response sections

5. Social Content Ops Agent
- Type: Agent
- Status: testing
- Priority: high
- Folder: agents/social_content_ops_agent
- Port: 8004
- Purpose: Generate social media content calendars, post concepts, and captions for GCC brands

6. Robot Demo Video Generator
- Type: Agent
- Status: testing
- Priority: medium
- Folder: agents/robot_demo_video_generator
- Port: 8005
- Purpose: Generate storyboards, scene plans, and AI image prompt packs for robot demo videos

7. Claw Hub Installer Agent
- Type: Agent
- Status: testing
- Priority: medium
- Folder: agents/claw_hub_installer_agent
- Port: 8006
- Purpose: Guide installation and setup for robotics platforms with compatibility checks

8. Tender Monitoring Agent
- Type: Agent
- Status: testing
- Priority: medium
- Folder: agents/tender_monitoring_agent
- Port: 8007
- Purpose: Monitor tender opportunities, match to company criteria, generate prioritized alert reports

9. AI Agent Download Center
- Type: Agent
- Status: testing
- Priority: high
- Folder: agents/ai_agent_download_center
- Port: 8008
- Purpose: Entitlement-based download center for AI agent products; catalog, access control, delivery

10. Protocol Marketplace Agent
- Type: Agent
- Status: testing
- Priority: very_high
- Folder: agents/protocol_marketplace_agent
- Port: 8009
- Purpose: Full marketplace for robot behavior protocol packs — catalog, inquiry, purchase, delivery

11. GCC Localization Packs
- Type: Protocol
- Status: ready
- Priority: high
- Folder: protocols/gcc_localization_packs
- Countries:
  - uae
  - saudi
  - qatar
  - kuwait
  - bahrain
  - oman
- Purpose: Cultural, etiquette, privacy, and interaction logic for robot deployment in GCC contexts

12. Core Skill Library
- Type: Skills
- Status: active
- Priority: high
- Folder: skills/
- Categories:
  - core
  - control
  - agent
  - rag
  - llmops
  - orchestration
  - execution
  - business
- Purpose: Reusable AI building blocks for all agents and protocol systems

Next priorities:
1. Connect Stripe payment to each agent's billing flow
2. Wire Protocol Marketplace to actual downloadable files in protocols/products/
3. Add CI/CD pipeline configuration
4. Add automated test suites for each agent
5. Deploy to RoboMarket production infrastructure
