# **SuperApp System Architecture Diagrams**

This document contains the Mermaid-based diagrams for the SuperApp project, providing visual representations of the system architecture, component interactions, and data flows.

## **1. Overall System Architecture**

```mermaid
flowchart TD
    User["User/Client"] --> FE["Super App Frontend\n(React/Next.js with TypeScript)"]
    FE --> APG["API Gateway\n(Express.js/FastAPI)"]
    APG --> Jobs["Job Preparation\nMicroservice"]
    APG --> Learn["Learning Assistant\nMicroservice"]
    APG --> Chat["Chatbot\nMicroservice"]
    APG --> Resume["Resume Builder\nMicroservice"]
    APG --> More["... Other\nMicroservices"]
    
    Jobs --> DL["Data Layer\n(MongoDB, PostgreSQL, Redis)"]
    Learn --> DL
    Chat --> DL
    Resume --> DL
    More --> DL
    
    DL --> AI["AI Services & Integrations\n(Gemini API, OpenAI, Local LLMs)"]
    AI --> Ext["External API Integrations\n(LinkedIn, LeetCode, GitHub, etc)"]
    
    classDef frontend fill:#f9f,stroke:#333,stroke-width:2px
    classDef gateway fill:#bbf,stroke:#333,stroke-width:2px
    classDef microservice fill:#dfd,stroke:#333,stroke-width:2px
    classDef data fill:#ffd,stroke:#333,stroke-width:2px
    classDef ai fill:#ddf,stroke:#333,stroke-width:2px
    classDef external fill:#fdd,stroke:#333,stroke-width:2px
    
    class User,FE frontend
    class APG gateway
    class Jobs,Learn,Chat,Resume,More microservice
    class DL data
    class AI ai
    class Ext external
```

## **2. AI-Driven Job Preparation Assistant**

```mermaid
flowchart TD
    DC["LinkedIn Data Collection\n(Profile & Content Analysis)"] --> CO["Content Optimization Engine\n(Gemini API-powered)"]
    CO --> SEO["SEO & Engagement Analysis\n(RAG-based Recommendation)"]
    SEO --> FB["User Feedback & Ranking\n(A/B Testing for Content)"]
    
    classDef collection fill:#bbf,stroke:#333,stroke-width:2px
    classDef engine fill:#ffd,stroke:#333,stroke-width:2px
    classDef analysis fill:#dfd,stroke:#333,stroke-width:2px
    classDef feedback fill:#fdb,stroke:#333,stroke-width:2px
    
    class DC collection
    class CO engine
    class SEO analysis
    class FB feedback
```

## **3. AI-Enhanced LeetCode Learning Assistant**

```mermaid
flowchart TD
    GQL["GraphQL Data Scraper\n(LeetCode Problem Collector)"] --> UC["User Comprehension Engine\n(Adaptive Learning Model)"]
    UC --> MSE["Multi-Mode Solution Explorer\n(Tiered Explanation System)"]
    MSE --> LRG["Learning Records Generator\n(README & Note Creation)"]
    
    classDef scraper fill:#bbf,stroke:#333,stroke-width:2px
    classDef engine fill:#ffd,stroke:#333,stroke-width:2px
    classDef explorer fill:#dfd,stroke:#333,stroke-width:2px
    classDef generator fill:#fdb,stroke:#333,stroke-width:2px
    
    class GQL scraper
    class UC engine
    class MSE explorer
    class LRG generator
```

## **4. Local API-Based Chatbot**

```mermaid
flowchart TD
    MM["Model Manager\n(Ollama, Gemini, OpenAI)"] --> KM["API Key Manager\n(Quota Distribution System)"]
    KM --> CM["Context Management\n(Chat History & Personalized\nResponse Generation)"]
    CM --> UI["Web UI\n(Mobile & Desktop Interface)"]
    
    classDef manager fill:#bbf,stroke:#333,stroke-width:2px
    classDef key fill:#ffd,stroke:#333,stroke-width:2px
    classDef context fill:#dfd,stroke:#333,stroke-width:2px
    classDef ui fill:#fdb,stroke:#333,stroke-width:2px
    
    class MM manager
    class KM key
    class CM context
    class UI ui
```

## **5. AI Resume & GSoC Tracking**

```mermaid
flowchart TD
    DA["Data Collection Agents\n(Profile & Activity Crawler)"] --> RE["Persona-Based Resume Engine\n(Job-Specific Resume Gen)"]
    RE --> PDF["PDF Generator\n(Markup-Based Formatting)"]
    PDF --> CT["Contribution Tracker\n(Proof-of-Work Portfolio)"]
    
    classDef agents fill:#bbf,stroke:#333,stroke-width:2px
    classDef engine fill:#ffd,stroke:#333,stroke-width:2px
    classDef generator fill:#dfd,stroke:#333,stroke-width:2px
    classDef tracker fill:#fdb,stroke:#333,stroke-width:2px
    
    class DA agents
    class RE engine
    class PDF generator
    class CT tracker
```

## **6. Deployment Architecture**

```mermaid
flowchart TD
    subgraph "Client Layer"
        Browser["Web Browser"]
        Mobile["Mobile App"]
    end
    
    subgraph "CDN / Edge"
        CDN["Content Delivery Network"]
    end
    
    subgraph "Application Layer"
        subgraph "Kubernetes Cluster"
            IngC["Ingress Controller"]
            APIGateway["API Gateway"]
            
            subgraph "Microservices"
                JobService["Job Preparation Service"]
                ChatService["Chatbot Service"]
                LearnService["Learning Service"]
                ResumeService["Resume Service"]
                Other["Other Services"]
            end
            
            subgraph "Auxiliary Services"
                Auth["Authentication Service"]
                Logging["Logging Service"]
                Monitor["Monitoring Service"]
            end
        end
    end
    
    subgraph "Data Layer"
        MongoDB[(MongoDB)]
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis)]
        VectorDB[(Vector Database)]
    end
    
    subgraph "AI Services"
        Gemini["Gemini API"]
        OpenAI["OpenAI API"]
        Ollama["Ollama (Local LLMs)"]
    end
    
    subgraph "External APIs"
        LinkedIn["LinkedIn API"]
        GitHub["GitHub API"]
        LeetCode["LeetCode API"]
        Other3P["Other 3rd Party APIs"]
    end
    
    Browser --> CDN
    Mobile --> CDN
    CDN --> IngC
    IngC --> APIGateway
    
    APIGateway --> JobService
    APIGateway --> ChatService
    APIGateway --> LearnService
    APIGateway --> ResumeService
    APIGateway --> Other
    APIGateway --> Auth
    
    JobService --> MongoDB
    JobService --> PostgreSQL
    JobService --> VectorDB
    ChatService --> MongoDB
    ChatService --> Redis
    LearnService --> PostgreSQL
    LearnService --> VectorDB
    ResumeService --> MongoDB
    
    JobService --> Gemini
    ChatService --> Gemini
    ChatService --> OpenAI
    ChatService --> Ollama
    LearnService --> Gemini
    ResumeService --> Gemini
    
    JobService --> LinkedIn
    LearnService --> LeetCode
    ResumeService --> GitHub
    
    classDef client fill:#f9f,stroke:#333,stroke-width:1px
    classDef cdn fill:#bbf,stroke:#333,stroke-width:1px
    classDef k8s fill:#dfd,stroke:#333,stroke-width:1px
    classDef service fill:#eff,stroke:#333,stroke-width:1px
    classDef db fill:#ffd,stroke:#333,stroke-width:1px
    classDef ai fill:#ddf,stroke:#333,stroke-width:1px
    classDef external fill:#fdd,stroke:#333,stroke-width:1px
    
    class Browser,Mobile client
    class CDN cdn
    class IngC,APIGateway k8s
    class JobService,ChatService,LearnService,ResumeService,Other,Auth,Logging,Monitor service
    class MongoDB,PostgreSQL,Redis,VectorDB db
    class Gemini,OpenAI,Ollama ai
    class LinkedIn,GitHub,LeetCode,Other3P external
```

## **7. LinkedIn Content Generation Sequence**

```mermaid
sequenceDiagram
    actor User
    participant UI as Web UI
    participant API as API Gateway
    participant LIN as LinkedIn Service
    participant AI as Gemini API
    participant DB as Database

    User->>UI: Request content generation
    UI->>API: POST /api/job-prep/content/generate
    API->>LIN: Forward request
    LIN->>DB: Fetch user profile & preferences
    LIN->>AI: Generate content with context
    AI->>LIN: Return generated content
    LIN->>DB: Store generated content
    LIN->>API: Return content variations
    API->>UI: Display content options
    UI->>User: Show multiple content options
    User->>UI: Select preferred content
    UI->>API: POST /api/job-prep/content/feedback
    API->>DB: Update content ranking
```

## **8. Chatbot with Model Switching Sequence**

```mermaid
sequenceDiagram
    actor User
    participant UI as Web UI
    participant API as API Gateway
    participant MM as Model Manager
    participant KM as Key Manager
    participant CM as Context Manager
    participant AI as AI Models

    User->>UI: Open chat interface
    UI->>API: GET /api/chat/models
    API->>MM: Request available models
    MM->>API: Return model list
    API->>UI: Display model options
    User->>UI: Select model & enter prompt
    UI->>API: POST /api/chat/completions
    API->>KM: Validate API quota
    KM->>API: Confirm quota available
    API->>CM: Fetch conversation context
    CM->>API: Return context history
    API->>MM: Send prompt with context
    MM->>AI: Generate completion
    AI->>MM: Return completion
    MM->>API: Return formatted response
    API->>CM: Store conversation update
    API->>UI: Display response
    UI->>User: Show AI response
```

## **9. RAG Query Processing Sequence**

```mermaid
sequenceDiagram
    actor User
    participant UI as Web UI
    participant API as API Gateway
    participant QP as Query Processor
    participant VS as Vector Store
    participant LLM as LLM Service
    participant DB as Document Store

    User->>UI: Submit query
    UI->>API: POST /api/rag/query
    API->>QP: Process query
    QP->>QP: Generate query embedding
    QP->>VS: Semantic search
    VS->>QP: Return relevant vectors
    QP->>DB: Fetch document chunks
    DB->>QP: Return document content
    QP->>QP: Rerank results
    QP->>LLM: Generate response with context
    LLM->>QP: Return generated answer
    QP->>API: Return answer with sources
    API->>UI: Display answer & references
    UI->>User: Show response & source links
```

## **10. Component Relationship Diagram**

```mermaid
classDiagram
    class User {
        +id: string
        +email: string
        +preferences: UserPreferences
        +apiKeys: ApiKey[]
        +register()
        +login()
        +updatePreferences()
    }
    
    class ApiKey {
        +id: string
        +service: string
        +key: string
        +quotaLimit: number
        +quotaUsed: number
        +isActive: boolean
        +validate()
        +updateUsage()
        +rotate()
    }
    
    class ChatSession {
        +id: string
        +userId: string
        +modelId: string
        +messages: Message[]
        +createMessage()
        +getHistory()
        +summarize()
    }
    
    class Message {
        +id: string
        +sessionId: string
        +role: string
        +content: string
        +timestamp: Date
    }
    
    class LinkedInProfile {
        +id: string
        +userId: string
        +linkedinId: string
        +fullName: string
        +headline: string
        +summary: string
        +fetchFromLinkedIn()
        +optimize()
        +analyze()
    }
    
    class LinkedInPost {
        +id: string
        +userId: string
        +content: string
        +engagement: EngagementMetrics
        +generateVariations()
        +publish()
        +trackPerformance()
    }
    
    class Document {
        +id: string
        +userId: string
        +title: string
        +content: string
        +chunks: DocumentChunk[]
        +process()
        +vectorize()
        +search()
    }
    
    class ModelAdapter {
        +id: string
        +name: string
        +provider: string
        +contextWindow: number
        +initialize()
        +generateResponse()
        +shutdown()
    }
    
    User "1" -- "many" ApiKey
    User "1" -- "many" ChatSession
    User "1" -- "1" LinkedInProfile
    User "1" -- "many" LinkedInPost
    User "1" -- "many" Document
    ChatSession "1" -- "many" Message
    Document "1" -- "many" DocumentChunk
```

## **11. Data Flow Diagram**

```mermaid
flowchart TD
    User((User)) --> |Inputs Query| UI[Web UI]
    UI --> |Sends Request| API[API Gateway]
    API --> |Routes Request| Auth[Authentication]
    Auth --> |Validates| Services{Service Router}
    
    Services --> |Job Prep| JP[Job Preparation]
    Services --> |Chatbot| CB[Chatbot]
    Services --> |Learning| LA[Learning Assistant]
    Services --> |Resume| RB[Resume Builder]
    
    JP --> |LinkedIn Data| LD[(LinkedIn Data)]
    JP --> |Content Generation| Gemini[Gemini API]
    Gemini --> |Generated Content| JP
    JP --> |Store Results| DB[(Database)]
    
    CB --> |Chat History| CH[(Chat History)]
    CB --> |Model Selection| MM[Model Manager]
    MM --> |Local Model| Ollama[Ollama]
    MM --> |Cloud Model| Gemini
    Ollama --> |Response| CB
    Gemini --> |Response| CB
    
    LA --> |Problem Data| PD[(Problem Data)]
    LA --> |Learning Context| LC[(Learning Context)]
    LA --> |Solution Generation| Gemini
    Gemini --> |Explanations| LA
    
    RB --> |Profile Data| Prof[(Profile Data)]
    RB --> |Contribution Data| Contrib[(Contribution Data)]
    RB --> |Resume Generation| Gemini
    Gemini --> |Formatted Resume| RB
    
    DB --> |Analytics| Analytics[Analytics Engine]
    Analytics --> |Insights| UI
    
    classDef user fill:#f9f,stroke:#333,stroke-width:2px
    classDef frontend fill:#bbf,stroke:#333,stroke-width:2px
    classDef api fill:#dfd,stroke:#333,stroke-width:2px
    classDef services fill:#ffd,stroke:#333,stroke-width:2px
    classDef data fill:#ddf,stroke:#333,stroke-width:2px
    classDef ai fill:#fdb,stroke:#333,stroke-width:2px
    
    class User user
    class UI frontend
    class API,Auth api
    class JP,CB,LA,RB services
    class LD,DB,CH,PD,LC,Prof,Contrib data
    class Gemini,Ollama,Analytics ai
```

## **12. Database Schema Diagram**

```mermaid
erDiagram
    USERS {
        id string PK
        email string
        password_hash string
        created_at datetime
        updated_at datetime
    }
    
    API_KEYS {
        id string PK
        user_id string FK
        service string
        api_key string
        quota_limit integer
        quota_used integer
        created_at datetime
    }
    
    QUOTA_SHARES {
        id string PK
        api_key_id string FK
        shared_with_user_id string FK
        quota_amount integer
        expires_at datetime
        created_at datetime
    }
    
    CHAT_SESSIONS {
        id string PK
        user_id string FK
        model_id string
        title string
        created_at datetime
        updated_at datetime
    }
    
    MESSAGES {
        id string PK
        session_id string FK
        role string
        content string
        timestamp datetime
    }
    
    LINKEDIN_PROFILES {
        id string PK
        user_id string FK
        linkedin_id string
        full_name string
        headline string
        summary string
        profile_data json
        last_updated datetime
    }
    
    LINKEDIN_POSTS {
        id string PK
        user_id string FK
        linkedin_post_id string
        content string
        published_at datetime
        engagement_data json
        content_embedding vector
        created_at datetime
    }
    
    DOCUMENTS {
        id string PK
        user_id string FK
        title string
        content string
        metadata json
        created_at datetime
        updated_at datetime
    }
    
    DOCUMENT_CHUNKS {
        id string PK
        document_id string FK
        content string
        start_idx integer
        end_idx integer
        embedding_id string
    }
    
    MODEL_PREFERENCES {
        id string PK
        user_id string FK
        default_model string
        temperature float
        max_tokens integer
        context_window integer
    }
    
    USERS ||--o{ API_KEYS : owns
    USERS ||--o{ CHAT_SESSIONS : creates
    USERS ||--o{ LINKEDIN_PROFILES : has
    USERS ||--o{ LINKEDIN_POSTS : authors
    USERS ||--o{ DOCUMENTS : uploads
    USERS ||--o{ MODEL_PREFERENCES : configures
    
    API_KEYS ||--o{ QUOTA_SHARES : shared_as
    USERS ||--o{ QUOTA_SHARES : receives
    
    CHAT_SESSIONS ||--o{ MESSAGES : contains
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : divided_into
``` 